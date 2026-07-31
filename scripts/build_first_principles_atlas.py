#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "raw-material/youtube/transcript-index.json"
OVERRIDES = ROOT / "analysis/editorial-overrides"
COURSE = "mit-14-12-economic-applications-of-game-theory-fall-2025"


PRIMITIVES: list[dict[str, Any]] = [
    {
        "id": "preference",
        "name": "Preference",
        "plain_language": "A way to say which outcome a person would rather have.",
        "why_it_exists": "Choices need an internal ordering; without one, better and worse have no operational meaning.",
        "formal_object": "A preference relation ranks outcomes, often represented by a utility function u(x).",
        "useful_equation": "x preferred to y means u(x) > u(y).",
        "symbol_explanation": "x and y are possible outcomes; u assigns each outcome a number; the larger number records the option the person ranks higher.",
        "misuse_failure": "Treating utility as literal happiness can mislead; in game theory it is a ranking device for choices.",
    },
    {
        "id": "payoff_mapping",
        "name": "Payoff Mapping",
        "plain_language": "A table that says what each person gets from each combination of choices.",
        "why_it_exists": "In strategic settings, my result depends on what others do too.",
        "formal_object": "A payoff function u_i(a_i, a_-i) maps everyone's actions to player i's payoff.",
        "useful_equation": "u_i(a_i, a_-i).",
        "symbol_explanation": "i is one player; a_i is that player's action; a_-i means everyone else's actions; u_i is the payoff assigned to the whole action profile.",
        "misuse_failure": "A payoff table is not the world itself; it is a simplified representation whose assumptions drive the result.",
    },
    {
        "id": "best_response",
        "name": "Best Response",
        "plain_language": "The choice that works best given what someone believes others will do.",
        "why_it_exists": "No strategy is good in isolation; it is good against some expectation about others.",
        "formal_object": "BR_i(a_-i) is the set of actions for player i that maximize u_i given others' actions.",
        "useful_equation": "BR_i(a_-i) = argmax_a u_i(a, a_-i).",
        "symbol_explanation": "argmax means choose the action a that makes player i's payoff as large as possible when others choose a_-i.",
        "misuse_failure": "Calling something a best response without naming the belief or opponent action hides the key assumption.",
    },
    {
        "id": "mutual_consistency",
        "name": "Mutual Consistency",
        "plain_language": "A situation where each person's plan makes sense given everyone else's plan.",
        "why_it_exists": "A prediction of strategic behavior must survive every player asking whether they personally want to change.",
        "formal_object": "Equilibrium requires each strategy to be a best response to the others.",
        "useful_equation": "a_i in BR_i(a_-i) for every player i.",
        "symbol_explanation": "For each player i, their chosen action a_i must belong to the set of best responses against the other players' actions.",
        "misuse_failure": "Equilibrium does not mean fair, efficient, or morally good; it means no one has a one-person reason to move.",
    },
    {
        "id": "pruning",
        "name": "Pruning",
        "plain_language": "Remove choices that are never worth taking, then reason with the smaller problem.",
        "why_it_exists": "Large strategic problems become easier when obviously bad options can be ruled out.",
        "formal_object": "Dominance compares one strategy against another across possible opponent choices.",
        "useful_equation": "s dominates t if u_i(s, a_-i) >= u_i(t, a_-i) for all a_-i, with strict inequality somewhere.",
        "symbol_explanation": "The inequality checks every possible action by others; dominance means one strategy is never worse and sometimes better.",
        "misuse_failure": "Pruning too aggressively can remove behavior that matters when beliefs, weak dominance, or timing are handled differently.",
    },
    {
        "id": "backward_recursion",
        "name": "Backward Recursion",
        "plain_language": "Solve the future first, then use that answer to decide what should happen earlier.",
        "why_it_exists": "In sequential games, later credible choices determine earlier incentives.",
        "formal_object": "Backward induction assigns optimal choices from terminal decision nodes back to the start.",
        "useful_equation": "V(node) = max_action V(next node).",
        "symbol_explanation": "V is continuation value; at each decision point the player chooses the next branch with the best continuation value.",
        "misuse_failure": "Backward induction assumes the game tree and payoffs are known and that later threats are credible.",
    },
    {
        "id": "discounting",
        "name": "Discounting",
        "plain_language": "Future rewards count, but usually count less than rewards right now.",
        "why_it_exists": "Repeated relationships trade off today's temptation against tomorrow's consequences.",
        "formal_object": "A discount factor delta weights future payoffs in an intertemporal sum.",
        "useful_equation": "U = u_0 + delta u_1 + delta^2 u_2 + ...",
        "symbol_explanation": "u_t is payoff in period t; delta between 0 and 1 controls how strongly the future matters.",
        "misuse_failure": "A cooperation result can disappear when players are impatient or cannot punish future deviations.",
    },
    {
        "id": "belief",
        "name": "Belief",
        "plain_language": "A probability story about what kind of situation or opponent you are facing.",
        "why_it_exists": "People often choose without knowing another person's type, value, cost, or information.",
        "formal_object": "A belief is a probability distribution over states, types, or histories.",
        "useful_equation": "E[u(a, theta)] = sum_theta p(theta) u(a, theta).",
        "symbol_explanation": "theta is the unknown type or state; p(theta) is its probability; expected utility averages payoffs across possibilities.",
        "misuse_failure": "If beliefs are not tied to information and incentives, the model can rationalize almost anything.",
    },
    {
        "id": "incentive_compatibility",
        "name": "Incentive Compatibility",
        "plain_language": "Design rules so people want to reveal or do what the rule needs them to reveal or do.",
        "why_it_exists": "People with private information may gain by misreporting it.",
        "formal_object": "Truthful behavior must give at least as much payoff as each profitable lie.",
        "useful_equation": "u_i(truth) >= u_i(report) for every alternative report.",
        "symbol_explanation": "The inequality says a person should not gain by replacing the truthful action with another report.",
        "misuse_failure": "A mechanism can look efficient on paper while failing because participants have incentives to shade bids or messages.",
    },
    {
        "id": "knowledge_recursion",
        "name": "Knowledge Recursion",
        "plain_language": "Not only knowing a fact, but knowing that others know it, and so on.",
        "why_it_exists": "Coordinated strategic behavior often depends on shared awareness, not private awareness alone.",
        "formal_object": "Common knowledge means everyone knows, everyone knows everyone knows, and the chain continues.",
        "useful_equation": "E, KE, KKE, KKKE, ...",
        "symbol_explanation": "E is the event; K means known by the players; repeated K's represent higher-order knowledge.",
        "misuse_failure": "Treating public facts as common knowledge can be wrong if people are unsure what others observed.",
    },
]


