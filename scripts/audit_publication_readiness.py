#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
REPORT = ROOT / "analysis/audits/publication-readiness-report.md"


def run(cmd: list[str]) -> tuple[int, str]:
    proc = subprocess.run(cmd, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return proc.returncode, proc.stdout.strip()


def main() -> int:
    concepts = json.loads((ROOT / "analysis/concepts/concept-atlas.json").read_text(encoding="utf-8"))
    themes = json.loads((ROOT / "analysis/themes/theme-map.json").read_text(encoding="utf-8"))
    subthemes = json.loads((ROOT / "analysis/themes/subtheme-map.json").read_text(encoding="utf-8"))
    evidence = json.loads((ROOT / "analysis/evidence/evidence-ledger.json").read_text(encoding="utf-8"))
    lectures = json.loads((ROOT / "analysis/lectures/lecture-path.json").read_text(encoding="utf-8"))
    supplemental = json.loads((ROOT / "analysis/lectures/lecture-evidence.json").read_text(encoding="utf-8"))
    primitives = json.loads((ROOT / "analysis/throughlines/primitives.json").read_text(encoding="utf-8"))
    derivations = json.loads((ROOT / "analysis/throughlines/derivations.json").read_text(encoding="utf-8"))
    families = json.loads((ROOT / "analysis/throughlines/method-families.json").read_text(encoding="utf-8"))
    first_principles_essays = json.loads((ROOT / "analysis/throughlines/first-principles-essays.json").read_text(encoding="utf-8"))
    why_matters = json.loads((ROOT / "analysis/throughlines/why-matters-checkpoints.json").read_text(encoding="utf-8"))
    application_map = json.loads((ROOT / "analysis/throughlines/application-map.json").read_text(encoding="utf-8"))
    everyday_glossary = json.loads((ROOT / "analysis/throughlines/everyday-glossary.json").read_text(encoding="utf-8"))
    review_cards = json.loads((ROOT / "analysis/throughlines/review-guide.json").read_text(encoding="utf-8"))
    publication_status = json.loads((ROOT / "analysis/throughlines/publication-status.json").read_text(encoding="utf-8"))
    queue = json.loads((ROOT / "analysis/evidence/evidence-review-queue.json").read_text(encoding="utf-8"))
    summary = json.loads((ROOT / "raw-material/youtube/summary.json").read_text(encoding="utf-8"))
    first_principles_coverage = {
        concept_id
        for collection in [first_principles_essays, application_map, everyday_glossary]
        for item in collection
        for concept_id in item.get("concept_ids", [])
    }

    log_code, log = run(["git", "log", "-1", "--oneline"])
    remote_code, remote = run(["git", "remote", "-v"])
    validation_code, validation = run(["python3", "scripts/validate_all.py"])

    lines = [
        "# Publication Readiness Report",
        "",
        "This report records local readiness evidence. Remote publication is verified by the final git status and push result.",
        "",
        "## Audit-Time Git Checkpoint",
        "",
        "```text",
        f"$ git log -1 --oneline\n{log or 'no commits yet'}",
        f"\n$ git remote -v\n{remote or 'No remote configured'}",
        "```",
        "",
        "## Corpus And Artifacts",
        "",
        f"- Playlist: {summary['playlist_title']}",
        f"- Videos: {summary['video_count']}",
        f"- Clean transcripts: {summary['transcript_count']}",
        f"- Transcript words: {summary['word_count']}",
        f"- Concepts: {len(concepts)}",
        f"- Themes: {len(themes)}",
        f"- Subthemes: {len(subthemes)}",
        f"- Evidence records: {len(evidence)}",
        f"- Lecture path entries: {len(lectures)}",
        f"- Supplemental lecture evidence records: {len(supplemental)}",
        f"- Evidence records queued for review: {len(queue)}",
        f"- Mathematical primitives: {len(primitives)}",
        f"- Derivation cards: {len(derivations)}",
        f"- Method families: {len(families)}",
        f"- First-principles essay cards: {len(first_principles_essays)}",
        f"- Why-it-matters checkpoints: {len(why_matters)}",
        f"- Cross-field application map cards: {len(application_map)}",
        f"- Everyday glossary terms: {len(everyday_glossary)}",
        f"- Concepts covered by first-principles layer: {len(first_principles_coverage & {concept['id'] for concept in concepts})}",
        f"- Review guide cards: {len(review_cards)}",
        f"- Publication status cards: {len(publication_status)}",
        f"- Root handoff present: {(ROOT / 'HANDOFF.md').exists()}",
        f"- Site HTML files: {len(list(SITE.rglob('*.html')))}",
        "",
        "## Validation Evidence",
        "",
        "```text",
        validation,
        "```",
        "",
        "## Requirement Audit",
        "",
        "- Transcript corpus: proven locally by `raw-material/youtube/transcript-index.json` and `summary.json`.",
        "- First-principles concept atlas: proven structurally by `scripts/validate_first_principles_atlas.py`; prose uses required hand-crafted overrides.",
        "- Evidence discipline: every concept has two transcript evidence records with local transcript windows and YouTube links.",
        "- Generic-template guard: validators reject the original template phrases in generated concept prose and published HTML.",
        "- Course-wide first-principles essay layer: `first-principles.html` gives plain-language long-form explanations of the whole course, why-it-matters checkpoints, a structured cross-field application map, and an everyday glossary for core vocabulary.",
        "- Plain-language style gate: `scripts/audit_plain_language.py` rejects banned filler, shallow essay sections, missing everyday setup, and missing limits or mistake language.",
        "- First-principles concept integration: every concept page links back to relevant course essays, application maps, or glossary entries.",
        "- Reviewability: `review-guide.html` gives an explicit route for checking first-principles depth, lecture faithfulness, math clarity, reader practice, and publication state.",
        "- Publication status: `publication-status.html` separates local build proof, remote branch proof, generated-site-branch proof, and public-hosting proof.",
        "- Handoff: `HANDOFF.md` gives a durable root-level review and continuation guide.",
        "- Reader-facing site: proven by static generation, link validation, evidence-anchor validation, diagrams, and screenshot render audit.",
        "- Remote sync: verified outside this report by `git status --short --branch`, `git log -1 --oneline`, remote branch hashes, and the push result.",
        "- Public hosting: a pushed `gh-pages` branch is not the same as an enabled public Pages URL; hosting status must be checked separately.",
        "",
        "## Browser Tooling",
        "",
        f"- node available: {bool(shutil.which('node'))}",
        f"- npx available: {bool(shutil.which('npx'))}",
        "",
        "## Current Conclusion",
        "",
        "Local research/build readiness is stronger than the first committed pass: the atlas now has hand-authored synthesis for themes, subthemes, primitives, method families, evidence payloads, a course-wide first-principles essay layer, why-it-matters checkpoints, a structured cross-field application map, an everyday glossary, a reviewer-facing audit route, an explicit publication-status surface, and a root handoff, with validators that reject the older generic patterns.",
        "",
    ]
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(lines), encoding="utf-8")
    print("wrote analysis/audits/publication-readiness-report.md")
    return validation_code


if __name__ == "__main__":
    raise SystemExit(main())
