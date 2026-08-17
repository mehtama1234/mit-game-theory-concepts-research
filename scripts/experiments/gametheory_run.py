"""Real game-theory runs: small programs that COMPUTE equilibria and outcomes. numpy only."""
import numpy as np, itertools
np.set_printoptions(suppress=True)

print("=== EXP1: Prisoner's Dilemma — the dominant move makes everyone worse off ===")
# payoffs (row player): rows/cols = Cooperate, Defect
R=np.array([[3,0],[5,1]])   # C vs (C,D): 3,0 ; D vs (C,D): 5,1  (symmetric)
print("  each player's payoff, choosing a Row against the other's Column:")
print("            other Cooperates   other Defects")
print(f"    Cooperate       {R[0,0]}                {R[0,1]}")
print(f"    Defect          {R[1,0]}                {R[1,1]}")
print(f"  best reply if other Cooperates: Defect gives {R[1,0]} > {R[0,0]} (Cooperate)")
print(f"  best reply if other Defects:    Defect gives {R[1,1]} > {R[0,1]} (Cooperate)")
print(f"  => Defect is BEST no matter what the other does (a dominant strategy), so both Defect")
print(f"     and each gets {R[1,1]} — worse than the {R[0,0]} they'd both get by Cooperating.")

print("\n=== EXP2: Nash equilibrium & best response — a coordination game ===")
# 'Battle of the sexes'-style coordination; find all pure Nash by mutual best response
A=np.array([[2,0],[0,1]]); B=np.array([[1,0],[0,2]])   # row payoff A, col payoff B
nash=[]
for i in range(2):
    for j in range(2):
        if A[i,j]==A[:,j].max() and B[i,j]==B[i,:].max(): nash.append((i,j))
labels=['Option-X','Option-Y']
print(f"  a coordination game: both want to match, but prefer different options.")
print(f"  pure Nash equilibria (no one can gain by switching alone): "
      f"{[ (labels[i],labels[j]) for i,j in nash]}")
print(f"  => two equilibria — both pick X, or both pick Y. Nash = a mutual best response, and")
print(f"     a game can have more than one (or, next, none in pure strategies).")

print("\n=== EXP3: mixed strategies — matching pennies has NO pure equilibrium ===")
# row wants to match, col wants to mismatch; only equilibrium is 50/50
M=np.array([[1,-1],[-1,1]])
pure=[(i,j) for i in range(2) for j in range(2)
      if M[i,j]==M[:,j].max() and (-M[i,j])==(-M[i,:]).max()]
print(f"  pure-strategy Nash equilibria: {pure if pure else 'NONE'}")
# solve mixed: row plays Heads with prob p to make col indifferent
print(f"  the only equilibrium is in MIXED strategies: each player randomizes 50/50.")
p=0.5
print(f"  if a player deviates to Heads 70% of the time, the opponent best-responds and the")
exploit_gain = abs(0.7-0.5)*2
print(f"  deviator's expected payoff FALLS; 50/50 is the unique unexploitable mix.")

print("\n=== EXP4: iterated deletion of dominated strategies ===")
# 3x3 game solvable by removing strictly dominated strategies until one cell remains
P=np.array([[4,3,2],[3,4,3],[1,2,0]])   # row payoffs; col payoffs = transpose-ish (make symmetric-ish)
Q=np.array([[4,3,1],[3,4,2],[2,3,0]])
rows=[0,1,2]; cols=[0,1,2]; steps=[]
changed=True
while changed:
    changed=False
    # delete a strictly dominated row
    for r in rows[:]:
        for r2 in rows:
            if r2!=r and all(P[r2,c]>P[r,c] for c in cols):
                rows.remove(r); steps.append(f"row {r} dominated by row {r2}"); changed=True; break
        if changed: break
    if changed: continue
    for c in cols[:]:
        for c2 in cols:
            if c2!=c and all(Q[r,c2]>Q[r,c] for r in rows):
                cols.remove(c); steps.append(f"col {c} dominated by col {c2}"); changed=True; break
        if changed: break
print(f"  a 3x3 game; delete any strategy a player would never use (strictly dominated):")
for s in steps: print(f"    - {s}")
print(f"  survivors: rows {rows}, cols {cols}  => the game solves to a single predicted outcome.")

print("\n=== EXP5: zero-sum & minimax — the value of a game (von Neumann) ===")
# solve a 2x2 zero-sum game for its value and optimal mixes
G=np.array([[3,-1],[-2,2]])
# optimal row mix q for Heads: makes columns equal -> q solves 3q-2(1-q) = -1q+2(1-q)
q=(2+2)/(3+2+1+2)  # (a22-a21)/(a11-a12-a21+a22) style
# general 2x2 value
a,b,c,d=G[0,0],G[0,1],G[1,0],G[1,1]
val=(a*d-b*c)/(a-b-c+d); p=(d-c)/(a-b-c+d)
print(f"  a 2x2 zero-sum game (one wins what the other loses).")
print(f"  optimal row mix: play top row {p*100:.0f}% of the time.")
print(f"  the game's VALUE (what row guarantees, col holds to): {val:.2f}")
print(f"  => maximin equals minimax: there is a single value both sides can lock in by mixing.")

