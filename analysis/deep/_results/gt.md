# Game theory — verified measured results (small programs that solve games)

Every number below is computed by a short program we ran. Script: scripts/experiments/gametheory_run.py.
Cite numbers verbatim; do NOT invent new ones.

## EXP1 — Prisoner's Dilemma & dominance (concepts: dominance)
- Payoffs (your reward for the Row you pick against the other's Column): Cooperate vs (Coop, Defect) =
  3, 0; Defect vs (Coop, Defect) = 5, 1.
- Best reply if the other Cooperates: Defect (5 > 3). Best reply if the other Defects: Defect (1 > 0).
- So Defect is best NO MATTER what the other does — a "dominant" strategy. Both defect and each gets
  **1**, worse than the **3** each would get by cooperating.
- Insight: a strategy that beats your alternatives in every situation is dominant; rational players
  play it — even when everyone would be better off doing something else. The dilemma is real.

## EXP2 — Nash equilibrium & best response (concepts: nash_equilibrium, best_response)
- A coordination game (both want to match, but prefer different options). Checking every cell for
  mutual best response finds **two** pure Nash equilibria: both pick Option-X, or both pick Option-Y.
- Insight: a Nash equilibrium is a combination where no one can gain by changing their choice alone —
  a mutual best response. A game can have several (or, as below, none in pure strategies).

## EXP3 — mixed strategies (concept: mixed_strategies)
- Matching pennies (one wants to match, the other to mismatch) has **NO** pure-strategy Nash
  equilibrium. Its only equilibrium is in mixed strategies: each player randomizes **50/50**.
- If a player deviates to Heads 70% of the time, the opponent can exploit the pattern and the
  deviator's expected payoff falls; 50/50 is the unique unexploitable mix.
- Insight: when any predictable choice can be exploited, the equilibrium is to be deliberately random.
  Mixed strategies guarantee an equilibrium exists in every finite game (Nash's theorem).

## EXP4 — iterated deletion of dominated strategies (concepts: iterated_deletion, rationalizability)
- A 3x3 game. Removing any strategy a player would never use (strictly dominated): row 2 is dominated
  by row 0, then column 2 is dominated by column 0. Survivors: rows {0,1} and columns {0,1}.
- Insight: you can shrink a game by repeatedly deleting strategies no rational player would ever pick,
  because a rational opponent knows you won't pick them either. What survives is "rationalizable".

## EXP5 — zero-sum games & minimax (concepts: zero_sum_games, minimax)
- A 2x2 zero-sum game (one player wins exactly what the other loses). Solved: the optimal mix is to
  play the top row **50%** of the time, and the game's **value is 0.50** — what the first player can
  guarantee and the second can hold them to.
- Insight: in a strictly competitive game there is a single number, the value, that both sides can lock
  in by mixing — "maximin equals minimax" (von Neumann's theorem), the bedrock of adversarial play.

## EXP6 — infinitely repeated games & the folk theorem (concepts: infinitely_repeated_games, folk_theorem)
- One-shot Prisoner's Dilemma payoffs: Temptation 5, Reward 3, Punishment 1, Sucker 0. With a
  grim-trigger strategy, always-cooperate is a Nash equilibrium of the REPEATED game if and only if
  the discount factor (how much the future matters) is at least **0.50**.
- Computed: at discount 0.3 cooperation breaks (defect now); at 0.5 and 0.7 it holds.
- Evolutionary check (why reciprocity, not blind niceness, wins): in a population of Tit-for-Tat, a
  native scores **2.81** per round while an invading Defector scores only **1.16** — defectors CANNOT
  invade, so Tit-for-Tat is evolutionarily stable. In a population of naive All-Cooperate, a native
  scores 3.02 but an invading Defector scores **4.86** — defectors DO invade.
- Insight: a one-shot dilemma flips when the game repeats and players value the future — cooperation
  becomes self-enforcing (the folk theorem), and reciprocation that punishes cheats is what survives.

## EXP7 — imperfect competition / Cournot (concept: imperfect_competition)
- Two firms choose output; the market price falls as total output rises. Best-reply iteration
  converges to each firm producing **4.0** units (the Cournot-Nash equilibrium). For comparison, a
  single monopoly would make **6.0** total, and full competition would make **12.0** total.
- Insight: self-interested rivals produce more than a cartel (competing away some profit) but less
  than full competition — a middle outcome that no firm chooses on purpose, it just falls out of
  everyone best-responding.

## EXP8 — backward induction & credible threats (concepts: backward_induction, subgame_perfection)
- An entry game: an entrant chooses In or Out; if In, the incumbent chooses Fight or Accommodate.
  Solving backward: if entry happens, the incumbent accommodates (payoff 2 > −1 from fighting), so the
  entrant, foreseeing that, enters (2 > 0 from staying out). Outcome: **In, Accommodate (2, 2)**.
- Insight: "I'll fight any entry!" is a Nash threat but not CREDIBLE — once entry has happened,
  fighting hurts the incumbent too. Backward induction (subgame perfection) throws out threats a player
  wouldn't actually carry out.

## EXP9 — auctions & revenue equivalence (concepts: auctions, revenue_equivalence)
- Four bidders with private values uniform on [0,1]. Expected revenue to the seller, simulated:
  a second-price auction (bid your true value, pay the runner-up's price) yields **0.600**; a
  first-price auction (shade your bid, pay your bid) yields **0.600** — the same.
- Insight: the two formats work completely differently — one rewards honesty, the other rewards
  strategic shading — yet they raise the SAME expected revenue. That's the Revenue Equivalence Theorem,
  a cornerstone of auction design.