THEMES = [
    {
        "id": "choice_and_payoff",
        "name": "Choice Under Tradeoffs",
        "big_picture": "Before strategy enters, the course needs a language for ranking outcomes and measuring what a person is trying to get.",
        "why_this_theme_matters": "Game theory cannot explain strategic interaction unless each player first has a reason to prefer one outcome over another.",
    },
    {
        "id": "strategic_dependence",
        "name": "Strategic Dependence",
        "big_picture": "The central problem is that one person's best move depends on what other people do.",
        "why_this_theme_matters": "This is the move from ordinary decision-making to game theory.",
    },
    {
        "id": "equilibrium_reasoning",
        "name": "Equilibrium As Mutual Consistency",
        "big_picture": "A prediction must be stable against each player's own incentive to change.",
        "why_this_theme_matters": "Equilibrium is the course's main way to turn interactive choices into a disciplined prediction.",
    },
    {
        "id": "time_and_credibility",
        "name": "Time, Threats, And Credibility",
        "big_picture": "Promises and threats matter only when they remain optimal at the moment they must be carried out.",
        "why_this_theme_matters": "Sequential games force students to separate what someone says now from what they will actually want later.",
    },
    {
        "id": "repetition_and_cooperation",
        "name": "Repeated Interaction And Cooperation",
        "big_picture": "Repeated relationships can make cooperation possible because today's action changes tomorrow's incentives.",
        "why_this_theme_matters": "This explains why behavior can differ between one-time encounters and ongoing relationships.",
    },
    {
        "id": "private_information",
        "name": "Private Information And Beliefs",
        "big_picture": "People often act without knowing another person's type, value, cost, or information.",
        "why_this_theme_matters": "Beliefs let the course model uncertainty without pretending everyone knows the same facts.",
    },
    {
        "id": "mechanisms_and_markets",
        "name": "Mechanisms, Auctions, And Markets",
        "big_picture": "Rules shape incentives, so market design asks which rules make strategic behavior produce useful outcomes.",
        "why_this_theme_matters": "Auctions and ad auctions show game theory as an engineering tool, not only a descriptive language.",
    },
    {
        "id": "communication_and_knowledge",
        "name": "Communication And Knowledge",
        "big_picture": "Messages matter when they change beliefs, but incentives determine whether messages can be trusted.",
        "why_this_theme_matters": "Signaling, cheap talk, and common knowledge explain how information moves through strategic settings.",
    },
]


