#!/usr/bin/env python3
from __future__ import annotations

import json
import html
import re
import sys
from pathlib import Path
from urllib.parse import urldefrag

from derivation_link_map import expected_derivation_ids_for_concept, expected_derivation_ids_for_lecture

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"


def words(text: str) -> int:
    return len(re.findall(r"\b\w+\b", text))


def main() -> int:
    errors: list[str] = []
    concepts = json.loads((ROOT / "analysis/concepts/concept-atlas.json").read_text(encoding="utf-8"))
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
    drills = json.loads((ROOT / "analysis/throughlines/problem-drills.json").read_text(encoding="utf-8"))
    equation_notes = json.loads((ROOT / "analysis/editorial-overrides/equation-walkthrough-notes.json").read_text(encoding="utf-8"))
    worked_examples = json.loads((ROOT / "analysis/editorial-overrides/worked-example-cards.json").read_text(encoding="utf-8"))
    concept_by_id = {concept["id"]: concept for concept in concepts}
    deriv_by_id = {derivation["id"]: derivation for derivation in derivations}
    primitive_by_id = {primitive["id"]: primitive for primitive in primitives}
    ev_by_id = {record["id"]: record for record in evidence}
    lecture_by_id = {lecture["id"]: lecture for lecture in lectures}
    lecture_by_evidence_id = {
        ev_id: lecture
        for lecture in lectures
        for ev_id in lecture.get("evidence_ids", [])
    }
    supplemental_ids = {record["id"] for record in supplemental}
    themes = json.loads((ROOT / "analysis/themes/theme-map.json").read_text(encoding="utf-8"))
    required = [SITE / name for name in ["index.html", "study-route.html", "recognition.html", "math-clinic.html", "drills.html", "cross-reference.html", "limits.html", "lectures.html", "concepts.html", "themes.html", "families.html", "primitives.html", "evidence.html", "assets/styles.css"]]
    required.extend(SITE / "concepts" / f"{c['id']}.html" for c in concepts)
    required.extend(SITE / "lectures" / f"{lecture['id']}.html" for lecture in lectures)
    for path in required:
        if not path.exists():
            errors.append(f"missing site file: {path.relative_to(ROOT)}")
    html_files = list(SITE.rglob("*.html"))
    evidence_html = (SITE / "evidence.html").read_text(encoding="utf-8") if (SITE / "evidence.html").exists() else ""
    lectures_html = (SITE / "lectures.html").read_text(encoding="utf-8") if (SITE / "lectures.html").exists() else ""
    themes_html = (SITE / "themes.html").read_text(encoding="utf-8") if (SITE / "themes.html").exists() else ""
    families_html = (SITE / "families.html").read_text(encoding="utf-8") if (SITE / "families.html").exists() else ""
    route_html = (SITE / "study-route.html").read_text(encoding="utf-8") if (SITE / "study-route.html").exists() else ""
    recognition_html = (SITE / "recognition.html").read_text(encoding="utf-8") if (SITE / "recognition.html").exists() else ""
    math_clinic_html = (SITE / "math-clinic.html").read_text(encoding="utf-8") if (SITE / "math-clinic.html").exists() else ""
    drills_html = (SITE / "drills.html").read_text(encoding="utf-8") if (SITE / "drills.html").exists() else ""
    cross_html = (SITE / "cross-reference.html").read_text(encoding="utf-8") if (SITE / "cross-reference.html").exists() else ""
    limits_html = (SITE / "limits.html").read_text(encoding="utf-8") if (SITE / "limits.html").exists() else ""
    index_html = (SITE / "index.html").read_text(encoding="utf-8") if (SITE / "index.html").exists() else ""
    if 'href="study-route.html"' not in index_html:
        errors.append("index page missing study route link")
    if 'href="recognition.html"' not in index_html:
        errors.append("index page missing recognition clinic link")
    if 'href="math-clinic.html"' not in index_html:
        errors.append("index page missing math clinic link")
    if 'href="drills.html"' not in index_html:
        errors.append("index page missing problem drills link")
    if 'href="cross-reference.html"' not in index_html:
        errors.append("index page missing cross-reference link")
    if 'href="limits.html"' not in index_html:
        errors.append("index page missing limits link")
    subthemes_by_concept: dict[str, list[dict]] = {}
    for subtheme in subthemes:
        for concept_id in subtheme.get("concepts", []):
            subthemes_by_concept.setdefault(concept_id, []).append(subtheme)
    lectures_by_concept: dict[str, list[dict]] = {}
    for lecture in lectures:
        for concept in lecture.get("concepts", []):
            lectures_by_concept.setdefault(concept["id"], []).append(lecture)
    if len(lectures) != 25:
        errors.append(f"expected 25 lectures, found {len(lectures)}")
    for item in route:
        if f'id="{item["id"]}"' not in route_html:
            errors.append(f"study route item not rendered: {item['id']}")
        for field in ["reader_question", "plain_language_goal", "checkpoint"]:
            if words(item.get(field, "")) < 10:
                errors.append(f"study route {item['id']} has shallow {field}")
            elif html.escape(item[field], quote=True) not in route_html:
                errors.append(f"study route {item['id']} {field} not rendered")
        for lecture_id in item.get("lectures", []):
            if lecture_id not in lecture_by_id:
                errors.append(f"study route {item['id']} references missing lecture: {lecture_id}")
            elif f'href="lectures/{lecture_id}.html"' not in route_html:
                errors.append(f"study route {item['id']} missing lecture link: {lecture_id}")
        for concept_id in item.get("concepts", []):
            if concept_id not in concept_by_id:
                errors.append(f"study route {item['id']} references missing concept: {concept_id}")
            elif f'href="concepts/{concept_id}.html"' not in route_html:
                errors.append(f"study route {item['id']} missing concept link: {concept_id}")
        for primitive_id in item.get("primitives", []):
            if primitive_id not in primitive_by_id:
                errors.append(f"study route {item['id']} references missing primitive: {primitive_id}")
            elif f'href="primitives.html#{primitive_id}"' not in route_html:
                errors.append(f"study route {item['id']} missing primitive link: {primitive_id}")
        for ev_id in item.get("evidence", []):
            if ev_id not in ev_by_id:
                errors.append(f"study route {item['id']} references missing evidence: {ev_id}")
            elif f'href="evidence.html#{ev_id}"' not in route_html:
                errors.append(f"study route {item['id']} missing evidence link: {ev_id}")
    for item in clinic:
        if f'id="{item["id"]}"' not in recognition_html:
            errors.append(f"recognition clinic item not rendered: {item['id']}")
        for field in ["reader_situation", "diagnostic_question", "first_principles_test", "mathematical_handle", "false_friend", "where_to_go_next"]:
            value = item.get(field, "")
            if words(value) < 10:
                errors.append(f"recognition clinic {item['id']} has shallow {field}")
            elif html.escape(value, quote=True) not in recognition_html:
                errors.append(f"recognition clinic {item['id']} {field} not rendered")
        if words(" ".join(str(item.get(field, "")) for field in ["reader_situation", "first_principles_test", "mathematical_handle", "false_friend", "where_to_go_next"])) < 95:
            errors.append(f"recognition clinic {item['id']} has shallow combined treatment")
        for concept_id in item.get("use_these_concepts", []):
            if concept_id not in concept_by_id:
                errors.append(f"recognition clinic {item['id']} references missing concept: {concept_id}")
            elif f'href="concepts/{concept_id}.html"' not in recognition_html:
                errors.append(f"recognition clinic {item['id']} missing concept link: {concept_id}")
        for primitive_id in item.get("use_these_primitives", []):
            if primitive_id not in primitive_by_id:
                errors.append(f"recognition clinic {item['id']} references missing primitive: {primitive_id}")
            elif f'href="primitives.html#{primitive_id}"' not in recognition_html:
                errors.append(f"recognition clinic {item['id']} missing primitive link: {primitive_id}")
        for ev_id in item.get("evidence_ids", []):
            if ev_id not in ev_by_id:
                errors.append(f"recognition clinic {item['id']} references missing evidence: {ev_id}")
            elif f'href="evidence.html#{ev_id}"' not in recognition_html:
                errors.append(f"recognition clinic {item['id']} missing evidence link: {ev_id}")
    if len(math_clinic) != len(derivations):
        errors.append(f"math clinic has {len(math_clinic)} cards for {len(derivations)} derivations")
    seen_math_derivations = set()
    for item in math_clinic:
        derivation_id = item.get("derivation_id", "")
        if f'id="{item["id"]}"' not in math_clinic_html:
            errors.append(f"math clinic item not rendered: {item['id']}")
        if derivation_id not in deriv_by_id:
            errors.append(f"math clinic {item['id']} references missing derivation: {derivation_id}")
        else:
            seen_math_derivations.add(derivation_id)
            if f'href="primitives.html#{derivation_id}"' not in math_clinic_html:
                errors.append(f"math clinic {item['id']} missing derivation link: {derivation_id}")
        for field in ["problem_before_math", "failed_shortcut", "plain_english_equation_reading", "worked_numbers", "why_this_changes_reasoning", "transfer_test"]:
            value = item.get(field, "")
            if words(value) < 14:
                errors.append(f"math clinic {item['id']} has shallow {field}")
            elif html.escape(value, quote=True) not in math_clinic_html:
                errors.append(f"math clinic {item['id']} {field} not rendered")
        if words(" ".join(str(item.get(field, "")) for field in ["problem_before_math", "failed_shortcut", "plain_english_equation_reading", "worked_numbers", "why_this_changes_reasoning", "transfer_test"])) < 120:
            errors.append(f"math clinic {item['id']} has shallow combined walkthrough")
        for concept_id in item.get("concepts", []):
            if concept_id not in concept_by_id:
                errors.append(f"math clinic {item['id']} references missing concept: {concept_id}")
            elif f'href="concepts/{concept_id}.html"' not in math_clinic_html:
                errors.append(f"math clinic {item['id']} missing concept link: {concept_id}")
        for ev_id in item.get("evidence_ids", []):
            if ev_id not in ev_by_id:
                errors.append(f"math clinic {item['id']} references missing evidence: {ev_id}")
            elif f'href="evidence.html#{ev_id}"' not in math_clinic_html:
                errors.append(f"math clinic {item['id']} missing evidence link: {ev_id}")
    missing_math_cards = set(deriv_by_id) - seen_math_derivations
    if missing_math_cards:
        errors.append(f"math clinic missing derivation cards: {', '.join(sorted(missing_math_cards))}")
    if len(drills) < 8:
        errors.append(f"problem drills has only {len(drills)} cards")
    for drill in drills:
        if f'id="{drill["id"]}"' not in drills_html:
            errors.append(f"problem drill not rendered: {drill['id']}")
        for field in ["scenario", "reader_task", "first_principles_answer", "math_move", "common_wrong_turn", "evidence_checkpoint"]:
            value = drill.get(field, "")
            if words(value) < 12:
                errors.append(f"problem drill {drill['id']} has shallow {field}")
            elif html.escape(value, quote=True) not in drills_html:
                errors.append(f"problem drill {drill['id']} {field} not rendered")
        if words(" ".join(str(drill.get(field, "")) for field in ["scenario", "first_principles_answer", "math_move", "common_wrong_turn", "evidence_checkpoint"])) < 105:
            errors.append(f"problem drill {drill['id']} has shallow combined treatment")
        for concept_id in drill.get("concepts", []):
            if concept_id not in concept_by_id:
                errors.append(f"problem drill {drill['id']} references missing concept: {concept_id}")
            elif f'href="concepts/{concept_id}.html"' not in drills_html:
                errors.append(f"problem drill {drill['id']} missing concept link: {concept_id}")
        for primitive_id in drill.get("primitives", []):
            if primitive_id not in primitive_by_id:
                errors.append(f"problem drill {drill['id']} references missing primitive: {primitive_id}")
            elif f'href="primitives.html#{primitive_id}"' not in drills_html:
                errors.append(f"problem drill {drill['id']} missing primitive link: {primitive_id}")
        for ev_id in drill.get("evidence_ids", []):
            if ev_id not in ev_by_id:
                errors.append(f"problem drill {drill['id']} references missing evidence: {ev_id}")
            elif f'href="evidence.html#{ev_id}"' not in drills_html:
                errors.append(f"problem drill {drill['id']} missing evidence link: {ev_id}")
    for concept in concepts:
        if f'id="xref-{concept["id"]}"' not in cross_html:
            errors.append(f"cross index missing concept anchor: {concept['id']}")
        if f'href="concepts/{concept["id"]}.html"' not in cross_html:
            errors.append(f"cross index missing concept link: {concept['id']}")
        if html.escape(concept["everyday_problem"], quote=True) not in cross_html:
            errors.append(f"cross index missing problem pressure: {concept['id']}")
        if html.escape(concept["mathematical_object"], quote=True) not in cross_html:
            errors.append(f"cross index missing mathematical handle: {concept['id']}")
        for ev_id in concept.get("course_evidence_ids", []):
            if f'href="evidence.html#{ev_id}"' not in cross_html:
                errors.append(f"cross index missing evidence link: {concept['id']} -> {ev_id}")
        for lecture in lectures_by_concept.get(concept["id"], []):
            if f'href="lectures/{lecture["id"]}.html"' not in cross_html:
                errors.append(f"cross index missing lecture link: {concept['id']} -> {lecture['id']}")
        for subtheme in subthemes_by_concept.get(concept["id"], []):
            if f'href="themes.html#{subtheme["id"]}"' not in cross_html:
                errors.append(f"cross index missing subtheme link: {concept['id']} -> {subtheme['id']}")
        for primitive_id in concept.get("mathematical_primitives", []):
            if primitive_id in primitive_by_id and f'href="primitives.html#{primitive_id}"' not in cross_html:
                errors.append(f"cross index missing primitive link: {concept['id']} -> {primitive_id}")
    for concept in concepts:
        if f'id="limit-{concept["id"]}"' not in limits_html:
            errors.append(f"limits page missing concept limit card: {concept['id']}")
        if f'href="concepts/{concept["id"]}.html"' not in limits_html:
            errors.append(f"limits page missing concept link: {concept['id']}")
        for field in ["common_misunderstanding", "student_trap", "course_boundary_note", "what_breaks_without_it"]:
            value = concept.get(field, "")
            if words(value) < 12:
                errors.append(f"concept {concept['id']} has shallow limit field: {field}")
            elif html.escape(value, quote=True) not in limits_html:
                errors.append(f"limits page missing {field}: {concept['id']}")
    for theme in themes:
        if f'id="theme-limit-{theme["id"]}"' not in limits_html:
            errors.append(f"limits page missing theme limit card: {theme['id']}")
        if f'href="themes.html#{theme["id"]}"' not in limits_html:
            errors.append(f"limits page missing theme link: {theme['id']}")
        if html.escape(theme["where_analogy_breaks"], quote=True) not in limits_html:
            errors.append(f"limits page missing theme boundary: {theme['id']}")
    for derivation in derivations:
        if f'id="derivation-limit-{derivation["id"]}"' not in limits_html:
            errors.append(f"limits page missing derivation limit card: {derivation['id']}")
        if f'href="primitives.html#{derivation["id"]}"' not in limits_html:
            errors.append(f"limits page missing derivation link: {derivation['id']}")
        if html.escape(derivation["common_misread"], quote=True) not in limits_html:
            errors.append(f"limits page missing derivation misread: {derivation['id']}")
    for lecture in lectures:
        if f'id="{lecture["id"]}"' not in lectures_html:
            errors.append(f"missing lecture anchor: {lecture['id']}")
        if not lecture.get("first_principles_role") or not lecture.get("what_to_watch_for"):
            errors.append(f"lecture missing treatment: {lecture['id']}")
        for key in ["argument_arc", "math_entry_point", "worked_mini_example", "common_failure"]:
            if not lecture.get(key):
                errors.append(f"lecture missing {key}: {lecture['id']}")
        total_evidence = len(lecture.get("evidence_ids", [])) + len(lecture.get("supplemental_evidence_ids", []))
        if total_evidence < 2:
            errors.append(f"lecture has thin evidence coverage: {lecture['id']} has {total_evidence} anchors")
        for ev_id in lecture.get("supplemental_evidence_ids", []):
            if ev_id not in supplemental_ids:
                errors.append(f"lecture references missing supplemental evidence: {lecture['id']} -> {ev_id}")
        detail = SITE / "lectures" / f"{lecture['id']}.html"
        if detail.exists():
            text = detail.read_text(encoding="utf-8")
            for heading in ["What This Lecture Teaches", "Where The Math Enters", "Equation Walkthroughs", "Worked Mini-Example", "Mistakes To Avoid", "Transcript Evidence Chain", "Supplemental Lecture Evidence"]:
                if heading not in text:
                    errors.append(f"lecture page {lecture['id']} missing heading: {heading}")
            lecture_concepts = [concept_by_id[c["id"]] for c in lecture["concepts"] if c["id"] in concept_by_id]
            expected_derivations = expected_derivation_ids_for_lecture(lecture_concepts, deriv_by_id)
            if expected_derivations and "../primitives.html#" not in text:
                errors.append(f"lecture page {lecture['id']} missing derivation links")
            for ev_id in lecture["evidence_ids"]:
                if f'id="{ev_id}"' not in text:
                    errors.append(f"lecture page {lecture['id']} missing evidence {ev_id}")
            for ev_id in lecture.get("supplemental_evidence_ids", []):
                if f'id="{ev_id}"' not in text:
                    errors.append(f"lecture page {lecture['id']} missing supplemental evidence {ev_id}")
    for ev in evidence:
        if f'id="{ev["id"]}"' not in evidence_html:
            errors.append(f"missing evidence anchor: {ev['id']}")
        for heading in ["Supports concepts", "Supports subthemes", "Lecture page"]:
            if heading not in evidence_html:
                errors.append(f"evidence page missing backlink heading: {heading}")
        for concept_id in ev.get("supports_concepts", []):
            if concept_id not in concept_by_id:
                errors.append(f"evidence {ev['id']} references missing concept: {concept_id}")
            elif f'href="concepts/{concept_id}.html"' not in evidence_html:
                errors.append(f"evidence {ev['id']} missing concept backlink: {concept_id}")
        for subtheme_id in ev.get("supports_subthemes", []):
            if f'href="themes.html#{subtheme_id}"' not in evidence_html:
                errors.append(f"evidence {ev['id']} missing subtheme backlink: {subtheme_id}")
        lecture = lecture_by_evidence_id.get(ev["id"])
        if not lecture:
            errors.append(f"evidence {ev['id']} missing lecture-page mapping")
        elif f'href="lectures/{lecture["id"]}.html"' not in evidence_html:
            errors.append(f"evidence {ev['id']} missing lecture backlink: {lecture['id']}")
        if re.search(r"Lecture \d+: Lecture \d+:", evidence_html):
            errors.append("evidence page contains duplicated lecture-number label")
    for subtheme in subthemes:
        if f'id="{subtheme["id"]}"' not in themes_html:
            errors.append(f"missing subtheme anchor: {subtheme['id']}")
        for heading in ["Everyday problem", "Hidden principle", "Mathematical lever", "Why it matters", "First-principles walkthrough", "Cross-links and limits", "Concept Pages", "Evidence Trail"]:
            if heading not in themes_html:
                errors.append(f"themes page missing subtheme heading: {heading}")
        for field in ["everyday_problem", "hidden_principle", "mathematical_lever", "why_it_matters", "first_principles_walkthrough", "cross_links_and_limits"]:
            value = subtheme.get(field, "")
            if words(value) < 18:
                errors.append(f"subtheme {subtheme['id']} has shallow {field}")
            elif html.escape(value, quote=True) not in themes_html:
                errors.append(f"subtheme {subtheme['id']} {field} not rendered")
        for concept_id in subtheme.get("concepts", []):
            if concept_id not in concept_by_id:
                errors.append(f"subtheme {subtheme['id']} references missing concept: {concept_id}")
            elif f'href="concepts/{concept_id}.html"' not in themes_html:
                errors.append(f"subtheme {subtheme['id']} missing concept link: {concept_id}")
        for example in subtheme.get("examples_from_courses", []):
            if f'href="evidence.html#{example["evidence_id"]}"' not in themes_html:
                errors.append(f"subtheme {subtheme['id']} missing evidence link: {example['evidence_id']}")
    for family in families:
        if f'id="{family["id"]}"' not in families_html:
            errors.append(f"missing family anchor: {family['id']}")
        for heading in ["Core Concepts", "Reusable Primitives", "Evidence Trail"]:
            if heading not in families_html:
                errors.append(f"families page missing heading: {heading}")
        for concept_id in family.get("concepts", []):
            if concept_id not in concept_by_id:
                errors.append(f"family {family['id']} references missing concept: {concept_id}")
            elif f'href="concepts/{concept_id}.html"' not in families_html:
                errors.append(f"family {family['id']} missing concept link: {concept_id}")
        for primitive_id in family.get("mathematical_primitive", []):
            if f'href="primitives.html#{primitive_id}"' not in families_html:
                errors.append(f"family {family['id']} missing primitive link: {primitive_id}")
        for ev_id in family.get("course_evidence_ids", []):
            if f'href="evidence.html#{ev_id}"' not in families_html:
                errors.append(f"family {family['id']} missing evidence link: {ev_id}")
    primitives_html = (SITE / "primitives.html").read_text(encoding="utf-8") if (SITE / "primitives.html").exists() else ""
    for primitive in primitives:
        if f'id="{primitive["id"]}"' not in primitives_html:
            errors.append(f"missing primitive anchor: {primitive['id']}")
        if "Concept Pages Using This Primitive" not in primitives_html:
            errors.append("primitives page missing concept backlink heading")
        for concept_id in primitive.get("concepts_in_atlas", []):
            if concept_id not in concept_by_id:
                errors.append(f"primitive {primitive['id']} references missing concept: {concept_id}")
            elif f'href="concepts/{concept_id}.html"' not in primitives_html:
                errors.append(f"primitive {primitive['id']} missing concept backlink: {concept_id}")
    for derivation in derivations:
        if f'id="{derivation["id"]}"' not in primitives_html:
            errors.append(f"missing derivation anchor: {derivation['id']}")
        for heading in ["Derivation In Plain English", "Symbol By Symbol", "Why This Relation Matters", "Common Misread"]:
            if heading not in primitives_html:
                errors.append(f"primitives page missing derivation heading: {heading}")
    for concept in concepts:
        text = (SITE / "concepts" / f"{concept['id']}.html").read_text(encoding="utf-8")
        if 'class="learning-diagram concept-flow"' not in text:
            errors.append(f"concept page missing diagram: {concept['id']}")
        card = worked_examples.get(concept["id"])
        if not card:
            errors.append(f"concept {concept['id']} missing worked example card")
        else:
            if "Worked Example Card" not in text:
                errors.append(f"concept page {concept['id']} missing worked example card section")
            for key in ["setup", "walkthrough", "lesson", "trap"]:
                value = card.get(key, "")
                if words(value) < 8:
                    errors.append(f"concept {concept['id']} has shallow worked example {key}")
                elif html.escape(value, quote=True) not in text:
                    errors.append(f"concept {concept['id']} worked example {key} not rendered")
        if "Equation Walkthroughs" not in text:
            errors.append(f"concept page missing derivation section: {concept['id']}")
        expected_derivations = expected_derivation_ids_for_concept(concept, deriv_by_id)
        if expected_derivations:
            note = equation_notes.get(concept["id"], "")
            if words(note) < 24:
                errors.append(f"concept {concept['id']} missing substantial equation walkthrough note")
            elif html.escape(note, quote=True) not in text:
                errors.append(f"concept {concept['id']} equation walkthrough note not rendered")
        for derivation_id in expected_derivations:
            if f'href="../primitives.html#{derivation_id}"' not in text:
                errors.append(f"concept page {concept['id']} missing derivation link: {derivation_id}")
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
