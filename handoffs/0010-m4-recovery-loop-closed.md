# Handoff 0010 — M4 recovery: the loop is closed (localization enables recovery)

- **Date:** 2026-06-30 (Session 3, cont.)
- **Milestone:** M4 (exp04, the HEADLINE) · **State:** full vertical slice complete

## What I did
- Built the recovery harness: repair the SAME constraint_drop failure three ways, re-decide, validate.

## What changed
- `experiments/exp04_recovery.py` + `decisions/exp04_blind_repair.json` + `results/`.
- targeted_repair / no_repair reuse the cached exp01 decisions; only blind_repair needed a fresh
  5-subagent batch (agents reacting to the misdiagnosis fix).

## Evidence produced (THE HEADLINE — $0, 5 new subscription agents + cached reuse)
```
repair policy        n  recovery
no_repair            5    0.00     (leave the dropped context -> books red-eye again)
blind_repair         5    0.00     (act on the auditor's MISDIAGNOSIS: add a date-check)
targeted_repair      5    1.00     (restore the dropped 'no red-eye' rule)
LOCALIZATION LIFT = +1.00  (targeted 1.00 vs blind 0.00)
```
- **Recovery only works when the fault is correctly localized.** Restoring the actual dropped
  constraint recovers 5/5; the blind auditor's plausible-but-wrong fix (a date-check) recovers 0/5
  — every agent still books the cheap red-eye. This is "localization enables recovery," measured.

## THE COMPLETE VERTICAL SLICE (all real inference, $0)
1. exp01 — drop the constraint -> agent books the red-eye:            degradation Δ = +1.00
2. exp02 — a trace-only auditor can't see it:                        attribution 0.00 -> 1.00 w/ policy
3. exp04 — recovery needs correct localization:                       0.00 blind -> 1.00 targeted
=> "A dropped constraint silently breaks the agent, is invisible in the trace, and is only
   recoverable once you can localize it." The whole thesis, demonstrated on one clean cell.

## Caveats (unchanged, must address before any paper claim)
- n=5 per cell, single tier, one fault type, one domain. Effects are saturated (0 vs 1), which is a
  convincing proof-of-mechanism but needs: bootstrap CIs, the 3 Claude tiers, sham controls, the
  other fault types, the 5 domains, and the toy-env date-filter fix (exp02 clean-trace FP artifact).

## Next session starts here
- [ ] CONSOLIDATE + SCALE: automate the subagent fan-out via a Workflow; widen to faults × tiers ×
      domains with sham controls + bootstrap CIs; fix the env date-filter.
- [ ] Draft the README results section + the one headline figure (the 3-panel slice above).
