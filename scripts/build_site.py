#!/usr/bin/env python3
from __future__ import annotations

import html
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from derivation_link_map import expected_derivation_ids_for_concept, expected_derivation_ids_for_lecture

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"


def load(path: str) -> Any:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def load_optional(path: str, default: Any) -> Any:
    full_path = ROOT / path
    return json.loads(full_path.read_text(encoding="utf-8")) if full_path.exists() else default


def esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(line.rstrip() for line in content.splitlines()) + "\n", encoding="utf-8")


def page(title: str, body: str, active: str = "", depth: int = 0) -> str:
    prefix = "../" * depth
    nav = [
        ("index.html", "Overview", "overview"),
        ("study-route.html", "Study Route", "study-route"),
        ("recognition.html", "Recognition", "recognition"),
        ("math-clinic.html", "Math Clinic", "math-clinic"),
        ("drills.html", "Drills", "drills"),
        ("solutions.html", "Solutions", "solutions"),
        ("cases.html", "Cases", "cases"),
        ("argument-chains.html", "Arguments", "argument-chains"),
        ("repairs.html", "Repairs", "repairs"),
        ("paper-reading.html", "Paper Reading", "paper-reading"),
        ("jargon-decoder.html", "Decoder", "jargon-decoder"),
        ("model-building.html", "Model Building", "model-building"),
        ("proof-sketches.html", "Proof Sketches", "proof-sketches"),
        ("assumptions.html", "Assumptions", "assumptions"),
        ("worked-transfer.html", "Worked Transfer", "worked-transfer"),
        ("capstone.html", "Capstone", "capstone"),
        ("cross-reference.html", "Cross Index", "cross-reference"),
        ("limits.html", "Limits", "limits"),
        ("lectures.html", "Lectures", "lectures"),
        ("concepts.html", "Concepts", "concepts"),
        ("themes.html", "Themes", "themes"),
        ("families.html", "Method Families", "families"),
        ("primitives.html", "Primitives", "primitives"),
        ("evidence.html", "Evidence", "evidence"),
    ]
    nav_html = "".join(
        f'<a class="{"active" if key == active else ""}" href="{prefix}{href}">{label}</a>' for href, label, key in nav
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(title)} · MIT Game Theory Concept Lab</title>
  <link rel="stylesheet" href="{prefix}assets/styles.css">
</head>
<body>
  <header class="topbar">
    <a class="brand" href="{prefix}index.html">MIT Game Theory Concept Lab</a>
    <nav>{nav_html}</nav>
  </header>
  <main>{body}</main>
</body>
</html>"""


def flow(title: str, steps: list[tuple[str, str]], kind: str = "concept-flow") -> str:
    return f"""<figure class="learning-diagram {kind}">
  <figcaption>{esc(title)}</figcaption>
  <div class="flow-steps">{''.join(f'<div class="flow-step"><span>{esc(label)}</span><p>{esc(text)}</p></div>' for label, text in steps)}</div>
</figure>"""


def evidence_map(evidence: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {record["id"]: record for record in evidence}


def concept_map(concepts: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {concept["id"]: concept for concept in concepts}


def subtheme_map(subthemes: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {subtheme["id"]: subtheme for subtheme in subthemes}


def lecture_evidence_map(lectures: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    mapping: dict[str, dict[str, Any]] = {}
    for lecture in lectures:
        for ev_id in lecture.get("evidence_ids", []):
            mapping[ev_id] = lecture
    return mapping


def derivation_map(derivations: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {derivation["id"]: derivation for derivation in derivations}


def derivation_links(ids: list[str], deriv_by_id: dict[str, dict[str, Any]], prefix: str = "") -> str:
    links = [
        f'<a class="chip derivation-link" href="{prefix}primitives.html#{esc(derivation_id)}">{esc(deriv_by_id[derivation_id]["title"])}</a>'
        for derivation_id in ids
        if derivation_id in deriv_by_id
    ]
    return "".join(links)


def concept_derivation_ids(concept: dict[str, Any], deriv_by_id: dict[str, dict[str, Any]]) -> list[str]:
    return expected_derivation_ids_for_concept(concept, deriv_by_id)


def lecture_derivation_ids(concepts: list[dict[str, Any]], deriv_by_id: dict[str, dict[str, Any]]) -> list[str]:
    return expected_derivation_ids_for_lecture(concepts, deriv_by_id)


def concept_card(concept: dict[str, Any], ev_by_id: dict[str, dict[str, Any]]) -> str:
    ev_items = []
    for ev_id in concept["course_evidence_ids"][:2]:
        ev = ev_by_id[ev_id]
        ev_items.append(f'<li><a href="evidence.html#{esc(ev_id)}">{esc(ev_id)}</a>: {esc(ev["video_title"])}</li>')
    return f"""<article class="concept-card" id="{esc(concept['id'])}">
  <p class="eyebrow">{esc(concept['theme_id']).replace('_', ' ')}</p>
  <h3><a href="concepts/{esc(concept['id'])}.html">{esc(concept['name'])}</a></h3>
  <p class="definition">{esc(concept['plain_language_definition'])}</p>
  <dl>
    <dt>Problem</dt><dd>{esc(concept['everyday_problem'])}</dd>
    <dt>Math</dt><dd>{esc(concept['mathematical_principle'])}</dd>
  </dl>
  <ul class="evidence-list">{''.join(ev_items)}</ul>
</article>"""


def evidence_row(
    ev: dict[str, Any],
    prefix: str = "",
    concept_by_id: dict[str, dict[str, Any]] | None = None,
    subtheme_by_id: dict[str, dict[str, Any]] | None = None,
    lecture_by_evidence_id: dict[str, dict[str, Any]] | None = None,
) -> str:
    when = f" {esc(ev['timestamp_start'])}" if ev.get("timestamp_start") else ""
    optional = ""
    for label, key in [
        ("Example or analogy", "example_or_analogy"),
        ("Conceptual payload", "conceptual_payload"),
        ("Why this span matters", "why_span_matters"),
        ("Transcript teaching note", "transcript_teaching_note"),
        ("Evidence boundary", "evidence_boundary"),
    ]:
        if ev.get(key):
            optional += f"  <p><strong>{esc(label)}:</strong> {esc(ev[key])}</p>\n"
    concept_by_id = concept_by_id or {}
    subtheme_by_id = subtheme_by_id or {}
    lecture_by_evidence_id = lecture_by_evidence_id or {}
    concept_links = "".join(
        f'<a class="chip" href="{prefix}concepts/{esc(concept_id)}.html">{esc(concept_by_id[concept_id]["name"])}</a>'
        for concept_id in ev.get("supports_concepts", [])
        if concept_id in concept_by_id
    )
    subtheme_links = "".join(
        f'<a class="chip" href="{prefix}themes.html#{esc(subtheme_id)}">{esc(subtheme_by_id[subtheme_id]["name"])}</a>'
        for subtheme_id in ev.get("supports_subthemes", [])
        if subtheme_id in subtheme_by_id
    )
    lecture = lecture_by_evidence_id.get(ev["id"])
    lecture_link = (
        f'<a class="chip" href="{prefix}lectures/{esc(lecture["id"])}.html">{esc(lecture["title"])}</a>'
        if lecture
        else ""
    )
    backlinks = ""
    if concept_by_id or subtheme_by_id or lecture_by_evidence_id:
        backlinks = f"""  <p><strong>Supports concepts:</strong> <span class="chips">{concept_links or '<span class="chip muted">No concept links</span>'}</span></p>
  <p><strong>Supports subthemes:</strong> <span class="chips">{subtheme_links or '<span class="chip muted">No subtheme links</span>'}</span></p>
  <p><strong>Lecture page:</strong> <span class="chips">{lecture_link or '<span class="chip muted">No lecture page link</span>'}</span></p>
"""
    backlink_block = f"{backlinks.rstrip()}\n" if backlinks else ""
    return f"""<article class="evidence" id="{esc(ev['id'])}">
  <h3><a href="{prefix}evidence.html#{esc(ev['id'])}">{esc(ev['id'])}</a>{when}</h3>
  <p class="meta">{esc(ev['video_title'])} · <a href="{esc(ev['youtube_url'])}">YouTube</a></p>
{backlink_block}  <p><strong>Lecture argument:</strong> {esc(ev['lecture_argument'])}</p>
{optional.rstrip()}
  <p><strong>Mathematical claim:</strong> {esc(ev['mathematical_claim'])}</p>
  <blockquote>{esc(ev['local_transcript_window'])}</blockquote>
</article>"""


def supplemental_evidence_row(ev: dict[str, Any]) -> str:
    when = f" {esc(ev['timestamp_start'])}" if ev.get("timestamp_start") else ""
    return f"""<article class="evidence" id="{esc(ev['id'])}">
  <h3>{esc(ev['id'])}{when}</h3>
  <p class="meta">{esc(ev['video_title'])} · <a href="{esc(ev['youtube_url'])}">YouTube</a></p>
  <p><strong>Lecture argument:</strong> {esc(ev['lecture_argument'])}</p>
  <p><strong>Conceptual payload:</strong> {esc(ev['conceptual_payload'])}</p>
  <p><strong>Why this span matters:</strong> {esc(ev['why_span_matters'])}</p>
  <blockquote>{esc(ev['local_transcript_window'])}</blockquote>
</article>"""


def build_index(concepts, themes, evidence, lectures):
    body = f"""<section class="hero">
  <div>
    <p class="eyebrow">Transcript-backed first-principles research</p>
    <h1>Understand game theory as a small set of ideas about choice, incentives, beliefs, time, rules, and knowledge.</h1>
    <p class="lead">This lab turns MIT 14.12's 25 lectures into a connected concept atlas. It starts with ordinary strategic problems, then introduces the math only when the idea needs it.</p>
  </div>
  <aside class="stats"><strong>{len(lectures)}</strong><span>lectures</span><strong>{len(concepts)}</strong><span>concepts</span><strong>{len(evidence)}</strong><span>evidence records</span></aside>
