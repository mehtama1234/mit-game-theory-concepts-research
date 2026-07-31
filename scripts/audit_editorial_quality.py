#!/usr/bin/env python3
from __future__ import annotations

import json
import html as html_lib
import re
from pathlib import Path

from derivation_link_map import expected_derivation_ids_for_concept, expected_derivation_ids_for_lecture

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
    supplemental = json.loads((ROOT / "analysis/lectures/lecture-evidence.json").read_text(encoding="utf-8"))
    primitives = json.loads((ROOT / "analysis/throughlines/primitives.json").read_text(encoding="utf-8"))
    derivations = json.loads((ROOT / "analysis/throughlines/derivations.json").read_text(encoding="utf-8"))
    families = json.loads((ROOT / "analysis/throughlines/method-families.json").read_text(encoding="utf-8"))
    route = json.loads((ROOT / "analysis/throughlines/study-route.json").read_text(encoding="utf-8"))
    clinic = json.loads((ROOT / "analysis/throughlines/recognition-clinic.json").read_text(encoding="utf-8"))
    math_clinic = json.loads((ROOT / "analysis/throughlines/math-walkthrough-clinic.json").read_text(encoding="utf-8"))
    equation_notes = json.loads((ROOT / "analysis/editorial-overrides/equation-walkthrough-notes.json").read_text(encoding="utf-8"))
    worked_examples = json.loads((ROOT / "analysis/editorial-overrides/worked-example-cards.json").read_text(encoding="utf-8"))
    concept_by_id = {concept["id"]: concept for concept in concepts}
    deriv_by_id = {derivation["id"]: derivation for derivation in derivations}

    ev_by_concept: dict[str, list[str]] = {}
    for ev in evidence:
        for cid in ev["supports_concepts"]:
            ev_by_concept.setdefault(cid, []).append(ev["id"])
    subthemes_by_concept: dict[str, list[dict[str, Any]]] = {}
    for subtheme in subthemes:
        for concept_id in subtheme.get("concepts", []):
            subthemes_by_concept.setdefault(concept_id, []).append(subtheme)
    lectures_by_concept: dict[str, list[dict[str, Any]]] = {}
    for lecture in lectures:
        for concept in lecture.get("concepts", []):
            lectures_by_concept.setdefault(concept["id"], []).append(lecture)
    lecture_by_evidence_id = {
        ev_id: lecture
        for lecture in lectures
        for ev_id in lecture.get("evidence_ids", [])
    }

    rows = []
    concept_pages_with_derivations = 0
    equation_note_words = []
    worked_example_words = []
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
        card = worked_examples.get(concept["id"])
        if not card:
            errors.append(f"concept {concept['id']} missing worked example card")
        else:
            card_words = words(" ".join(str(card.get(key, "")) for key in ["setup", "walkthrough", "lesson", "trap"]))
            worked_example_words.append(card_words)
            if card_words < 55:
                errors.append(f"concept {concept['id']} worked example card is shallow: {card_words} words")
            if "Worked Example Card" not in html:
                errors.append(f"concept {concept['id']} worked example card not rendered")
            for key in ["setup", "walkthrough", "lesson", "trap"]:
                value = str(card.get(key, ""))
                if words(value) < 8:
                    errors.append(f"concept {concept['id']} has shallow worked example {key}")
                if value and html_lib.escape(value, quote=True) not in html:
                    errors.append(f"concept {concept['id']} worked example {key} not rendered")
        expected_derivations = expected_derivation_ids_for_concept(concept, deriv_by_id)
        linked_derivations = [derivation_id for derivation_id in expected_derivations if f'href="../primitives.html#{derivation_id}"' in html]
        if expected_derivations and not linked_derivations:
            errors.append(f"concept {concept['id']} has no linked equation walkthrough")
        if expected_derivations:
            note = equation_notes.get(concept["id"], "")
            note_words = words(note)
            equation_note_words.append(note_words)
            if note_words < 24:
                errors.append(f"concept {concept['id']} has shallow equation walkthrough note: {note_words} words")
            if note and html_lib.escape(note, quote=True) not in html:
                errors.append(f"concept {concept['id']} equation walkthrough note not rendered")
        if linked_derivations:
            concept_pages_with_derivations += 1
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
    themes_html = (SITE / "themes.html").read_text(encoding="utf-8") if (SITE / "themes.html").exists() else ""
    rendered_subthemes = 0
    subtheme_concept_links = 0
    subtheme_evidence_links = 0
    for subtheme in subthemes:
        if f'id="{subtheme["id"]}"' in themes_html:
            rendered_subthemes += 1
        else:
            errors.append(f"subtheme {subtheme['id']} not rendered on themes page")
        for field in ["everyday_problem", "hidden_principle", "mathematical_lever", "why_it_matters", "first_principles_walkthrough", "cross_links_and_limits"]:
            value = str(subtheme.get(field, ""))
            if value and html_lib.escape(value, quote=True) not in themes_html:
                errors.append(f"subtheme {subtheme['id']} {field} not rendered")
        linked_concepts = [cid for cid in subtheme.get("concepts", []) if f'href="concepts/{cid}.html"' in themes_html]
        linked_evidence = [example["evidence_id"] for example in subtheme.get("examples_from_courses", []) if f'href="evidence.html#{example["evidence_id"]}"' in themes_html]
        subtheme_concept_links += len(linked_concepts)
        subtheme_evidence_links += len(linked_evidence)
        if len(linked_concepts) != len(subtheme.get("concepts", [])):
            errors.append(f"subtheme {subtheme['id']} missing concept links")
        if len(linked_evidence) != len(subtheme.get("examples_from_courses", [])):
            errors.append(f"subtheme {subtheme['id']} missing evidence links")
    primitive_words = [words(" ".join(str(p.get(f, "")) for f in ["everyday_setup", "plain_language_principle", "formal_object", "symbol_explanation", "course_appearances", "why_it_matters", "misuse_warning"])) for p in primitives]
    primitives_html = (SITE / "primitives.html").read_text(encoding="utf-8") if (SITE / "primitives.html").exists() else ""
    primitive_backlinks = 0
    for primitive in primitives:
        linked = [
            concept_id
            for concept_id in primitive.get("concepts_in_atlas", [])
            if f'href="concepts/{concept_id}.html"' in primitives_html
        ]
        primitive_backlinks += len(linked)
        if len(linked) != len(primitive.get("concepts_in_atlas", [])):
            errors.append(f"primitive {primitive['id']} missing concept backlinks")
    derivation_words = [words(" ".join(str(d.get(f, "")) for f in ["everyday_setup", "equation", "symbol_by_symbol", "why_it_matters", "common_misread"]) + " " + " ".join(d.get("derivation_steps", []))) for d in derivations]
    family_words = [words(" ".join(str(f.get(k, "")) for k in ["family_problem", "first_principles_pattern", "mathematical_signature", "why_family_matters", "family_walkthrough", "where_analogy_breaks", "lecture_evidence_chain", "paper_family_treatment"])) for f in families]
    route_html = (SITE / "study-route.html").read_text(encoding="utf-8") if (SITE / "study-route.html").exists() else ""
    route_words = [words(" ".join(str(item.get(k, "")) for k in ["reader_question", "plain_language_goal", "checkpoint"])) for item in route]
    route_lecture_links = 0
    route_concept_links = 0
    route_primitive_links = 0
    route_evidence_links = 0
    for item in route:
        if f'id="{item["id"]}"' not in route_html:
            errors.append(f"study route {item['id']} not rendered")
        linked_lectures = [lid for lid in item.get("lectures", []) if f'href="lectures/{lid}.html"' in route_html]
        linked_concepts = [cid for cid in item.get("concepts", []) if f'href="concepts/{cid}.html"' in route_html]
        linked_primitives = [pid for pid in item.get("primitives", []) if f'href="primitives.html#{pid}"' in route_html]
        linked_evidence = [eid for eid in item.get("evidence", []) if f'href="evidence.html#{eid}"' in route_html]
        route_lecture_links += len(linked_lectures)
        route_concept_links += len(linked_concepts)
        route_primitive_links += len(linked_primitives)
        route_evidence_links += len(linked_evidence)
        if words(" ".join(str(item.get(k, "")) for k in ["reader_question", "plain_language_goal", "checkpoint"])) < 35:
            errors.append(f"study route {item['id']} has shallow orientation text")
        if len(linked_lectures) != len(item.get("lectures", [])):
            errors.append(f"study route {item['id']} missing lecture links")
        if len(linked_concepts) != len(item.get("concepts", [])):
            errors.append(f"study route {item['id']} missing concept links")
        if len(linked_primitives) != len(item.get("primitives", [])):
            errors.append(f"study route {item['id']} missing primitive links")
        if len(linked_evidence) != len(item.get("evidence", [])):
            errors.append(f"study route {item['id']} missing evidence links")
    recognition_html = (SITE / "recognition.html").read_text(encoding="utf-8") if (SITE / "recognition.html").exists() else ""
    recognition_cards = 0
    recognition_concept_links = 0
    recognition_primitive_links = 0
    recognition_evidence_links = 0
    recognition_words = []
    for item in clinic:
        if f'id="{item["id"]}"' in recognition_html:
            recognition_cards += 1
        else:
            errors.append(f"recognition clinic {item['id']} not rendered")
        text = " ".join(
            str(item.get(k, ""))
            for k in ["reader_situation", "diagnostic_question", "first_principles_test", "mathematical_handle", "false_friend", "where_to_go_next"]
        )
        treatment_words = words(text)
        recognition_words.append(treatment_words)
        if treatment_words < 95:
            errors.append(f"recognition clinic {item['id']} has shallow diagnostic treatment: {treatment_words} words")
        linked_concepts = [cid for cid in item.get("use_these_concepts", []) if f'href="concepts/{cid}.html"' in recognition_html]
        linked_primitives = [pid for pid in item.get("use_these_primitives", []) if f'href="primitives.html#{pid}"' in recognition_html]
        linked_evidence = [eid for eid in item.get("evidence_ids", []) if f'href="evidence.html#{eid}"' in recognition_html]
        recognition_concept_links += len(linked_concepts)
        recognition_primitive_links += len(linked_primitives)
        recognition_evidence_links += len(linked_evidence)
        if len(linked_concepts) != len(item.get("use_these_concepts", [])):
            errors.append(f"recognition clinic {item['id']} missing concept links")
        if len(linked_primitives) != len(item.get("use_these_primitives", [])):
            errors.append(f"recognition clinic {item['id']} missing primitive links")
        if len(linked_evidence) != len(item.get("evidence_ids", [])):
            errors.append(f"recognition clinic {item['id']} missing evidence links")
    math_clinic_html = (SITE / "math-clinic.html").read_text(encoding="utf-8") if (SITE / "math-clinic.html").exists() else ""
    math_clinic_cards = 0
    math_clinic_derivation_links = 0
    math_clinic_concept_links = 0
    math_clinic_evidence_links = 0
    math_clinic_words = []
    for item in math_clinic:
        if f'id="{item["id"]}"' in math_clinic_html:
            math_clinic_cards += 1
        else:
            errors.append(f"math clinic {item['id']} not rendered")
        text = " ".join(
            str(item.get(k, ""))
            for k in ["problem_before_math", "failed_shortcut", "plain_english_equation_reading", "worked_numbers", "why_this_changes_reasoning", "transfer_test"]
        )
        treatment_words = words(text)
        math_clinic_words.append(treatment_words)
        if treatment_words < 120:
            errors.append(f"math clinic {item['id']} has shallow walkthrough: {treatment_words} words")
        derivation_id = item.get("derivation_id", "")
        if f'href="primitives.html#{derivation_id}"' in math_clinic_html:
            math_clinic_derivation_links += 1
        else:
            errors.append(f"math clinic {item['id']} missing derivation link")
        linked_concepts = [cid for cid in item.get("concepts", []) if f'href="concepts/{cid}.html"' in math_clinic_html]
        linked_evidence = [eid for eid in item.get("evidence_ids", []) if f'href="evidence.html#{eid}"' in math_clinic_html]
        math_clinic_concept_links += len(linked_concepts)
        math_clinic_evidence_links += len(linked_evidence)
        if len(linked_concepts) != len(item.get("concepts", [])):
            errors.append(f"math clinic {item['id']} missing concept links")
        if len(linked_evidence) != len(item.get("evidence_ids", [])):
            errors.append(f"math clinic {item['id']} missing evidence links")
    if len(math_clinic) != len(derivations):
        errors.append(f"math clinic has {len(math_clinic)} cards for {len(derivations)} derivations")
    cross_html = (SITE / "cross-reference.html").read_text(encoding="utf-8") if (SITE / "cross-reference.html").exists() else ""
    cross_concept_cards = 0
    cross_lecture_links = 0
    cross_subtheme_links = 0
    cross_primitive_links = 0
    cross_evidence_links = 0
    for concept in concepts:
        if f'id="xref-{concept["id"]}"' in cross_html:
            cross_concept_cards += 1
        else:
            errors.append(f"cross index missing concept card: {concept['id']}")
        if f'href="concepts/{concept["id"]}.html"' not in cross_html:
            errors.append(f"cross index missing concept page link: {concept['id']}")
        linked_lectures = [lecture["id"] for lecture in lectures_by_concept.get(concept["id"], []) if f'href="lectures/{lecture["id"]}.html"' in cross_html]
        linked_subthemes = [subtheme["id"] for subtheme in subthemes_by_concept.get(concept["id"], []) if f'href="themes.html#{subtheme["id"]}"' in cross_html]
        linked_primitives = [pid for pid in concept.get("mathematical_primitives", []) if f'href="primitives.html#{pid}"' in cross_html]
        linked_evidence = [eid for eid in concept.get("course_evidence_ids", []) if f'href="evidence.html#{eid}"' in cross_html]
        cross_lecture_links += len(linked_lectures)
        cross_subtheme_links += len(linked_subthemes)
        cross_primitive_links += len(linked_primitives)
        cross_evidence_links += len(linked_evidence)
        if len(linked_lectures) != len(lectures_by_concept.get(concept["id"], [])):
            errors.append(f"cross index missing lecture links for {concept['id']}")
        if len(linked_subthemes) != len(subthemes_by_concept.get(concept["id"], [])):
            errors.append(f"cross index missing subtheme links for {concept['id']}")
        if len(linked_evidence) != len(concept.get("course_evidence_ids", [])):
            errors.append(f"cross index missing evidence links for {concept['id']}")
    limits_html = (SITE / "limits.html").read_text(encoding="utf-8") if (SITE / "limits.html").exists() else ""
    limit_concept_cards = 0
    limit_theme_cards = 0
    limit_derivation_cards = 0
    limit_words = []
    for concept in concepts:
        if f'id="limit-{concept["id"]}"' in limits_html:
            limit_concept_cards += 1
        else:
            errors.append(f"limits page missing concept card: {concept['id']}")
        if f'href="concepts/{concept["id"]}.html"' not in limits_html:
            errors.append(f"limits page missing concept link: {concept['id']}")
        text = " ".join(str(concept.get(field, "")) for field in ["common_misunderstanding", "student_trap", "course_boundary_note", "what_breaks_without_it"])
        limit_words.append(words(text))
        if words(text) < 75:
            errors.append(f"concept {concept['id']} has shallow combined limit treatment")
    for theme in themes:
        if f'id="theme-limit-{theme["id"]}"' in limits_html:
            limit_theme_cards += 1
        else:
            errors.append(f"limits page missing theme card: {theme['id']}")
        if f'href="themes.html#{theme["id"]}"' not in limits_html:
            errors.append(f"limits page missing theme link: {theme['id']}")
    for derivation in derivations:
        if f'id="derivation-limit-{derivation["id"]}"' in limits_html:
            limit_derivation_cards += 1
        else:
            errors.append(f"limits page missing derivation card: {derivation['id']}")
        if f'href="primitives.html#{derivation["id"]}"' not in limits_html:
            errors.append(f"limits page missing derivation link: {derivation['id']}")
    families_html = (SITE / "families.html").read_text(encoding="utf-8") if (SITE / "families.html").exists() else ""
    family_concept_links = 0
    family_primitive_links = 0
    family_evidence_links = 0
    for family in families:
        if f'id="{family["id"]}"' not in families_html:
            errors.append(f"method family {family['id']} not rendered")
        linked_concepts = [cid for cid in family.get("concepts", []) if f'href="concepts/{cid}.html"' in families_html]
        linked_primitives = [pid for pid in family.get("mathematical_primitive", []) if f'href="primitives.html#{pid}"' in families_html]
        linked_evidence = [eid for eid in family.get("course_evidence_ids", []) if f'href="evidence.html#{eid}"' in families_html]
        family_concept_links += len(linked_concepts)
        family_primitive_links += len(linked_primitives)
        family_evidence_links += len(linked_evidence)
        if len(linked_concepts) != len(family.get("concepts", [])):
            errors.append(f"method family {family['id']} missing concept links")
        if len(linked_primitives) != len(family.get("mathematical_primitive", [])):
            errors.append(f"method family {family['id']} missing primitive links")
        if len(linked_evidence) != len(family.get("course_evidence_ids", [])):
            errors.append(f"method family {family['id']} missing evidence links")
    deep_evidence = [record for record in evidence if record.get("transcript_teaching_note") and record.get("evidence_boundary")]
    evidence_html = (SITE / "evidence.html").read_text(encoding="utf-8") if (SITE / "evidence.html").exists() else ""
    evidence_concept_backlinks = 0
    evidence_subtheme_backlinks = 0
    evidence_lecture_backlinks = 0
    for record in evidence:
        linked_concepts = [cid for cid in record.get("supports_concepts", []) if f'href="concepts/{cid}.html"' in evidence_html]
        linked_subthemes = [sid for sid in record.get("supports_subthemes", []) if f'href="themes.html#{sid}"' in evidence_html]
        lecture = lecture_by_evidence_id.get(record["id"])
        has_lecture = bool(lecture and f'href="lectures/{lecture["id"]}.html"' in evidence_html)
        evidence_concept_backlinks += len(linked_concepts)
        evidence_subtheme_backlinks += len(linked_subthemes)
        evidence_lecture_backlinks += int(has_lecture)
        if len(linked_concepts) != len(record.get("supports_concepts", [])):
            errors.append(f"evidence {record['id']} missing concept backlinks")
        if len(linked_subthemes) != len(record.get("supports_subthemes", [])):
            errors.append(f"evidence {record['id']} missing subtheme backlinks")
        if not has_lecture:
            errors.append(f"evidence {record['id']} missing lecture backlink")
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
    thin_lectures = [
        lecture["id"]
        for lecture in lectures
        if len(lecture.get("evidence_ids", [])) + len(lecture.get("supplemental_evidence_ids", [])) < 2
    ]
    if thin_lectures:
        errors.append(f"lectures with fewer than 2 total evidence anchors: {', '.join(thin_lectures)}")
    for record in supplemental:
        for key in ["lecture_argument", "conceptual_payload", "why_span_matters", "local_transcript_window"]:
            if words(record.get(key, "")) < 10:
                errors.append(f"supplemental evidence {record['id']} has shallow {key}")
    lecture_words = [words(f"{lecture.get('first_principles_role', '')} {lecture.get('what_to_watch_for', '')}") for lecture in lectures]
    for lecture, count in zip(lectures, lecture_words):
        if count < 30:
            errors.append(f"lecture {lecture['id']} has shallow path treatment: {count} words")
        treatment_count = words(" ".join(str(lecture.get(field, "")) for field in ["argument_arc", "math_entry_point", "worked_mini_example", "common_failure"]))
        if treatment_count < 90:
            errors.append(f"lecture {lecture['id']} has shallow hand-authored treatment: {treatment_count} words")
    lecture_page_words = []
    lecture_pages_with_derivations = 0
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
        for heading in ["What This Lecture Teaches", "Where The Math Enters", "Equation Walkthroughs", "Worked Mini-Example", "Mistakes To Avoid", "How To Recognize This Later", "Transcript Evidence Chain"]:
            if heading not in text:
                errors.append(f"lecture detail page {lecture['id']} missing heading: {heading}")
        lecture_concepts = [concept_by_id[c["id"]] for c in lecture["concepts"] if c["id"] in concept_by_id]
        expected_derivations = expected_derivation_ids_for_lecture(lecture_concepts, deriv_by_id)
        if expected_derivations and "../primitives.html#" not in text:
            errors.append(f"lecture detail page {lecture['id']} has no linked equation walkthrough")
        if "../primitives.html#" in text:
            lecture_pages_with_derivations += 1

    for theme, count in zip(themes, theme_words):
        if count < 180:
            errors.append(f"theme {theme['id']} has low synthesis depth: {count} words")
    for subtheme, count in zip(subthemes, subtheme_words):
        if count < 180:
            errors.append(f"subtheme {subtheme['id']} has low synthesis depth: {count} words")
    for primitive, count in zip(primitives, primitive_words):
        if count < 140:
            errors.append(f"primitive {primitive['id']} has low synthesis depth: {count} words")
    if len(derivations) < 8:
        errors.append(f"only {len(derivations)} derivation cards")
    for derivation, count in zip(derivations, derivation_words):
        if count < 115:
            errors.append(f"derivation {derivation['id']} has low teaching depth: {count} words")
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
        f"- Rendered subtheme study cards: {rendered_subthemes}",
        f"- Subtheme concept links: {subtheme_concept_links}",
        f"- Subtheme evidence links: {subtheme_evidence_links}",
        f"- Primitive treatment words: min {min(primitive_words)}, max {max(primitive_words)}",
        f"- Primitive-to-concept backlinks: {primitive_backlinks}",
        f"- Derivation-card words: min {min(derivation_words) if derivation_words else 0}, max {max(derivation_words) if derivation_words else 0}",
        f"- Concept pages with derivation links: {concept_pages_with_derivations}",
        f"- Concept equation note words: min {min(equation_note_words) if equation_note_words else 0}, max {max(equation_note_words) if equation_note_words else 0}",
        f"- Concept worked-example card words: min {min(worked_example_words) if worked_example_words else 0}, max {max(worked_example_words) if worked_example_words else 0}",
        f"- Lecture pages with derivation links: {lecture_pages_with_derivations}",
        f"- Method-family treatment words: min {min(family_words)}, max {max(family_words)}",
        f"- Method-family concept links: {family_concept_links}",
        f"- Method-family primitive links: {family_primitive_links}",
        f"- Method-family evidence links: {family_evidence_links}",
        f"- Study route cards: {len(route)}",
        f"- Study route words: min {min(route_words) if route_words else 0}, max {max(route_words) if route_words else 0}",
        f"- Study route lecture links: {route_lecture_links}",
        f"- Study route concept links: {route_concept_links}",
        f"- Study route primitive links: {route_primitive_links}",
        f"- Study route evidence links: {route_evidence_links}",
        f"- Recognition clinic cards: {recognition_cards}",
        f"- Recognition clinic words: min {min(recognition_words) if recognition_words else 0}, max {max(recognition_words) if recognition_words else 0}",
        f"- Recognition clinic concept links: {recognition_concept_links}",
        f"- Recognition clinic primitive links: {recognition_primitive_links}",
        f"- Recognition clinic evidence links: {recognition_evidence_links}",
        f"- Math clinic cards: {math_clinic_cards}",
        f"- Math clinic words: min {min(math_clinic_words) if math_clinic_words else 0}, max {max(math_clinic_words) if math_clinic_words else 0}",
        f"- Math clinic derivation links: {math_clinic_derivation_links}",
        f"- Math clinic concept links: {math_clinic_concept_links}",
        f"- Math clinic evidence links: {math_clinic_evidence_links}",
        f"- Cross-index concept cards: {cross_concept_cards}",
        f"- Cross-index lecture links: {cross_lecture_links}",
        f"- Cross-index subtheme links: {cross_subtheme_links}",
        f"- Cross-index primitive links: {cross_primitive_links}",
        f"- Cross-index evidence links: {cross_evidence_links}",
        f"- Limits concept cards: {limit_concept_cards}",
        f"- Limits theme cards: {limit_theme_cards}",
        f"- Limits derivation cards: {limit_derivation_cards}",
        f"- Limits concept words: min {min(limit_words) if limit_words else 0}, max {max(limit_words) if limit_words else 0}",
        f"- Evidence records with transcript teaching notes: {len(deep_evidence)}",
        f"- Evidence concept backlinks: {evidence_concept_backlinks}",
        f"- Evidence subtheme backlinks: {evidence_subtheme_backlinks}",
        f"- Evidence lecture backlinks: {evidence_lecture_backlinks}",
        f"- Evidence records still marked weak: {len(weak_evidence)}",
        f"- Evidence windows with repeated caption overlap: {len(overlap_records)}",
        f"- Lecture path entries: {len(lectures)}",
        f"- Supplemental lecture evidence records: {len(supplemental)}",
        f"- Lectures below 2 total evidence anchors: {len(thin_lectures)}",
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
