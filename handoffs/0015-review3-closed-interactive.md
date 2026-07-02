# Handoff 0015 — round-3 review CLOSED (interactive rollout + conference redesign), adversarially verified

- **Date:** 2026-07-02 (Session 5, ultracode) · **Milestone:** close Codex round 3 · **State:** DONE

## What I did
- Fixed all 5 blockers + 3 issues from the round-3 Codex review, then **adversarially verified**
  closure with a 9-agent workflow (each red-teamer ran its own repros), and ran a real-model smoke.

## What changed (code)
- `d2b/rollout.py` (NEW) — `interactive_rollout` (ReAct loop; world=truth, `Injector` corrupts only
  the shown observation; `parse_fail` outcome; non-dict decision guarded), `scripted_policy_fn`.
- `d2b/conference.py` (REWRITTEN) — quote-versioned `latest_quote` (surge: F1 list $650 / live $950
  → F1+H1 $1350 > $1200; F4+H1 $1180 is the only compliant+affordable pick); event-log validator
  (exactly-one-booking, confirm-latest-quote-for-booked-pair, file-then-send order); NO get_policy
  tool; inert rental-car rule for a valid sham; staleness/contradiction/sham_note injectors.
- `d2b/faults.py` — constraint_drop scrubs dropped-rule text from message contents; sham uses
  `sham_constraint_index` (fallback = last rule, never a position-dependent binding one).
- `d2b/validate.py` — `TaskSpec.sham_plan`. `d2b/detective.py` — `grade_attribution` (specific rule).
- `experiments/grid.py` — parse_fail counted, not crashed. `d2b/domains.py` — CONFERENCE_TRIP in
  ALL_DOMAINS. Tests: `tests/test_conference.py` rewritten (13 tests incl. interactive + gameability
  + grade_attribution). 91 tests green, ruff clean.

## Evidence
- Adversarial-verification workflow: 8/8 verified findings CLOSED with independent repros (the 9th,
  constraint_drop-leak, hit a StructuredOutput failure but I re-verified it myself: no get_policy
  tool, no rule re-leaks across all 8 rules). Regression: 91 passed, ruff clean.
- **Interactive staleness bites (scripted):** agent SEES "$1050 (cached)", validator fails "over
  budget (live total $1350)"; world truth = 1350 regardless of injection.
- **Real-model smoke (n=4/cond):** books the over-budget F1 trap — control 0/4, stale 2/4 (Fisher
  p=0.43, n.s.). Staleness causally lures a real model; partial (the "(cached)" tell + confirm-quote
  rule save 2/4). `experiments/decisions/conf_staleness_smoke.json`.

## Next session starts here (scope-enlargement, now unblocked)
- [ ] Write an experiment that runs degrade/attribute/recover on CONFERENCE_TRIP via
      interactive_rollout (real subagents step-by-step) + grade_attribution — the loop is structurally
      ready; only the harness/experiment wiring is missing.
- [ ] Add parameterized task variants (different catalogs/surges) so n becomes task-level, not
      resamples of one prompt.
- [ ] Then the blame-gap map across fault types on the multi-step task; M5 mitigation frontier.
