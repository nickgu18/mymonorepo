not gonna implement.

the idea is simple: adopt a elo like rating system to rank founders.

Each founder has a certain set of properties, use LLM as a judge, provide it with

**jduge criteria**
1. critieria of good founder (from HBR for example)
2. current macro economic trends (interest rate for example)
3. Industry performance during different economic trends

**founder properties**
1. career experience
2. prevvious company performance
3. network analysis
4. education history
5. personality traits (analyze from social media, categorize using Merrill-Reid Social Personality Styles, i.e driver, analytical, expressive, amiable)
6. previous failures, i.e number of failed startups
7. expertise domain (not just from education, maybe infer this from their publications, blogs)
8. current startup domain if any

Then use LLM to do a battle between founders, answer given judge criteria, and founder properties of founder A and founder B.
Who are likely to build a company with better returns for investor with real exits?

Then the standard elo algorithm:
Ratings start at `R=1500`. After each head-to-head:
- Expected score: `E_A = 1 / (1 + 10^((R_B - R_A)/400))`, `E_B = 1 - E_A`
- Actual score: `S_A ∈ {1, 0.5, 0}`, `S_B = 1 - S_A`
- Update: `R'_A = R_A + K * (S_A - E_A)`, `R'_B = R_B + K * (S_B - E_B)`
- Typical `K`: 16–32; use higher for fewer matches or early stages.

Outcome mapping for founder battles:
- Judge picks A → `S_A = 1`
- Judge picks B → `S_A = 0`
- Judge calls tie → `S_A = 0.5`

Example (K=32): `R_A=1500`, `R_B=1600`, A wins (`S_A=1`)
- `E_A = 1 / (1 + 10^((1600-1500)/400)) ≈ 0.36`
- `Δ_A = 32 * (1 - 0.36) ≈ +20.5` → `R'_A ≈ 1520.5`
- `Δ_B = 32 * (0 - 0.64) ≈ -20.5` → `R'_B ≈ 1579.5`

Batch processing:
For a list of matches, apply updates sequentially in match order.

Pseudocode:
```
function updateElo(Ra, Rb, Sa, K):
  Ea = 1 / (1 + 10 ** ((Rb - Ra) / 400))
  Eb = 1 - Ea
  Ra2 = Ra + K * (Sa - Ea)
  Sb = 1 - Sa
  Rb2 = Rb + K * (Sb - Eb)
  return Ra2, Rb2
```