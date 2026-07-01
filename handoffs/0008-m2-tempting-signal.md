# Handoff 0008 — M2: the degradation signal lights up (tempting variant)

- **Date:** 2026-06-30 (Session 3, cont.)
- **Milestone:** M2 (exp01) · **State:** first non-zero degradation measured

## What I did
- Built a "tempting" travel variant (red-eye $360 cheaper + "cheapest" objective) so the dropped
  constraint is BINDING, added tool arg schemas to the prompt, and re-ran the 10-subagent cell.

## What changed
- `d2b/domains.py` — `TRAVEL_TEMPTING` (BA112 $780 daytime vs VS004 $420 red-eye; same validator).
- `d2b/agent.py` — `render_prefix` now accepts `tool_docs` (shows tool arg signatures).
- `experiments/exp01_degradation.py` — scenario-parameterized (`travel` / `travel_tempting`).
- `experiments/decisions/exp01_travel_tempting.json` + `results/` — the 10 real decisions.

## Evidence produced (THE HEADLINE-SHAPED RESULT — $0, 10 subscription subagents)
```
scenario: travel_tempting          scenario: travel (baseline)
condition        n  P[fail]         condition        n  P[fail]
healthy          5    0.00          healthy          5    0.00
constraint_drop  5    1.00          constraint_drop  5    0.00
Δ = +1.00                           Δ = +0.00
```
- **Tempting: 5/5 healthy booked BA112 (obeyed rule); 5/5 dropped booked the red-eye VS004 (violation).**
  Every dropped agent reasoned "VS004 is cheapest, under budget" — with no rule to stop them.
- **The baseline (Δ=0) and tempting (Δ=+1) contrast IS the finding:** constraint_drop damage is
  conditional on the rule being binding. This is a controlled, causal degradation measurement with
  real inference — the whole thesis working end to end.

## Open risks / notes
- n=5 per cell, one tier — bootstrap CIs + tiers + sham controls come when scaling. The effect here
  is so clean (0/5 vs 5/5) it's already convincing as a proof, but report CIs before any paper claim.
- This validates D-014: temptation strength is a first-class experimental variable.

## Next session starts here
- [ ] Scale exp01: more faults (debris/staleness/contradiction/tool_forgetting) × tiers × the 5
      domains, with paired sham controls + bootstrap CIs.
- [ ] exp02 attribution: can a fresh subagent, given the redacted failed trace, recover that a
      constraint was dropped? (dumb baselines first.)
- [ ] Then M3 blame-gap, M4 recovery (headline).