</section>
<section><h2>The Big Throughline</h2><p>Game theory studies situations where choosing well means reasoning about other choosers. Equilibrium, credibility, beliefs, auctions, signaling, and common knowledge are different answers to the same pressure: my best move depends on what others do, know, want, and expect.</p></section>
<section><h2>Use The Study Route</h2><p>The route map gives a compact path through the course: choice, representation, equilibrium, time, information, and design.</p><p><a class="button" href="study-route.html">Open the study route</a></p></section>
<section><h2>Diagnose A New Problem</h2><p>The recognition clinic teaches how to look at a fresh strategic situation and decide which course idea is actually doing the work.</p><p><a class="button" href="recognition.html">Open the recognition clinic</a></p></section>
<section><h2>Read The Math As A Move</h2><p>The math clinic turns core equations into problem-driven walkthroughs with failed shortcuts, worked numbers, and transfer tests.</p><p><a class="button" href="math-clinic.html">Open the math clinic</a></p></section>
<section><h2>Practice The Move</h2><p>The drills page gives small strategic situations and asks the reader to identify the concept, math move, wrong turn, and transcript evidence.</p><p><a class="button" href="drills.html">Open problem drills</a></p></section>
<section><h2>Work Full Solutions</h2><p>The solution workshop gives deeper solved problems: choose the model, solve the key comparison, audit assumptions, diagnose the wrong answer, and transfer the lesson to new papers or systems.</p><p><a class="button" href="solutions.html">Open solution workshop</a></p></section>
<section><h2>Follow A Full Case</h2><p>The case studies combine concepts, primitives, math clinic cards, drills, and transcript evidence inside realistic strategic situations.</p><p><a class="button" href="cases.html">Open case studies</a></p></section>
<section><h2>Follow The Lecture Argument</h2><p>The argument chains show how transcript-backed claims accumulate across lectures into larger first-principles throughlines.</p><p><a class="button" href="argument-chains.html">Open argument chains</a></p></section>
<section><h2>Repair Common Misreads</h2><p>The repair map starts from common wrong interpretations and points to the correction, concept pages, limits, drills, and evidence.</p><p><a class="button" href="repairs.html">Open misconception repairs</a></p></section>
<section><h2>Read New Papers And Models</h2><p>The paper-reading guide teaches how to recognize game-theory primitives when a paper uses different vocabulary for objectives, equilibrium, timing, information, mechanisms, or shared knowledge.</p><p><a class="button" href="paper-reading.html">Open paper-reading guide</a></p></section>
<section><h2>Decode The Vocabulary</h2><p>The jargon decoder translates course and paper terms into everyday pressure, mathematical object, reading test, common confusion, and transcript-backed links.</p><p><a class="button" href="jargon-decoder.html">Open the decoder</a></p></section>
<section><h2>Build The Model</h2><p>The model-building workbook walks from an ordinary situation to players, actions, timing, information, payoffs, solution concept, and model boundaries.</p><p><a class="button" href="model-building.html">Open model-building workbook</a></p></section>
<section><h2>Understand Why Results Are True</h2><p>The proof-sketch lab explains core theorem-like moves in everyday language: what setup is needed, why the result follows, which math relation does the work, and where it breaks.</p><p><a class="button" href="proof-sketches.html">Open proof sketches</a></p></section>
<section><h2>Audit The Assumptions</h2><p>The assumption-audit lab teaches how to check whether payoff, action, timing, belief, monitoring, auction, and communication assumptions are doing hidden work.</p><p><a class="button" href="assumptions.html">Open assumption audits</a></p></section>
<section><h2>Work New Scenarios End To End</h2><p>The worked-transfer examples take unfamiliar modern situations and walk from ordinary facts to model construction, mathematical move, assumption check, and transcript-backed lesson.</p><p><a class="button" href="worked-transfer.html">Open worked transfer examples</a></p></section>
<section><h2>Prove You Can Use It</h2><p>The capstone self-test gives transfer scenarios that force the reader to choose the model, read the math, avoid the wrong answer, and cite transcript evidence.</p><p><a class="button" href="capstone.html">Open the capstone</a></p></section>
<section><h2>Find A Concept By Pressure</h2><p>The cross index lets a reader jump from an everyday problem to the relevant concept, lecture, primitive, subtheme, and evidence record.</p><p><a class="button" href="cross-reference.html">Open the cross index</a></p></section>
<section><h2>Check The Limits</h2><p>The limits page collects common misunderstandings, student traps, and places where an analogy stops working.</p><p><a class="button" href="limits.html">Open limits and traps</a></p></section>
<section><h2>Start With The Course Path</h2><p>The lecture path follows the MIT sequence while linking each session to atlas concepts and transcript evidence.</p><p><a class="button" href="lectures.html">Open the lecture path</a></p></section>
<section><h2>Start With Concepts</h2><div class="grid">{''.join(concept_card(c, evidence_map(evidence)) for c in concepts[:6])}</div><p><a class="button" href="concepts.html">Open the full atlas</a></p></section>"""
    write(SITE / "index.html", page("Overview", body, "overview"))


def build_study_route(route, lecture_by_id, concept_by_id, primitive_by_id, ev_by_id):
    cards = []
    for item in route:
        lecture_links = "".join(
            f'<a class="chip" href="lectures/{esc(lecture_id)}.html">{esc(lecture_by_id[lecture_id]["title"])}</a>'
            for lecture_id in item.get("lectures", [])
            if lecture_id in lecture_by_id
        )
        concept_links = "".join(
            f'<a class="chip" href="concepts/{esc(concept_id)}.html">{esc(concept_by_id[concept_id]["name"])}</a>'
            for concept_id in item.get("concepts", [])
            if concept_id in concept_by_id
        )
        primitive_links = "".join(
            f'<a class="chip" href="primitives.html#{esc(primitive_id)}">{esc(primitive_by_id[primitive_id]["name"])}</a>'
            for primitive_id in item.get("primitives", [])
            if primitive_id in primitive_by_id
        )
        evidence_links = "".join(
            f'<li><a href="evidence.html#{esc(ev_id)}">{esc(ev_id)}</a>: {esc(ev_by_id[ev_id]["video_title"])}</li>'
            for ev_id in item.get("evidence", [])
            if ev_id in ev_by_id
        )
        cards.append(f"""<article class="wide-card route-card" id="{esc(item["id"])}">
  <p class="eyebrow">Study route</p>
  <h2>{esc(item["title"])}</h2>
  <p><strong>Reader question:</strong> {esc(item["reader_question"])}</p>
  <p><strong>Plain-language goal:</strong> {esc(item["plain_language_goal"])}</p>
  <p><strong>Problem pressure:</strong> {esc(item["problem_pressure"])}</p>
  <p><strong>Why this stage comes now:</strong> {esc(item["why_this_stage_comes_now"])}</p>
  <p><strong>Mathematical lever:</strong> {esc(item["mathematical_lever"])}</p>
  <p><strong>Misuse warning:</strong> {esc(item["misuse_warning"])}</p>
  <p><strong>Bridge to next stage:</strong> {esc(item["bridge_to_next_stage"])}</p>
  <h3>Lectures</h3><p class="chips">{lecture_links}</p>
  <h3>Concepts</h3><p class="chips">{concept_links}</p>
  <h3>Primitives</h3><p class="chips">{primitive_links}</p>
  <h3>Evidence Checkpoints</h3><ul class="evidence-list">{evidence_links}</ul>
  <h3>Checkpoint</h3><p>{esc(item["checkpoint"])}</p>
</article>""")
    body = '<section class="page-head"><h1>Study Route</h1><p>A compact path through the course, from first choice primitives to evidence-backed strategic reasoning.</p></section>' + "".join(cards)
    write(SITE / "study-route.html", page("Study Route", body, "study-route"))


def build_recognition_clinic(clinic, concept_by_id, primitive_by_id, ev_by_id):
    cards = []
    for item in clinic:
        concept_links = "".join(
            f'<a class="chip" href="concepts/{esc(concept_id)}.html">{esc(concept_by_id[concept_id]["name"])}</a>'
            for concept_id in item.get("use_these_concepts", [])
            if concept_id in concept_by_id
        )
        primitive_links = "".join(
            f'<a class="chip" href="primitives.html#{esc(primitive_id)}">{esc(primitive_by_id[primitive_id]["name"])}</a>'
            for primitive_id in item.get("use_these_primitives", [])
            if primitive_id in primitive_by_id
        )
        evidence_links = "".join(
            f'<li><a href="evidence.html#{esc(ev_id)}">{esc(ev_id)}</a>: {esc(ev_by_id[ev_id]["video_title"])}</li>'
            for ev_id in item.get("evidence_ids", [])
            if ev_id in ev_by_id
        )
        cards.append(f"""<article class="wide-card recognition-card" id="{esc(item["id"])}">
  <p class="eyebrow">Recognition clinic</p>
  <h2>{esc(item["title"])}</h2>
  <p><strong>Reader situation:</strong> {esc(item["reader_situation"])}</p>
  <p><strong>Diagnostic question:</strong> {esc(item["diagnostic_question"])}</p>
  <p><strong>Decision cue:</strong> {esc(item["decision_cue"])}</p>
  <p><strong>First-principles test:</strong> {esc(item["first_principles_test"])}</p>
  <p><strong>Mathematical handle:</strong> {esc(item["mathematical_handle"])}</p>
  <p><strong>Wrong diagnosis cost:</strong> {esc(item["wrong_diagnosis_cost"])}</p>
  <p><strong>Worked recognition:</strong> {esc(item["worked_recognition"])}</p>
  <p><strong>False friend:</strong> {esc(item["false_friend"])}</p>
  <p><strong>Transfer check:</strong> {esc(item["transfer_check"])}</p>
  <h3>Use These Concepts</h3><p class="chips">{concept_links}</p>
  <h3>Reusable Primitives</h3><p class="chips">{primitive_links}</p>
  <h3>Evidence Trail</h3><ul class="evidence-list">{evidence_links}</ul>
  <p><strong>Where to go next:</strong> {esc(item["where_to_go_next"])}</p>
</article>""")
    body = """<section class="page-head">
  <h1>Recognition Clinic</h1>
  <p>A diagnostic layer for fresh problems. Start with the situation in front of you, ask the simple test question, then jump into the concept, primitive, and transcript evidence that fit.</p>
</section>""" + "".join(cards)
    write(SITE / "recognition.html", page("Recognition Clinic", body, "recognition"))


def build_math_clinic(clinic, deriv_by_id, concept_by_id, ev_by_id):
    cards = []
    for item in clinic:
        derivation = deriv_by_id.get(item["derivation_id"], {})
        concept_links = "".join(
            f'<a class="chip" href="concepts/{esc(concept_id)}.html">{esc(concept_by_id[concept_id]["name"])}</a>'
            for concept_id in item.get("concepts", [])
            if concept_id in concept_by_id
        )
        evidence_links = "".join(
            f'<li><a href="evidence.html#{esc(ev_id)}">{esc(ev_id)}</a>: {esc(ev_by_id[ev_id]["video_title"])}</li>'
            for ev_id in item.get("evidence_ids", [])
            if ev_id in ev_by_id
        )
        derivation_link = f'<a class="chip derivation-link" href="primitives.html#{esc(item["derivation_id"])}">{esc(derivation.get("title", item["derivation_id"]))}</a>'
        cards.append(f"""<article class="wide-card math-clinic-card" id="{esc(item["id"])}">
  <p class="eyebrow">Math walkthrough clinic</p>
  <h2>{esc(item["title"])}</h2>
  <p class="chips">{derivation_link}</p>
  <p><strong>Problem before math:</strong> {esc(item["problem_before_math"])}</p>
  <p><strong>Failed shortcut:</strong> {esc(item["failed_shortcut"])}</p>
  <p><strong>Plain-English equation reading:</strong> {esc(item["plain_english_equation_reading"])}</p>
  <p><strong>Symbol by symbol:</strong> {esc(item["symbol_by_symbol"])}</p>
  <p><strong>Worked numbers:</strong> {esc(item["worked_numbers"])}</p>
  <p><strong>Why the math has to exist:</strong> {esc(item["why_math_has_to_exist"])}</p>
  <p><strong>Assumption check:</strong> {esc(item["assumption_check"])}</p>
  <p><strong>Why this changes reasoning:</strong> {esc(item["why_this_changes_reasoning"])}</p>
  <p><strong>Misuse repair:</strong> {esc(item["misuse_repair"])}</p>
  <p><strong>Transfer test:</strong> {esc(item["transfer_test"])}</p>
  <h3>Concept Pages</h3><p class="chips">{concept_links}</p>
  <h3>Evidence Trail</h3><ul class="evidence-list">{evidence_links}</ul>
</article>""")
    body = """<section class="page-head">
  <h1>Math Walkthrough Clinic</h1>
  <p>Core equations treated as reasoning moves. Each card starts with the ordinary problem, shows the shortcut that fails, reads the equation in plain language, and gives a small numerical or concrete test.</p>
</section>""" + "".join(cards)
    write(SITE / "math-clinic.html", page("Math Walkthrough Clinic", body, "math-clinic"))


def build_problem_drills(drills, concept_by_id, primitive_by_id, ev_by_id):
    cards = []
    for drill in drills:
        concept_links = "".join(
            f'<a class="chip" href="concepts/{esc(concept_id)}.html">{esc(concept_by_id[concept_id]["name"])}</a>'
            for concept_id in drill.get("concepts", [])
            if concept_id in concept_by_id
        )
        primitive_links = "".join(
            f'<a class="chip" href="primitives.html#{esc(primitive_id)}">{esc(primitive_by_id[primitive_id]["name"])}</a>'
            for primitive_id in drill.get("primitives", [])
            if primitive_id in primitive_by_id
        )
        evidence_links = "".join(
            f'<li><a href="evidence.html#{esc(ev_id)}">{esc(ev_id)}</a>: {esc(ev_by_id[ev_id]["video_title"])}</li>'
            for ev_id in drill.get("evidence_ids", [])
            if ev_id in ev_by_id
        )
        cards.append(f"""<article class="wide-card drill-card" id="{esc(drill["id"])}">
  <p class="eyebrow">Problem drill</p>
  <h2>{esc(drill["title"])}</h2>
  <p><strong>Scenario:</strong> {esc(drill["scenario"])}</p>
  <p><strong>Reader task:</strong> {esc(drill["reader_task"])}</p>
  <p><strong>Setup pressure:</strong> {esc(drill["setup_pressure"])}</p>
  <p><strong>First-principles answer:</strong> {esc(drill["first_principles_answer"])}</p>
  <p><strong>Math move:</strong> {esc(drill["math_move"])}</p>
  <p><strong>Worked resolution:</strong> {esc(drill["worked_resolution"])}</p>
  <p><strong>Assumption check:</strong> {esc(drill["assumption_check"])}</p>
  <p><strong>Common wrong turn:</strong> {esc(drill["common_wrong_turn"])}</p>
  <p><strong>Transfer prompt:</strong> {esc(drill["transfer_prompt"])}</p>
  <p><strong>Evidence checkpoint:</strong> {esc(drill["evidence_checkpoint"])}</p>
  <h3>Concept Pages</h3><p class="chips">{concept_links}</p>
  <h3>Reusable Primitives</h3><p class="chips">{primitive_links}</p>
  <h3>Transcript Evidence</h3><ul class="evidence-list">{evidence_links}</ul>
