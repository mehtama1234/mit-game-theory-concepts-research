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
        ("cross-reference.html", "Cross Index", "cross-reference"),
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
<section><h2>Find A Concept By Pressure</h2><p>The cross index lets a reader jump from an everyday problem to the relevant concept, lecture, primitive, subtheme, and evidence record.</p><p><a class="button" href="cross-reference.html">Open the cross index</a></p></section>
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
  <h3>Lectures</h3><p class="chips">{lecture_links}</p>
  <h3>Concepts</h3><p class="chips">{concept_links}</p>
  <h3>Primitives</h3><p class="chips">{primitive_links}</p>
  <h3>Evidence Checkpoints</h3><ul class="evidence-list">{evidence_links}</ul>
  <h3>Checkpoint</h3><p>{esc(item["checkpoint"])}</p>
</article>""")
    body = '<section class="page-head"><h1>Study Route</h1><p>A compact path through the course, from first choice primitives to evidence-backed strategic reasoning.</p></section>' + "".join(cards)
    write(SITE / "study-route.html", page("Study Route", body, "study-route"))


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
  {diagram}
  <h3>Plain-Language Principle</h3><p>{esc(primitive.get("plain_language_principle", primitive["why_it_exists"]))}</p>
  <h3>Symbol By Symbol</h3><p>{esc(primitive["symbol_explanation"])}</p>
  <h3>Where It Appears</h3><p>{esc(primitive["course_appearances"])}</p>
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
    build_index(concepts, themes, evidence, lectures)
    build_study_route(route, lecture_by_id, concept_by_id, primitive_by_id, ev_by_id)
    build_cross_reference(concepts, themes, subthemes, primitives, lectures, evidence)
    build_lectures(lectures, ev_by_id, concept_by_id, deriv_by_id)
    build_concepts(concepts, evidence, deriv_by_id, equation_notes, worked_examples)
    build_themes(themes, subthemes, concepts)
    build_primitives(primitives, derivations, concept_by_id)
    build_families(families, concept_by_id, ev_by_id)
    build_evidence(evidence, concept_by_id, subtheme_by_id, lecture_by_evidence_id)
    build_assets()


if __name__ == "__main__":
    main()