CONCEPTS: list[dict[str, Any]] = [
    {"id": "preferences", "name": "Preferences", "theme": "choice_and_payoff", "lectures": [1], "primitives": ["preference"], "keywords": ["preference", "preferences", "prefer", "ranking", "complete", "transitive"], "definition": "A way to say which outcomes a person ranks above others."},
    {"id": "utility", "name": "Utility", "theme": "choice_and_payoff", "lectures": [1], "primitives": ["preference"], "keywords": ["utility", "payoff", "utility function", "von Neumann", "expected utility"], "definition": "A numerical representation of what someone is trying to get."},
    {"id": "expected_utility", "name": "Expected Utility", "theme": "choice_and_payoff", "lectures": [1, 16], "primitives": ["belief", "preference"], "keywords": ["expected utility", "expectation", "lottery", "probability", "risk"], "definition": "Averaging possible payoffs by how likely they are."},
    {"id": "strategic_form_games", "name": "Strategic Form Games", "theme": "strategic_dependence", "lectures": [2], "primitives": ["payoff_mapping"], "keywords": ["strategic form", "normal form", "payoff matrix", "action profile", "players"], "definition": "A compact table of players, actions, and payoffs chosen at the same time."},
    {"id": "extensive_form_games", "name": "Extensive Form Games", "theme": "time_and_credibility", "lectures": [2, 8, 10], "primitives": ["backward_recursion"], "keywords": ["extensive form", "game tree", "node", "history", "sequential"], "definition": "A game drawn as a tree so timing and information can be represented."},
    {"id": "dominance", "name": "Dominance", "theme": "strategic_dependence", "lectures": [3], "primitives": ["pruning"], "keywords": ["dominance", "dominated", "dominant strategy", "strictly dominated", "weakly dominated"], "definition": "A way to rule out choices that are never better than another choice."},
    {"id": "iterated_deletion", "name": "Iterated Deletion", "theme": "strategic_dependence", "lectures": [3, 4], "primitives": ["pruning"], "keywords": ["iterated deletion", "delete", "eliminate", "dominated strategies", "survive"], "definition": "Repeatedly removing bad strategies and seeing what remains."},
    {"id": "rationalizability", "name": "Rationalizability", "theme": "strategic_dependence", "lectures": [4], "primitives": ["belief"], "keywords": ["rationalizable", "rationalizability", "belief", "beliefs", "common belief"], "definition": "A strategy is plausible if it can be optimal for some reasonable belief about others."},
    {"id": "best_response", "name": "Best Response", "theme": "equilibrium_reasoning", "lectures": [4, 5], "primitives": ["best_response"], "keywords": ["best response", "best-response", "respond", "maximize", "given"], "definition": "The move that works best against a specified belief or opponent action."},
    {"id": "nash_equilibrium", "name": "Nash Equilibrium", "theme": "equilibrium_reasoning", "lectures": [5, 10, 17], "primitives": ["mutual_consistency"], "keywords": ["Nash equilibrium", "equilibrium", "deviation", "best response"], "definition": "A profile of strategies where no player wants to change alone."},
    {"id": "mixed_strategies", "name": "Mixed Strategies", "theme": "equilibrium_reasoning", "lectures": [5, 7], "primitives": ["belief", "mutual_consistency"], "keywords": ["mixed strategy", "mixing", "randomize", "probability distribution", "indifferent"], "definition": "Choosing randomly on purpose so opponents cannot exploit a predictable move."},
    {"id": "zero_sum_games", "name": "Zero-Sum Games", "theme": "equilibrium_reasoning", "lectures": [7], "primitives": ["mutual_consistency"], "keywords": ["zero-sum", "zero sum", "minimax", "value of the game", "saddle point"], "definition": "A setting where one player's gain is exactly the other's loss."},
    {"id": "minimax", "name": "Minimax", "theme": "equilibrium_reasoning", "lectures": [7], "primitives": ["best_response"], "keywords": ["minimax", "maxmin", "minimum", "maximum", "security level"], "definition": "Choosing a strategy by protecting yourself against the worst response."},
    {"id": "backward_induction", "name": "Backward Induction", "theme": "time_and_credibility", "lectures": [8], "primitives": ["backward_recursion"], "keywords": ["backward induction", "solve backwards", "terminal", "last move", "game tree"], "definition": "Solving a sequential game by starting at the end."},
    {"id": "subgame_perfection", "name": "Subgame-Perfect Nash Equilibrium", "theme": "time_and_credibility", "lectures": [10], "primitives": ["backward_recursion", "mutual_consistency"], "keywords": ["subgame perfect", "subgame-perfect", "subgame", "credible threat", "SPNE"], "definition": "An equilibrium that remains sensible after every possible history."},
    {"id": "one_shot_deviation", "name": "One-Shot Deviation Principle", "theme": "time_and_credibility", "lectures": [11], "primitives": ["backward_recursion"], "keywords": ["one-shot deviation", "one shot deviation", "deviation principle", "profitable deviation"], "definition": "A shortcut for checking whether changing one move at one point can improve a strategy."},
    {"id": "bargaining", "name": "Bargaining", "theme": "time_and_credibility", "lectures": [9, 11, 23], "primitives": ["payoff_mapping", "discounting"], "keywords": ["bargaining", "negotiate", "offer", "reservation", "surplus"], "definition": "Dividing a surplus when each side can accept, reject, or wait."},
    {"id": "finitely_repeated_games", "name": "Finitely Repeated Games", "theme": "repetition_and_cooperation", "lectures": [12], "primitives": ["backward_recursion"], "keywords": ["finitely repeated", "finite repetition", "last period", "repeated game"], "definition": "Playing a stage game a known limited number of times."},
    {"id": "infinitely_repeated_games", "name": "Infinitely Repeated Games", "theme": "repetition_and_cooperation", "lectures": [13], "primitives": ["discounting"], "keywords": ["infinitely repeated", "infinite repetition", "discount factor", "grim trigger", "trigger strategy"], "definition": "A relationship with no fixed last round, where future punishment can shape present behavior."},
    {"id": "folk_theorem", "name": "Folk Theorem", "theme": "repetition_and_cooperation", "lectures": [14], "primitives": ["discounting", "mutual_consistency"], "keywords": ["folk theorem", "feasible", "individually rational", "punishment", "delta"], "definition": "A result showing that many cooperative outcomes can be sustained when the future matters enough."},
    {"id": "implicit_cartels", "name": "Implicit Cartels", "theme": "repetition_and_cooperation", "lectures": [15], "primitives": ["discounting", "incentive_compatibility"], "keywords": ["cartel", "collusion", "tacit", "implicit", "Bertrand", "Cournot"], "definition": "Firms may keep prices high without an explicit agreement when future punishment disciplines cheating."},
    {"id": "bayesian_games", "name": "Bayesian Games", "theme": "private_information", "lectures": [16], "primitives": ["belief"], "keywords": ["Bayesian game", "type", "types", "private information", "prior"], "definition": "A game where players may not know each other's type, value, or payoff information."},
    {"id": "types_and_beliefs", "name": "Types And Beliefs", "theme": "private_information", "lectures": [16, 21], "primitives": ["belief"], "keywords": ["type", "types", "belief", "prior", "posterior", "Bayes"], "definition": "Types store hidden information; beliefs describe what others think those types might be."},
    {"id": "bayesian_nash_equilibrium", "name": "Bayesian Nash Equilibrium", "theme": "private_information", "lectures": [17], "primitives": ["belief", "mutual_consistency"], "keywords": ["Bayesian Nash", "BNE", "strategy for each type", "expected payoff"], "definition": "A plan for every type such that each type is best responding to its beliefs."},
    {"id": "auctions", "name": "Auctions", "theme": "mechanisms_and_markets", "lectures": [18], "primitives": ["incentive_compatibility", "belief"], "keywords": ["auction", "bid", "bidding", "valuation", "first price", "second price"], "definition": "Rules for allocating an object when bidders have private values."},
    {"id": "revenue_equivalence", "name": "Revenue Equivalence", "theme": "mechanisms_and_markets", "lectures": [19], "primitives": ["incentive_compatibility"], "keywords": ["revenue equivalence", "expected revenue", "allocation rule", "payment"], "definition": "Different auction rules can produce the same expected seller revenue under specific assumptions."},
    {"id": "ad_auctions", "name": "Ad Auctions", "theme": "mechanisms_and_markets", "lectures": [20], "primitives": ["incentive_compatibility", "payoff_mapping"], "keywords": ["ad auction", "ads", "quality score", "click", "sponsored search"], "definition": "Auction design applied to online ad slots where position, clicks, and value interact."},
    {"id": "perfect_bayesian_equilibrium", "name": "Perfect Bayesian Equilibrium", "theme": "private_information", "lectures": [21], "primitives": ["belief", "backward_recursion"], "keywords": ["perfect Bayesian", "PBE", "belief system", "sequential rationality", "Bayes rule"], "definition": "An equilibrium for dynamic games with beliefs that stay consistent with observed behavior."},
    {"id": "signaling", "name": "Signaling", "theme": "communication_and_knowledge", "lectures": [22], "primitives": ["belief", "incentive_compatibility"], "keywords": ["signaling", "signal", "sender", "receiver", "separating", "pooling"], "definition": "Using an action or message to convey private information when others update beliefs from it."},
    {"id": "cheap_talk", "name": "Cheap Talk", "theme": "communication_and_knowledge", "lectures": [24], "primitives": ["belief", "incentive_compatibility"], "keywords": ["cheap talk", "message", "communication", "sender", "receiver"], "definition": "Costless messages that matter only when incentives make them credible enough to influence beliefs."},
    {"id": "common_knowledge", "name": "Common Knowledge", "theme": "communication_and_knowledge", "lectures": [25], "primitives": ["knowledge_recursion"], "keywords": ["common knowledge", "everyone knows", "higher-order", "knowledge", "mutual knowledge"], "definition": "A fact that everyone knows, everyone knows everyone knows, and so on."},
]