</article>""")
    body = """<section class="page-head">
  <h1>Problem Drills</h1>
  <p>Small transfer problems for checking whether the reader can choose the right concept, name the math move, avoid the common wrong turn, and return to transcript evidence.</p>
</section>""" + "".join(cards)
    write(SITE / "drills.html", page("Problem Drills", body, "drills"))


def build_solution_workshop(solutions, concept_by_id, primitive_by_id, drill_by_id, case_by_id, math_clinic_by_id, decoder_by_id, ev_by_id):
    cards = []
    for item in solutions:
        concept_links = "".join(
            f'<a class="chip" href="concepts/{esc(concept_id)}.html">{esc(concept_by_id[concept_id]["name"])}</a>'
            for concept_id in item.get("concepts", [])
            if concept_id in concept_by_id
        )
        primitive_links = "".join(
            f'<a class="chip" href="primitives.html#{esc(primitive_id)}">{esc(primitive_by_id[primitive_id]["name"])}</a>'
            for primitive_id in item.get("primitives", [])
            if primitive_id in primitive_by_id
        )
        drill_links = "".join(
            f'<a class="chip" href="drills.html#{esc(drill_id)}">{esc(drill_by_id[drill_id]["title"])}</a>'
            for drill_id in item.get("drill_ids", [])
            if drill_id in drill_by_id
        )
        case_links = "".join(
            f'<a class="chip" href="cases.html#{esc(case_id)}">{esc(case_by_id[case_id]["title"])}</a>'
            for case_id in item.get("case_ids", [])
            if case_id in case_by_id
        )
        math_links = "".join(
            f'<a class="chip" href="math-clinic.html#{esc(card_id)}">{esc(math_clinic_by_id[card_id]["title"])}</a>'
            for card_id in item.get("math_clinic_ids", [])
            if card_id in math_clinic_by_id
        )
        decoder_links = "".join(
            f'<a class="chip" href="jargon-decoder.html#{esc(decoder_id)}">{esc(decoder_by_id[decoder_id]["term_family"])}</a>'
            for decoder_id in item.get("decoder_ids", [])
            if decoder_id in decoder_by_id
        )
        evidence_links = "".join(
            f'<li><a href="evidence.html#{esc(ev_id)}">{esc(ev_id)}</a>: {esc(ev_by_id[ev_id]["video_title"])}</li>'
            for ev_id in item.get("evidence_ids", [])
            if ev_id in ev_by_id
        )
        cards.append(f"""<article class="wide-card solution-card" id="{esc(item["id"])}">
  <p class="eyebrow">Solution workshop</p>
  <h2>{esc(item["title"])}</h2>
  <p><strong>Problem:</strong> {esc(item["problem"])}</p>
  <p><strong>Ordinary setup:</strong> {esc(item["ordinary_setup"])}</p>
  <p><strong>Model choice:</strong> {esc(item["model_choice"])}</p>
  <p><strong>Worked solution:</strong> {esc(item["worked_solution"])}</p>
  <p><strong>Math check:</strong> {esc(item["math_check"])}</p>
  <p><strong>Assumption audit:</strong> {esc(item["assumption_audit"])}</p>
  <p><strong>Common wrong answer:</strong> {esc(item["common_wrong_answer"])}</p>
  <p><strong>Transfer rule:</strong> {esc(item["transfer_rule"])}</p>
  <h3>Concept Pages</h3><p class="chips">{concept_links}</p>
  <h3>Reusable Primitives</h3><p class="chips">{primitive_links}</p>
  <h3>Related Drills</h3><p class="chips">{drill_links}</p>
  <h3>Related Cases</h3><p class="chips">{case_links or '<span class="chip muted">Standalone solution</span>'}</p>
  <h3>Math Clinic Cards</h3><p class="chips">{math_links}</p>
  <h3>Decoder Cards</h3><p class="chips">{decoder_links}</p>
  <h3>Transcript Evidence</h3><ul class="evidence-list">{evidence_links}</ul>
</article>""")
    body = """<section class="page-head">
  <h1>Solution Workshop</h1>
  <p>Deeper solved problems for learning how to use the course. Each walkthrough starts from an ordinary situation, chooses the game representation, solves the key comparison, audits assumptions, and states a transfer rule for reading new models.</p>
</section>""" + "".join(cards)
    write(SITE / "solutions.html", page("Solution Workshop", body, "solutions"))


def build_case_studies(cases, concept_by_id, primitive_by_id, math_clinic_by_id, drill_by_id, ev_by_id):
    cards = []
    for case in cases:
        concept_links = "".join(
            f'<a class="chip" href="concepts/{esc(concept_id)}.html">{esc(concept_by_id[concept_id]["name"])}</a>'
            for concept_id in case.get("concepts", [])
            if concept_id in concept_by_id
        )
        primitive_links = "".join(
            f'<a class="chip" href="primitives.html#{esc(primitive_id)}">{esc(primitive_by_id[primitive_id]["name"])}</a>'
            for primitive_id in case.get("primitives", [])
            if primitive_id in primitive_by_id
        )
        math_links = "".join(
            f'<a class="chip" href="math-clinic.html#{esc(card_id)}">{esc(math_clinic_by_id[card_id]["title"])}</a>'
            for card_id in case.get("math_clinic_ids", [])
            if card_id in math_clinic_by_id
        )
        drill_links = "".join(
            f'<a class="chip" href="drills.html#{esc(drill_id)}">{esc(drill_by_id[drill_id]["title"])}</a>'
            for drill_id in case.get("drill_ids", [])
            if drill_id in drill_by_id
        )
        evidence_links = "".join(
            f'<li><a href="evidence.html#{esc(ev_id)}">{esc(ev_id)}</a>: {esc(ev_by_id[ev_id]["video_title"])}</li>'
            for ev_id in case.get("evidence_ids", [])
            if ev_id in ev_by_id
        )
        cards.append(f"""<article class="wide-card case-card" id="{esc(case["id"])}">
  <p class="eyebrow">Case study</p>
  <h2>{esc(case["title"])}</h2>
  <p><strong>Real-world setup:</strong> {esc(case["real_world_setup"])}</p>
  <p><strong>First-principles question:</strong> {esc(case["first_principles_question"])}</p>
  <p><strong>Modeling path:</strong> {esc(case["modeling_path"])}</p>
  <p><strong>Mathematical spine:</strong> {esc(case["mathematical_spine"])}</p>
  <p><strong>Worked walkthrough:</strong> {esc(case["worked_walkthrough"])}</p>
  <p><strong>Where the simple story breaks:</strong> {esc(case["where_simple_story_breaks"])}</p>
  <p><strong>What to check in transcript:</strong> {esc(case["what_to_check_in_transcript"])}</p>
  <h3>Concept Pages</h3><p class="chips">{concept_links}</p>
  <h3>Reusable Primitives</h3><p class="chips">{primitive_links}</p>
  <h3>Math Clinic Cards</h3><p class="chips">{math_links}</p>
  <h3>Practice Drills</h3><p class="chips">{drill_links}</p>
  <h3>Transcript Evidence</h3><ul class="evidence-list">{evidence_links}</ul>
</article>""")
    body = """<section class="page-head">
  <h1>Case Studies</h1>
  <p>Applied strategic situations that combine representation, concept choice, mathematical primitives, worked reasoning, failure modes, and transcript evidence.</p>
</section>""" + "".join(cards)
    write(SITE / "cases.html", page("Case Studies", body, "cases"))


def build_argument_chains(chains, lecture_by_id, concept_by_id, primitive_by_id, ev_by_id):
    cards = []
    for chain in chains:
        lecture_links = "".join(
            f'<a class="chip" href="lectures/{esc(lecture_id)}.html">{esc(lecture_by_id[lecture_id]["title"])}</a>'
            for lecture_id in chain.get("lecture_sequence", [])
            if lecture_id in lecture_by_id
        )
        concept_links = "".join(
            f'<a class="chip" href="concepts/{esc(concept_id)}.html">{esc(concept_by_id[concept_id]["name"])}</a>'
            for concept_id in chain.get("concepts", [])
            if concept_id in concept_by_id
        )
        primitive_links = "".join(
            f'<a class="chip" href="primitives.html#{esc(primitive_id)}">{esc(primitive_by_id[primitive_id]["name"])}</a>'
            for primitive_id in chain.get("primitives", [])
            if primitive_id in primitive_by_id
        )
        evidence_links = "".join(
            f'<li><a href="evidence.html#{esc(ev_id)}">{esc(ev_id)}</a>: {esc(ev_by_id[ev_id]["video_title"])}</li>'
            for ev_id in chain.get("evidence_ids", [])
            if ev_id in ev_by_id
        )
        steps = "".join(f"<li>{esc(step)}</li>" for step in chain.get("argument_steps", []))
        cards.append(f"""<article class="wide-card argument-chain-card" id="{esc(chain["id"])}">
  <p class="eyebrow">Lecture argument chain</p>
  <h2>{esc(chain["title"])}</h2>
  <p><strong>Chain question:</strong> {esc(chain["chain_question"])}</p>
  <p><strong>Plain-language thesis:</strong> {esc(chain["plain_language_thesis"])}</p>
  <h3>Lecture Sequence</h3><p class="chips">{lecture_links}</p>
  <h3>Argument Steps</h3><ol>{steps}</ol>
  <p><strong>First-principles payoff:</strong> {esc(chain["first_principles_payoff"])}</p>
  <p><strong>Where to be careful:</strong> {esc(chain["where_to_be_careful"])}</p>
  <p><strong>Hidden assumption:</strong> {esc(chain["hidden_assumption"])}</p>
  <p><strong>Failed shortcut:</strong> {esc(chain["failed_shortcut"])}</p>
  <p><strong>Lecture handoff:</strong> {esc(chain["lecture_handoff"])}</p>
  <p><strong>Where the analogy breaks:</strong> {esc(chain["where_the_analogy_breaks"])}</p>
  <p><strong>Reader test:</strong> {esc(chain["reader_test"])}</p>
  <h3>Concept Pages</h3><p class="chips">{concept_links}</p>
  <h3>Reusable Primitives</h3><p class="chips">{primitive_links}</p>
  <h3>Transcript Evidence</h3><ul class="evidence-list">{evidence_links}</ul>
</article>""")
    body = """<section class="page-head">
  <h1>Lecture Argument Chains</h1>
  <p>Transcript-backed chains that show how the course builds larger ideas across lectures. Each chain keeps synthesis separate from the evidence records that support it.</p>
