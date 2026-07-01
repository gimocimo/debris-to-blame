# Handoff 0002 — dependability reframe

- **Date:** 2026-06-30 (Session 1)
- **Milestone:** M0 — novelty kill · **State:** in progress

## What I did
- Stress-tested the scope against an external scan of 2026 open problems (OpenAI Codex).
- **Verified all 8 benchmarks Codex cited are REAL** (agent sub-pass, primary sources): STATE-Bench,
  ReliabilityBench 2601.06112, SentinelBench 2606.05342, AuditBench 2602.22755, SLEIGHT-Bench
  2605.16626, MemGym 2605.20833, SciAgentArena 2606.12736, OpenAI Deployment Simulation. METR numbers
  were a paraphrase (real: ~14.5h@50% Opus 4.6, ~2.5–3.5h@80%); reward-hack confound is real.

## What changed (files / claims / decisions)
- **Reframe, not re-scope.** Raised narrative altitude to the dependability frontier (PROJECT_PLAN
  §2a) and adopted dependability metrics — pass^k, recovery/irreversible-error/unnecessary-escalation
  rates (§7, ROADMAP §3). Build surface UNCHANGED.
- **Declined the runtime.** Codex's headline (build a recoverable agent-OS) rejected as scope-poison
  (D-003). Added bounded **M6 recovery-probe** as the bridge instead (D-004).
- **New nearest neighbor:** ReliabilityBench 2601.06112 (injects faults for pass^k, not attribution
  labels) — kill-list #4, ROADMAP R5, D-005. AuditBench/SLEIGHT-Bench added as blame-gap citations.

## Evidence produced
- None empirical. Verified-literature map expanded; scope docs updated.

## Open risks / surprises
- Codex's citations were *unusually accurate* — trust it more than a typical LLM pass, but still
  verify. ReliabilityBench is the surprise neighbor; must read in full in M0.

## Next session starts here (M0)
- [ ] Read ReliabilityBench 2601.06112 in full (highest-priority diff — does it grade attribution?).
- [ ] Read ConstraintRot 2606.22528 in full; confirm 5-axis diff.
- [ ] Dedicated searches: injection-for-attribution-ground-truth; tool-use-limits/MCP failures.
- [ ] Finalize the one-paragraph gap; if closed, log a pivot decision.
- [ ] Owner decision: make the GitHub repo public + push? (still private + uncommitted)
