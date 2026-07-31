#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


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
    concepts = load("analysis/concepts/concept-atlas.json")
    themes = load("analysis/themes/theme-map.json")
    subthemes = load("analysis/themes/subtheme-map.json")
    evidence = load("analysis/evidence/evidence-ledger.json")
    primitives = load("analysis/throughlines/primitives.json")
    families = load("analysis/throughlines/method-families.json")
    forbidden_generic = [
        "strategic settings are interdependent: a choice is not good by itself",
        "A naive approach would ask what one person wants and stop there",
        "Mini-example: suppose two firms, bidders, negotiators, or speakers face each other",
        "look for the same pressure: someone chooses under strategic dependence",
        "as a label to memorize",
        "This concept matters because it turns a loose strategic story into a checkable claim",
        "Without this concept, the analysis can name the players and choices",
        "The naive move is to describe what happened and call it rational",
        "The simple story fails when another feasible action",
        "The lecture treats this as a working instrument",
        "The same primitive returns whenever the course asks whether",
        "not a lecture label",
        "The mathematical spine is built from primitives such as",
        "Evidence comes from the listed concept pages",
    ]
    forbidden_evidence = [
        "the course treats",
        "as a mechanism for the strategic problem where choices, beliefs, timing, or information change what a person should do",
        "The important lecture move is that the instructor is not merely naming",
        "It also helps separate transcript evidence from atlas synthesis",
    ]

    concept_ids = {c["id"] for c in concepts}
    theme_ids = {t["id"] for t in themes}
    subtheme_ids = {s["id"] for s in subthemes}
    evidence_ids = [e["id"] for e in evidence]
    if len(evidence_ids) != len(set(evidence_ids)):
        errors.append("duplicate evidence ids")

    concept_fields = [
        "plain_language_definition", "everyday_problem", "first_principles_reason", "mathematical_principle",
        "lecture_depth_walkthrough", "mathematical_intuition", "why_math_has_to_exist",
        "why_it_matters", "what_breaks_without_it", "naive_problem", "failed_simple_approach",
        "mathematical_object", "operation", "worked_mini_example", "student_trap", "course_boundary_note", "lecture_emphasis",
        "common_misunderstanding", "cross_course_connections", "recognize_in_new_work",
    ]
    for concept in concepts:
        concept_blob = " ".join(str(concept.get(field, "")) for field in concept_fields)
        for phrase in forbidden_generic:
            if phrase in concept_blob:
                errors.append(f"concept {concept['id']} contains generic template phrase: {phrase}")
        if concept.get("theme_id") not in theme_ids:
            errors.append(f"concept {concept['id']} has missing theme")
        if len(concept.get("course_evidence_ids", [])) < 1:
            errors.append(f"concept {concept['id']} has no evidence")
        if sum(words(str(concept.get(field, ""))) for field in concept_fields) < 620:
            errors.append(f"concept {concept['id']} is shallow")
        if re.match(r"^(equilibrium|utility|preference|Bayesian|Nash|dominance)\b", concept.get("everyday_problem", ""), re.I):
            errors.append(f"concept {concept['id']} starts with jargon")
        for ev_id in concept.get("course_evidence_ids", []):
            if ev_id not in evidence_ids:
                errors.append(f"concept {concept['id']} references missing evidence {ev_id}")

    for theme in themes:
        if not theme.get("subthemes"):
            errors.append(f"theme {theme['id']} has no subthemes")
        for sub_id in theme.get("subthemes", []):
            if sub_id not in subtheme_ids:
                errors.append(f"theme {theme['id']} references missing subtheme {sub_id}")
        if words(" ".join(str(theme.get(f, "")) for f in ["big_picture", "why_this_theme_matters", "cross_course_argument", "mathematical_spine", "where_analogy_breaks", "lecture_evidence_chain"])) < 180:
            errors.append(f"theme {theme['id']} is shallow")

    for subtheme in subthemes:
        if subtheme.get("parent_theme") not in theme_ids:
            errors.append(f"subtheme {subtheme['id']} missing parent theme")
        if not subtheme.get("examples_from_courses"):
            errors.append(f"subtheme {subtheme['id']} has no examples")
        if words(" ".join(str(subtheme.get(f, "")) for f in ["everyday_problem", "hidden_principle", "mathematical_lever", "why_it_matters", "first_principles_walkthrough", "cross_links_and_limits"])) < 180:
            errors.append(f"subtheme {subtheme['id']} is shallow")

    for record in evidence:
        for phrase in forbidden_evidence:
            if phrase in record.get("lecture_argument", ""):
                errors.append(f"evidence {record['id']} contains generic evidence phrase: {phrase}")
        if len(record.get("lecture_argument", "").split()) < 22:
            errors.append(f"evidence {record['id']} has shallow lecture_argument")
        if len(record.get("example_or_analogy", "").split()) < 18:
            errors.append(f"evidence {record['id']} has shallow example_or_analogy")
        if len(record.get("why_span_matters", "").split()) < 18:
            errors.append(f"evidence {record['id']} has shallow why_span_matters")
        if record.get("transcript_teaching_note") and len(record["transcript_teaching_note"].split()) < 35:
            errors.append(f"evidence {record['id']} has shallow transcript_teaching_note")
        if record.get("evidence_boundary") and len(record["evidence_boundary"].split()) < 20:
            errors.append(f"evidence {record['id']} has shallow evidence_boundary")
        if not (ROOT / record["transcript_path"]).exists():
            errors.append(f"evidence {record['id']} transcript missing")
        if words(record.get("local_transcript_window", "")) < 8:
            errors.append(f"evidence {record['id']} has weak window")
        if repeated_adjacent_ngrams(record.get("local_transcript_window", "")):
            errors.append(f"evidence {record['id']} has repeated caption overlap")
        if not record.get("matched_terms"):
            errors.append(f"evidence {record['id']} missing matched terms")
        for concept_id in record.get("supports_concepts", []):
            if concept_id not in concept_ids:
                errors.append(f"evidence {record['id']} missing concept {concept_id}")
        for sub_id in record.get("supports_subthemes", []):
            if sub_id not in subtheme_ids:
                errors.append(f"evidence {record['id']} missing subtheme {sub_id}")

    deep_evidence = [record for record in evidence if record.get("transcript_teaching_note") and record.get("evidence_boundary")]
    if len(deep_evidence) < len(evidence):
        errors.append(f"only {len(deep_evidence)} evidence records have transcript teaching notes")
    weak_evidence = [
        record
        for record in evidence
        if record.get("confidence") == "weak" or "weak" in str(record.get("evidence_boundary", "")).lower()
    ]
    if weak_evidence:
        errors.append(f"{len(weak_evidence)} evidence records still marked weak")

    for field in [field for field in concept_fields if field != "mathematical_principle"]:
        seen: dict[str, list[str]] = {}
        for concept in concepts:
            value = str(concept.get(field, "")).strip()
            seen.setdefault(value, []).append(concept["id"])
        for value, ids in seen.items():
            if value and len(ids) > 1:
                errors.append(f"concept {field} repeated across pages: {', '.join(ids[:4])}")

    for field in ["lecture_argument", "why_span_matters", "conceptual_payload"]:
        seen: dict[str, list[str]] = {}
        for record in evidence:
            value = str(record.get(field, "")).strip()
            seen.setdefault(value, []).append(record["id"])
        for value, ids in seen.items():
            if value and len(ids) > 1:
                errors.append(f"evidence {field} repeated across records: {', '.join(ids[:4])}")

    for primitive in primitives:
        if not primitive.get("concepts_in_atlas"):
            errors.append(f"primitive {primitive['id']} unused")
        for field in ["formal_object", "useful_equation", "symbol_explanation", "misuse_failure"]:
            if not primitive.get(field):
                errors.append(f"primitive {primitive['id']} missing {field}")
        if words(" ".join(str(primitive.get(f, "")) for f in ["everyday_setup", "plain_language_principle", "formal_object", "symbol_explanation", "course_appearances", "why_it_matters", "misuse_warning"])) < 140:
            errors.append(f"primitive {primitive['id']} is shallow")

    for family in families:
        if not family.get("course_evidence_ids"):
            errors.append(f"family {family['id']} has no evidence")
        if words(" ".join(str(family.get(f, "")) for f in ["family_problem", "first_principles_pattern", "mathematical_signature", "why_family_matters", "family_walkthrough", "where_analogy_breaks", "lecture_evidence_chain", "paper_family_treatment"])) < 180:
            errors.append(f"family {family['id']} is shallow")

    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"validated {len(concepts)} concepts, {len(themes)} themes, {len(subthemes)} subthemes, {len(evidence)} evidence records, {len(primitives)} primitives, {len(families)} method families")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