</section>""" + "".join(cards)
    write(SITE / "argument-chains.html", page("Lecture Argument Chains", body, "argument-chains"))


def build_misconception_repairs(repairs, concept_by_id, drill_by_id, ev_by_id):
    cards = []
    for repair in repairs:
        concept_links = "".join(
            f'<a class="chip" href="concepts/{esc(concept_id)}.html">{esc(concept_by_id[concept_id]["name"])}</a>'
            for concept_id in repair.get("concepts", [])
            if concept_id in concept_by_id
        )
        drill_links = "".join(
            f'<a class="chip" href="drills.html#{esc(drill_id)}">{esc(drill_by_id[drill_id]["title"])}</a>'
            for drill_id in repair.get("drill_ids", [])
            if drill_id in drill_by_id
        )
        limit_links = "".join(
            f'<a class="chip" href="limits.html#limit-{esc(concept_id)}">{esc(concept_by_id[concept_id]["name"])}</a>'
            for concept_id in repair.get("limit_concepts", [])
            if concept_id in concept_by_id
        )
        evidence_links = "".join(
            f'<li><a href="evidence.html#{esc(ev_id)}">{esc(ev_id)}</a>: {esc(ev_by_id[ev_id]["video_title"])}</li>'
            for ev_id in repair.get("evidence_ids", [])
            if ev_id in ev_by_id
        )
        cards.append(f"""<article class="wide-card repair-card" id="{esc(repair["id"])}">
  <p class="eyebrow">Misconception repair</p>
  <h2>{esc(repair["mistaken_belief"])}</h2>
  <p><strong>Why it is tempting:</strong> {esc(repair["why_it_is_tempting"])}</p>
  <p><strong>First-principles repair:</strong> {esc(repair["first_principles_repair"])}</p>
  <p><strong>Diagnostic question:</strong> {esc(repair["diagnostic_question"])}</p>
  <p><strong>What breaks if ignored:</strong> {esc(repair["what_breaks_if_ignored"])}</p>
  <p><strong>Worked correction:</strong> {esc(repair["worked_correction"])}</p>
  <p><strong>Transfer test:</strong> {esc(repair["transfer_test"])}</p>
  <p><strong>Evidence note:</strong> {esc(repair["evidence_note"])}</p>
  <h3>Concept Pages</h3><p class="chips">{concept_links}</p>
  <h3>Limits And Traps</h3><p class="chips">{limit_links}</p>
  <h3>Practice Drill</h3><p class="chips">{drill_links}</p>
  <h3>Transcript Evidence</h3><ul class="evidence-list">{evidence_links}</ul>
</article>""")
    body = """<section class="page-head">
  <h1>Misconception Repairs</h1>
  <p>A correction map for common wrong turns. Start from the mistaken belief, then follow the repair into concepts, limits, drills, and transcript evidence.</p>
</section>""" + "".join(cards)
    write(SITE / "repairs.html", page("Misconception Repairs", body, "repairs"))


def build_paper_reading_guide(guides, concept_by_id, primitive_by_id, family_by_id, case_by_id, drill_by_id, math_clinic_by_id, ev_by_id):
    cards = []
    for guide in guides:
        concept_links = "".join(
            f'<a class="chip" href="concepts/{esc(concept_id)}.html">{esc(concept_by_id[concept_id]["name"])}</a>'
            for concept_id in guide.get("concepts", [])
            if concept_id in concept_by_id
        )
        primitive_links = "".join(
            f'<a class="chip" href="primitives.html#{esc(primitive_id)}">{esc(primitive_by_id[primitive_id]["name"])}</a>'
            for primitive_id in guide.get("primitives", [])
            if primitive_id in primitive_by_id
        )
        family_links = "".join(
            f'<a class="chip" href="families.html#{esc(family_id)}">{esc(family_by_id[family_id]["name"])}</a>'
            for family_id in guide.get("family_ids", [])
            if family_id in family_by_id
        )
        case_links = "".join(
            f'<a class="chip" href="cases.html#{esc(case_id)}">{esc(case_by_id[case_id]["title"])}</a>'
            for case_id in guide.get("case_ids", [])
            if case_id in case_by_id
        )
        drill_links = "".join(
            f'<a class="chip" href="drills.html#{esc(drill_id)}">{esc(drill_by_id[drill_id]["title"])}</a>'
            for drill_id in guide.get("drill_ids", [])
            if drill_id in drill_by_id
        )
        math_links = "".join(
            f'<a class="chip" href="math-clinic.html#{esc(card_id)}">{esc(math_clinic_by_id[card_id]["title"])}</a>'
            for card_id in guide.get("math_clinic_ids", [])
            if card_id in math_clinic_by_id
        )
        evidence_links = "".join(
            f'<li><a href="evidence.html#{esc(ev_id)}">{esc(ev_id)}</a>: {esc(ev_by_id[ev_id]["video_title"])}</li>'
            for ev_id in guide.get("evidence_ids", [])
            if ev_id in ev_by_id
        )
        cards.append(f"""<article class="wide-card paper-reading-card" id="{esc(guide["id"])}">
  <p class="eyebrow">Paper reading guide</p>
  <h2>{esc(guide["title"])}</h2>
  <p><strong>Paper signal:</strong> {esc(guide["paper_signal"])}</p>
  <p><strong>Everyday reading:</strong> {esc(guide["everyday_reading"])}</p>
  <p><strong>First-principles test:</strong> {esc(guide["first_principles_test"])}</p>
  <p><strong>Mathematical handle:</strong> {esc(guide["mathematical_handle"])}</p>
  <p><strong>What to check in the model:</strong> {esc(guide["what_to_check_in_the_model"])}</p>
  <p><strong>Common misread:</strong> {esc(guide["common_misread"])}</p>
  <p><strong>Course bridge:</strong> {esc(guide["course_bridge"])}</p>
  <h3>Concept Pages</h3><p class="chips">{concept_links}</p>
  <h3>Reusable Primitives</h3><p class="chips">{primitive_links}</p>
  <h3>Method Families</h3><p class="chips">{family_links}</p>
  <h3>Case Studies</h3><p class="chips">{case_links}</p>
  <h3>Practice Drills</h3><p class="chips">{drill_links}</p>
  <h3>Math Clinic Cards</h3><p class="chips">{math_links}</p>
  <h3>Transcript Evidence</h3><ul class="evidence-list">{evidence_links}</ul>
</article>""")
    body = """<section class="page-head">
  <h1>Paper Reading Guide</h1>
  <p>A transfer layer for new papers, models, and applied writeups. Each card starts from the wording a reader may see, then maps it back to the course's ordinary problem, mathematical handle, common misread, and transcript-backed concepts.</p>
</section>""" + "".join(cards)
    write(SITE / "paper-reading.html", page("Paper Reading Guide", body, "paper-reading"))


def build_jargon_decoder(decoder, concept_by_id, primitive_by_id, ev_by_id):
    cards = []
    for item in decoder:
        concept_links = "".join(
            f'<a class="chip" href="concepts/{esc(concept_id)}.html">{esc(concept_by_id[concept_id]["name"])}</a>'
            for concept_id in item.get("concepts", [])
            if concept_id in concept_by_id
        )
        primitive_links = "".join(
            f'<a class="chip" href="primitives.html#{esc(primitive_id)}">{esc(primitive_by_id[primitive_id]["name"])}</a>'
            for primitive_id in item.get("primitives", [])
            if primitive_id in primitive_by_id
        )
        evidence_links = "".join(
            f'<li><a href="evidence.html#{esc(ev_id)}">{esc(ev_id)}</a>: {esc(ev_by_id[ev_id]["video_title"])}</li>'
            for ev_id in item.get("evidence_ids", [])
            if ev_id in ev_by_id
        )
        cards.append(f"""<article class="wide-card decoder-card" id="{esc(item["id"])}">
  <p class="eyebrow">Jargon decoder</p>
  <h2>{esc(item["term_family"])}</h2>
  <p><strong>Where the reader sees it:</strong> {esc(item["where_reader_sees_it"])}</p>
  <p><strong>Plain translation:</strong> {esc(item["plain_translation"])}</p>
  <p><strong>First-principles pressure:</strong> {esc(item["first_principles_pressure"])}</p>
  <p><strong>Mathematical object:</strong> {esc(item["mathematical_object"])}</p>
  <p><strong>Reading test:</strong> {esc(item["reading_test"])}</p>
  <p><strong>Common confusion:</strong> {esc(item["common_confusion"])}</p>
  <p><strong>How to unpack it in a paper:</strong> {esc(item["how_to_unpack_in_a_paper"])}</p>
  <p><strong>What this term repairs:</strong> {esc(item["what_the_term_repairs"])}</p>
  <p><strong>Where the translation breaks:</strong> {esc(item["where_translation_breaks"])}</p>
  <h3>Concept Pages</h3><p class="chips">{concept_links}</p>
  <h3>Reusable Primitives</h3><p class="chips">{primitive_links}</p>
  <h3>Transcript Evidence</h3><ul class="evidence-list">{evidence_links}</ul>
</article>""")
    body = """<section class="page-head">
  <h1>Jargon Decoder</h1>
  <p>A plain-language bridge for terms that appear in lectures, problem sets, and papers. Each card translates the term family into the everyday problem, the mathematical object, a reading test, and the confusion to avoid.</p>
</section>""" + "".join(cards)
    write(SITE / "jargon-decoder.html", page("Jargon Decoder", body, "jargon-decoder"))


def build_model_building_workbook(workbook, concept_by_id, primitive_by_id, drill_by_id, decoder_by_id, ev_by_id):
    cards = []
    for item in workbook:
        concept_links = "".join(
            f'<a class="chip" href="concepts/{esc(concept_id)}.html">{esc(concept_by_id[concept_id]["name"])}</a>'
            for concept_id in item.get("concepts", [])
            if concept_id in concept_by_id
        )
        primitive_links = "".join(
            f'<a class="chip" href="primitives.html#{esc(primitive_id)}">{esc(primitive_by_id[primitive_id]["name"])}</a>'
            for primitive_id in item.get("primitives", [])
            if primitive_id in primitive_by_id
        )
        drill_links = "".join(
            f'<a class="chip" href="drills.html#{esc(drill_id)}">{esc(drill_by_id[drill_id]["title"])}</a>'
            for drill_id in item.get("drill_ids", [])
            if drill_id in drill_by_id
        )
        decoder_links = "".join(
            f'<a class="chip" href="jargon-decoder.html#{esc(decoder_id)}">{esc(decoder_by_id[decoder_id]["term_family"])}</a>'
            for decoder_id in item.get("decoder_ids", [])
            if decoder_id in decoder_by_id
        )
        evidence_links = "".join(
            f'<li><a href="evidence.html#{esc(ev_id)}">{esc(ev_id)}</a>: {esc(ev_by_id[ev_id]["video_title"])}</li>'
            for ev_id in item.get("evidence_ids", [])
            if ev_id in ev_by_id
        )
        cards.append(f"""<article class="wide-card model-building-card" id="{esc(item["id"])}">
  <p class="eyebrow">Model-building workbook</p>
  <h2>{esc(item["title"])}</h2>
  <p><strong>Ordinary question:</strong> {esc(item["ordinary_question"])}</p>
  <p><strong>Formal slot:</strong> {esc(item["formal_slot"])}</p>
  <p><strong>Why this slot exists:</strong> {esc(item["why_this_slot_exists"])}</p>
  <p><strong>Construction move:</strong> {esc(item["construction_move"])}</p>
  <p><strong>Math check:</strong> {esc(item["math_check"])}</p>
  <p><strong>Failure if skipped:</strong> {esc(item["failure_if_skipped"])}</p>
  <p><strong>Worked prompt:</strong> {esc(item["worked_prompt"])}</p>
  <p><strong>Naive shortcut:</strong> {esc(item["naive_shortcut"])}</p>
  <p><strong>Step-by-step use:</strong> {esc(item["step_by_step_use"])}</p>
  <p><strong>Transfer check:</strong> {esc(item["transfer_check"])}</p>
  <h3>Concept Pages</h3><p class="chips">{concept_links}</p>
  <h3>Reusable Primitives</h3><p class="chips">{primitive_links}</p>
  <h3>Practice Drills</h3><p class="chips">{drill_links}</p>
  <h3>Decoder Cards</h3><p class="chips">{decoder_links}</p>
  <h3>Transcript Evidence</h3><ul class="evidence-list">{evidence_links}</ul>
</article>""")
    body = """<section class="page-head">
  <h1>Model-Building Workbook</h1>
  <p>A from-scratch checklist for turning an ordinary strategic situation into a usable game model. Each step names the everyday question, the formal slot, the math check, the failure mode, and transcript-backed links.</p>