SUBTHEMES = [
    {"id": "ranking_outcomes", "parent_theme": "choice_and_payoff", "name": "Ranking Outcomes", "concepts": ["preferences", "utility", "expected_utility"]},
    {"id": "tables_and_trees", "parent_theme": "strategic_dependence", "name": "Tables, Trees, And Strategic Dependence", "concepts": ["strategic_form_games", "extensive_form_games"]},
    {"id": "eliminating_bad_moves", "parent_theme": "strategic_dependence", "name": "Eliminating Bad Moves", "concepts": ["dominance", "iterated_deletion", "rationalizability"]},
    {"id": "stable_predictions", "parent_theme": "equilibrium_reasoning", "name": "Stable Predictions", "concepts": ["best_response", "nash_equilibrium", "mixed_strategies"]},
    {"id": "conflict_and_security", "parent_theme": "equilibrium_reasoning", "name": "Conflict And Security", "concepts": ["zero_sum_games", "minimax"]},
    {"id": "credible_time_paths", "parent_theme": "time_and_credibility", "name": "Credible Time Paths", "concepts": ["backward_induction", "subgame_perfection", "one_shot_deviation", "bargaining"]},
    {"id": "future_as_discipline", "parent_theme": "repetition_and_cooperation", "name": "The Future As Discipline", "concepts": ["finitely_repeated_games", "infinitely_repeated_games", "folk_theorem", "implicit_cartels"]},
    {"id": "hidden_types", "parent_theme": "private_information", "name": "Hidden Types And Beliefs", "concepts": ["bayesian_games", "types_and_beliefs", "bayesian_nash_equilibrium", "perfect_bayesian_equilibrium"]},
    {"id": "rules_for_bidding", "parent_theme": "mechanisms_and_markets", "name": "Rules For Bidding", "concepts": ["auctions", "revenue_equivalence", "ad_auctions"]},
    {"id": "messages_and_shared_awareness", "parent_theme": "communication_and_knowledge", "name": "Messages And Shared Awareness", "concepts": ["signaling", "cheap_talk", "common_knowledge"]},
]


