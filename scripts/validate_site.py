#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from urllib.parse import urldefrag

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"


def main() -> int:
    errors: list[str] = []
    concepts = json.loads((ROOT / "analysis/concepts/concept-atlas.json").read_text(encoding="utf-8"))
    evidence = json.loads((ROOT / "analysis/evidence/evidence-ledger.json").read_text(encoding="utf-8"))
    lectures = json.loads((ROOT / "analysis/lectures/lecture-path.json").read_text(encoding="utf-8"))
    required = [SITE / name for name in ["index.html", "lectures.html", "concepts.html", "themes.html", "families.html", "primitives.html", "evidence.html", "assets/styles.css"]]
    required.extend(SITE / "concepts" / f"{c['id']}.html" for c in concepts)
    required.extend(SITE / "lectures" / f"{lecture['id']}.html" for lecture in lectures)
    for path in required:
        if not path.exists():
            errors.append(f"missing site file: {path.relative_to(ROOT)}")
    html_files = list(SITE.rglob("*.html"))
    evidence_html = (SITE / "evidence.html").read_text(encoding="utf-8") if (SITE / "evidence.html").exists() else ""
    lectures_html = (SITE / "lectures.html").read_text(encoding="utf-8") if (SITE / "lectures.html").exists() else ""
    if len(lectures) != 25:
        errors.append(f"expected 25 lectures, found {len(lectures)}")
    for lecture in lectures:
        if f'id="{lecture["id"]}"' not in lectures_html:
            errors.append(f"missing lecture anchor: {lecture['id']}")
        if not lecture.get("first_principles_role") or not lecture.get("what_to_watch_for"):
            errors.append(f"lecture missing treatment: {lecture['id']}")
        detail = SITE / "lectures" / f"{lecture['id']}.html"
        if detail.exists():
            text = detail.read_text(encoding="utf-8")
            for heading in ["What This Lecture Teaches", "Where The Math Enters", "Mistakes To Avoid", "Transcript Evidence Chain"]:
                if heading not in text:
                    errors.append(f"lecture page {lecture['id']} missing heading: {heading}")
            for ev_id in lecture["evidence_ids"]:
                if f'id="{ev_id}"' not in text:
                    errors.append(f"lecture page {lecture['id']} missing evidence {ev_id}")
    for ev in evidence:
        if f'id="{ev["id"]}"' not in evidence_html:
            errors.append(f"missing evidence anchor: {ev['id']}")
    for concept in concepts:
        text = (SITE / "concepts" / f"{concept['id']}.html").read_text(encoding="utf-8")
        if 'class="learning-diagram concept-flow"' not in text:
            errors.append(f"concept page missing diagram: {concept['id']}")
        if "Transcript Evidence" not in text:
            errors.append(f"concept page missing evidence section: {concept['id']}")
    for path in html_files:
        text = path.read_text(encoding="utf-8")
        if "<main>" not in text or "</main>" not in text:
            errors.append(f"missing main element: {path.relative_to(ROOT)}")
        for href in re.findall(r'href="([^"]+)"', text):
            if href.startswith(("http://", "https://", "mailto:")):
                continue
            href_path, frag = urldefrag(href)
            target = (path.parent / href_path).resolve() if href_path else path.resolve()
            try:
                target.relative_to(SITE.resolve())
            except ValueError:
                errors.append(f"link escapes site: {path.relative_to(ROOT)} -> {href}")
                continue
            if href_path and not target.exists():
                errors.append(f"broken link: {path.relative_to(ROOT)} -> {href}")
            if frag and target.exists() and f'id="{frag}"' not in target.read_text(encoding="utf-8"):
                errors.append(f"missing anchor: {path.relative_to(ROOT)} -> {href}")
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"validated {len(html_files)} html files and {len(evidence)} evidence anchors")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
