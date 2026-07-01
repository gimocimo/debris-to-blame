# Handoff 0006 — M1b: 5 stateful domains + validators + replay/resume

- **Date:** 2026-06-30 (Session 3, cont.)
- **Milestone:** M1b · **State:** DONE

## What I did
- Built the stateful-environment framework and all 5 v0.1 domains.

## What changed
- `d2b/env.py` — `World` (dict) + stateful `Tool(fn(args, world))` + `Environment`. Tools now mutate
  state, so success is judged on STATE not prose (Codex: "validate final state, not prose").
- `d2b/validate.py` — `TaskSpec(name, goal, make_env, make_trajectory, validate, critical_step)` +
  `ValidationResult`.
- `d2b/replay.py` — deterministic `replay`/`evaluate` (static, catches call-changing faults) + the
  `resume`/`Policy` interface for resume-live (M2 wires the model) + `replay_tail_policy` oracle.
- `d2b/domains.py` — 5 domains: **travel, repo_triage, calendar, ecommerce, spreadsheet**. Each has a
  stateful env + a hand-authored successful trajectory + a deterministic validator + `critical_step`.
- `d2b/faults.py` — `wrong_tool` now swaps for a **real in-domain tool** (from `trajectory.tools`),
  domain-agnostic + more realistic (was hardcoded travel neighbours).
- `tests/test_domains.py` — per-domain: healthy validates; wrong_tool@critical breaks the validator;
  context-only fault leaves static replay valid (documents two-mode design); resume oracle works.

## Evidence produced
- **47 tests green, ruff clean.** All 5 domains: healthy=True with real state reasons; wrong_tool at
  the critical step breaks the state validator. Still ZERO model calls / $0.
- Key design proof: the **stateful validator catches a call-changing fault with no model** — the
  degradation signal is real, not LLM-judged.

## Open risks / surprises
- Two-mode reminder: static replay only catches *call-changing* faults (wrong_tool). Context faults
  (debris/staleness/contradiction/constraint_drop/tool_forgetting) need **resume-live** (a model),
  which is M2. The harness + oracle policy are ready; only the model policy is missing.

## Next session starts here (M2)
- [ ] Write the model-backed `Policy` (subscription-native subagent): given a redacted prefix +
      tools, emit the continuation; execute against the env; validate.
- [ ] exp01 degradation (per fault × tier × domain, vs sham control, bootstrap CIs).
- [ ] exp02 attribution (dumb baselines + LLM methods on `.public` traces vs known labels).
- [ ] Then M3 blame-gap, M4 recovery (headline).