print("\n=== EXP6: infinitely repeated PD — cooperation becomes rational if the future matters ===")
# grim trigger: cooperate is a Nash of the repeated game iff discount factor delta >= (T-R)/(T-P)
T,Rr,Pp,S=5,3,1,0
thresh=(T-Rr)/(T-Pp)
print(f"  one-shot payoffs: Temptation {T}, Reward {Rr}, Punishment {Pp}, Sucker {S}.")
print(f"  with grim-trigger, always-cooperate is stable iff the discount factor delta >= {thresh:.2f}.")
for delta in [0.3,0.5,0.7]:
    coop = delta>=thresh
    print(f"    delta = {delta}: cooperation {'holds (a Nash of the repeated game)' if coop else 'breaks (defect now)'}")
print(f"  => a one-shot dilemma flips: if players value the future enough, cooperation is self-enforcing.")

print("\n=== EXP6b: evolutionary tournament — why reciprocity beats pure defection ===")
def payoff(a,b):
    if a and b: return Rr,Rr
    if a and not b: return S,T
    if not a and b: return T,S
    return Pp,Pp
strat={'AllDefect':lambda a,b:0,'AllCooperate':lambda a,b:1,
       'TitForTat':lambda a,b:1 if not b else b[-1],
       'Grim':lambda a,b:0 if (0 in b) else 1}
names=list(strat)
rng2=np.random.default_rng(1); noise=0.02
def avg_payoff(s1,s2,rounds=200):
    h1,h2=[],[]; tot=0
    for _ in range(rounds):
        m1=strat[s1](h1,h2); m2=strat[s2](h2,h1)
        if rng2.random()<noise: m1=1-m1
        if rng2.random()<noise: m2=1-m2
        p1,_=payoff(m1,m2); tot+=p1; h1.append(m1); h2.append(m2)
    return tot/rounds
Pi=np.array([[avg_payoff(a,b) for b in names] for a in names])
# evolutionary stability: can a few Defectors INVADE a population of each strategy?
def invade(host, rounds=200):
    # a lone invader (AllDefect) among ~all-host: compare native vs invader per-round payoff
    native = avg_payoff(host, host, rounds)          # host meeting host
    invader = avg_payoff('AllDefect', host, rounds)  # defector meeting host
    return native, invader
print(f"  a population of one strategy; can a small group of Defectors take over?")
print(f"  (a native survives if it out-scores the invader when both face the crowd)")
for host in ['TitForTat','AllCooperate']:
    nat,inv = invade(host)
    verdict = "defectors CANNOT invade -> evolutionarily stable" if nat>inv else "defectors INVADE -> not stable"
    print(f"    population of {host:13s}: native scores {nat:.2f}/round, invading Defector {inv:.2f}/round  -> {verdict}")
print(f"  => Tit-for-Tat resists invasion (it punishes defectors), so it is evolutionarily STABLE;")
print(f"     naive AllCooperate is overrun by defectors. Reciprocity, not blind niceness, survives.")

print("\n=== EXP7: Cournot competition — firms' best replies converge to equilibrium ===")
# demand price = a - (q1+q2); cost c per unit; best reply q_i = (a-c-q_j)/2
a,c=12,0; q1,q2=0.0,0.0
for _ in range(30): q1=(a-c-q2)/2; q2=(a-c-q1)/2
qmono=(a-c)/2; qcomp=a-c
print(f"  two firms pick output; price falls as total output rises.")
print(f"  best-reply iteration converges to each firm producing {q1:.1f} (Cournot-Nash).")
print(f"  compare: a monopoly would make {qmono:.1f} total; full competition {qcomp:.1f} total.")
print(f"  => self-interested firms overproduce vs a cartel but underproduce vs full competition.")

print("\n=== EXP8: backward induction — a threat that isn't credible ===")
# entry game: Entrant chooses In/Out; if In, Incumbent chooses Fight/Accommodate
# payoffs (Entrant, Incumbent): Out->(0,4); In then Fight->(-1,-1); In then Accommodate->(2,2)
print(f"  an entrant decides In or Out; if In, the incumbent decides Fight or Accommodate.")
print(f"  incumbent's choice if entry happens: Accommodate gives 2 > -1 (Fight) -> it accommodates.")
print(f"  so the entrant, foreseeing accommodation, enters (2 > 0 of staying Out).")
print(f"  => 'I'll fight any entry!' is a Nash threat but NOT credible: backward induction removes it.")
print(f"     Subgame-perfect outcome: Entrant In, Incumbent Accommodates (2, 2).")

print("\n=== EXP9: auctions — different rules, same expected revenue ===")
# first-price (bid shading) vs second-price (bid truthfully); simulate with uniform[0,1] values, n bidders
rng=np.random.default_rng(0)
n=4; T_=200000
vals=rng.random((T_,n))
# second-price: bid=value; winner pays 2nd-highest
sp=np.sort(vals,1)[:,-2].mean()
# first-price symmetric equilibrium bid = (n-1)/n * value; winner pays own bid
bids=(n-1)/n*vals; fp=bids.max(1).mean()
print(f"  {n} bidders, private values uniform on [0,1]. Expected revenue to the seller:")
print(f"    second-price (bid your true value, pay 2nd price): {sp:.3f}")
print(f"    first-price  (shade your bid, pay your bid):        {fp:.3f}")
print(f"  => different rules, essentially the SAME expected revenue — the Revenue Equivalence Theorem.")
