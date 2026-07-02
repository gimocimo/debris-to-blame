# Handoff 0016 — interactive experiment harness + first real multi-step degradation result

- **Date:** 2026-07-02 (Session 5, ultracode) · **Milestone:** run the loop on the multi-step task · **State:** first result landed

## What I did
- Built the interactive experiment driver and ran the FIRST real interactive degradation batch on
  CONFERENCE_TRIP (real subagents driving full ReAct rollouts).

## What changed
- `experiments/step.py` — stateful CLI (init/start/act/result). A real agent-under-test drives one
  rollout by calling `act` per step; Python executes the tool + applies observation injectors +
  validates behind the CLI, so the agent never sees its condition and the world stays ground truth.
- `tests/test_step.py` — healthy passes; staleness shows $1050 cached but validator uses true $1350;
  cdrop removes the rule; start prompt hides the condition. (95 tests green.)
- Workflow `conf-interactive-degrade` (9 agents, 3 conditions x 3) drove the rollouts.
- `scripts/make_figure.py` → `assets/conf_degrade.png`; `docs/results.md` interactive section.
- Data: `experiments/decisions/conf_interactive.json` (real decision sequences),
  `results/conf_interactive_degrade.json` (matrix).

## Evidence (real interactive rollouts, n=3/condition)
```
healthy                     P[fail] 0/3 = 0.00 [0.00,0.56]   all booked F4+H1 $1180 (avoided surged F1)
staleness                   P[fail] 3/3 = 1.00 [0.44,1.00]   all lured to F1 by cached $1050 -> true $1350
constraint_drop:refundable  P[fail] 3/3 = 1.00 [0.44,1.00]   all took the cheaper non-refundable H2
Fisher healthy-vs-fault p = 0.10 (floor at n=3)
```
- Staleness degrades 3/3 interactively (vs 2/4 single-shot smoke) — agents commit to F1 mid-flow.
- constraint_drop on the *refundable* rule gives a DISTINCT failure (non-refundable hotel), showing
  per-rule degradation the single-decision task couldn't.

## Next session starts here (scale + the rest of the loop)
- [ ] Scale n (>=8) and add parameterized task VARIANTS (different catalogs/surge) so n is task-level,
      not resamples of one prompt — the real independence fix.
- [ ] Wire attribution (grade_attribution) + recovery on CONFERENCE_TRIP via the interactive harness.
- [ ] Then the blame-gap map across fault types on the multi-step task; M5 mitigation frontier.
- Note: to re-run, pre-init state files then launch the `conf-interactive-degrade` workflow; score
  with `python3 experiments/step.py <state> result`.