</section>""" + "".join(cards)
    write(SITE / "model-building.html", page("Model-Building Workbook", body, "model-building"))


def build_proof_sketch_lab(proofs, concept_by_id, primitive_by_id, math_clinic_by_id, decoder_by_id, ev_by_id):
    cards = []
    for item in proofs:
        concept_links = "".join(
            f'<a class="chip" href="concepts/{esc(concept_id)}.html">{esc(concept_by_id[concept_id]["name"])}</a>'
            for concept_id in item.get("concepts", [])
            if concept_id in concept_by_id
        )
        primitive_links = "".join(
            f'<a class="chip" href="primitives.html#{esc(primitive_id)}">{esc(primitive_by_id[primitive_id]["name"])}</a>'
            for primitive_id in item.get("primitives", [])
            if primitive_id in primitive_by_id
        )
        math_links = "".join(
            f'<a class="chip" href="math-clinic.html#{esc(card_id)}">{esc(math_clinic_by_id[card_id]["title"])}</a>'
            for card_id in item.get("math_clinic_ids", [])
            if card_id in math_clinic_by_id
        )
        decoder_links = "".join(
            f'<a class="chip" href="jargon-decoder.html#{esc(decoder_id)}">{esc(decoder_by_id[decoder_id]["term_family"])}</a>'
            for decoder_id in item.get("decoder_ids", [])
            if decoder_id in decoder_by_id
        )
        evidence_links = "".join(
            f'<li><a href="evidence.html#{esc(ev_id)}">{esc(ev_id)}</a>: {esc(ev_by_id[ev_id]["video_title"])}</li>'
            for ev_id in item.get("evidence_ids", [])
            if ev_id in ev_by_id
        )
        cards.append(f"""<article class="wide-card proof-sketch-card" id="{esc(item["id"])}">
  <p class="eyebrow">Proof-sketch lab</p>
  <h2>{esc(item["title"])}</h2>
  <p><strong>Ordinary claim:</strong> {esc(item["ordinary_claim"])}</p>
  <p><strong>Minimal setup:</strong> {esc(item["minimal_setup"])}</p>
  <p><strong>Proof idea:</strong> {esc(item["proof_idea"])}</p>
  <p><strong>Mathematical move:</strong> {esc(item["mathematical_move"])}</p>
  <p><strong>Why it matters:</strong> {esc(item["why_it_matters"])}</p>
  <p><strong>Where it breaks:</strong> {esc(item["where_it_breaks"])}</p>
  <p><strong>Proof-reading move:</strong> {esc(item["proof_reading_move"])}</p>
  <p><strong>Student trap:</strong> {esc(item["student_trap"])}</p>
  <p><strong>Rebuild check:</strong> {esc(item["rebuild_check"])}</p>
  <h3>Concept Pages</h3><p class="chips">{concept_links}</p>
  <h3>Reusable Primitives</h3><p class="chips">{primitive_links}</p>
  <h3>Math Clinic Cards</h3><p class="chips">{math_links}</p>
  <h3>Decoder Cards</h3><p class="chips">{decoder_links}</p>
  <h3>Transcript Evidence</h3><ul class="evidence-list">{evidence_links}</ul>
</article>""")
    body = """<section class="page-head">
  <h1>Proof-Sketch Lab</h1>
  <p>Plain-language proof intuition for the course's core result patterns. Each card states the ordinary claim, the setup that makes it true, the mathematical move, and the boundary where the result stops applying.</p>
</section>""" + "".join(cards)
    write(SITE / "proof-sketches.html", page("Proof-Sketch Lab", body, "proof-sketches"))


def build_assumption_audit_lab(audits, concept_by_id, primitive_by_id, proof_by_id, model_step_by_id, decoder_by_id, ev_by_id):
    cards = []
    for item in audits:
        concept_links = "".join(
            f'<a class="chip" href="concepts/{esc(concept_id)}.html">{esc(concept_by_id[concept_id]["name"])}</a>'
            for concept_id in item.get("concepts", [])
            if concept_id in concept_by_id
        )
        primitive_links = "".join(
            f'<a class="chip" href="primitives.html#{esc(primitive_id)}">{esc(primitive_by_id[primitive_id]["name"])}</a>'
            for primitive_id in item.get("primitives", [])
            if primitive_id in primitive_by_id
        )
        proof_links = "".join(
            f'<a class="chip" href="proof-sketches.html#{esc(proof_id)}">{esc(proof_by_id[proof_id]["title"])}</a>'
            for proof_id in item.get("proof_ids", [])
            if proof_id in proof_by_id
        )
        model_links = "".join(
            f'<a class="chip" href="model-building.html#{esc(step_id)}">{esc(model_step_by_id[step_id]["title"])}</a>'
            for step_id in item.get("model_step_ids", [])
            if step_id in model_step_by_id
        )
        decoder_links = "".join(
            f'<a class="chip" href="jargon-decoder.html#{esc(decoder_id)}">{esc(decoder_by_id[decoder_id]["term_family"])}</a>'
            for decoder_id in item.get("decoder_ids", [])
            if decoder_id in decoder_by_id
        )
        evidence_links = "".join(
            f'<li><a href="evidence.html#{esc(ev_id)}">{esc(ev_id)}</a>: {esc(ev_by_id[ev_id]["video_title"])}</li>'
            for ev_id in item.get("evidence_ids", [])
            if ev_id in ev_by_id
        )
        cards.append(f"""<article class="wide-card assumption-card" id="{esc(item["id"])}">
  <p class="eyebrow">Assumption audit</p>
  <h2>{esc(item["title"])}</h2>
  <p><strong>Hidden assumption:</strong> {esc(item["hidden_assumption"])}</p>
  <p><strong>Why it exists:</strong> {esc(item["why_it_exists"])}</p>
  <p><strong>Audit test:</strong> {esc(item["audit_test"])}</p>
  <p><strong>What changes if false:</strong> {esc(item["what_changes_if_false"])}</p>
  <p><strong>Mathematical symptom:</strong> {esc(item["mathematical_symptom"])}</p>
  <p><strong>Repair move:</strong> {esc(item["repair_move"])}</p>
  <p><strong>Naive overread:</strong> {esc(item["naive_overread"])}</p>
  <p><strong>Stress test:</strong> {esc(item["stress_test"])}</p>
  <p><strong>Transfer red flag:</strong> {esc(item["transfer_red_flag"])}</p>
  <h3>Concept Pages</h3><p class="chips">{concept_links}</p>
  <h3>Reusable Primitives</h3><p class="chips">{primitive_links}</p>
  <h3>Proof Sketches</h3><p class="chips">{proof_links}</p>
  <h3>Model-Building Steps</h3><p class="chips">{model_links}</p>
  <h3>Decoder Cards</h3><p class="chips">{decoder_links}</p>
  <h3>Transcript Evidence</h3><ul class="evidence-list">{evidence_links}</ul>
</article>""")
    body = """<section class="page-head">
  <h1>Assumption-Audit Lab</h1>
  <p>A guardrail for using game-theory results outside the lecture example. Each card names a hidden assumption, explains why the math needs it, gives an audit test, and shows what changes when it fails.</p>
</section>""" + "".join(cards)
    write(SITE / "assumptions.html", page("Assumption-Audit Lab", body, "assumptions"))


def build_worked_transfer_examples(examples, concept_by_id, primitive_by_id, model_step_by_id, proof_by_id, assumption_by_id, decoder_by_id, ev_by_id):
    cards = []
    for item in examples:
        concept_links = "".join(
            f'<a class="chip" href="concepts/{esc(concept_id)}.html">{esc(concept_by_id[concept_id]["name"])}</a>'
            for concept_id in item.get("concepts", [])
            if concept_id in concept_by_id
        )
        primitive_links = "".join(
            f'<a class="chip" href="primitives.html#{esc(primitive_id)}">{esc(primitive_by_id[primitive_id]["name"])}</a>'
            for primitive_id in item.get("primitives", [])
            if primitive_id in primitive_by_id
        )
        model_links = "".join(
            f'<a class="chip" href="model-building.html#{esc(step_id)}">{esc(model_step_by_id[step_id]["title"])}</a>'
            for step_id in item.get("model_step_ids", [])
            if step_id in model_step_by_id
        )
        proof_links = "".join(
            f'<a class="chip" href="proof-sketches.html#{esc(proof_id)}">{esc(proof_by_id[proof_id]["title"])}</a>'
            for proof_id in item.get("proof_ids", [])
            if proof_id in proof_by_id
        )
        assumption_links = "".join(
            f'<a class="chip" href="assumptions.html#{esc(assumption_id)}">{esc(assumption_by_id[assumption_id]["title"])}</a>'
            for assumption_id in item.get("assumption_ids", [])
            if assumption_id in assumption_by_id
        )
        decoder_links = "".join(
            f'<a class="chip" href="jargon-decoder.html#{esc(decoder_id)}">{esc(decoder_by_id[decoder_id]["term_family"])}</a>'
            for decoder_id in item.get("decoder_ids", [])
            if decoder_id in decoder_by_id
        )
        evidence_links = "".join(
            f'<li><a href="evidence.html#{esc(ev_id)}">{esc(ev_id)}</a>: {esc(ev_by_id[ev_id]["video_title"])}</li>'
            for ev_id in item.get("evidence_ids", [])
            if ev_id in ev_by_id
        )
        cards.append(f"""<article class="wide-card worked-transfer-card" id="{esc(item["id"])}">
  <p class="eyebrow">Worked transfer example</p>
  <h2>{esc(item["title"])}</h2>
  <p><strong>New situation:</strong> {esc(item["new_situation"])}</p>
  <p><strong>Model construction:</strong> {esc(item["model_construction"])}</p>
  <p><strong>First-principles solution:</strong> {esc(item["first_principles_solution"])}</p>
  <p><strong>Math move:</strong> {esc(item["math_move"])}</p>
  <p><strong>Assumption check:</strong> {esc(item["assumption_check"])}</p>
  <p><strong>Evidence bridge:</strong> {esc(item["evidence_bridge"])}</p>
  <p><strong>Transfer lesson:</strong> {esc(item["transfer_lesson"])}</p>
  <h3>Concept Pages</h3><p class="chips">{concept_links}</p>
  <h3>Reusable Primitives</h3><p class="chips">{primitive_links}</p>
  <h3>Model-Building Steps</h3><p class="chips">{model_links}</p>
  <h3>Proof Sketches</h3><p class="chips">{proof_links}</p>
  <h3>Assumption Audits</h3><p class="chips">{assumption_links}</p>
  <h3>Decoder Cards</h3><p class="chips">{decoder_links}</p>
  <h3>Transcript Evidence</h3><ul class="evidence-list">{evidence_links}</ul>
</article>""")
    body = """<section class="page-head">
  <h1>Worked Transfer Examples</h1>
  <p>Full worked examples for applying the course outside the lecture setting. Each card starts with an unfamiliar situation, builds the model, states the mathematical move, audits assumptions, and ties the reasoning back to transcript evidence.</p>
</section>""" + "".join(cards)
    write(SITE / "worked-transfer.html", page("Worked Transfer Examples", body, "worked-transfer"))


def build_capstone_self_test(capstones, concept_by_id, primitive_by_id, case_by_id, drill_by_id, paper_by_id, decoder_by_id, ev_by_id):
    cards = []
    for item in capstones:
        concept_links = "".join(
            f'<a class="chip" href="concepts/{esc(concept_id)}.html">{esc(concept_by_id[concept_id]["name"])}</a>'
            for concept_id in item.get("concepts", [])
            if concept_id in concept_by_id
        )
        primitive_links = "".join(
            f'<a class="chip" href="primitives.html#{esc(primitive_id)}">{esc(primitive_by_id[primitive_id]["name"])}</a>'
            for primitive_id in item.get("primitives", [])
            if primitive_id in primitive_by_id
        )
        case_links = "".join(
            f'<a class="chip" href="cases.html#{esc(case_id)}">{esc(case_by_id[case_id]["title"])}</a>'
            for case_id in item.get("case_ids", [])
            if case_id in case_by_id
        )
        drill_links = "".join(
            f'<a class="chip" href="drills.html#{esc(drill_id)}">{esc(drill_by_id[drill_id]["title"])}</a>'
            for drill_id in item.get("drill_ids", [])
            if drill_id in drill_by_id
        )
        paper_links = "".join(
            f'<a class="chip" href="paper-reading.html#{esc(paper_id)}">{esc(paper_by_id[paper_id]["title"])}</a>'
            for paper_id in item.get("paper_reading_ids", [])
            if paper_id in paper_by_id
        )
        decoder_links = "".join(
            f'<a class="chip" href="jargon-decoder.html#{esc(decoder_id)}">{esc(decoder_by_id[decoder_id]["term_family"])}</a>'
            for decoder_id in item.get("decoder_ids", [])
            if decoder_id in decoder_by_id
        )
        evidence_links = "".join(
            f'<li><a href="evidence.html#{esc(ev_id)}">{esc(ev_id)}</a>: {esc(ev_by_id[ev_id]["video_title"])}</li>'
            for ev_id in item.get("evidence_ids", [])
            if ev_id in ev_by_id
        )
        cards.append(f"""<article class="wide-card capstone-card" id="{esc(item["id"])}">
  <p class="eyebrow">Capstone self-test</p>
  <h2>{esc(item["title"])}</h2>
  <p><strong>Scenario:</strong> {esc(item["scenario"])}</p>
  <p><strong>Reader task:</strong> {esc(item["reader_task"])}</p>
  <p><strong>Expected reasoning:</strong> {esc(item["expected_reasoning"])}</p>
  <p><strong>Math check:</strong> {esc(item["math_check"])}</p>
  <p><strong>Evidence check:</strong> {esc(item["evidence_check"])}</p>
  <p><strong>What a wrong answer reveals:</strong> {esc(item["what_wrong_answer_reveals"])}</p>
  <p><strong>Transfer prompt:</strong> {esc(item["transfer_prompt"])}</p>
  <h3>Concept Pages</h3><p class="chips">{concept_links}</p>
  <h3>Reusable Primitives</h3><p class="chips">{primitive_links}</p>
  <h3>Case Study</h3><p class="chips">{case_links}</p>
  <h3>Practice Drills</h3><p class="chips">{drill_links}</p>
  <h3>Paper Reading Cards</h3><p class="chips">{paper_links}</p>
  <h3>Decoder Cards</h3><p class="chips">{decoder_links}</p>
  <h3>Transcript Evidence</h3><ul class="evidence-list">{evidence_links}</ul>
