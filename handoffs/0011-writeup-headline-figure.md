# Handoff 0011 — write-up: results section + headline figure

- **Date:** 2026-06-30 (Session 3, end)
- **Milestone:** consolidation (between M4 and scaling) · **State:** repo now shows the story

## What I did
- Turned the vertical-slice results into a visible, self-explaining part of the repo.

## What changed
- `scripts/make_figure.py` — renders `assets/headline.png` (the 3-panel Degrade/Attribute/Recover
  figure) deterministically from the cached `results/*.json`. No model calls.
- `README.md` — new "First result" section: the figure + a 3-row table + the one-sentence thesis +
  the honest caveat, linking to the full write-up.
- `docs/results.md` — full write-up: each experiment's numbers, findings, caveats, and a reproduce
  block.

## Evidence produced
- `assets/headline.png` committed. README renders it at the top. 53 tests still green, ruff clean.

## State of the project (end of session 3)
- **The whole thesis is demonstrated on one cell** (constraint_drop / travel, $0):
  Degrade Δ=+1.00 → Attribute 0.00→1.00 → Recover 0.00→1.00. Repo now communicates this at a glance.
- Nothing is a paper claim yet (n=5, one tier/fault/domain, no CIs/sham, toy-env date artifact).

## Next session starts here (scaling — the agreed next milestone)
- [ ] Automate the subagent fan-out via a Workflow (inject → decide → validate → attribute → recover).
- [ ] Widen: 6 faults × 3 Claude tiers × 5 domains, with **paired sham controls** + **bootstrap CIs**.
- [ ] Fix the mock `search_flights` date handling (removes the exp02 clean-trace FP artifact).
- [ ] Grow the blame-gap map (C3) across faults; then M5 mitigation frontier (v0.2).
