#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PLAYLIST_URL = "https://www.youtube.com/watch?v=WRibE2nt8wM&list=PLUl4u3cNGP63quuKvMHCt3cmTmt0O2qpv"
COURSE_SLUG = "mit-14-12-economic-applications-of-game-theory-fall-2025"
BASE = ROOT / "raw-material/youtube/transcripts" / COURSE_SLUG
SUMMARY = ROOT / "raw-material/youtube/summary.json"
INDEX = ROOT / "raw-material/youtube/transcript-index.json"


def run(cmd: list[str]) -> str:
    proc = subprocess.run(cmd, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=True)
    return proc.stdout


def slugify(value: str) -> str:
    value = value.replace("|", " ")
    value = re.sub(r"[^\w .:()&-]+", "", value, flags=re.UNICODE)
    value = re.sub(r"\s+", " ", value).strip()
    return value[:150]


def clean_vtt(path: Path) -> str:
    lines: list[str] = []
    seen: set[str] = set()
    for raw in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw.strip()
        if not line or line == "WEBVTT" or line.startswith(("Kind:", "Language:", "NOTE")):
            continue
        if "-->" in line or re.match(r"^[0-9]+$", line):
            continue
        line = re.sub(r"<[^>]+>", "", line)
        line = re.sub(r"&amp;", "&", line)
        line = re.sub(r"\s+", " ", line).strip()
        if not line or line in seen:
            continue
        seen.add(line)
        lines.append(line)
    return "\n".join(lines).strip() + "\n"


def select_vtt(raw_dir: Path, video_id: str) -> Path | None:
    candidates = sorted(raw_dir.glob(f"*{video_id}*.vtt"))
    if not candidates:
        return None
    preferred = [path for path in candidates if ".en-orig." in path.name]
    return (preferred or candidates)[0]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--summary-only", action="store_true")
    args = parser.parse_args()

    (BASE / "raw-vtt").mkdir(parents=True, exist_ok=True)
    (BASE / "raw-info").mkdir(parents=True, exist_ok=True)
    (BASE / "clean").mkdir(parents=True, exist_ok=True)
    SUMMARY.parent.mkdir(parents=True, exist_ok=True)

    playlist = json.loads(
        run(["yt-dlp", "--flat-playlist", "--dump-single-json", PLAYLIST_URL])
    )
    entries = playlist.get("entries", [])

    if not args.summary_only:
        output_template = str(BASE / "raw-vtt" / "%(playlist_index)03d-%(id)s-%(title).150B.%(ext)s")
        info_template = str(BASE / "raw-info" / "%(playlist_index)03d-%(id)s-%(title).150B.%(ext)s")
        run(
            [
                "yt-dlp",
                "--skip-download",
                "--write-info-json",
                "--write-subs",
                "--write-auto-subs",
                "--sub-langs",
                "en,en-orig,en-US",
                "--sub-format",
                "vtt",
                "--output",
                output_template,
                "--paths",
                f"infojson:{BASE / 'raw-info'}",
                PLAYLIST_URL,
            ]
        )

    rows: list[dict[str, Any]] = []
    for i, entry in enumerate(entries, 1):
        video_id = entry["id"]
        title = entry["title"]
        raw_vtt = select_vtt(BASE / "raw-vtt", video_id)
        clean_path = BASE / "clean" / f"{i:03d}-{video_id}-{slugify(title)}.txt"
        words = 0
        if raw_vtt and raw_vtt.exists():
            clean = clean_vtt(raw_vtt)
            clean_path.write_text(clean, encoding="utf-8")
            words = len(re.findall(r"\b\w+\b", clean))
        rows.append(
            {
                "course_slug": COURSE_SLUG,
                "course_title": playlist.get("title"),
                "playlist_url": playlist.get("webpage_url") or PLAYLIST_URL,
                "playlist_index": i,
                "video_id": video_id,
                "title": title,
                "url": f"https://www.youtube.com/watch?v={video_id}",
                "duration": entry.get("duration"),
                "raw_vtt": str(raw_vtt.relative_to(ROOT)) if raw_vtt else None,
                "clean_txt": str(clean_path.relative_to(ROOT)) if clean_path.exists() else None,
                "word_count": words,
            }
        )

    summary = {
        "playlist_id": playlist.get("id"),
        "playlist_title": playlist.get("title"),
        "playlist_url": playlist.get("webpage_url") or PLAYLIST_URL,
        "channel": playlist.get("channel"),
        "course_slug": COURSE_SLUG,
        "video_count": len(rows),
        "transcript_count": sum(1 for row in rows if row["clean_txt"]),
        "word_count": sum(row["word_count"] for row in rows),
        "videos": rows,
    }
    SUMMARY.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    INDEX.write_text(json.dumps(rows, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(
        f"wrote {INDEX.relative_to(ROOT)} with {len(rows)} videos, "
        f"{summary['transcript_count']} transcripts, {summary['word_count']} words"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
