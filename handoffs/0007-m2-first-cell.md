# Handoff 0007 — M2: first real degradation cell (subscription-native)

- **Date:** 2026-06-30 (Session 3, cont.)
- **Milestone:** M2 (exp01) · **State:** harness working; first cell run

## What I did
- Built the model-backed resume path and ran the FIRST real (subscription-native) degradation cell.

## What changed
- `d2b/agent.py` — `render_prefix` (the leakage-free prompt the agent-under-test sees), `parse_decision`,
  `decision_to_messages`. `d2b/replay.py` — `scripted_policy` (plays back a captured model decision).
- `experiments/exp01_degradation.py` — travel + constraint_drop vs healthy control; scores recorded
  decisions with the deterministic state validator. `experiments/decisions/exp01_travel.json` — the
  10 real decisions (cached inference outcomes). `results/exp01_travel_constraint_drop.json`.
- `d2b/domains.py` — `book_flight` now tolerates `id`/`flight` arg synonyms.

## Evidence produced (FIRST REAL RESULT — $0, 10 subscription subagents)
- **healthy: 5/5 booked BA112 (valid). constraint_drop: 5/5 booked BA112 (valid). Degradation Δ = 0.00.**
- Pipeline proven: inject → redact → fresh subagent decides on the `.public` prefix → replay →
  state validator → number. Fully leakage-free; each agent saw only the redacted prefix.

## The insight (why the null result is useful)
- **A dropped constraint only causes damage if it was BINDING.** Here the model *intrinsically*
  avoids red-eyes (one dropped-condition agent even called its choice "non-red-eye"), and the red-eye
  was only $50 cheaper — no temptation. So constraint_drop ≈ 0 damage in this fixture.
- **Design lesson (D-014):** to measure constraint_drop, the fixture must make violating the rule
  TEMPTING (e.g. red-eye = the much-cheaper / only clearly-under-budget option). Build a "tempting"
  travel variant next.
- **Prompt lesson (D-014):** the agent used `{"flight": ...}` because the prompt lacked tool arg
  schemas. Render tool signatures in `render_prefix` before scaling.

## Next session starts here
- [ ] Add a "tempting" travel variant (cheap red-eye) and re-run — expect constraint_drop damage > 0.
- [ ] Add tool arg schemas to `render_prefix`.
- [ ] Then scale exp01 across faults × tiers × domains with sham controls + bootstrap CIs.
