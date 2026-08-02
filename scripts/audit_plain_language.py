#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "analysis/audits/plain-language-report.md"


def words(text: str) -> int:
    return len(re.findall(r"\b\w+\b", text))


def sentences(text: str) -> list[str]:
    return [part.strip() for part in re.split(r"(?<=[.!?])\s+", text) if part.strip()]


def load_json(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    essays = load_json("analysis/throughlines/first-principles-essays.json")
    why_matters = load_json("analysis/throughlines/why-matters-checkpoints.json")
    application_map = load_json("analysis/throughlines/application-map.json")
    glossary = load_json("analysis/throughlines/everyday-glossary.json")

    banned_phrases = [
        "crucial role",
        "complex dynamics",
        "provides insights",
        "real-world applications",
        "plays a role",
        "robust framework",
        "paradigm",
        "leverage",
        "utilize",
        "aforementioned",
        "it is important to note",
    ]
    allowed_terms = {
        "action",
        "actions",
        "auction",
        "belief",
        "beliefs",
        "bid",
        "bids",
        "choice",
        "choices",
        "common knowledge",
        "credibility",
        "discounting",
        "dominance",
        "equilibrium",
        "fixed point",
        "information",
        "mechanism",
        "mixed strategy",
        "payoff",
        "payoffs",
        "player",
        "players",
        "screening",
        "signal",
        "signals",
        "strategy",
        "type",
        "types",
        "utility",
        "welfare",
    }
    technical_terms = [
        "Bayesian",
        "Nash",
        "subgame",
        "perfect Bayesian",
        "revenue equivalence",
        "mixed strategy",
        "fixed point",
        "compactness",
        "convexity",
        "continuity",
        "mechanism design",
        "common knowledge",
    ]

    glossary_terms = {str(item.get("term", "")).lower() for item in glossary}
    allowed_terms |= glossary_terms

    essay_word_counts = []
    long_sentence_count = 0
    technical_mentions = 0
    for essay in essays:
        text_parts = [essay.get("plain_purpose", "")]
        for section in essay.get("sections", []):
            body = section.get("body", "")
            text_parts.append(body)
            if words(body) < 60:
                errors.append(f"essay {essay['id']} section is shallow: {section.get('heading', '')}")
            for sentence in sentences(body):
                if words(sentence) > 42:
                    long_sentence_count += 1
                    warnings.append(f"long sentence in essay {essay['id']}: {sentence[:90]}")
        for application in essay.get("applications", []):
            text_parts.append(application.get("body", ""))
        text = " ".join(text_parts)
        essay_word_counts.append(words(text))
        lower = text.lower()
        if not any(marker in lower for marker in ["everyday", "imagine", "person", "people", "firm", "buyer", "bidder", "platform"]):
            errors.append(f"essay {essay['id']} lacks an everyday setup marker")
        if not any(marker in lower for marker in ["break", "wrong", "mistake", "fail", "misuse", "danger"]):
            errors.append(f"essay {essay['id']} lacks a limits/mistake marker")
        for phrase in banned_phrases:
            if phrase in lower:
                errors.append(f"essay {essay['id']} uses banned filler phrase: {phrase}")
        for term in technical_terms:
            if term.lower() in lower:
                technical_mentions += lower.count(term.lower())

    application_word_counts = []
    why_matters_word_counts = []
    why_fields = ["everyday_situation", "mistaken_reading", "first_principles_correction", "why_it_matters", "where_else_it_applies"]
    for item in why_matters:
        combined = " ".join(str(item.get(field, "")) for field in why_fields)
        why_matters_word_counts.append(words(combined))
        if words(combined) < 95:
            errors.append(f"why-it-matters {item['id']} is shallow")
        lower = combined.lower()
        if "mistake" not in str(item.get("mistaken_reading", "")).lower():
            errors.append(f"why-it-matters {item['id']} missing explicit mistake language")
        if words(str(item.get("why_it_matters", ""))) < 14:
            errors.append(f"why-it-matters {item['id']} has shallow why_it_matters")
        for field in why_fields:
            if words(str(item.get(field, ""))) < 12:
                errors.append(f"why-it-matters {item['id']} shallow field: {field}")
        for phrase in banned_phrases:
            if phrase in lower:
                errors.append(f"why-it-matters {item['id']} uses banned filler phrase: {phrase}")

    for item in application_map:
        combined = " ".join(
            str(item.get(field, ""))
            for field in [
                "plain_question",
                "players_or_objects",
                "choices",
                "information",
                "timing",
                "outcome_logic",
                "why_it_matters",
                "where_it_breaks",
            ]
        )
        application_word_counts.append(words(combined))
        for field in ["players_or_objects", "choices", "information", "timing", "outcome_logic", "why_it_matters", "where_it_breaks"]:
            if words(str(item.get(field, ""))) < 12:
                errors.append(f"application map {item['id']} shallow field: {field}")
        lower = combined.lower()
        for phrase in banned_phrases:
            if phrase in lower:
                errors.append(f"application map {item['id']} uses banned filler phrase: {phrase}")

    glossary_word_counts = []
    for item in glossary:
        combined = " ".join(str(item.get(field, "")) for field in ["everyday_definition", "why_word_exists", "beginner_mistake"])
        glossary_word_counts.append(words(combined))
        if words(combined) < 35:
            errors.append(f"glossary {item['id']} is shallow")
        for field in ["everyday_definition", "why_word_exists", "beginner_mistake"]:
            value = str(item.get(field, ""))
            if words(value) < 8:
                errors.append(f"glossary {item['id']} shallow field: {field}")
        lower = combined.lower()
        for phrase in banned_phrases:
            if phrase in lower:
                errors.append(f"glossary {item['id']} uses banned filler phrase: {phrase}")

    lines = [
        "# Plain Language Report",
        "",
        "This audit checks the first-principles layer for simple wording, everyday setup, explicit limits, and banned filler phrases.",
        "",
        "## Summary",
        "",
        f"- Essay cards: {len(essays)}",
        f"- Essay words: min {min(essay_word_counts) if essay_word_counts else 0}, max {max(essay_word_counts) if essay_word_counts else 0}",
        f"- Why-it-matters checkpoints: {len(why_matters)}",
        f"- Why-it-matters words: min {min(why_matters_word_counts) if why_matters_word_counts else 0}, max {max(why_matters_word_counts) if why_matters_word_counts else 0}",
        f"- Application map cards: {len(application_map)}",
        f"- Application map words: min {min(application_word_counts) if application_word_counts else 0}, max {max(application_word_counts) if application_word_counts else 0}",
        f"- Glossary terms: {len(glossary)}",
        f"- Glossary words: min {min(glossary_word_counts) if glossary_word_counts else 0}, max {max(glossary_word_counts) if glossary_word_counts else 0}",
        f"- Technical mentions checked: {technical_mentions}",
        f"- Long sentences flagged for review: {long_sentence_count}",
        f"- Errors: {len(errors)}",
        "",
        "## Warnings",
        "",
    ]
    lines.extend(f"- {warning}" for warning in warnings[:20]) if warnings else lines.append("- None")
    lines.extend(["", "## Errors", ""])
    lines.extend(f"- {error}" for error in errors) if errors else lines.append("- None")
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"audited plain language for {len(essays)} essays, {len(why_matters)} checkpoints, {len(application_map)} applications, {len(glossary)} glossary terms; errors: {len(errors)}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
