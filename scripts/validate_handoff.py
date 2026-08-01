#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HANDOFF = ROOT / "HANDOFF.md"
README = ROOT / "README.md"


def main() -> int:
    errors: list[str] = []
    if not HANDOFF.exists():
        errors.append("missing HANDOFF.md")
        text = ""
    else:
        text = HANDOFF.read_text(encoding="utf-8")
    readme = README.read_text(encoding="utf-8") if README.exists() else ""

    required_phrases = [
        "MIT 14.12 Economic Applications of Game Theory",
        "site/review-guide.html",
        "site/publication-status.html",
        "analysis/audits/editorial-quality-report.md",
        "analysis/audits/publication-readiness-report.md",
        "http://127.0.0.1:8899/review-guide.html",
        "http://127.0.0.1:8899/publication-status.html",
        "python3 scripts/build_first_principles_atlas.py",
        "python3 scripts/build_lecture_path.py",
        "python3 scripts/build_site.py",
        "python3 scripts/validate_all.py",
        "python3 -m py_compile scripts/*.py",
        "git diff --check",
        "origin/main",
        "origin/gh-pages",
        "git subtree split --prefix site",
        "Your current plan does not support GitHub Pages for this repository.",
        "public GitHub Pages serving still blocked",
        "analysis/concepts/concept-atlas.json",
        "analysis/evidence/evidence-ledger.json",
        "analysis/throughlines/publication-status.json",
        "scripts/validate_handoff.py",
        ".openai/hosting.json",
        "package.json",
        "app/page.tsx",
        "scripts/prepare_sites_public.mjs",
        "scripts/finalize_sites_dist.mjs",
        "npm run check:site-app",
        "npm run build",
        "dist/.openai/hosting.json",
        "The Sites project id is stored in `.openai/hosting.json`.",
        "https://mit-game-theory-concept-lab.manish694182.chatgpt.site",
        "owner-only custom access",
        "exact latest version and deployment ids should be checked",
    ]
    for phrase in required_phrases:
        if phrase not in text:
            errors.append(f"HANDOFF.md missing required phrase: {phrase}")

    required_sections = [
        "## What Is Built",
        "## Fast Local Review",
        "## Validation Command",
        "## Publication Boundary",
        "## Main Source Artifacts",
        "## Build Scripts",
        "## Sites Deployment Wrapper",
        "## Push And Generated-Site Refresh",
        "## What To Improve Next",
    ]
    for section in required_sections:
        if section not in text:
            errors.append(f"HANDOFF.md missing section: {section}")

    if "HANDOFF.md" not in readme:
        errors.append("README.md does not link HANDOFF.md")
    if "site/publication-status.html" not in readme:
        errors.append("README.md does not link publication status page")
    if "not the same as a live public site" not in text:
        errors.append("HANDOFF.md does not separate gh-pages from public hosting")

    if errors:
        for error in errors:
            print(error)
        return 1
    print("validated HANDOFF.md and README.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