</article>""")
    body = """<section class="page-head">
  <h1>Capstone Self-Test</h1>
  <p>Transfer checks for whether the reader can use the lab, not just recognize labels. Each card asks for a model choice, a mathematical check, a mistake diagnosis, and transcript-backed evidence.</p>
</section>""" + "".join(cards)
    write(SITE / "capstone.html", page("Capstone Self-Test", body, "capstone"))


def build_cross_reference(concepts, themes, subthemes, primitives, lectures, evidence):
    theme_by_id = {theme["id"]: theme for theme in themes}
    subthemes_by_concept: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for subtheme in subthemes:
        for concept_id in subtheme.get("concepts", []):
            subthemes_by_concept[concept_id].append(subtheme)
    primitive_by_id = {primitive["id"]: primitive for primitive in primitives}
    lectures_by_concept: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for lecture in lectures:
        for concept in lecture.get("concepts", []):
            lectures_by_concept[concept["id"]].append(lecture)
    ev_by_id = evidence_map(evidence)
    rows = []
    for concept in concepts:
        theme = theme_by_id.get(concept["theme_id"], {"name": concept["theme_id"]})
        lecture_links = "".join(
            f'<a class="chip" href="lectures/{esc(lecture["id"])}.html">{esc(lecture["title"])}</a>'
            for lecture in lectures_by_concept.get(concept["id"], [])
        )
        subtheme_links = "".join(
            f'<a class="chip" href="themes.html#{esc(subtheme["id"])}">{esc(subtheme["name"])}</a>'
            for subtheme in subthemes_by_concept.get(concept["id"], [])
        )
        primitive_links = "".join(
            f'<a class="chip" href="primitives.html#{esc(primitive_id)}">{esc(primitive_by_id[primitive_id]["name"])}</a>'
            for primitive_id in concept.get("mathematical_primitives", [])
            if primitive_id in primitive_by_id
        )
        evidence_links = "".join(
            f'<a class="chip" href="evidence.html#{esc(ev_id)}">{esc(ev_id)}</a>'
            for ev_id in concept.get("course_evidence_ids", [])
            if ev_id in ev_by_id
        )
        rows.append(f"""<article class="wide-card xref-card" id="xref-{esc(concept["id"])}">
  <p class="eyebrow">{esc(theme["name"])}</p>
  <h2><a href="concepts/{esc(concept["id"])}.html">{esc(concept["name"])}</a></h2>
  <p><strong>Problem pressure:</strong> {esc(concept["everyday_problem"])}</p>
  <p><strong>Mathematical handle:</strong> {esc(concept["mathematical_object"])}</p>
  <h3>Lectures</h3><p class="chips">{lecture_links}</p>
  <h3>Subthemes</h3><p class="chips">{subtheme_links}</p>
  <h3>Primitives</h3><p class="chips">{primitive_links}</p>
  <h3>Evidence</h3><p class="chips">{evidence_links}</p>
</article>""")
    body = '<section class="page-head"><h1>Cross Index</h1><p>Every concept indexed by the problem pressure it answers, with direct jumps into lectures, subthemes, primitives, and transcript evidence.</p></section>' + "".join(rows)
    write(SITE / "cross-reference.html", page("Cross Index", body, "cross-reference"))


def build_limits(concepts, themes, derivations):
    concept_cards = []
    for concept in concepts:
        concept_cards.append(f"""<article class="wide-card limit-card" id="limit-{esc(concept["id"])}">
  <p class="eyebrow">Concept limit</p>
  <h2><a href="concepts/{esc(concept["id"])}.html">{esc(concept["name"])}</a></h2>
  <p><strong>Common misunderstanding:</strong> {esc(concept["common_misunderstanding"])}</p>
  <p><strong>Student trap:</strong> {esc(concept["student_trap"])}</p>
  <p><strong>Where the idea stops working:</strong> {esc(concept["course_boundary_note"])}</p>
  <p><strong>What breaks without it:</strong> {esc(concept["what_breaks_without_it"])}</p>
  <p><strong>Failed shortcut:</strong> {esc(concept["failed_simple_approach"])}</p>
  <p><strong>Why the formal idea has to exist:</strong> {esc(concept["why_math_has_to_exist"])}</p>
  <p><strong>Mathematical intuition:</strong> {esc(concept["mathematical_intuition"])}</p>
  <p><strong>Where it reappears:</strong> {esc(concept["cross_course_connections"])}</p>
  <p><strong>How to recognize it elsewhere:</strong> {esc(concept["recognize_in_new_work"])}</p>
</article>""")
    theme_cards = []
    for theme in themes:
        theme_cards.append(f"""<article class="wide-card limit-card" id="theme-limit-{esc(theme["id"])}">
  <p class="eyebrow">Theme limit</p>
  <h2><a href="themes.html#{esc(theme["id"])}">{esc(theme["name"])}</a></h2>
  <p><strong>Where the analogy breaks:</strong> {esc(theme["where_analogy_breaks"])}</p>
</article>""")
    derivation_cards = []
    for derivation in derivations:
        derivation_cards.append(f"""<article class="wide-card limit-card" id="derivation-limit-{esc(derivation["id"])}">
  <p class="eyebrow">Equation misread</p>
  <h2><a href="primitives.html#{esc(derivation["id"])}">{esc(derivation["title"])}</a></h2>
  <p><strong>Common misread:</strong> {esc(derivation["common_misread"])}</p>
</article>""")
    body = f"""<section class="page-head">
  <h1>Limits And Traps</h1>
  <p>A reader-facing guardrail against overgeneralizing the course machinery. These are the places where the concept, theme, or equation can be precise and still be misused.</p>
</section>
<section><h2>Concept-Level Traps</h2>{''.join(concept_cards)}</section>
<section><h2>Theme-Level Boundaries</h2>{''.join(theme_cards)}</section>
<section><h2>Equation Misreads</h2>{''.join(derivation_cards)}</section>"""
    write(SITE / "limits.html", page("Limits And Traps", body, "limits"))


def lecture_filename(lecture: dict[str, Any]) -> str:
    return f"{lecture['id']}.html"


def build_lectures(lectures, ev_by_id, concept_by_id, deriv_by_id):
    cards = []
    for lecture in lectures:
        chips = "".join(
            f'<a class="chip" href="concepts/{esc(concept["id"])}.html">{esc(concept["name"])}</a>'
            for concept in lecture["concepts"]
        )
        evidence_links = "".join(
            f'<li><a href="evidence.html#{esc(eid)}">{esc(eid)}</a>: {esc(ev_by_id[eid]["supports_concepts"][0]).replace("_", " ")}</li>'
            for eid in lecture["evidence_ids"]
            if eid in ev_by_id
        )
        themes = ", ".join(esc(theme["name"]) for theme in lecture["themes"]) or "No direct evidence theme yet"
        detail_href = f"lectures/{lecture_filename(lecture)}"
        cards.append(f"""<article class="wide-card lecture-card" id="{esc(lecture["id"])}">
  <p class="eyebrow">Lecture {lecture["playlist_index"]} · {lecture["word_count"]:,} words · {themes}</p>
  <h2>{esc(lecture["title"])}</h2>
  <p>{esc(lecture["first_principles_role"])}</p>
  {flow("How To Read This Lecture", [
      ("Pressure", lecture["first_principles_role"]),
      ("Watch", lecture["what_to_watch_for"]),
      ("Evidence", lecture["coverage_note"]),
      ("Transcript", lecture["transcript_path"]),
  ], "lecture-flow")}
  <h3>Linked Concepts</h3>
  <p class="chips">{chips or '<span class="chip muted">No direct concept anchors yet</span>'}</p>
  <h3>Evidence Anchors</h3>
  <ul class="evidence-list">{evidence_links or '<li>No current evidence anchors for this lecture.</li>'}</ul>
  <p><a class="button" href="{esc(detail_href)}">Open lecture study page</a></p>
  <p><a class="button" href="{esc(lecture["youtube_url"])}">Open YouTube lecture</a></p>
</article>""")
    body = '<section class="page-head"><h1>Lecture Path</h1><p>Follow the course in order, with each lecture tied to first-principles roles, concepts, and transcript evidence.</p></section>' + "".join(cards)
    write(SITE / "lectures.html", page("Lectures", body, "lectures"))
    for lecture in lectures:
        build_lecture_detail(lecture, ev_by_id, concept_by_id, deriv_by_id)


def build_lecture_detail(lecture, ev_by_id, concept_by_id, deriv_by_id):
    records = [ev_by_id[eid] for eid in lecture["evidence_ids"] if eid in ev_by_id]
    supplemental_records = lecture.get("supplemental_evidence", [])
    concept_ids = [concept["id"] for concept in lecture["concepts"]]
    concepts = [concept_by_id[cid] for cid in concept_ids if cid in concept_by_id]
    lecture_derivs = lecture_derivation_ids(concepts, deriv_by_id)
    lecture_deriv_links = derivation_links(lecture_derivs, deriv_by_id, "../")
    themes = ", ".join(esc(theme["name"]) for theme in lecture["themes"]) or "Course sequence context"
    concept_links = "".join(
        f'<a class="chip" href="../concepts/{esc(concept["id"])}.html">{esc(concept["name"])}</a>'
        for concept in concepts
    )
    concept_blocks = "".join(
        f"""<article class="wide-card">
  <h3>{esc(concept["name"])}</h3>
  <p><strong>Problem:</strong> {esc(concept["everyday_problem"])}</p>
  <p><strong>Mathematical handle:</strong> {esc(concept["mathematical_object"])}</p>
  <p><strong>What breaks without it:</strong> {esc(concept["what_breaks_without_it"])}</p>
  <p><a href="../concepts/{esc(concept["id"])}.html">Open concept page</a></p>
</article>"""
        for concept in concepts
    )
    evidence_blocks = "".join(evidence_row(record, "../") for record in records)
    supplemental_blocks = "".join(supplemental_evidence_row(record) for record in supplemental_records)
    concept_mistake_notes = " ".join(concept["student_trap"] for concept in concepts)
    concept_math_notes = " ".join(concept["why_math_has_to_exist"] for concept in concepts)
    recognition_notes = " ".join(concept["recognize_in_new_work"] for concept in concepts) if concepts else "In later work, recognize this lecture by asking where the same strategic pressure returns under a different name."
    body = f"""<section class="page-head">
  <p class="eyebrow">Lecture {lecture["playlist_index"]} · {themes}</p>
  <h1>{esc(lecture["title"])}</h1>
  <p>{esc(lecture["first_principles_role"])}</p>
  <p><a class="button" href="{esc(lecture["youtube_url"])}">Open YouTube lecture</a></p>
