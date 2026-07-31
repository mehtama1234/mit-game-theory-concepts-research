#!/usr/bin/env python3
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
OVERRIDES = ROOT / "analysis/editorial-overrides"

ROLE_BY_TITLE = {
    "Introduction to Individual Decision-Making": {
        "first_principles_role": "Builds the individual-choice foundation: preferences, utility, beliefs, lotteries, and the idea that choices need a payoff language before strategy can begin.",
        "what_to_watch_for": "Watch for the course separating a person's ranking from the later strategic problem. This is where payoffs stop being arbitrary numbers and start as representations of choice.",
    },
    "Representation of Games": {
        "first_principles_role": "Turns social situations into formal objects: players, histories, strategies, strategy profiles, payoffs, and the difference between trees and compact strategic form.",
        "what_to_watch_for": "Watch how a representation can hide or reveal timing. The lecture is a warning that a wrong game form can make later equilibrium analysis precise but wrong.",
    },
    "Dominance": {
        "first_principles_role": "Introduces pruning: some strategies can be ruled out because another strategy does better across the relevant contingencies.",
        "what_to_watch_for": "Watch for the distinction between deleting a move by proof and deleting it because it feels unlikely. Dominance is powerful exactly because it avoids belief speculation when it applies.",
    },
    "Rationalizability": {
        "first_principles_role": "Adds beliefs to pruning. A strategy can remain plausible if some coherent belief about others makes it a best response.",
        "what_to_watch_for": "Watch the course move from strict deletion to belief-supported survival. This is the bridge between dominance and equilibrium.",
    },
    "Nash Equilibrium": {
        "first_principles_role": "Closes the best-response loop: every player must be choosing optimally given the others' choices.",
        "what_to_watch_for": "Watch for Nash being used as a stability test, not a welfare claim. The central question is whether anyone wants to deviate alone.",
    },
    "Imperfect Competition": {
        "first_principles_role": "Applies strategic reasoning to firm competition, where prices or quantities interact through demand and payoff consequences.",
        "what_to_watch_for": "Watch for payoff mapping in an economic application: the model has to say how a firm's action and rivals' actions jointly determine profit.",
    },
    "Zero-Sum Games": {
        "first_principles_role": "Studies exact conflict, where one player's gain is the other's loss and minimax/security reasoning becomes natural.",
        "what_to_watch_for": "Watch the boundary: many competitive situations are not zero-sum. The lecture matters because it shows what becomes special when conflict is exact.",
    },
    "Backward Induction": {
        "first_principles_role": "Makes credibility calculable by solving later choices first and folding their values back into earlier decisions.",
        "what_to_watch_for": "Watch for the shift from chronological storytelling to recursive reasoning. The future determines what earlier threats and promises mean.",
    },
    "Negotiation": {
        "first_principles_role": "Treats bargaining as strategic surplus division shaped by offers, rejection, timing, patience, and outside options.",
        "what_to_watch_for": "Watch how bargaining power gets modeled as incentives and timing rather than personality or moral entitlement.",
    },
    "Subgame-Perfect Nash Equilibrium": {
        "first_principles_role": "Repairs Nash for dynamic games by requiring continuation behavior to remain rational inside every subgame.",
        "what_to_watch_for": "Watch for noncredible threats. This lecture asks whether a threat would still be worth carrying out after the threatened history happens.",
    },
    "One-Shot Deviation Principle and Bargaining": {
        "first_principles_role": "Adds a practical dynamic-equilibrium check and returns to bargaining with sharper tools for deviations over time.",
        "what_to_watch_for": "Watch how a local deviation test can stand in for many possible strategy changes when the theorem conditions are right.",
    },
    "Finitely Repeated Games": {
        "first_principles_role": "Shows why a known last round can unravel cooperation even when the game is played many times.",
        "what_to_watch_for": "Watch the endpoint. Repetition alone is not enough; the future has to retain disciplinary force.",
    },
    "Infinitely Repeated Games": {
        "first_principles_role": "Removes the known last round and turns future punishment into a possible enforcement mechanism, where ongoing relationships can change one-shot incentives.",
        "what_to_watch_for": "Watch the discount factor and continuation value. Cooperation becomes an inequality comparing today's temptation with future loss, not a vague claim that repetition builds trust.",
    },
    "Folk Theorem": {
        "first_principles_role": "Explains how patient repeated games can sustain many feasible and individually rational payoff patterns.",
        "what_to_watch_for": "Watch the tradeoff between possibility and prediction. The theorem expands what can happen, but that can make selection harder.",
    },
    "Implicit Cartels": {
        "first_principles_role": "Applies repeated-game enforcement to firms that may sustain collusion without an explicit enforceable contract.",
        "what_to_watch_for": "Watch self-enforcement. Punishment must be in the punishers' interest too, or the cartel path is just a story.",
    },
    "Bayesian Games": {
        "first_principles_role": "Introduces hidden types and priors so strategy can be modeled when players do not share the same information.",
        "what_to_watch_for": "Watch the type space. The model's quality depends on what private information is represented and what beliefs are assigned.",
    },
    "Bayesian Nash Equilibrium: Applications": {
        "first_principles_role": "Solves applied incomplete-information games by checking expected-payoff best responses for each type.",
        "what_to_watch_for": "Watch for type-contingent plans. Equilibrium is no longer one action per player; it is a plan for each possible type.",
    },
    "Auctions": {
        "first_principles_role": "Turns private values into strategic bids under allocation and payment rules.",
        "what_to_watch_for": "Watch deviations in bids. A bid is a strategic action shaped by the rule, not a transparent report of value.",
    },
    "Revenue Equivalence": {
        "first_principles_role": "Shows when different auction formats produce the same expected revenue because strategic bid adjustments offset rule differences.",
        "what_to_watch_for": "Watch assumptions. The theorem is as much about the conditions for equivalence as about the equivalence itself.",
    },
    "Ad Auctions": {
        "first_principles_role": "Moves auction design into platform markets where rank, clicks, quality, and advertiser value interact.",
        "what_to_watch_for": "Watch the object being sold. The platform allocates attention and expected clicks, not just a single indivisible item.",
    },
    "Perfect Bayesian Equilibrium": {
        "first_principles_role": "Combines dynamic credibility with belief updating in games where histories can reveal private information and observed actions change what players infer.",
        "what_to_watch_for": "Watch the equilibrium object: strategies plus beliefs. Either half alone is incomplete because continuation actions depend on what players think the history has revealed.",
    },
    "Signaling": {
        "first_principles_role": "Studies how privately informed senders can influence receivers through observable actions that may reveal type.",
        "what_to_watch_for": "Watch imitation. A signal separates types only when the wrong type does not want to copy it.",
    },
    "Bargaining with Incomplete Information": {
        "first_principles_role": "Adds hidden values or costs to negotiation, making delay and offers partly about learning what the other side knows.",
        "what_to_watch_for": "Watch how uncertainty changes offers. Delay can be strategic information management, not just impatience or stubbornness.",
    },
    "Cheap Talk": {
        "first_principles_role": "Asks when costless, nonbinding messages can transmit information despite incentives to mislead.",
        "what_to_watch_for": "Watch preference alignment. Speech works only when the sender benefits from moving the receiver toward a useful action.",
    },
    "Common Knowledge": {
        "first_principles_role": "Climbs from private knowledge to shared higher-order knowledge, where everyone knows and knows that others know.",
        "what_to_watch_for": "Watch publicness. A fact can be true and individually known without becoming strong enough to coordinate behavior.",
    },
}


