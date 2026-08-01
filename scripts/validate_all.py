#!/usr/bin/env python3
from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(cmd: list[str]) -> None:
    print("+", " ".join(cmd))
    subprocess.run(cmd, cwd=ROOT, check=True)


def main() -> int:
    try:
        run(["python3", "scripts/build_first_principles_atlas.py"])
        run(["python3", "scripts/validate_first_principles_atlas.py"])
        run(["python3", "scripts/build_lecture_path.py"])
        run(["python3", "scripts/build_site.py"])
        run(["python3", "scripts/validate_site.py"])
        run(["python3", "scripts/validate_handoff.py"])
        run(["python3", "scripts/audit_editorial_quality.py"])
        run(["python3", "scripts/audit_site_render.py"])
    except subprocess.CalledProcessError as exc:
        return exc.returncode
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