</section>
{flow("Lecture Study Map", [
    ("Problem", lecture["argument_arc"]),
    ("Watch", lecture["what_to_watch_for"]),
    ("Math", lecture["math_entry_point"]),
    ("Evidence", lecture.get("total_coverage_note", lecture["coverage_note"])),
], "lecture-flow")}
<section class="treatment">
  <h2>What This Lecture Teaches</h2>
  <p>{esc(lecture["argument_arc"])}</p>
  <h2>Where The Math Enters</h2>
  <p>{esc(lecture["math_entry_point"])}</p>
  {f'<p>{esc(concept_math_notes)}</p>' if concept_math_notes else ''}
  <h2>Equation Walkthroughs</h2>
  <p class="chips">{lecture_deriv_links or '<span class="chip muted">No direct derivation cards yet</span>'}</p>
  <h2>Worked Mini-Example</h2>
  <p>{esc(lecture["worked_mini_example"])}</p>
  <h2>Mistakes To Avoid</h2>
  <p>{esc(lecture["common_failure"])}</p>
  {f'<p>{esc(concept_mistake_notes)}</p>' if concept_mistake_notes else ''}
  <h2>How To Recognize This Later</h2>
  <p>{esc(recognition_notes)}</p>
  <p class="chips">{concept_links or '<span class="chip muted">No direct concept anchors yet</span>'}</p>
</section>
<section>
  <h2>Concepts In This Lecture</h2>
  {concept_blocks or '<p>No direct concept anchors yet.</p>'}
</section>
<section>
  <h2>Transcript Evidence Chain</h2>
  <div class="evidence-stack">{evidence_blocks or '<p>No direct evidence anchors yet.</p>'}</div>
</section>
<section>
  <h2>Supplemental Lecture Evidence</h2>
  <div class="evidence-stack">{supplemental_blocks or '<p>No supplemental lecture anchors for this page.</p>'}</div>
</section>
<section class="wide-card">
  <h2>Source Context</h2>
  <p><strong>Transcript:</strong> {esc(lecture["transcript_path"])}</p>
  <p><strong>Words:</strong> {lecture["word_count"]:,} · <strong>Duration:</strong> {lecture["duration_seconds"]} seconds</p>
</section>"""
    write(SITE / "lectures" / lecture_filename(lecture), page(lecture["title"], body, "lectures", depth=1))


def worked_example_card(card: dict[str, Any]) -> str:
    return f"""<aside class="wide-card worked-example-card">
  <h2>Worked Example Card</h2>
  <p><strong>Setup:</strong> {esc(card["setup"])}</p>
  <p><strong>Walkthrough:</strong> {esc(card["walkthrough"])}</p>
  <p><strong>Lesson:</strong> {esc(card["lesson"])}</p>
  <p><strong>Trap:</strong> {esc(card["trap"])}</p>
</aside>"""


def build_concepts(concepts, evidence, deriv_by_id, equation_notes, worked_examples):
    ev_by_id = evidence_map(evidence)
    concept_ids = {c["id"] for c in concepts}
    body = f'<section class="page-head"><h1>Concept Atlas</h1><p>Each page explains the strategic pressure, the mathematical object, what breaks without it, and transcript evidence.</p></section><section class="grid">{"".join(concept_card(c, ev_by_id) for c in concepts)}</section>'
    write(SITE / "concepts.html", page("Concepts", body, "concepts"))
    for concept in concepts:
        related = "".join(
            f'<a class="chip" href="{esc(r)}.html">{esc(r).replace("_", " ")}</a>'
            if r in concept_ids else f'<span class="chip muted">{esc(r).replace("_", " ")}</span>'
            for r in concept["related_concepts"]
        )
        ev_html = "".join(evidence_row(ev_by_id[ev_id], "../") for ev_id in concept["course_evidence_ids"])
        deriv_ids = concept_derivation_ids(concept, deriv_by_id)
        deriv_html = derivation_links(deriv_ids, deriv_by_id, "../")
        equation_note = equation_notes.get(concept["id"], "")
        worked_card = worked_examples.get(concept["id"], {})
        diagram = flow("First-Principles Map", [
            ("Problem", concept["everyday_problem"]),
            ("Constraint", concept["first_principles_reason"]),
            ("Math Handle", concept["mathematical_object"]),
            ("Failure Mode", concept["what_breaks_without_it"]),
        ])
        sections = [
            ("What real-world problem is this about?", concept["everyday_problem"]),
            ("Why does this problem exist?", concept["first_principles_reason"]),
            ("What is the mathematical idea underneath?", concept["mathematical_principle"]),
            ("Lecture-Depth Walkthrough", concept["lecture_depth_walkthrough"]),
            ("Mathematical Intuition", concept["mathematical_intuition"]),
            ("Why This Mathematical Object Has To Exist", concept["why_math_has_to_exist"]),
            ("Why is this concept important?", concept["why_it_matters"]),
            ("What breaks without it?", concept["what_breaks_without_it"]),
            ("Worked Mini-Example", concept["worked_mini_example"]),
            ("Where Students Get Stuck", concept["student_trap"]),
            ("Where The Idea Stops Working", concept["course_boundary_note"]),
            ("Common Misunderstanding", concept["common_misunderstanding"]),
            ("How to Recognize This in a New Paper or Model", concept["recognize_in_new_work"]),
            ("Connected Concepts", concept["cross_course_connections"]),
        ]
        treatment = "".join(f"<h2>{esc(h)}</h2><p>{esc(text)}</p>" for h, text in sections)
        body = f"""<section class="page-head"><p class="eyebrow">{esc(concept['theme_id']).replace('_', ' ')}</p><h1>{esc(concept['name'])}</h1><p>{esc(concept['plain_language_definition'])}</p></section>
{diagram}
<section class="treatment">{treatment}{worked_example_card(worked_card) if worked_card else ''}<h2>Equation Walkthroughs</h2>{f'<p>{esc(equation_note)}</p>' if equation_note else ''}<p class="chips">{deriv_html or '<span class="chip muted">No direct derivation cards yet</span>'}</p><p class="chips">{related}</p></section>
<section><h2>Transcript Evidence</h2><div class="evidence-stack">{ev_html}</div></section>"""
        write(SITE / "concepts" / f"{concept['id']}.html", page(concept["name"], body, "concepts", depth=1))


def build_themes(themes, subthemes, concepts):
    concept_by_id = {c["id"]: c for c in concepts}
    names = {c["id"]: c["name"] for c in concepts}
    sub_by_theme = defaultdict(list)
    for sub in subthemes:
        sub_by_theme[sub["parent_theme"]].append(sub)
    blocks = []
    for theme in themes:
        diagram = flow("Theme Map", [
            ("Pressure", theme["big_picture"]),
            ("Math Spine", theme["mathematical_spine"]),
            ("Limit", theme["where_analogy_breaks"]),
            ("Evidence", theme["lecture_evidence_chain"]),
        ], "theme-flow")
        subs = "".join(f"<li><a href=\"#{esc(s['id'])}\"><strong>{esc(s['name'])}</strong></a>: {', '.join(esc(names[c]) for c in s['concepts'])}</li>" for s in sub_by_theme[theme["id"]])
        subtheme_cards = []
        for subtheme in sub_by_theme[theme["id"]]:
            concept_links = "".join(
                f'<a class="chip" href="concepts/{esc(concept_id)}.html">{esc(concept_by_id[concept_id]["name"])}</a>'
                for concept_id in subtheme["concepts"]
                if concept_id in concept_by_id
            )
            evidence_notes = "".join(
                f'<li>{esc(example["video_title"])}: <a href="evidence.html#{esc(example["evidence_id"])}">{esc(example["concept"]).replace("_", " ")}</a></li>'
                for example in subtheme.get("examples_from_courses", [])
            )
            subtheme_cards.append(f"""<article class="wide-card subtheme-card" id="{esc(subtheme["id"])}">
  <p class="eyebrow">Subtheme · {esc(theme["name"])}</p>
  <h3>{esc(subtheme["name"])}</h3>
  <p><strong>Everyday problem:</strong> {esc(subtheme["everyday_problem"])}</p>
  <p><strong>Hidden principle:</strong> {esc(subtheme["hidden_principle"])}</p>
  <p><strong>Mathematical lever:</strong> {esc(subtheme["mathematical_lever"])}</p>
  <p><strong>Why it matters:</strong> {esc(subtheme["why_it_matters"])}</p>
  <p><strong>First-principles walkthrough:</strong> {esc(subtheme["first_principles_walkthrough"])}</p>
  <p><strong>Cross-links and limits:</strong> {esc(subtheme["cross_links_and_limits"])}</p>
  <h4>Concept Pages</h4><p class="chips">{concept_links}</p>
  <h4>Evidence Trail</h4><ul class="evidence-list">{evidence_notes}</ul>
</article>""")
        blocks.append(f"""<article class="wide-card" id="{esc(theme["id"])}">
  <h2>{esc(theme["name"])}</h2>
  <p>{esc(theme["big_picture"])}</p>
  {diagram}
  <h3>Why This Theme Matters</h3><p>{esc(theme["why_this_theme_matters"])}</p>
  <h3>Cross-Course Argument</h3><p>{esc(theme["cross_course_argument"])}</p>
  <h3>Lecture Evidence Chain</h3><p>{esc(theme["lecture_evidence_chain"])}</p>
  <h3>Subthemes</h3><ul>{subs}</ul>
  <section class="subtheme-stack">{''.join(subtheme_cards)}</section>
</article>""")
    write(SITE / "themes.html", page("Themes", '<section class="page-head"><h1>Themes And Subthemes</h1></section>' + "".join(blocks), "themes"))


def derivation_card(derivation: dict[str, Any]) -> str:
    steps = "".join(f"<li>{esc(step)}</li>" for step in derivation["derivation_steps"])
    return f"""<article class="wide-card derivation-card" id="{esc(derivation["id"])}">
  <p class="eyebrow">{esc(derivation["primitive_id"]).replace("_", " ")}</p>
  <h2>{esc(derivation["title"])}</h2>
  <p>{esc(derivation["everyday_setup"])}</p>
  <blockquote>{esc(derivation["equation"])}</blockquote>
  <h3>Derivation In Plain English</h3>
  <ol>{steps}</ol>
  <h3>Symbol By Symbol</h3><p>{esc(derivation["symbol_by_symbol"])}</p>
  <h3>Why This Relation Matters</h3><p>{esc(derivation["why_it_matters"])}</p>
  <h3>Common Misread</h3><p>{esc(derivation["common_misread"])}</p>
</article>"""


def build_primitives(primitives, derivations, concept_by_id):
    cards = []
    for primitive in primitives:
        concept_links = "".join(
            f'<a class="chip" href="concepts/{esc(concept_id)}.html">{esc(concept_by_id[concept_id]["name"])}</a>'
            for concept_id in primitive.get("concepts_in_atlas", [])
            if concept_id in concept_by_id
        )
        diagram = flow("Equation Breakdown", [
            ("Why Needed", primitive["why_it_exists"]),
            ("Formal Object", primitive["formal_object"]),
            ("Equation", primitive["useful_equation"]),
            ("Misuse", primitive["misuse_failure"]),
        ], "primitive-flow")
        cards.append(f"""<article class="wide-card" id="{esc(primitive["id"])}">
  <h2>{esc(primitive["name"])}</h2>
  <p>{esc(primitive["plain_language"])}</p>
  <h3>Everyday Setup</h3><p>{esc(primitive["everyday_setup"])}</p>
  {diagram}
  <h3>Plain-Language Principle</h3><p>{esc(primitive.get("plain_language_principle", primitive["why_it_exists"]))}</p>
  <h3>Symbol By Symbol</h3><p>{esc(primitive["symbol_explanation"])}</p>
  <h3>First-Principles Pressure</h3><p>{esc(primitive["first_principles_pressure"])}</p>
  <h3>Worked Micro-Case</h3><p>{esc(primitive["worked_micro_case"])}</p>
  <h3>Where It Appears</h3><p>{esc(primitive["course_appearances"])}</p>
  <h3>Why This Primitive Matters</h3><p>{esc(primitive["why_it_matters"])}</p>
  <h3>Transfer Test</h3><p>{esc(primitive["transfer_test"])}</p>
  <h3>Concept Pages Using This Primitive</h3><p class="chips">{concept_links or '<span class="chip muted">No linked concept pages yet</span>'}</p>
  <h3>Why Misuse Breaks The Model</h3><p>{esc(primitive.get("misuse_warning", primitive["misuse_failure"]))}</p>