def load(path: str) -> Any:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def load_overrides(name: str) -> dict[str, Any]:
    path = OVERRIDES / name
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def lecture_key(title: str) -> str:
    return title.split(": ", 1)[-1]


def plural(count: int, singular: str, plural_form: str | None = None) -> str:
    return singular if count == 1 else (plural_form or f"{singular}s")


def coverage_note(record_count: int, concept_count: int) -> str:
    if record_count == 0:
        return "No current evidence anchors point to this lecture; it remains represented through course sequence context."
    verb = "connects" if record_count == 1 else "connect"
    return (
        f"{record_count} transcript evidence {plural(record_count, 'anchor')} {verb} "
        f"this lecture to {concept_count} atlas {plural(concept_count, 'concept')}."
    )


def supplemental_coverage_note(concept_record_count: int, supplemental_count: int) -> str:
    total = concept_record_count + supplemental_count
    return (
        f"{total} total lecture evidence {plural(total, 'anchor')} "
        f"({concept_record_count} concept-linked, {supplemental_count} supplemental)."
    )


def main() -> None:
    index = load("raw-material/youtube/transcript-index.json")
    concepts = load("analysis/concepts/concept-atlas.json")
    evidence = load("analysis/evidence/evidence-ledger.json")
    themes = load("analysis/themes/theme-map.json")
    lecture_overrides = load_overrides("lectures.json")
    supplemental_overrides = load_overrides("lecture-evidence.json")
    concept_by_id = {concept["id"]: concept for concept in concepts}
    theme_by_id = {theme["id"]: theme for theme in themes}
    evidence_by_title: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in evidence:
        evidence_by_title[record["video_title"]].append(record)

    lecture_path = []
    for row in sorted(index, key=lambda item: item["playlist_index"]):
        records = evidence_by_title.get(row["title"], [])
        concept_ids = []
        theme_ids = []
        for record in records:
            for concept_id in record["supports_concepts"]:
                if concept_id not in concept_ids:
                    concept_ids.append(concept_id)
                    theme_id = concept_by_id[concept_id]["theme_id"]
                    if theme_id not in theme_ids:
                        theme_ids.append(theme_id)
        key = lecture_key(row["title"])
        role = ROLE_BY_TITLE.get(key, {
            "first_principles_role": "Connects course concepts to transcript-backed game-theory reasoning.",
            "what_to_watch_for": "Watch how the lecture changes the modeling object or the incentive check.",
        })
        treatment = lecture_overrides.get(key)
        if treatment is None:
            raise ValueError(f"missing hand-crafted lecture treatment for {key}")
        supplemental_evidence = supplemental_overrides.get(f"lecture-{row['playlist_index']:02d}", [])
        lecture_path.append({
            "id": f"lecture-{row['playlist_index']:02d}",
            "playlist_index": row["playlist_index"],
            "title": row["title"],
            "youtube_url": row["url"],
            "duration_seconds": row["duration"],
            "word_count": row["word_count"],
            "transcript_path": row["clean_txt"],
            "first_principles_role": role["first_principles_role"],
            "what_to_watch_for": role["what_to_watch_for"],
            "concepts": [
                {
                    "id": concept_id,
                    "name": concept_by_id[concept_id]["name"],
                    "theme_id": concept_by_id[concept_id]["theme_id"],
                    "theme_name": theme_by_id[concept_by_id[concept_id]["theme_id"]]["name"],
                }
                for concept_id in concept_ids
            ],
            "evidence_ids": [record["id"] for record in records],
            "themes": [
                {"id": theme_id, "name": theme_by_id[theme_id]["name"]}
                for theme_id in theme_ids
            ],
            "coverage_note": coverage_note(len(records), len(concept_ids)),
            "total_coverage_note": supplemental_coverage_note(len(records), len(supplemental_evidence)),
            "argument_arc": treatment["argument_arc"],
            "math_entry_point": treatment["math_entry_point"],
            "worked_mini_example": treatment["worked_mini_example"],
            "common_failure": treatment["common_failure"],
            "supplemental_evidence": supplemental_evidence,
            "supplemental_evidence_ids": [record["id"] for record in supplemental_evidence],
        })

    out = ROOT / "analysis/lectures/lecture-path.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(lecture_path, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    supplemental_out = ROOT / "analysis/lectures/lecture-evidence.json"
    supplemental_out.write_text(json.dumps([
        record | {"lecture_id": lecture_id}
        for lecture_id, records in supplemental_overrides.items()
        for record in records
    ], indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {out.relative_to(ROOT)} with {len(lecture_path)} lectures")


if __name__ == "__main__":
    main()