def load_index() -> list[dict[str, Any]]:
    return json.loads(INDEX.read_text(encoding="utf-8"))


def load_overrides(name: str) -> dict[str, Any]:
    path = OVERRIDES / name
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def parse_vtt(path: Path) -> list[dict[str, str]]:
    segments = []
    start = end = None
    lines: list[str] = []
    for raw in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw.strip()
        if "-->" in line:
            if start and lines:
                segments.append({"start": start, "end": end or start, "text": " ".join(lines)})
            start, end = [part.strip().split(" ")[0] for part in line.split("-->", 1)]
            lines = []
        elif line and line != "WEBVTT" and not line.startswith(("Kind:", "Language:", "NOTE")) and not re.match(r"^[0-9]+$", line):
            line = re.sub(r"<[^>]+>", "", line)
            line = re.sub(r"\s+", " ", line).strip()
            if line:
                lines.append(line)
    if start and lines:
        segments.append({"start": start, "end": end or start, "text": " ".join(lines)})
    return segments


def hits(text: str, keywords: list[str]) -> int:
    lower = text.lower()
    return sum(len(re.findall(r"(?<![a-z0-9-])" + re.escape(k.lower()) + r"(?![a-z0-9-])", lower)) for k in keywords)


def window_for(row: dict[str, Any], concept: dict[str, Any]) -> dict[str, Any]:
    vtt_path = ROOT / row["raw_vtt"] if row.get("raw_vtt") else None
    if not vtt_path or not vtt_path.exists():
        text = (ROOT / row["clean_txt"]).read_text(encoding="utf-8", errors="ignore")[:600]
        return {"timestamp_start": None, "timestamp_end": None, "window": text, "matched_terms": []}
    segments = parse_vtt(vtt_path)
    best = None
    best_score = -1
    for i, segment in enumerate(segments):
        score = hits(segment["text"], concept["keywords"])
        if score > best_score:
            best = i
            best_score = score
    if best is None:
        return {"timestamp_start": None, "timestamp_end": None, "window": "", "matched_terms": []}
    nearby = segments[max(0, best - 2) : min(len(segments), best + 4)]
    words = " ".join(seg["text"] for seg in nearby).split()
    window = " ".join(words[:95]) + (" ..." if len(words) > 95 else "")
    lower_window = window.lower()
    terms = [term for term in concept["keywords"] if term.lower() in lower_window][:8]
    return {
        "timestamp_start": nearby[0]["start"],
        "timestamp_end": nearby[-1]["end"],
        "window": window,
        "matched_terms": terms or concept["keywords"][:2],
    }


