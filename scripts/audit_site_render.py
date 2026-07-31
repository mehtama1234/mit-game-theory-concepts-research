#!/usr/bin/env python3
from __future__ import annotations

import os
import socket
import struct
import subprocess
import sys
import time
from pathlib import Path
from shutil import which

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
REPORT = ROOT / "analysis/audits/site-render-report.md"
SCREENSHOTS = ROOT / "analysis/audits/screenshots"
BROWSER_LIBS = ROOT / "analysis/audits/browser-libs"
BROWSER_LIB_PATH = BROWSER_LIBS / "root/usr/lib/x86_64-linux-gnu"
CHROME = Path.home() / ".cache/ms-playwright/chromium_headless_shell-1228/chrome-headless-shell-linux64/chrome-headless-shell"

PAGES = [
    ("desktop-index", "index.html", "1280,900"),
    ("desktop-concepts", "concepts.html", "1280,900"),
    ("desktop-nash-equilibrium", "concepts/nash_equilibrium.html", "1280,900"),
    ("desktop-auctions", "concepts/auctions.html", "1280,900"),
    ("mobile-index", "index.html", "390,844"),
    ("mobile-nash-equilibrium", "concepts/nash_equilibrium.html", "390,844"),
]


def run(cmd: list[str], env: dict[str, str] | None = None, timeout: int = 90, cwd: Path | None = None) -> tuple[int, str]:
    proc = subprocess.run(cmd, cwd=cwd or ROOT, env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=timeout)
    return proc.returncode, proc.stdout.strip()


def browser_env() -> dict[str, str]:
    env = os.environ.copy()
    if BROWSER_LIB_PATH.exists():
        existing = env.get("LD_LIBRARY_PATH", "")
        env["LD_LIBRARY_PATH"] = str(BROWSER_LIB_PATH) + (":" + existing if existing else "")
    return env


def missing_libs(env: dict[str, str]) -> list[str]:
    if not CHROME.exists():
        return ["Playwright Chromium executable missing"]
    code, output = run(["ldd", str(CHROME)], env=env, timeout=30)
    if code != 0:
        return [output or "ldd failed"]
    return [line.strip() for line in output.splitlines() if "not found" in line]


def prepare_browser(env: dict[str, str]) -> tuple[dict[str, str], list[str]]:
    notes = []
    if not missing_libs(env):
        return env, ["Chromium dependencies satisfied by system libraries or existing local cache."]
    if not which("apt-get") or not which("dpkg-deb"):
        return env, ["Missing browser libraries and no local package extraction tools available."]
    package_dir = BROWSER_LIBS / "packages"
    root_dir = BROWSER_LIBS / "root"
    package_dir.mkdir(parents=True, exist_ok=True)
    root_dir.mkdir(parents=True, exist_ok=True)
    code, output = run(["apt-get", "download", "libnspr4", "libnss3", "libasound2t64"], env=env, timeout=120, cwd=package_dir)
    if code != 0:
        return env, [output]
    for deb in package_dir.glob("*.deb"):
        run(["dpkg-deb", "-x", str(deb), str(root_dir)], env=env, timeout=60)
    env = browser_env()
    notes.append("Chromium dependencies satisfied by ignored local browser-lib cache." if not missing_libs(env) else "Browser libraries still missing.")
    return env, notes


def find_port() -> int:
    for port in range(8896, 8916):
        sock = socket.socket()
        try:
            sock.bind(("127.0.0.1", port))
            return port
        except OSError:
            continue
        finally:
            sock.close()
    raise RuntimeError("no free port")


def png_size(path: Path) -> tuple[int, int]:
    with path.open("rb") as handle:
        if handle.read(8) != b"\x89PNG\r\n\x1a\n":
            raise ValueError(f"{path} is not a PNG")
        handle.read(4)
        if handle.read(4) != b"IHDR":
            raise ValueError(f"{path} has no IHDR")
        return struct.unpack(">II", handle.read(8))


def main() -> int:
    errors: list[str] = []
    SCREENSHOTS.mkdir(parents=True, exist_ok=True)
    env, notes = prepare_browser(browser_env())
    errors.extend(missing_libs(env))
    port = find_port()
    server = subprocess.Popen([sys.executable, "-m", "http.server", str(port), "--directory", str(SITE)], cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(0.5)
    rows = []
    try:
        for name, page, viewport in PAGES:
            target = SCREENSHOTS / f"{name}.png"
            code, output = run(["npx", "-y", "playwright", "screenshot", f"--viewport-size={viewport}", "--wait-for-timeout=500", f"http://127.0.0.1:{port}/{page}", str(target)], env=env, timeout=120)
            if code != 0:
                errors.append(f"{name} failed: {output}")
                continue
            width, height = png_size(target)
            size = target.stat().st_size
            expected = tuple(int(x) for x in viewport.split(","))
            if (width, height) != expected:
                errors.append(f"{name} expected {viewport}, got {width}x{height}")
            if size < 20_000:
                errors.append(f"{name} screenshot suspiciously small: {size}")
            rows.append((name, page, viewport, width, height, size))
    finally:
        server.terminate()
        try:
            server.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server.kill()

    lines = ["# Site Render Report", "", "Playwright render audit for representative desktop and mobile pages.", "", "## Browser Setup", ""]
    lines.extend(f"- {note}" for note in notes)
    lines.extend(["", "## Screenshots", ""])
    for row in rows:
        lines.append(f"- {row[0]}: `{row[1]}`, viewport {row[2]}, captured {row[3]}x{row[4]}, {row[5]} bytes")
    lines.extend(["", "## Errors", ""])
    lines.extend(f"- {e}" for e in errors) if errors else lines.append("- None")
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"render-audited {len(rows)} screenshots; errors: {len(errors)}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
