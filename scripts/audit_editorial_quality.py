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
    "lecture_depth_walkthrough",
    "mathematical_intuition",
    "why_math_has_to_exist",
    "why_it_matters",
    "what_breaks_without_it",
    "naive_problem",
    "failed_simple_approach",
    "mathematical_object",
    "operation",
    "worked_mini_example",
    "student_trap",
    "course_boundary_note",
    "lecture_emphasis",
    "common_misunderstanding",
    "cross_course_connections",
    "recognize_in_new_work",
]

REQUIRED_HEADINGS = [
    "What real-world problem is this about?",
    "Why does this problem exist?",
    "What is the mathematical idea underneath?",
    "Lecture-Depth Walkthrough",
    "Mathematical Intuition",
    "Why This Mathematical Object Has To Exist",
    "Why is this concept important?",
    "What breaks without it?",
    "Worked Mini-Example",
    "Where Students Get Stuck",
    "Where The Idea Stops Working",
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
    "this concept matters because it turns a loose strategic story into a checkable claim",
    "without this concept, the analysis can name the players and choices",
    "the naive move is to describe what happened and call it rational",
    "the simple story fails when another feasible action",
    "the lecture treats this as a working instrument",
    "the same primitive returns whenever the course asks whether",
    "the important lecture move is that the instructor is not merely naming",
    "it also helps separate transcript evidence from atlas synthesis",
    "not a lecture label",
    "the mathematical spine is built from primitives such as",
    "evidence comes from the listed concept pages",
]


def words(text: str) -> int:
    return len(re.findall(r"\b\w+\b", text))


def repeated_adjacent_ngrams(text: str) -> int:
    tokens = re.findall(r"\b\w+\b", text.lower())
    repeats = 0
    for width in range(2, 8):
        for i in range(len(tokens) - (2 * width) + 1):
            if tokens[i : i + width] == tokens[i + width : i + 2 * width]:
                repeats += 1
    return repeats


def main() -> int:
    errors: list[str] = []
    concepts = json.loads((ROOT / "analysis/concepts/concept-atlas.json").read_text(encoding="utf-8"))
    themes = json.loads((ROOT / "analysis/themes/theme-map.json").read_text(encoding="utf-8"))
    subthemes = json.loads((ROOT / "analysis/themes/subtheme-map.json").read_text(encoding="utf-8"))
    evidence = json.loads((ROOT / "analysis/evidence/evidence-ledger.json").read_text(encoding="utf-8"))
    lectures = json.loads((ROOT / "analysis/lectures/lecture-path.json").read_text(encoding="utf-8"))
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
        if count < 620:
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

    for field in [field for field in CONCEPT_FIELDS if field != "mathematical_principle"]:
        seen: dict[str, list[str]] = {}
        for concept in concepts:
            value = str(concept.get(field, "")).strip()
            seen.setdefault(value, []).append(concept["id"])
        for value, ids in seen.items():
            if value and len(ids) > 1:
                errors.append(f"concept {field} repeated across pages: {', '.join(ids[:4])}")

    theme_words = [words(" ".join(str(t.get(f, "")) for f in ["big_picture", "why_this_theme_matters", "cross_course_argument", "mathematical_spine", "where_analogy_breaks", "lecture_evidence_chain"])) for t in themes]
    subtheme_words = [words(" ".join(str(s.get(f, "")) for f in ["everyday_problem", "hidden_principle", "mathematical_lever", "why_it_matters", "first_principles_walkthrough", "cross_links_and_limits"])) for s in subthemes]
    primitive_words = [words(" ".join(str(p.get(f, "")) for f in ["everyday_setup", "plain_language_principle", "formal_object", "symbol_explanation", "course_appearances", "why_it_matters", "misuse_warning"])) for p in primitives]
    family_words = [words(" ".join(str(f.get(k, "")) for k in ["family_problem", "first_principles_pattern", "mathematical_signature", "why_family_matters", "family_walkthrough", "where_analogy_breaks", "lecture_evidence_chain", "paper_family_treatment"])) for f in families]
    deep_evidence = [record for record in evidence if record.get("transcript_teaching_note") and record.get("evidence_boundary")]
    weak_evidence = [
        record
        for record in evidence
        if record.get("confidence") == "weak" or "weak" in str(record.get("evidence_boundary", "")).lower()
    ]
    if len(deep_evidence) < len(evidence):
        errors.append(f"only {len(deep_evidence)} evidence records have transcript teaching notes")
    if weak_evidence:
        errors.append(f"{len(weak_evidence)} evidence records still marked weak")
    overlap_records = [record for record in evidence if repeated_adjacent_ngrams(record.get("local_transcript_window", ""))]
    if overlap_records:
        errors.append(f"{len(overlap_records)} evidence windows contain repeated caption overlap")
    if len(lectures) != 25:
        errors.append(f"lecture path has {len(lectures)} lectures")
    lecture_words = [words(f"{lecture.get('first_principles_role', '')} {lecture.get('what_to_watch_for', '')}") for lecture in lectures]
    for lecture, count in zip(lectures, lecture_words):
        if count < 30:
            errors.append(f"lecture {lecture['id']} has shallow path treatment: {count} words")
    lecture_page_words = []
    for lecture in lectures:
        path = SITE / "lectures" / f"{lecture['id']}.html"
        if not path.exists():
            errors.append(f"lecture detail page missing: {lecture['id']}")
            continue
        text = path.read_text(encoding="utf-8")
        detail_words = words(text)
        lecture_page_words.append(detail_words)
        if detail_words < 450:
            errors.append(f"lecture detail page {lecture['id']} is shallow: {detail_words} words")
        for heading in ["What This Lecture Teaches", "Where The Math Enters", "Mistakes To Avoid", "How To Recognize This Later", "Transcript Evidence Chain"]:
            if heading not in text:
                errors.append(f"lecture detail page {lecture['id']} missing heading: {heading}")

    for theme, count in zip(themes, theme_words):
        if count < 180:
            errors.append(f"theme {theme['id']} has low synthesis depth: {count} words")
    for subtheme, count in zip(subthemes, subtheme_words):
        if count < 180:
            errors.append(f"subtheme {subtheme['id']} has low synthesis depth: {count} words")
    for primitive, count in zip(primitives, primitive_words):
        if count < 140:
            errors.append(f"primitive {primitive['id']} has low synthesis depth: {count} words")
    for family, count in zip(families, family_words):
        if count < 180:
            errors.append(f"method family {family['id']} has low synthesis depth: {count} words")

    for field in ["lecture_argument", "why_span_matters", "conceptual_payload"]:
        seen: dict[str, list[str]] = {}
        for record in evidence:
            value = str(record.get(field, "")).strip()
            seen.setdefault(value, []).append(record["id"])
        for value, ids in seen.items():
            if value and len(ids) > 1:
                errors.append(f"evidence {field} repeated across records: {', '.join(ids[:4])}")

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
        f"- Evidence records with transcript teaching notes: {len(deep_evidence)}",
        f"- Evidence records still marked weak: {len(weak_evidence)}",
        f"- Evidence windows with repeated caption overlap: {len(overlap_records)}",
        f"- Lecture path entries: {len(lectures)}",
        f"- Lecture path treatment words: min {min(lecture_words)}, max {max(lecture_words)}",
        f"- Lecture detail page words: min {min(lecture_page_words) if lecture_page_words else 0}, max {max(lecture_page_words) if lecture_page_words else 0}",
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
