# Handoff 0013 — breadth: sham control × 3 tiers (Workflow fan-out)

- **Date:** 2026-07-02 (Session 4) · **Milestone:** scaling pieces 2-3 (sham) + breadth · **State:** done

## What I did
- Completed the three requested scaling pieces: sham controls, env date fix (prior commit), and a
  breadth grid run.

## What changed
- `experiments/grid.py` — constraint_drop × {healthy, fault, sham} × 3 Claude tiers; builds prefixes
  (fault = drop binding no-red-eye; sham = `sham_inject` drops the non-binding budget rule), scores
  a P[fail] matrix with Wilson CIs.
- Ran it via a **Workflow** (`d2b-grid-constraint-drop`, 36 agent-under-test decisions, per-tier
  model override). Decisions cached in `experiments/decisions/grid_constraint_drop_tiers.json`;
  matrix in `results/grid_constraint_drop_tiers.json`.
- `scripts/make_figure.py` — now also writes `assets/grid.png` (grouped bars, tier × condition).
- `docs/results.md` — breadth section (table + figure + the two findings).

## Evidence produced ($0, 36 subscription agents across Opus/Sonnet/Haiku)
```
tier    healthy   fault              sham
opus    0/4       4/4 = 1.00         0/4
sonnet  0/4       2/4 = 0.50         0/3
haiku   0/4       4/4 = 1.00         0/4
```
1. **Sham control works:** dropping a non-binding rule → 0 violations everywhere; only the BINDING
   drop degrades. Isolates the specific rule from generic perturbation.
2. **Not a clean death-spiral:** Sonnet resisted 2/4 with the rule gone; Opus & Haiku 4/4. Non-
   monotonic in capability — honest surprise (n=4, noisy).

## Caveats
- n=4/cell (one sonnet/sham lost to a structured-output failure → n=3). Effect direction clear;
  tier-ordering nuance needs more samples. Still one fault, one domain.

## Next session starts here
- [ ] More samples per cell (tighten CIs; confirm/deny the Sonnet non-monotonicity).
- [ ] Genuine multi-fault / multi-domain breadth needs richer MULTI-STEP tasks (single-decision
      fixtures under-expose debris/staleness/wrong_tool/tool_forgetting) — design those next.
- [ ] Grow the blame-gap map (C3) across fault types; then M5 mitigation frontier (v0.2).
