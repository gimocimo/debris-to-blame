# Handoff 0012 — statistical rigor: Wilson CIs on the slice

- **Date:** 2026-07-02 (Session 4 start)
- **Milestone:** scaling — rigor piece 1 of 3 (CIs done; sham + breadth next) · **State:** in progress

## What I did
- Added honest confidence intervals to the existing vertical-slice results (cheapest credibility win,
  applies to what we already have, $0/deterministic).

## What changed
- `d2b/stats.py` — `wilson_ci(k, n)` + `fmt_rate(k, n)`. Wilson (not bootstrap) because n=5 estimates
  are saturated (0/5, 5/5) and bootstrap over identical samples is degenerate.
- `tests/test_stats.py` — 7 tests (endpoints, symmetry, contains-point, more-data-tightens).
- `scripts/report.py` — one command prints the whole Degrade/Attribute/Recover slice with 95% CIs.
- `docs/results.md` — added a CI table + interpretation; `report.py` added to the reproduce block.

## Evidence produced
- 60 tests green, ruff clean. `python scripts/report.py`:
  every stage 0/5=0.00 [0.00,0.43] vs 5/5=1.00 [0.57,1.00] — intervals DON'T overlap (direction real)
  but are wide (magnitude not yet established). This makes the "proof of mechanism, not a claim"
  framing quantitative and honest.

## Next session starts here (remaining scaling pieces)
- [ ] SHAM CONTROLS (rigor piece 2): a volume-matched neutral injection per fault, so degradation is
      fault-vs-sham (isolates the specific fault from generic perturbation). Add `sham_inject` + tests.
- [ ] Fix mock `search_flights` date handling (removes exp02 clean-trace FP artifact) — but note it
      invalidates the cached exp02 verdicts, so do it as part of a re-run at scale.
- [ ] BREADTH: automate subagent fan-out (Workflow) → 6 faults × 3 Claude tiers × 5 domains, with
      sham + CIs → the blame-gap map (C3). Then M5 mitigation frontier (v0.2).
