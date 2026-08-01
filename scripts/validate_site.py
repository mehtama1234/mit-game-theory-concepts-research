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
    solutions = json.loads((ROOT / "analysis/throughlines/solution-workshop.json").read_text(encoding="utf-8"))
    cases = json.loads((ROOT / "analysis/throughlines/case-studies.json").read_text(encoding="utf-8"))
    chains = json.loads((ROOT / "analysis/throughlines/argument-chains.json").read_text(encoding="utf-8"))
    repairs = json.loads((ROOT / "analysis/throughlines/misconception-repairs.json").read_text(encoding="utf-8"))
    paper_reading = json.loads((ROOT / "analysis/throughlines/paper-reading-guide.json").read_text(encoding="utf-8"))
    jargon_decoder = json.loads((ROOT / "analysis/throughlines/jargon-decoder.json").read_text(encoding="utf-8"))
    workbook = json.loads((ROOT / "analysis/throughlines/model-building-workbook.json").read_text(encoding="utf-8"))
    proofs = json.loads((ROOT / "analysis/throughlines/proof-sketch-lab.json").read_text(encoding="utf-8"))
    assumptions = json.loads((ROOT / "analysis/throughlines/assumption-audit-lab.json").read_text(encoding="utf-8"))
    worked_transfer = json.loads((ROOT / "analysis/throughlines/worked-transfer-examples.json").read_text(encoding="utf-8"))
    capstones = json.loads((ROOT / "analysis/throughlines/capstone-self-test.json").read_text(encoding="utf-8"))
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
    required = [SITE / name for name in ["index.html", "study-route.html", "recognition.html", "math-clinic.html", "drills.html", "solutions.html", "cases.html", "argument-chains.html", "repairs.html", "paper-reading.html", "jargon-decoder.html", "model-building.html", "proof-sketches.html", "assumptions.html", "worked-transfer.html", "capstone.html", "cross-reference.html", "limits.html", "lectures.html", "concepts.html", "themes.html", "families.html", "primitives.html", "evidence.html", "assets/styles.css"]]
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
    solutions_html = (SITE / "solutions.html").read_text(encoding="utf-8") if (SITE / "solutions.html").exists() else ""
    cases_html = (SITE / "cases.html").read_text(encoding="utf-8") if (SITE / "cases.html").exists() else ""
    chains_html = (SITE / "argument-chains.html").read_text(encoding="utf-8") if (SITE / "argument-chains.html").exists() else ""
    repairs_html = (SITE / "repairs.html").read_text(encoding="utf-8") if (SITE / "repairs.html").exists() else ""
    paper_reading_html = (SITE / "paper-reading.html").read_text(encoding="utf-8") if (SITE / "paper-reading.html").exists() else ""
    jargon_decoder_html = (SITE / "jargon-decoder.html").read_text(encoding="utf-8") if (SITE / "jargon-decoder.html").exists() else ""
    workbook_html = (SITE / "model-building.html").read_text(encoding="utf-8") if (SITE / "model-building.html").exists() else ""
    proofs_html = (SITE / "proof-sketches.html").read_text(encoding="utf-8") if (SITE / "proof-sketches.html").exists() else ""
    assumptions_html = (SITE / "assumptions.html").read_text(encoding="utf-8") if (SITE / "assumptions.html").exists() else ""
    worked_transfer_html = (SITE / "worked-transfer.html").read_text(encoding="utf-8") if (SITE / "worked-transfer.html").exists() else ""
    capstone_html = (SITE / "capstone.html").read_text(encoding="utf-8") if (SITE / "capstone.html").exists() else ""
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
    if 'href="solutions.html"' not in index_html:
        errors.append("index page missing solution workshop link")
    if 'href="cases.html"' not in index_html:
        errors.append("index page missing case studies link")
    if 'href="argument-chains.html"' not in index_html:
        errors.append("index page missing argument chains link")
    if 'href="repairs.html"' not in index_html:
        errors.append("index page missing misconception repairs link")
    if 'href="paper-reading.html"' not in index_html:
        errors.append("index page missing paper-reading guide link")
    if 'href="jargon-decoder.html"' not in index_html:
        errors.append("index page missing jargon decoder link")
    if 'href="model-building.html"' not in index_html:
        errors.append("index page missing model-building workbook link")
    if 'href="proof-sketches.html"' not in index_html:
        errors.append("index page missing proof-sketch lab link")
    if 'href="assumptions.html"' not in index_html:
        errors.append("index page missing assumption-audit lab link")
    if 'href="worked-transfer.html"' not in index_html:
        errors.append("index page missing worked-transfer examples link")
    if 'href="capstone.html"' not in index_html:
        errors.append("index page missing capstone link")
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
        for field in ["reader_question", "plain_language_goal", "problem_pressure", "why_this_stage_comes_now", "mathematical_lever", "misuse_warning", "bridge_to_next_stage", "checkpoint"]:
            minimum = 10 if field in ["reader_question", "plain_language_goal", "checkpoint"] else 30
            if words(item.get(field, "")) < minimum:
                errors.append(f"study route {item['id']} has shallow {field}")
            elif html.escape(item[field], quote=True) not in route_html:
                errors.append(f"study route {item['id']} {field} not rendered")
        combined = " ".join(
            str(item.get(field, ""))
            for field in ["reader_question", "plain_language_goal", "problem_pressure", "why_this_stage_comes_now", "mathematical_lever", "misuse_warning", "bridge_to_next_stage", "checkpoint"]
        )
        if words(combined) < 210:
            errors.append(f"study route {item['id']} has shallow combined route treatment")
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
        fields = ["reader_situation", "diagnostic_question", "decision_cue", "first_principles_test", "mathematical_handle", "wrong_diagnosis_cost", "worked_recognition", "false_friend", "transfer_check", "where_to_go_next"]
        for field in fields:
            value = item.get(field, "")
            minimum = 10 if field in ["diagnostic_question", "where_to_go_next"] else 24
            if words(value) < minimum:
                errors.append(f"recognition clinic {item['id']} has shallow {field}")
            elif html.escape(value, quote=True) not in recognition_html:
                errors.append(f"recognition clinic {item['id']} {field} not rendered")
        if words(" ".join(str(item.get(field, "")) for field in fields)) < 310:
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
        fields = ["problem_before_math", "failed_shortcut", "plain_english_equation_reading", "symbol_by_symbol", "worked_numbers", "why_math_has_to_exist", "assumption_check", "why_this_changes_reasoning", "misuse_repair", "transfer_test"]
        for field in fields:
            value = item.get(field, "")
            if words(value) < 22:
                errors.append(f"math clinic {item['id']} has shallow {field}")
            elif html.escape(value, quote=True) not in math_clinic_html:
                errors.append(f"math clinic {item['id']} {field} not rendered")
        if words(" ".join(str(item.get(field, "")) for field in fields)) < 330:
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
        fields = ["scenario", "reader_task", "setup_pressure", "first_principles_answer", "math_move", "worked_resolution", "assumption_check", "common_wrong_turn", "transfer_prompt", "evidence_checkpoint"]
        for field in fields:
            value = drill.get(field, "")
            minimum = 12 if field in ["scenario", "reader_task", "evidence_checkpoint"] else 24
            if words(value) < minimum:
                errors.append(f"problem drill {drill['id']} has shallow {field}")
            elif html.escape(value, quote=True) not in drills_html:
                errors.append(f"problem drill {drill['id']} {field} not rendered")
        if words(" ".join(str(drill.get(field, "")) for field in fields)) < 285:
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
    math_clinic_by_id = {item["id"]: item for item in math_clinic}
    drill_by_id = {drill["id"]: drill for drill in drills}
    family_by_id = {family["id"]: family for family in families}
    case_by_id = {case["id"]: case for case in cases}
    paper_by_id = {item["id"]: item for item in paper_reading}
    decoder_by_id = {item["id"]: item for item in jargon_decoder}
    model_step_by_id = {item["id"]: item for item in workbook}
    proof_by_id = {item["id"]: item for item in proofs}
    assumption_by_id = {item["id"]: item for item in assumptions}
    if len(solutions) < 8:
        errors.append(f"solution workshop has only {len(solutions)} cards")
    for item in solutions:
        if f'id="{item["id"]}"' not in solutions_html:
            errors.append(f"solution workshop item not rendered: {item['id']}")
        fields = ["problem", "ordinary_setup", "model_choice", "worked_solution", "math_check", "assumption_audit", "common_wrong_answer", "transfer_rule"]
        for field in fields:
            value = item.get(field, "")
            if words(value) < 22:
                errors.append(f"solution workshop {item['id']} has shallow {field}")
            elif html.escape(value, quote=True) not in solutions_html:
                errors.append(f"solution workshop {item['id']} {field} not rendered")
        combined = " ".join(str(item.get(field, "")) for field in fields)
        if words(combined) < 285:
            errors.append(f"solution workshop {item['id']} has shallow combined treatment")
        for concept_id in item.get("concepts", []):
            if concept_id not in concept_by_id:
                errors.append(f"solution workshop {item['id']} references missing concept: {concept_id}")
            elif f'href="concepts/{concept_id}.html"' not in solutions_html:
                errors.append(f"solution workshop {item['id']} missing concept link: {concept_id}")
        for primitive_id in item.get("primitives", []):
            if primitive_id not in primitive_by_id:
                errors.append(f"solution workshop {item['id']} references missing primitive: {primitive_id}")
            elif f'href="primitives.html#{primitive_id}"' not in solutions_html:
                errors.append(f"solution workshop {item['id']} missing primitive link: {primitive_id}")
        for drill_id in item.get("drill_ids", []):
            if drill_id not in drill_by_id:
                errors.append(f"solution workshop {item['id']} references missing drill: {drill_id}")
            elif f'href="drills.html#{drill_id}"' not in solutions_html:
                errors.append(f"solution workshop {item['id']} missing drill link: {drill_id}")
        for case_id in item.get("case_ids", []):
            if case_id not in case_by_id:
                errors.append(f"solution workshop {item['id']} references missing case: {case_id}")
            elif f'href="cases.html#{case_id}"' not in solutions_html:
                errors.append(f"solution workshop {item['id']} missing case link: {case_id}")
        for card_id in item.get("math_clinic_ids", []):
            if card_id not in math_clinic_by_id:
                errors.append(f"solution workshop {item['id']} references missing math clinic card: {card_id}")
            elif f'href="math-clinic.html#{card_id}"' not in solutions_html:
                errors.append(f"solution workshop {item['id']} missing math clinic link: {card_id}")
        for decoder_id in item.get("decoder_ids", []):
            if decoder_id not in decoder_by_id:
                errors.append(f"solution workshop {item['id']} references missing decoder card: {decoder_id}")
            elif f'href="jargon-decoder.html#{decoder_id}"' not in solutions_html:
                errors.append(f"solution workshop {item['id']} missing decoder link: {decoder_id}")
        for ev_id in item.get("evidence_ids", []):
            if ev_id not in ev_by_id:
                errors.append(f"solution workshop {item['id']} references missing evidence: {ev_id}")
            elif f'href="evidence.html#{ev_id}"' not in solutions_html:
                errors.append(f"solution workshop {item['id']} missing evidence link: {ev_id}")
    if len(cases) < 5:
        errors.append(f"case studies has only {len(cases)} cards")
    case_fields = [
        "real_world_setup",
        "first_principles_question",
        "modeling_path",
        "mathematical_spine",
        "worked_walkthrough",
        "where_simple_story_breaks",
        "what_to_check_in_transcript",
        "why_this_case_matters",
        "transfer_lesson",
        "failure_audit",
    ]
    for case in cases:
        if f'id="{case["id"]}"' not in cases_html:
            errors.append(f"case study not rendered: {case['id']}")
        for field in case_fields:
            value = case.get(field, "")
            if words(value) < 14:
                errors.append(f"case study {case['id']} has shallow {field}")
            elif html.escape(value, quote=True) not in cases_html:
                errors.append(f"case study {case['id']} {field} not rendered")
        if words(" ".join(str(case.get(field, "")) for field in case_fields)) < 390:
            errors.append(f"case study {case['id']} has shallow combined treatment")
        for concept_id in case.get("concepts", []):
            if concept_id not in concept_by_id:
                errors.append(f"case study {case['id']} references missing concept: {concept_id}")
            elif f'href="concepts/{concept_id}.html"' not in cases_html:
                errors.append(f"case study {case['id']} missing concept link: {concept_id}")
        for primitive_id in case.get("primitives", []):
            if primitive_id not in primitive_by_id:
                errors.append(f"case study {case['id']} references missing primitive: {primitive_id}")
            elif f'href="primitives.html#{primitive_id}"' not in cases_html:
                errors.append(f"case study {case['id']} missing primitive link: {primitive_id}")
        for card_id in case.get("math_clinic_ids", []):
            if card_id not in math_clinic_by_id:
                errors.append(f"case study {case['id']} references missing math clinic card: {card_id}")
            elif f'href="math-clinic.html#{card_id}"' not in cases_html:
                errors.append(f"case study {case['id']} missing math clinic link: {card_id}")
        for drill_id in case.get("drill_ids", []):
            if drill_id not in drill_by_id:
                errors.append(f"case study {case['id']} references missing drill: {drill_id}")
            elif f'href="drills.html#{drill_id}"' not in cases_html:
                errors.append(f"case study {case['id']} missing drill link: {drill_id}")
        for ev_id in case.get("evidence_ids", []):
            if ev_id not in ev_by_id:
                errors.append(f"case study {case['id']} references missing evidence: {ev_id}")
            elif f'href="evidence.html#{ev_id}"' not in cases_html:
                errors.append(f"case study {case['id']} missing evidence link: {ev_id}")
    if len(chains) < 6:
        errors.append(f"argument chains has only {len(chains)} cards")
    for chain in chains:
        if f'id="{chain["id"]}"' not in chains_html:
            errors.append(f"argument chain not rendered: {chain['id']}")
        chain_fields = [
            "chain_question",
            "plain_language_thesis",
            "first_principles_payoff",
            "where_to_be_careful",
            "hidden_assumption",
            "failed_shortcut",
            "lecture_handoff",
            "where_the_analogy_breaks",
            "reader_test",
        ]
        for field in chain_fields:
            value = chain.get(field, "")
            if words(value) < 22:
                errors.append(f"argument chain {chain['id']} has shallow {field}")
            elif html.escape(value, quote=True) not in chains_html:
                errors.append(f"argument chain {chain['id']} {field} not rendered")
        if len(chain.get("argument_steps", [])) < 3:
            errors.append(f"argument chain {chain['id']} has too few steps")
        for step in chain.get("argument_steps", []):
            if words(step) < 12:
                errors.append(f"argument chain {chain['id']} has shallow step")
            elif html.escape(step, quote=True) not in chains_html:
                errors.append(f"argument chain {chain['id']} step not rendered")
        if words(" ".join(str(chain.get(field, "")) for field in chain_fields) + " " + " ".join(chain.get("argument_steps", []))) < 430:
            errors.append(f"argument chain {chain['id']} has shallow combined treatment")
        for lecture_id in chain.get("lecture_sequence", []):
            if lecture_id not in lecture_by_id:
                errors.append(f"argument chain {chain['id']} references missing lecture: {lecture_id}")
            elif f'href="lectures/{lecture_id}.html"' not in chains_html:
                errors.append(f"argument chain {chain['id']} missing lecture link: {lecture_id}")
        for concept_id in chain.get("concepts", []):
            if concept_id not in concept_by_id:
                errors.append(f"argument chain {chain['id']} references missing concept: {concept_id}")
            elif f'href="concepts/{concept_id}.html"' not in chains_html:
                errors.append(f"argument chain {chain['id']} missing concept link: {concept_id}")
        for primitive_id in chain.get("primitives", []):
            if primitive_id not in primitive_by_id:
                errors.append(f"argument chain {chain['id']} references missing primitive: {primitive_id}")
            elif f'href="primitives.html#{primitive_id}"' not in chains_html:
                errors.append(f"argument chain {chain['id']} missing primitive link: {primitive_id}")
        for ev_id in chain.get("evidence_ids", []):
            if ev_id not in ev_by_id:
                errors.append(f"argument chain {chain['id']} references missing evidence: {ev_id}")
            elif f'href="evidence.html#{ev_id}"' not in chains_html:
                errors.append(f"argument chain {chain['id']} missing evidence link: {ev_id}")
    if len(repairs) < 8:
        errors.append(f"misconception repairs has only {len(repairs)} cards")
    for repair in repairs:
        if f'id="{repair["id"]}"' not in repairs_html:
            errors.append(f"misconception repair not rendered: {repair['id']}")
        fields = ["mistaken_belief", "why_it_is_tempting", "first_principles_repair", "diagnostic_question", "what_breaks_if_ignored", "worked_correction", "transfer_test", "evidence_note"]
        for field in fields:
            value = repair.get(field, "")
            minimum = 12 if field in ["mistaken_belief", "diagnostic_question", "evidence_note"] else 24
            if words(value) < minimum:
                errors.append(f"misconception repair {repair['id']} has shallow {field}")
            elif html.escape(value, quote=True) not in repairs_html:
                errors.append(f"misconception repair {repair['id']} {field} not rendered")
        if words(" ".join(str(repair.get(field, "")) for field in fields)) < 260:
            errors.append(f"misconception repair {repair['id']} has shallow combined treatment")
        for concept_id in repair.get("concepts", []):
            if concept_id not in concept_by_id:
                errors.append(f"misconception repair {repair['id']} references missing concept: {concept_id}")
            elif f'href="concepts/{concept_id}.html"' not in repairs_html:
                errors.append(f"misconception repair {repair['id']} missing concept link: {concept_id}")
        for concept_id in repair.get("limit_concepts", []):
            if concept_id not in concept_by_id:
                errors.append(f"misconception repair {repair['id']} references missing limit concept: {concept_id}")
            elif f'href="limits.html#limit-{concept_id}"' not in repairs_html:
                errors.append(f"misconception repair {repair['id']} missing limit link: {concept_id}")
        for drill_id in repair.get("drill_ids", []):
            if drill_id not in drill_by_id:
                errors.append(f"misconception repair {repair['id']} references missing drill: {drill_id}")
            elif f'href="drills.html#{drill_id}"' not in repairs_html:
                errors.append(f"misconception repair {repair['id']} missing drill link: {drill_id}")
        for ev_id in repair.get("evidence_ids", []):
            if ev_id not in ev_by_id:
                errors.append(f"misconception repair {repair['id']} references missing evidence: {ev_id}")
            elif f'href="evidence.html#{ev_id}"' not in repairs_html:
                errors.append(f"misconception repair {repair['id']} missing evidence link: {ev_id}")
    if len(paper_reading) < 7:
        errors.append(f"paper-reading guide has only {len(paper_reading)} cards")
    for guide in paper_reading:
        if f'id="{guide["id"]}"' not in paper_reading_html:
            errors.append(f"paper-reading guide not rendered: {guide['id']}")
        for field in ["paper_signal", "everyday_reading", "first_principles_test", "mathematical_handle", "what_to_check_in_the_model", "common_misread", "course_bridge"]:
            value = guide.get(field, "")
            if words(value) < 16:
                errors.append(f"paper-reading guide {guide['id']} has shallow {field}")
            elif html.escape(value, quote=True) not in paper_reading_html:
                errors.append(f"paper-reading guide {guide['id']} {field} not rendered")
        combined = " ".join(str(guide.get(field, "")) for field in ["paper_signal", "everyday_reading", "first_principles_test", "mathematical_handle", "what_to_check_in_the_model", "common_misread", "course_bridge"])
        if words(combined) < 190:
            errors.append(f"paper-reading guide {guide['id']} has shallow combined treatment")
        for concept_id in guide.get("concepts", []):
            if concept_id not in concept_by_id:
                errors.append(f"paper-reading guide {guide['id']} references missing concept: {concept_id}")
            elif f'href="concepts/{concept_id}.html"' not in paper_reading_html:
                errors.append(f"paper-reading guide {guide['id']} missing concept link: {concept_id}")
        for primitive_id in guide.get("primitives", []):
            if primitive_id not in primitive_by_id:
                errors.append(f"paper-reading guide {guide['id']} references missing primitive: {primitive_id}")
            elif f'href="primitives.html#{primitive_id}"' not in paper_reading_html:
                errors.append(f"paper-reading guide {guide['id']} missing primitive link: {primitive_id}")
        for family_id in guide.get("family_ids", []):
            if family_id not in family_by_id:
                errors.append(f"paper-reading guide {guide['id']} references missing method family: {family_id}")
            elif f'href="families.html#{family_id}"' not in paper_reading_html:
                errors.append(f"paper-reading guide {guide['id']} missing family link: {family_id}")
        for case_id in guide.get("case_ids", []):
            if case_id not in case_by_id:
                errors.append(f"paper-reading guide {guide['id']} references missing case: {case_id}")
            elif f'href="cases.html#{case_id}"' not in paper_reading_html:
                errors.append(f"paper-reading guide {guide['id']} missing case link: {case_id}")
        for drill_id in guide.get("drill_ids", []):
            if drill_id not in drill_by_id:
                errors.append(f"paper-reading guide {guide['id']} references missing drill: {drill_id}")
            elif f'href="drills.html#{drill_id}"' not in paper_reading_html:
                errors.append(f"paper-reading guide {guide['id']} missing drill link: {drill_id}")
        for card_id in guide.get("math_clinic_ids", []):
            if card_id not in math_clinic_by_id:
                errors.append(f"paper-reading guide {guide['id']} references missing math clinic card: {card_id}")
            elif f'href="math-clinic.html#{card_id}"' not in paper_reading_html:
                errors.append(f"paper-reading guide {guide['id']} missing math clinic link: {card_id}")
        for ev_id in guide.get("evidence_ids", []):
            if ev_id not in ev_by_id:
                errors.append(f"paper-reading guide {guide['id']} references missing evidence: {ev_id}")
            elif f'href="evidence.html#{ev_id}"' not in paper_reading_html:
                errors.append(f"paper-reading guide {guide['id']} missing evidence link: {ev_id}")
    if len(jargon_decoder) < 10:
        errors.append(f"jargon decoder has only {len(jargon_decoder)} cards")
    for item in jargon_decoder:
        if f'id="{item["id"]}"' not in jargon_decoder_html:
            errors.append(f"jargon decoder item not rendered: {item['id']}")
        decoder_fields = [
            "where_reader_sees_it",
            "plain_translation",
            "first_principles_pressure",
            "mathematical_object",
            "reading_test",
            "common_confusion",
            "how_to_unpack_in_a_paper",
            "what_the_term_repairs",
            "where_translation_breaks",
        ]
        for field in decoder_fields:
            value = item.get(field, "")
            if words(value) < 16:
                errors.append(f"jargon decoder {item['id']} has shallow {field}")
            elif html.escape(value, quote=True) not in jargon_decoder_html:
                errors.append(f"jargon decoder {item['id']} {field} not rendered")
        combined = " ".join(str(item.get(field, "")) for field in decoder_fields)
        if words(combined) < 300:
            errors.append(f"jargon decoder {item['id']} has shallow combined treatment")
        for concept_id in item.get("concepts", []):
            if concept_id not in concept_by_id:
                errors.append(f"jargon decoder {item['id']} references missing concept: {concept_id}")
            elif f'href="concepts/{concept_id}.html"' not in jargon_decoder_html:
                errors.append(f"jargon decoder {item['id']} missing concept link: {concept_id}")
        for primitive_id in item.get("primitives", []):
            if primitive_id not in primitive_by_id:
                errors.append(f"jargon decoder {item['id']} references missing primitive: {primitive_id}")
            elif f'href="primitives.html#{primitive_id}"' not in jargon_decoder_html:
                errors.append(f"jargon decoder {item['id']} missing primitive link: {primitive_id}")
        for ev_id in item.get("evidence_ids", []):
            if ev_id not in ev_by_id:
                errors.append(f"jargon decoder {item['id']} references missing evidence: {ev_id}")
            elif f'href="evidence.html#{ev_id}"' not in jargon_decoder_html:
                errors.append(f"jargon decoder {item['id']} missing evidence link: {ev_id}")
    if len(workbook) < 7:
        errors.append(f"model-building workbook has only {len(workbook)} cards")
    for item in workbook:
        if f'id="{item["id"]}"' not in workbook_html:
            errors.append(f"model-building workbook item not rendered: {item['id']}")
        workbook_fields = [
            "ordinary_question",
            "formal_slot",
            "why_this_slot_exists",
            "construction_move",
            "math_check",
            "failure_if_skipped",
            "worked_prompt",
            "naive_shortcut",
            "step_by_step_use",
            "transfer_check",
        ]
        for field in workbook_fields:
            value = item.get(field, "")
            if words(value) < 16:
                errors.append(f"model-building workbook {item['id']} has shallow {field}")
            elif html.escape(value, quote=True) not in workbook_html:
                errors.append(f"model-building workbook {item['id']} {field} not rendered")
        combined = " ".join(str(item.get(field, "")) for field in workbook_fields)
        if words(combined) < 360:
            errors.append(f"model-building workbook {item['id']} has shallow combined treatment")
        for concept_id in item.get("concepts", []):
            if concept_id not in concept_by_id:
                errors.append(f"model-building workbook {item['id']} references missing concept: {concept_id}")
            elif f'href="concepts/{concept_id}.html"' not in workbook_html:
                errors.append(f"model-building workbook {item['id']} missing concept link: {concept_id}")
        for primitive_id in item.get("primitives", []):
            if primitive_id not in primitive_by_id:
                errors.append(f"model-building workbook {item['id']} references missing primitive: {primitive_id}")
            elif f'href="primitives.html#{primitive_id}"' not in workbook_html:
                errors.append(f"model-building workbook {item['id']} missing primitive link: {primitive_id}")
        for drill_id in item.get("drill_ids", []):
            if drill_id not in drill_by_id:
                errors.append(f"model-building workbook {item['id']} references missing drill: {drill_id}")
            elif f'href="drills.html#{drill_id}"' not in workbook_html:
                errors.append(f"model-building workbook {item['id']} missing drill link: {drill_id}")
        for decoder_id in item.get("decoder_ids", []):
            if decoder_id not in decoder_by_id:
                errors.append(f"model-building workbook {item['id']} references missing decoder card: {decoder_id}")
            elif f'href="jargon-decoder.html#{decoder_id}"' not in workbook_html:
                errors.append(f"model-building workbook {item['id']} missing decoder link: {decoder_id}")
        for ev_id in item.get("evidence_ids", []):
            if ev_id not in ev_by_id:
                errors.append(f"model-building workbook {item['id']} references missing evidence: {ev_id}")
            elif f'href="evidence.html#{ev_id}"' not in workbook_html:
                errors.append(f"model-building workbook {item['id']} missing evidence link: {ev_id}")
    if len(proofs) < 8:
        errors.append(f"proof-sketch lab has only {len(proofs)} cards")
    proof_fields = [
        "ordinary_claim",
        "minimal_setup",
        "proof_idea",
        "mathematical_move",
        "why_it_matters",
        "where_it_breaks",
        "proof_reading_move",
        "student_trap",
        "rebuild_check",
    ]
    for item in proofs:
        if f'id="{item["id"]}"' not in proofs_html:
            errors.append(f"proof-sketch lab item not rendered: {item['id']}")
        for field in proof_fields:
            value = item.get(field, "")
            if words(value) < 18:
                errors.append(f"proof-sketch lab {item['id']} has shallow {field}")
            elif html.escape(value, quote=True) not in proofs_html:
                errors.append(f"proof-sketch lab {item['id']} {field} not rendered")
        combined = " ".join(str(item.get(field, "")) for field in proof_fields)
        if words(combined) < 390:
            errors.append(f"proof-sketch lab {item['id']} has shallow combined treatment")
        for concept_id in item.get("concepts", []):
            if concept_id not in concept_by_id:
                errors.append(f"proof-sketch lab {item['id']} references missing concept: {concept_id}")
            elif f'href="concepts/{concept_id}.html"' not in proofs_html:
                errors.append(f"proof-sketch lab {item['id']} missing concept link: {concept_id}")
        for primitive_id in item.get("primitives", []):
            if primitive_id not in primitive_by_id:
                errors.append(f"proof-sketch lab {item['id']} references missing primitive: {primitive_id}")
            elif f'href="primitives.html#{primitive_id}"' not in proofs_html:
                errors.append(f"proof-sketch lab {item['id']} missing primitive link: {primitive_id}")
        for card_id in item.get("math_clinic_ids", []):
            if card_id not in math_clinic_by_id:
                errors.append(f"proof-sketch lab {item['id']} references missing math clinic card: {card_id}")
            elif f'href="math-clinic.html#{card_id}"' not in proofs_html:
                errors.append(f"proof-sketch lab {item['id']} missing math clinic link: {card_id}")
        for decoder_id in item.get("decoder_ids", []):
            if decoder_id not in decoder_by_id:
                errors.append(f"proof-sketch lab {item['id']} references missing decoder card: {decoder_id}")
            elif f'href="jargon-decoder.html#{decoder_id}"' not in proofs_html:
                errors.append(f"proof-sketch lab {item['id']} missing decoder link: {decoder_id}")
        for ev_id in item.get("evidence_ids", []):
            if ev_id not in ev_by_id:
                errors.append(f"proof-sketch lab {item['id']} references missing evidence: {ev_id}")
            elif f'href="evidence.html#{ev_id}"' not in proofs_html:
                errors.append(f"proof-sketch lab {item['id']} missing evidence link: {ev_id}")
    if len(assumptions) < 7:
        errors.append(f"assumption-audit lab has only {len(assumptions)} cards")
    for item in assumptions:
        if f'id="{item["id"]}"' not in assumptions_html:
            errors.append(f"assumption-audit lab item not rendered: {item['id']}")
        assumption_fields = [
            "hidden_assumption",
            "why_it_exists",
            "audit_test",
            "what_changes_if_false",
            "mathematical_symptom",
            "repair_move",
            "naive_overread",
            "stress_test",
            "transfer_red_flag",
        ]
        for field in assumption_fields:
            value = item.get(field, "")
            if words(value) < 18:
                errors.append(f"assumption-audit lab {item['id']} has shallow {field}")
            elif html.escape(value, quote=True) not in assumptions_html:
                errors.append(f"assumption-audit lab {item['id']} {field} not rendered")
        combined = " ".join(str(item.get(field, "")) for field in assumption_fields)
        if words(combined) < 360:
            errors.append(f"assumption-audit lab {item['id']} has shallow combined treatment")
        for concept_id in item.get("concepts", []):
            if concept_id not in concept_by_id:
                errors.append(f"assumption-audit lab {item['id']} references missing concept: {concept_id}")
            elif f'href="concepts/{concept_id}.html"' not in assumptions_html:
                errors.append(f"assumption-audit lab {item['id']} missing concept link: {concept_id}")
        for primitive_id in item.get("primitives", []):
            if primitive_id not in primitive_by_id:
                errors.append(f"assumption-audit lab {item['id']} references missing primitive: {primitive_id}")
            elif f'href="primitives.html#{primitive_id}"' not in assumptions_html:
                errors.append(f"assumption-audit lab {item['id']} missing primitive link: {primitive_id}")
        for proof_id in item.get("proof_ids", []):
            if proof_id not in proof_by_id:
                errors.append(f"assumption-audit lab {item['id']} references missing proof sketch: {proof_id}")
            elif f'href="proof-sketches.html#{proof_id}"' not in assumptions_html:
                errors.append(f"assumption-audit lab {item['id']} missing proof-sketch link: {proof_id}")
        for step_id in item.get("model_step_ids", []):
            if step_id not in model_step_by_id:
                errors.append(f"assumption-audit lab {item['id']} references missing model-building step: {step_id}")
            elif f'href="model-building.html#{step_id}"' not in assumptions_html:
                errors.append(f"assumption-audit lab {item['id']} missing model-building link: {step_id}")
        for decoder_id in item.get("decoder_ids", []):
            if decoder_id not in decoder_by_id:
                errors.append(f"assumption-audit lab {item['id']} references missing decoder card: {decoder_id}")
            elif f'href="jargon-decoder.html#{decoder_id}"' not in assumptions_html:
                errors.append(f"assumption-audit lab {item['id']} missing decoder link: {decoder_id}")
        for ev_id in item.get("evidence_ids", []):
            if ev_id not in ev_by_id:
                errors.append(f"assumption-audit lab {item['id']} references missing evidence: {ev_id}")
            elif f'href="evidence.html#{ev_id}"' not in assumptions_html:
                errors.append(f"assumption-audit lab {item['id']} missing evidence link: {ev_id}")
    if len(worked_transfer) < 6:
        errors.append(f"worked transfer examples has only {len(worked_transfer)} cards")
    for item in worked_transfer:
        if f'id="{item["id"]}"' not in worked_transfer_html:
            errors.append(f"worked transfer example not rendered: {item['id']}")
        fields = ["new_situation", "model_construction", "first_principles_solution", "math_move", "assumption_check", "evidence_bridge", "transfer_lesson"]
        for field in fields:
            value = item.get(field, "")
            if words(value) < 18:
                errors.append(f"worked transfer example {item['id']} has shallow {field}")
            elif html.escape(value, quote=True) not in worked_transfer_html:
                errors.append(f"worked transfer example {item['id']} {field} not rendered")
        combined = " ".join(str(item.get(field, "")) for field in fields)
        if words(combined) < 220:
            errors.append(f"worked transfer example {item['id']} has shallow combined treatment")
        for concept_id in item.get("concepts", []):
            if concept_id not in concept_by_id:
                errors.append(f"worked transfer example {item['id']} references missing concept: {concept_id}")
            elif f'href="concepts/{concept_id}.html"' not in worked_transfer_html:
                errors.append(f"worked transfer example {item['id']} missing concept link: {concept_id}")
        for primitive_id in item.get("primitives", []):
            if primitive_id not in primitive_by_id:
                errors.append(f"worked transfer example {item['id']} references missing primitive: {primitive_id}")
            elif f'href="primitives.html#{primitive_id}"' not in worked_transfer_html:
                errors.append(f"worked transfer example {item['id']} missing primitive link: {primitive_id}")
        for step_id in item.get("model_step_ids", []):
            if step_id not in model_step_by_id:
                errors.append(f"worked transfer example {item['id']} references missing model-building step: {step_id}")
            elif f'href="model-building.html#{step_id}"' not in worked_transfer_html:
                errors.append(f"worked transfer example {item['id']} missing model-building link: {step_id}")
        for proof_id in item.get("proof_ids", []):
            if proof_id not in proof_by_id:
                errors.append(f"worked transfer example {item['id']} references missing proof sketch: {proof_id}")
            elif f'href="proof-sketches.html#{proof_id}"' not in worked_transfer_html:
                errors.append(f"worked transfer example {item['id']} missing proof-sketch link: {proof_id}")
        for assumption_id in item.get("assumption_ids", []):
            if assumption_id not in assumption_by_id:
                errors.append(f"worked transfer example {item['id']} references missing assumption audit: {assumption_id}")
            elif f'href="assumptions.html#{assumption_id}"' not in worked_transfer_html:
                errors.append(f"worked transfer example {item['id']} missing assumption-audit link: {assumption_id}")
        for decoder_id in item.get("decoder_ids", []):
            if decoder_id not in decoder_by_id:
                errors.append(f"worked transfer example {item['id']} references missing decoder card: {decoder_id}")
            elif f'href="jargon-decoder.html#{decoder_id}"' not in worked_transfer_html:
                errors.append(f"worked transfer example {item['id']} missing decoder link: {decoder_id}")
        for ev_id in item.get("evidence_ids", []):
            if ev_id not in ev_by_id:
                errors.append(f"worked transfer example {item['id']} references missing evidence: {ev_id}")
            elif f'href="evidence.html#{ev_id}"' not in worked_transfer_html:
                errors.append(f"worked transfer example {item['id']} missing evidence link: {ev_id}")
    if len(capstones) < 6:
        errors.append(f"capstone self-test has only {len(capstones)} cards")
    capstone_fields = [
        "scenario",
        "reader_task",
        "expected_reasoning",
        "math_check",
        "evidence_check",
        "what_wrong_answer_reveals",
        "transfer_prompt",
        "minimum_passing_answer",
        "self_audit_checklist",
        "transfer_failure_mode",
    ]
    for item in capstones:
        if f'id="{item["id"]}"' not in capstone_html:
            errors.append(f"capstone self-test item not rendered: {item['id']}")
        for field in capstone_fields:
            value = item.get(field, "")
            if words(value) < 16:
                errors.append(f"capstone self-test {item['id']} has shallow {field}")
            elif html.escape(value, quote=True) not in capstone_html:
                errors.append(f"capstone self-test {item['id']} {field} not rendered")
        combined = " ".join(str(item.get(field, "")) for field in capstone_fields)
        if words(combined) < 400:
            errors.append(f"capstone self-test {item['id']} has shallow combined treatment")
        for concept_id in item.get("concepts", []):
            if concept_id not in concept_by_id:
                errors.append(f"capstone self-test {item['id']} references missing concept: {concept_id}")
            elif f'href="concepts/{concept_id}.html"' not in capstone_html:
                errors.append(f"capstone self-test {item['id']} missing concept link: {concept_id}")
        for primitive_id in item.get("primitives", []):
            if primitive_id not in primitive_by_id:
                errors.append(f"capstone self-test {item['id']} references missing primitive: {primitive_id}")
            elif f'href="primitives.html#{primitive_id}"' not in capstone_html:
                errors.append(f"capstone self-test {item['id']} missing primitive link: {primitive_id}")
        for case_id in item.get("case_ids", []):
            if case_id not in case_by_id:
                errors.append(f"capstone self-test {item['id']} references missing case: {case_id}")
            elif f'href="cases.html#{case_id}"' not in capstone_html:
                errors.append(f"capstone self-test {item['id']} missing case link: {case_id}")
        for drill_id in item.get("drill_ids", []):
            if drill_id not in drill_by_id:
                errors.append(f"capstone self-test {item['id']} references missing drill: {drill_id}")
            elif f'href="drills.html#{drill_id}"' not in capstone_html:
                errors.append(f"capstone self-test {item['id']} missing drill link: {drill_id}")
        for paper_id in item.get("paper_reading_ids", []):
            if paper_id not in paper_by_id:
                errors.append(f"capstone self-test {item['id']} references missing paper-reading card: {paper_id}")
            elif f'href="paper-reading.html#{paper_id}"' not in capstone_html:
                errors.append(f"capstone self-test {item['id']} missing paper-reading link: {paper_id}")
        for decoder_id in item.get("decoder_ids", []):
            if decoder_id not in decoder_by_id:
                errors.append(f"capstone self-test {item['id']} references missing decoder card: {decoder_id}")
            elif f'href="jargon-decoder.html#{decoder_id}"' not in capstone_html:
                errors.append(f"capstone self-test {item['id']} missing decoder link: {decoder_id}")
        for ev_id in item.get("evidence_ids", []):
            if ev_id not in ev_by_id:
                errors.append(f"capstone self-test {item['id']} references missing evidence: {ev_id}")
            elif f'href="evidence.html#{ev_id}"' not in capstone_html:
                errors.append(f"capstone self-test {item['id']} missing evidence link: {ev_id}")
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
        limit_fields = [
            "common_misunderstanding",
            "student_trap",
            "course_boundary_note",
            "what_breaks_without_it",
            "failed_simple_approach",
            "why_math_has_to_exist",
            "mathematical_intuition",
            "cross_course_connections",
            "recognize_in_new_work",
        ]
        for field in limit_fields:
            value = concept.get(field, "")
            if words(value) < 8:
                errors.append(f"concept {concept['id']} has shallow limit field: {field}")
            elif html.escape(value, quote=True) not in limits_html:
                errors.append(f"limits page missing {field}: {concept['id']}")
        if words(" ".join(str(concept.get(field, "")) for field in limit_fields)) < 260:
            errors.append(f"concept {concept['id']} has shallow combined limit treatment")
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
        primitive_fields = [
            "everyday_setup",
            "plain_language_principle",
            "formal_object",
            "symbol_explanation",
            "first_principles_pressure",
            "worked_micro_case",
            "course_appearances",
            "why_it_matters",
            "transfer_test",
            "misuse_warning",
        ]
        for field in primitive_fields:
            value = primitive.get(field, "")
            if words(value) < 8:
                errors.append(f"primitive {primitive['id']} has shallow {field}")
            elif html.escape(value, quote=True) not in primitives_html:
                errors.append(f"primitive {primitive['id']} missing rendered field: {field}")
        if words(" ".join(str(primitive.get(field, "")) for field in primitive_fields)) < 320:
            errors.append(f"primitive {primitive['id']} has shallow combined treatment")
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
