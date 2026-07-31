#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
REPORT = ROOT / "analysis/audits/editorial-quality-report.md"

CONCEPT_FIELDS = [
    "everyday_problem",
    "first_principles_reason",
    "mathematical_principle",
    "why_it_matters",
    "what_breaks_without_it",
    "naive_problem",
    "failed_simple_approach",
    "mathematical_object",
    "operation",
    "worked_mini_example",
    "lecture_emphasis",
    "common_misunderstanding",
    "cross_course_connections",
    "recognize_in_new_work",
]

REQUIRED_HEADINGS = [
    "What real-world problem is this about?",
    "Why does this problem exist?",
    "What is the mathematical idea underneath?",
    "Why is this concept important?",
    "What breaks without it?",
    "Worked Mini-Example",
    "Common Misunderstanding",
    "How to Recognize This in a New Paper or Model",
    "Transcript Evidence",
]

FORBIDDEN = [
    "this improves performance",
    "lorem ipsum",
    "todo",
    "placeholder",
    "course-level support",
    "as vocabulary to memorize",
    "strategic settings are interdependent: a choice is not good by itself",
    "a naive approach would ask what one person wants and stop there",
    "mini-example: suppose two firms, bidders, negotiators, or speakers face each other",
    "look for the same pressure: someone chooses under strategic dependence",
    "as a label to memorize",
]


def words(text: str) -> int:
    return len(re.findall(r"\b\w+\b", text))


def main() -> int:
    errors: list[str] = []
    concepts = json.loads((ROOT / "analysis/concepts/concept-atlas.json").read_text(encoding="utf-8"))
    themes = json.loads((ROOT / "analysis/themes/theme-map.json").read_text(encoding="utf-8"))
    subthemes = json.loads((ROOT / "analysis/themes/subtheme-map.json").read_text(encoding="utf-8"))
    evidence = json.loads((ROOT / "analysis/evidence/evidence-ledger.json").read_text(encoding="utf-8"))
    primitives = json.loads((ROOT / "analysis/throughlines/primitives.json").read_text(encoding="utf-8"))
    families = json.loads((ROOT / "analysis/throughlines/method-families.json").read_text(encoding="utf-8"))

    ev_by_concept: dict[str, list[str]] = {}
    for ev in evidence:
        for cid in ev["supports_concepts"]:
            ev_by_concept.setdefault(cid, []).append(ev["id"])

    rows = []
    for concept in concepts:
        count = words(" ".join(str(concept.get(field, "")) for field in CONCEPT_FIELDS))
        ev_count = len(ev_by_concept.get(concept["id"], []))
        html = (SITE / "concepts" / f"{concept['id']}.html").read_text(encoding="utf-8")
        if count < 420:
            errors.append(f"concept {concept['id']} has low teaching depth: {count} words")
        if ev_count < 1:
            errors.append(f"concept {concept['id']} has no reviewed evidence")
        for heading in REQUIRED_HEADINGS:
            if heading not in html:
                errors.append(f"concept {concept['id']} missing heading: {heading}")
        rows.append((concept["id"], count, ev_count))

    site_text = "\n".join(path.read_text(encoding="utf-8", errors="ignore") for path in SITE.rglob("*.html")).lower()
    for phrase in FORBIDDEN:
        if phrase in site_text:
            errors.append(f"published site contains forbidden phrase: {phrase}")

    theme_words = [words(" ".join(str(t.get(f, "")) for f in ["big_picture", "cross_course_argument", "mathematical_spine", "where_analogy_breaks", "lecture_evidence_chain"])) for t in themes]
    subtheme_words = [words(" ".join(str(s.get(f, "")) for f in ["everyday_problem", "hidden_principle", "mathematical_lever", "why_it_matters", "first_principles_walkthrough", "cross_links_and_limits"])) for s in subthemes]
    primitive_words = [words(" ".join(str(p.get(f, "")) for f in ["everyday_setup", "formal_object", "symbol_explanation", "course_appearances", "misuse_failure"])) for p in primitives]
    family_words = [words(" ".join(str(f.get(k, "")) for k in ["family_walkthrough", "where_analogy_breaks", "lecture_evidence_chain", "paper_family_treatment"])) for f in families]

    lines = [
        "# Editorial Quality Report",
        "",
        "This static audit checks explanatory depth, required teaching sections, evidence coverage, and generic prose in the generated site.",
        "",
        "## Summary",
        "",
        f"- Concepts audited: {len(concepts)}",
        f"- Concept teaching words: min {min(r[1] for r in rows)}, max {max(r[1] for r in rows)}",
        f"- Evidence per concept: min {min(r[2] for r in rows)}, max {max(r[2] for r in rows)}",
        f"- Theme treatment words: min {min(theme_words)}, max {max(theme_words)}",
        f"- Subtheme treatment words: min {min(subtheme_words)}, max {max(subtheme_words)}",
        f"- Primitive treatment words: min {min(primitive_words)}, max {max(primitive_words)}",
        f"- Method-family treatment words: min {min(family_words)}, max {max(family_words)}",
        f"- Errors: {len(errors)}",
        "",
        "## Lowest Concept Depth",
        "",
    ]
    for cid, count, ev_count in sorted(rows, key=lambda row: row[1])[:10]:
        lines.append(f"- {cid}: {count} teaching words, {ev_count} evidence records")
    lines.extend(["", "## Errors", ""])
    lines.extend(f"- {error}" for error in errors) if errors else lines.append("- None")
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"audited editorial quality for {len(concepts)} concepts; errors: {len(errors)}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
