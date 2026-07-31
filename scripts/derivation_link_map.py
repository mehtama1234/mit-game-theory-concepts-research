from __future__ import annotations

from typing import Any

DERIVATIONS_BY_CONCEPT = {
    "expected_utility": ["expected_utility"],
    "best_response": ["best_response"],
    "dominance": ["dominance_inequality"],
    "iterated_deletion": ["dominance_inequality"],
    "nash_equilibrium": ["nash_equilibrium", "best_response"],
    "mixed_strategies": ["nash_equilibrium", "expected_utility"],
    "backward_induction": ["backward_induction"],
    "subgame_perfection": ["backward_induction", "nash_equilibrium"],
    "one_shot_deviation": ["backward_induction"],
    "finitely_repeated_games": ["backward_induction"],
    "infinitely_repeated_games": ["discounted_sum"],
    "folk_theorem": ["discounted_sum", "nash_equilibrium"],
    "implicit_cartels": ["discounted_sum"],
    "bayesian_games": ["expected_utility", "bayes_rule"],
    "types_and_beliefs": ["bayes_rule", "expected_utility"],
    "bayesian_nash_equilibrium": ["expected_utility", "best_response"],
    "screening_and_adverse_selection": ["bayes_rule", "expected_utility"],
    "auctions": ["auction_expected_payment", "expected_utility"],
    "revenue_equivalence": ["auction_expected_payment"],
    "ad_auctions": ["auction_expected_payment"],
    "perfect_bayesian_equilibrium": ["bayes_rule", "backward_induction"],
    "signaling": ["bayes_rule"],
    "cheap_talk": ["bayes_rule"],
    "common_knowledge": ["common_knowledge_recursion"],
    "imperfect_competition": ["best_response"],
    "minimax": ["best_response"],
    "zero_sum_games": ["nash_equilibrium", "best_response"],
}


def expected_derivation_ids_for_concept(
    concept: dict[str, Any],
    derivations: dict[str, dict[str, Any]] | list[dict[str, Any]],
    limit: int = 3,
) -> list[str]:
    deriv_by_id = derivations if isinstance(derivations, dict) else {derivation["id"]: derivation for derivation in derivations}
    mapped = DERIVATIONS_BY_CONCEPT.get(concept["id"], [])
    fallback = [
        derivation_id
        for derivation_id, derivation in deriv_by_id.items()
        if derivation["primitive_id"] in concept.get("mathematical_primitives", [])
    ]
    return list(dict.fromkeys(mapped + fallback))[:limit]


def expected_derivation_ids_for_lecture(
    concepts: list[dict[str, Any]],
    derivations: dict[str, dict[str, Any]] | list[dict[str, Any]],
    limit: int = 5,
) -> list[str]:
    ids: list[str] = []
    for concept in concepts:
        ids.extend(expected_derivation_ids_for_concept(concept, derivations))
    return list(dict.fromkeys(ids))[:limit]