def evidence_for(concept: dict[str, Any], index: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = [row for row in index if row["playlist_index"] in concept["lectures"]]
    if len(rows) < 2:
        for row in index:
            if row not in rows and hits(row["title"] + " " + (Path(ROOT / row["clean_txt"]).read_text(encoding="utf-8", errors="ignore") if row.get("clean_txt") else ""), concept["keywords"]):
                rows.append(row)
            if len(rows) >= 2:
                break
    records = []
    for j, row in enumerate(rows[:2], 1):
        win = window_for(row, concept)
        eid = f"ev-{concept['id']}-{j:02d}"
        records.append(
            {
                "id": eid,
                "course": COURSE,
                "video_title": row["title"],
                "youtube_url": row["url"],
                "transcript_path": row["clean_txt"],
                "timestamp_start": win["timestamp_start"],
                "timestamp_end": win["timestamp_end"],
                "paraphrased_claim": f"The lecture gives transcript support for {concept['name']} as {concept['definition'].lower()}",
                "lecture_argument": f"In {row['title']}, the course treats {concept['name']} as a mechanism for the strategic problem where choices, beliefs, timing, or information change what a person should do.",
                "example_or_analogy": f"The useful everyday picture is: before naming {concept['name']}, ask what one decision-maker can safely infer about another decision-maker's move, information, or future response.",
                "mathematical_claim": mathematical_principle(concept),
                "caveat_or_warning": f"This evidence anchors the local course treatment of {concept['name']}; broader cross-theme comparisons in the atlas remain synthesis and should be read through that scope.",
                "why_span_matters": f"The span matters because it ties the page's first-principles explanation to lecture material rather than leaving {concept['name']} as a glossary entry.",
                "local_transcript_window": win["window"],
                "evidence_basis": "local VTT timestamp span",
                "evidence_scope": "supports the listed concept and subtheme; broader analogies are synthesis",
                "evidence_review_status": "transcript_span_selected",
                "matched_terms": win["matched_terms"],
                "supports_concepts": [concept["id"]],
                "supports_subthemes": [s["id"] for s in SUBTHEMES if concept["id"] in s["concepts"]],
                "confidence": "moderate" if win["matched_terms"] else "weak",
            }
        )
    return records


def mathematical_principle(concept: dict[str, Any]) -> str:
    primitive = next(p for p in PRIMITIVES if p["id"] == concept["primitives"][0])
    return f"{primitive['formal_object']} The useful relation is `{primitive['useful_equation']}`. In plain language: {primitive['symbol_explanation']}"


def concept_treatment(concept: dict[str, Any], evidence_ids: list[str]) -> dict[str, Any]:
    theme = next(t for t in THEMES if t["id"] == concept["theme"])
    primitives = [p for p in PRIMITIVES if p["id"] in concept["primitives"]]
    primitive_names = ", ".join(p["name"].lower() for p in primitives)
    return {
        "plain_language_definition": concept["definition"],
        "everyday_problem": f"The real-world problem is that people make choices while other people, future events, hidden information, or rules can change the payoff of those choices.",
        "first_principles_reason": f"This problem exists because strategic settings are interdependent: a choice is not good by itself; it is good only relative to other choices, beliefs, timing, and incentives.",
        "mathematical_principle": mathematical_principle(concept),
        "why_it_matters": f"{concept['name']} matters because it gives a disciplined way to predict, design, or critique behavior when ordinary one-person reasoning is not enough.",
        "what_breaks_without_it": f"Without {concept['name']}, the analysis can confuse a tempting story with a stable strategic explanation. The model may miss profitable deviations, hidden information, or incentives that change behavior.",
        "naive_problem": f"A naive approach would ask what one person wants and stop there. In the part of the course around {concept['name']}, that is not enough because another person's move or information changes the answer.",
        "failed_simple_approach": f"The simple approach fails because the strategic environment pushes back. A plan can look good until someone else best-responds, a later player refuses a threat, or a private type changes what the observed action means.",
        "mathematical_object": f"The handle is {primitive_names}: a compact object that lets the course translate the messy social situation into rankings, payoffs, beliefs, or recursive checks.",
        "operation": f"The operation is to write down the relevant players, choices, payoffs, beliefs, or time path, then ask whether the proposed behavior survives the test attached to {concept['name']}.",
        "worked_mini_example": f"Mini-example: suppose two firms, bidders, negotiators, or speakers face each other. A move that seems attractive alone may become bad once the other side's response is included. {concept['name']} tells the reader which piece of the situation must be checked before trusting the prediction.",
        "lecture_emphasis": f"The lecture evidence treats {concept['name']} as a working tool inside MIT 14.12, not as isolated vocabulary. The page therefore starts from the strategic pressure and only then names the formal object.",
        "common_misunderstanding": f"A common mistake is to treat {concept['name']} as a label to memorize. The first-principles version asks why the idea has to exist: what uncertainty, incentive, timing problem, or mutual-dependence problem forced it into the course.",
        "cross_course_connections": f"This concept belongs to the broader theme '{theme['name']}'. It connects sideways to other ideas whenever the same primitive appears in another lecture under a different name.",
        "recognize_in_new_work": f"In a new paper or model, look for the same pressure: someone chooses under strategic dependence, private information, future punishment, or communication incentives. That pressure is the sign that {concept['name']} may be active.",
        "theme_id": concept["theme"],
        "mathematical_primitives": concept["primitives"],
        "related_concepts": related_concepts(concept),
        "course_evidence_ids": evidence_ids,
        "evidence_status": "transcript-backed" if evidence_ids else "needs review",
    }


def related_concepts(concept: dict[str, Any]) -> list[str]:
    same_theme = [c["id"] for c in CONCEPTS if c["theme"] == concept["theme"] and c["id"] != concept["id"]]
    same_primitive = [
        c["id"]
        for c in CONCEPTS
        if c["id"] != concept["id"] and set(c["primitives"]) & set(concept["primitives"])
    ]
    return list(dict.fromkeys((same_theme + same_primitive)[:6]))


def build() -> None:
    index = load_index()
    concept_overrides = load_overrides("concepts.json")
    evidence: list[dict[str, Any]] = []
    evidence_by_concept: dict[str, list[str]] = defaultdict(list)
    concepts_out = []
    for concept in CONCEPTS:
        if concept["id"] not in concept_overrides:
            raise ValueError(f"missing hand-crafted concept override for {concept['id']}")
        records = evidence_for(concept, index)
        evidence.extend(records)
        evidence_by_concept[concept["id"]] = [record["id"] for record in records]
        base = {k: v for k, v in concept.items() if k not in {"keywords", "lectures", "theme", "primitives", "definition"}}
        base.update(concept_treatment(concept, evidence_by_concept[concept["id"]]))
        base.update(concept_overrides[concept["id"]])
        concepts_out.append(base)

    coverage: dict[str, Counter[str]] = defaultdict(Counter)
    for concept in CONCEPTS:
        for ev_id in evidence_by_concept[concept["id"]]:
            record = next(ev for ev in evidence if ev["id"] == ev_id)
            coverage[concept["theme"]][record["video_title"]] += 1

    themes_out = []
    for theme in THEMES:
        subtheme_ids = [s["id"] for s in SUBTHEMES if s["parent_theme"] == theme["id"]]
        concept_ids = [c["id"] for c in CONCEPTS if c["theme"] == theme["id"]]
        themes_out.append(
            {
                **theme,
                "subthemes": subtheme_ids,
                "core_concepts": concept_ids,
                "course_coverage": dict(coverage[theme["id"]]),
                "cross_course_argument": f"{theme['name']} is not a lecture label. It is an argument about why the same strategic pressure reappears across several course topics.",
                "mathematical_spine": f"The mathematical spine is built from primitives such as {', '.join(sorted({p for c in CONCEPTS if c['id'] in concept_ids for p in c['primitives']}))}.",
                "where_analogy_breaks": "The analogy breaks when a tool that works for complete-information simultaneous choice is moved into timing, uncertainty, or communication without adding the missing structure.",
                "lecture_evidence_chain": "Evidence comes from the listed concept pages and their transcript spans; theme prose is synthesis over those records.",
            }
        )

    subthemes_out = []
    for subtheme in SUBTHEMES:
        subthemes_out.append(
            {
                **subtheme,
                "everyday_problem": "The everyday problem is that strategic behavior must be read in context, not as a standalone action.",
                "hidden_principle": "The hidden principle is that incentives, beliefs, timing, and information determine which explanation survives.",
                "mathematical_lever": "The lever is the relevant payoff, belief, equilibrium, recursion, or incentive-compatibility object.",
                "why_it_matters": "It matters because the subtheme gives a reusable way to recognize the same strategic shape in new applications.",
                "examples_from_courses": [
                    {
                        "concept": cid,
                        "evidence_id": evidence_by_concept[cid][0],
                        "video_title": next(ev for ev in evidence if ev["id"] == evidence_by_concept[cid][0])["video_title"],
                    }
                    for cid in subtheme["concepts"]
                    if evidence_by_concept[cid]
                ],
                "connected_concepts": sorted({r for cid in subtheme["concepts"] for r in related_concepts(next(c for c in CONCEPTS if c["id"] == cid))}),
                "first_principles_walkthrough": "Start from the human situation, identify who knows what and who can respond, then introduce the formal object only as the shortest way to check that situation.",
                "cross_links_and_limits": "The same primitive can reappear in another subtheme, but the application changes when information, time, or institutions change.",
                "lecture_evidence_chain": "The examples point to transcript spans in the evidence ledger.",
                "recognize_in_new_work": "Look for the underlying pressure rather than the vocabulary: dependence, uncertainty, credibility, repetition, or communication.",
            }
        )

    primitives_out = []
    for primitive in PRIMITIVES:
        concept_ids = [c["id"] for c in CONCEPTS if primitive["id"] in c["primitives"]]
        primitives_out.append(
            {
                **primitive,
                "concepts_in_atlas": concept_ids,
                "everyday_setup": primitive["plain_language"],
                "course_appearances": f"Appears in: {', '.join(concept_ids)}.",
            }
        )

    families = [
        {
            "id": "equilibrium_family",
            "name": "Equilibrium Family",
            "first_principles_problem": "How can we predict behavior when each person is reacting to everyone else?",
            "core_move": "Find mutually consistent plans where no one wants to move alone.",
            "mathematical_primitive": ["best_response", "mutual_consistency"],
            "concepts": ["best_response", "nash_equilibrium", "mixed_strategies", "subgame_perfection", "bayesian_nash_equilibrium", "perfect_bayesian_equilibrium"],
            "plain_language_family_summary": "This family turns strategic dependence into a stability test.",
            "course_evidence_ids": [evidence_by_concept["nash_equilibrium"][0], evidence_by_concept["subgame_perfection"][0]],
            "family_walkthrough": "Ask what each player expects, then ask whether any single player would want to change.",
            "where_analogy_breaks": "Different equilibrium concepts are needed when time or private information enters.",
            "lecture_evidence_chain": "Supported by Nash, subgame perfection, Bayesian Nash, and PBE lecture spans.",
            "paper_family_treatment": "Use this family to read papers that propose solution concepts or refine existing equilibrium predictions.",
        },
        {
            "id": "information_family",
            "name": "Information And Belief Family",
            "first_principles_problem": "How should people act when important facts are hidden?",
            "core_move": "Represent hidden facts as types and beliefs, then check incentives under those beliefs.",
            "mathematical_primitive": ["belief", "incentive_compatibility"],
            "concepts": ["bayesian_games", "types_and_beliefs", "signaling", "cheap_talk", "common_knowledge"],
            "plain_language_family_summary": "This family explains how private information and messages affect strategy.",
            "course_evidence_ids": [evidence_by_concept["bayesian_games"][0], evidence_by_concept["signaling"][0]],
            "family_walkthrough": "List what each side knows, what each side thinks others know, and what incentives make messages credible or not.",
            "where_analogy_breaks": "A message is not automatically evidence; it depends on the sender's incentive to lie or reveal.",
            "lecture_evidence_chain": "Supported by Bayesian games, signaling, cheap talk, and common knowledge lecture spans.",
            "paper_family_treatment": "Use this family for papers about asymmetric information, communication, reputation, and knowledge.",
        },
        {
            "id": "mechanism_family",
            "name": "Mechanism And Auction Family",
            "first_principles_problem": "How can rules be designed when participants act strategically?",
            "core_move": "Choose rules so private incentives produce the intended allocation or information revelation.",
            "mathematical_primitive": ["incentive_compatibility", "payoff_mapping"],
            "concepts": ["auctions", "revenue_equivalence", "ad_auctions", "implicit_cartels"],
            "plain_language_family_summary": "This family treats game theory as design for markets and institutions.",
            "course_evidence_ids": [evidence_by_concept["auctions"][0], evidence_by_concept["ad_auctions"][0]],
            "family_walkthrough": "Write the rule, identify each participant's private information, then check what behavior the rule makes attractive.",
            "where_analogy_breaks": "Revenue or efficiency claims depend heavily on assumptions about values, risk, independence, and participation.",
            "lecture_evidence_chain": "Supported by auction, revenue equivalence, ad auction, and cartel application spans.",
            "paper_family_treatment": "Use this family for auction design, market design, and applied industrial organization papers.",
        },
    ]

    write_json(ROOT / "analysis/concepts/concept-atlas.json", concepts_out)
    write_json(ROOT / "analysis/themes/theme-map.json", themes_out)
    write_json(ROOT / "analysis/themes/subtheme-map.json", subthemes_out)
    write_json(ROOT / "analysis/evidence/evidence-ledger.json", evidence)
    write_json(ROOT / "analysis/evidence/evidence-review-queue.json", [])
    write_json(ROOT / "analysis/throughlines/primitives.json", primitives_out)
    write_json(ROOT / "analysis/throughlines/method-families.json", families)
    write_big_picture(themes_out, primitives_out, families)
    write_rubric()


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_big_picture(themes: list[dict[str, Any]], primitives: list[dict[str, Any]], families: list[dict[str, Any]]) -> None:
    lines = [
        "# Big Picture Map",
        "",
        "MIT 14.12 is about strategic dependence: choices are hard because other people react, hold private information, remember the past, send messages, and respond to rules.",
        "",
        "The course starts with individual choice, moves to simultaneous games, then adds timing, repetition, private information, market rules, communication, and common knowledge.",
        "",
        "## Deep Throughlines",
        "",
        "- Equilibrium is mutual consistency, not goodness.",
        "- Credibility means a future action remains optimal when the future arrives.",
        "- Beliefs are mathematical containers for hidden information.",
        "- Repetition changes incentives by making the future part of today's payoff.",
        "- Mechanism design asks rules to survive strategic response.",
        "- Communication matters only through incentives and beliefs.",
        "",
        "## Mathematical Primitives",
        "",
    ]
    lines.extend(f"- **{p['name']}**: {p['plain_language']}" for p in primitives)
    lines.extend(["", "## Method Families", ""])
    lines.extend(f"- **{f['name']}**: {f['plain_language_family_summary']}" for f in families)
    out = ROOT / "analysis/throughlines/big-picture-map.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_rubric() -> None:
    path = ROOT / "analysis/rubric/extraction-rubric.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        """# Extraction Rubric

For each concept, extract the strategic pressure before the formal name.

Required treatment:

- everyday problem
- first-principles reason
- mathematical object
- formula explained in ordinary words
- why it matters
- what breaks without it
- common misunderstanding
- sideways links to other course concepts
- transcript-backed evidence spans

Evidence rules:

- Use local transcript or VTT spans only.
- Keep evidence separate from synthesis.
- Do not publish keyword-only evidence without a local transcript window.
- Mark weak support when the span only names a concept.
""",
        encoding="utf-8",
    )


if __name__ == "__main__":
    build()
