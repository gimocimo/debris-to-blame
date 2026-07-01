# Handoff 0005 — Codex audit adopted + recovery-headline reframe

- **Date:** 2026-06-30 (Session 3)
- **Milestone:** M1 hardened ✅ · next = M1b (domains+validators) → M2 · **State:** in progress

## What I did
- Ran an adversarial Codex audit of the repo; triaged its findings into "real now" vs "resolves at
  M2"; adopted the real ones and the owner's bar-raising directives.

## Code fixes (M1 hardened — experiment-independent, all Codex-correct)
- **Answer leakage FIXED (D-009):** `inject()` now returns a `Corruption` with `.corrupted`
  (internal, marked), `.public` (redacted, leakage-free — what attributors see), and `.label`
  (private `FaultRecord`). `redact_for_attribution()` strips `injected` markers + label meta.
  Per-fault test asserts `.public` leaks nothing.
- **Kind-tagged `FaultSite(kind, ref)`** replaces the ambiguous raw-int position.
- **Real `volume` severity for all 6 faults** (was a no-op for 4): staleness price, contradiction
  strength, wrong-tool distance, constraint count, debris count, decoy count.
- Relaxed the premature enum-freeze test → asserts manifest *presence*, not closure (D-013).
- 25 tests green, ruff clean, demo shows a live leakage check (0 markers / 0 label-meta).

## Scope reshape (owner directives — RAISE THE BAR)
- **D-010 recovery → v0.1 HEADLINE** (Claim C4): "agents recover X% more when attribution works."
  Replay-based rollback in mock env, not a runtime. Supersedes the old M6 stretch probe.
- **D-011 5-domain suite** (travel, calendar/email, ecommerce, repo-triage, spreadsheet/DB).
- **D-012 stay $0 Claude-tiers-only**; call them tiers (not families); circularity documented (R6).
- **D-013 trim mitigations to 3** (v0.2); don't freeze the fault enum.
- Adopted for M2: deterministic **validators**, **dumb baselines**, **paired sham controls**,
  **bootstrap CIs**. Honest reframe: "known injected-site + causal-effect validation", not "perfect
  causal labels".
- Fixed all the doc consistency debt Codex flagged (README <$1k→<$100 + status; §8 matrix; novelty
  status; claim language).

## Next session starts here (M1b → M2)
- [ ] M1b: build 4 more domains (mock tools + fixture + `validator`); `d2b/validate.py` (TaskSpec)
      and `d2b/replay.py` (deterministic re-exec + resume-live).
- [ ] Then M2 exp01/exp02 subscription-native on 3 Claude tiers; sham controls + bootstrap CIs.
- [ ] Recovery (M4/exp04) is the headline — design the checkpoint/rollback replay early.
