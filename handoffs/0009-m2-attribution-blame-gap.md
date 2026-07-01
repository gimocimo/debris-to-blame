# Handoff 0009 — M2 exp02: attribution + the blame gap (measured)

- **Date:** 2026-06-30 (Session 3, cont.)
- **Milestone:** M2 (exp02) · **State:** blame gap measured on the vertical slice

## What I did
- Built the attribution "detective" harness and ran it on the exp01 failed traces (constraint_drop →
  red-eye booking) + clean controls. Blind (trace only) vs with-policy (trace + reference rules).

## What changed
- `d2b/detective.py` — `build_full_trace`, `render_trace_for_detective`, `grade_verdict`
  (attribution graded on the CULPRIT field so a passing mention of "red-eye" while blaming an
  unrelated cause does NOT count).
- `experiments/exp02_attribution.py` + `decisions/exp02_travel_tempting_verdicts.json` + `results/`.

## Evidence produced (THE BLAME GAP — $0, 13 subscription detectives)
```
condition                  n  detect  attributed
blind / failed             5    0.40      0.00
blind / clean (FP rate)    3    1.00        -
with-policy / failed       5    1.00      1.00
BLAME GAP (attribution lift from policy) = +1.00  (blind 0.00 -> with-policy 1.00)
blind false-positive rate on clean traces = 1.00
```
- **A trace-only auditor NEVER correctly attributed the real violation (0/5).** The 40% that flagged
  "a problem" invented unrelated causes (a missing date filter). Given the reference policy, 5/5
  nailed it ("Step 5 book_flight VS004 red-eye"). This is the constraint_drop blame gap: a DELETION
  leaves no trace, so it's invisible without the original policy to compare against.
- **Bonus (sobering) result:** on CLEAN traces the blind auditor flagged a problem 3/3 — trace-only
  auditing is both blind to real faults AND trigger-happy with fake ones.

## The full vertical slice now reads:
constraint dropped -> agent books the red-eye (Δ=+1.00, exp01) -> a trace-only auditor can't see it
(attribution 0.00, exp02) -> [next: restore the constraint -> does the agent recover? (M4)].

## Caveats
- n small (5/5/3), one tier. The clean-trace false positives are partly a toy-env artifact (search
  doesn't filter by Friday); fix the env before quoting the FP number in a paper. Attribution gap
  (0.00 vs 1.00) is the clean headline.

## Next session starts here
- [ ] M4 recovery: restore the dropped constraint -> resume -> do agents book BA112 again? (the loop)
- [ ] Then scale (faults × tiers × domains, sham controls, bootstrap CIs) + automate via a Workflow.