</article>""")
    derivation_section = '<section class="page-head"><h1>Derivation Cards</h1><p>Core equations unpacked as plain-language operations.</p></section>' + "".join(derivation_card(d) for d in derivations)
    write(SITE / "primitives.html", page("Primitives", '<section class="page-head"><h1>Mathematical Primitives</h1></section>' + "".join(cards) + derivation_section, "primitives"))


def build_families(families, concept_by_id, ev_by_id):
    cards = []
    for family in families:
        concept_links = "".join(
            f'<a class="chip" href="concepts/{esc(concept_id)}.html">{esc(concept_by_id[concept_id]["name"])}</a>'
            for concept_id in family.get("concepts", [])
            if concept_id in concept_by_id
        )
        primitive_links = "".join(
            f'<a class="chip" href="primitives.html#{esc(primitive_id)}">{esc(primitive_id).replace("_", " ")}</a>'
            for primitive_id in family.get("mathematical_primitive", [])
        )
        evidence_links = "".join(
            f'<li><a href="evidence.html#{esc(ev_id)}">{esc(ev_id)}</a>: {esc(ev_by_id[ev_id]["video_title"])}</li>'
            for ev_id in family.get("course_evidence_ids", [])
            if ev_id in ev_by_id
        )
        diagram = flow("Method-Family Reading Path", [
            ("Pressure", family["first_principles_problem"]),
            ("Core Move", family["core_move"]),
            ("Limit", family["where_analogy_breaks"]),
            ("Evidence", family["lecture_evidence_chain"]),
        ], "family-flow")
        cards.append(f"""<article class="wide-card" id="{esc(family["id"])}">
  <h2>{esc(family["name"])}</h2>
  <p>{esc(family["plain_language_family_summary"])}</p>
  {diagram}
  <h3>Family Walkthrough</h3><p>{esc(family["family_walkthrough"])}</p>
  <h3>Mathematical Signature</h3><p>{esc(family.get("mathematical_signature", ", ".join(family["mathematical_primitive"])))}</p>
  <h3>Why This Family Matters</h3><p>{esc(family.get("why_family_matters", family["paper_family_treatment"]))}</p>
  <h3>How To Read Papers In This Family</h3><p>{esc(family["paper_family_treatment"])}</p>
  <h3>Core Concepts</h3><p class="chips">{concept_links}</p>
  <h3>Reusable Primitives</h3><p class="chips">{primitive_links}</p>
  <h3>Evidence Trail</h3><ul class="evidence-list">{evidence_links}</ul>
</article>""")
    write(SITE / "families.html", page("Method Families", '<section class="page-head"><h1>Method Families</h1></section>' + "".join(cards), "families"))


def build_evidence(evidence, concept_by_id, subtheme_by_id, lecture_by_evidence_id):
    body = '<section class="page-head"><h1>Evidence Ledger</h1><p>Transcript evidence is kept separate from synthesis.</p></section><section class="evidence-stack">' + "".join(
        evidence_row(ev, "", concept_by_id, subtheme_by_id, lecture_by_evidence_id) for ev in evidence
    ) + "</section>"
    write(SITE / "evidence.html", page("Evidence", body, "evidence"))


def build_assets():
    css = """:root{--bg:#f8f7f2;--ink:#202124;--muted:#5f6673;--line:#d9d6ca;--accent:#8a4b16;--accent-dark:#6f3b10;--panel:#fff;--soft:#f4eadf}*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;line-height:1.58}a{color:var(--accent-dark)}.topbar{position:sticky;top:0;z-index:5;display:flex;justify-content:space-between;align-items:center;gap:24px;padding:14px 28px;border-bottom:1px solid var(--line);background:rgba(248,247,242,.94);backdrop-filter:blur(10px)}.brand{font-weight:800;text-decoration:none;color:var(--ink)}nav{display:flex;flex-wrap:wrap;gap:8px}nav a{padding:7px 9px;border-radius:6px;text-decoration:none;color:var(--muted);font-size:14px}nav a.active,nav a:hover{background:var(--soft);color:var(--accent-dark)}main{max-width:1180px;margin:0 auto;padding:28px}.hero{display:grid;grid-template-columns:minmax(0,1fr) 190px;gap:32px;align-items:center;min-height:520px;padding:42px 0 46px;border-bottom:1px solid var(--line)}h1{font-size:clamp(36px,5.2vw,62px);line-height:1.04;margin:0 0 20px;letter-spacing:0}h2{font-size:28px;margin:34px 0 12px}h3{font-size:20px;margin:0 0 10px}.lead{font-size:19px;color:var(--muted);max-width:780px}.eyebrow,.meta{color:var(--muted);font-size:13px;text-transform:uppercase;letter-spacing:0}.stats{display:grid;gap:2px;border-left:4px solid var(--accent);padding-left:18px}.stats strong{font-size:44px;line-height:1}.stats span{color:var(--muted);margin-bottom:14px}.grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px}.concept-card,.wide-card,.evidence{background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:18px}.concept-card h3 a{text-decoration:none;color:var(--ink)}dl{display:grid;gap:8px;margin:14px 0}dt{font-weight:800}dd{margin:0;color:var(--muted)}.page-head{max-width:840px;padding:26px 0 18px}.page-head h1{font-size:clamp(34px,5vw,58px)}.treatment{max-width:870px}.evidence-list{padding-left:18px;color:var(--muted)}.evidence-stack{display:grid;gap:14px}.wide-card{margin:14px 0}.chips{display:flex;flex-wrap:wrap;gap:8px}.chip,.button{display:inline-flex;align-items:center;min-height:32px;padding:6px 10px;border-radius:6px;background:var(--soft);color:var(--accent-dark);text-decoration:none;font-size:14px}.button{background:var(--accent);color:white}blockquote{margin:12px 0 0;padding:12px 14px;border-left:4px solid var(--accent);background:#fbfaf7;color:var(--muted)}.learning-diagram{margin:18px 0 30px;padding:0;border:1px solid var(--line);border-radius:8px;background:var(--panel);overflow:hidden}.learning-diagram figcaption{padding:12px 16px;border-bottom:1px solid var(--line);color:var(--accent-dark);font-weight:800}.flow-steps{display:grid;grid-template-columns:repeat(4,minmax(0,1fr))}.flow-step{min-height:160px;padding:16px;border-right:1px solid var(--line);background:linear-gradient(180deg,#fff,#fbfaf7)}.flow-step:last-child{border-right:0}.flow-step span{display:inline-flex;margin-bottom:10px;padding:4px 8px;border-radius:6px;background:var(--soft);color:var(--accent-dark);font-size:13px;font-weight:800}.flow-step p{margin:0;color:var(--muted);font-size:14px;overflow-wrap:anywhere}@media(max-width:820px){.topbar{align-items:flex-start;flex-direction:column;padding:12px 18px}main{padding:18px}.hero,.grid{grid-template-columns:1fr}.hero{min-height:0;padding-top:32px}h1{font-size:clamp(34px,10vw,44px)}.flow-steps{grid-template-columns:1fr}.flow-step{min-height:0;border-right:0;border-bottom:1px solid var(--line)}.flow-step:last-child{border-bottom:0}}"""
    write(SITE / "assets/styles.css", css)


def main():
    concepts = load("analysis/concepts/concept-atlas.json")
    themes = load("analysis/themes/theme-map.json")
    subthemes = load("analysis/themes/subtheme-map.json")
    evidence = load("analysis/evidence/evidence-ledger.json")
    primitives = load("analysis/throughlines/primitives.json")
    derivations = load("analysis/throughlines/derivations.json")
    families = load("analysis/throughlines/method-families.json")
    route = load("analysis/throughlines/study-route.json")
    clinic = load("analysis/throughlines/recognition-clinic.json")
    math_clinic = load("analysis/throughlines/math-walkthrough-clinic.json")
    drills = load("analysis/throughlines/problem-drills.json")
    solutions = load("analysis/throughlines/solution-workshop.json")
    cases = load("analysis/throughlines/case-studies.json")
    chains = load("analysis/throughlines/argument-chains.json")
    repairs = load("analysis/throughlines/misconception-repairs.json")
    paper_reading = load("analysis/throughlines/paper-reading-guide.json")
    jargon_decoder = load("analysis/throughlines/jargon-decoder.json")
    workbook = load("analysis/throughlines/model-building-workbook.json")
    proofs = load("analysis/throughlines/proof-sketch-lab.json")
    assumptions = load("analysis/throughlines/assumption-audit-lab.json")
    worked_transfer = load("analysis/throughlines/worked-transfer-examples.json")
    capstones = load("analysis/throughlines/capstone-self-test.json")
    lectures = load("analysis/lectures/lecture-path.json")
    equation_notes = load_optional("analysis/editorial-overrides/equation-walkthrough-notes.json", {})
    worked_examples = load_optional("analysis/editorial-overrides/worked-example-cards.json", {})
    ev_by_id = evidence_map(evidence)
    concept_by_id = concept_map(concepts)
    lecture_by_id = {lecture["id"]: lecture for lecture in lectures}
    primitive_by_id = {primitive["id"]: primitive for primitive in primitives}
    subtheme_by_id = subtheme_map(subthemes)
    lecture_by_evidence_id = lecture_evidence_map(lectures)
    deriv_by_id = derivation_map(derivations)
    math_clinic_by_id = {item["id"]: item for item in math_clinic}
    drill_by_id = {item["id"]: item for item in drills}
    family_by_id = {item["id"]: item for item in families}
    case_by_id = {item["id"]: item for item in cases}
    paper_by_id = {item["id"]: item for item in paper_reading}
    decoder_by_id = {item["id"]: item for item in jargon_decoder}
    model_step_by_id = {item["id"]: item for item in workbook}
    proof_by_id = {item["id"]: item for item in proofs}
    assumption_by_id = {item["id"]: item for item in assumptions}
    build_index(concepts, themes, evidence, lectures)
    build_study_route(route, lecture_by_id, concept_by_id, primitive_by_id, ev_by_id)
    build_recognition_clinic(clinic, concept_by_id, primitive_by_id, ev_by_id)
    build_math_clinic(math_clinic, deriv_by_id, concept_by_id, ev_by_id)
    build_problem_drills(drills, concept_by_id, primitive_by_id, ev_by_id)
    build_solution_workshop(solutions, concept_by_id, primitive_by_id, drill_by_id, case_by_id, math_clinic_by_id, decoder_by_id, ev_by_id)
    build_case_studies(cases, concept_by_id, primitive_by_id, math_clinic_by_id, drill_by_id, ev_by_id)
    build_argument_chains(chains, lecture_by_id, concept_by_id, primitive_by_id, ev_by_id)
    build_misconception_repairs(repairs, concept_by_id, drill_by_id, ev_by_id)
    build_paper_reading_guide(paper_reading, concept_by_id, primitive_by_id, family_by_id, case_by_id, drill_by_id, math_clinic_by_id, ev_by_id)
    build_jargon_decoder(jargon_decoder, concept_by_id, primitive_by_id, ev_by_id)
    build_model_building_workbook(workbook, concept_by_id, primitive_by_id, drill_by_id, decoder_by_id, ev_by_id)
    build_proof_sketch_lab(proofs, concept_by_id, primitive_by_id, math_clinic_by_id, decoder_by_id, ev_by_id)
    build_assumption_audit_lab(assumptions, concept_by_id, primitive_by_id, proof_by_id, model_step_by_id, decoder_by_id, ev_by_id)
    build_worked_transfer_examples(worked_transfer, concept_by_id, primitive_by_id, model_step_by_id, proof_by_id, assumption_by_id, decoder_by_id, ev_by_id)
    build_capstone_self_test(capstones, concept_by_id, primitive_by_id, case_by_id, drill_by_id, paper_by_id, decoder_by_id, ev_by_id)
    build_cross_reference(concepts, themes, subthemes, primitives, lectures, evidence)
    build_limits(concepts, themes, derivations)
    build_lectures(lectures, ev_by_id, concept_by_id, deriv_by_id)
    build_concepts(concepts, evidence, deriv_by_id, equation_notes, worked_examples)
    build_themes(themes, subthemes, concepts)
    build_primitives(primitives, derivations, concept_by_id)
    build_families(families, concept_by_id, ev_by_id)
    build_evidence(evidence, concept_by_id, subtheme_by_id, lecture_by_evidence_id)
    build_assets()


if __name__ == "__main__":
    main()
