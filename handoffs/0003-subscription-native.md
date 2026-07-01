# Handoff 0003 — subscription-native + novelty deprioritized

- **Date:** 2026-06-30 (Session 2)
- **Milestone:** M0 — related-work scan (downgraded) · **State:** in progress

## What I did
- Two owner directives folded into scope (both pre-commit).

## What changed (files / claims / decisions)
- **D-006 — novelty deprioritized.** Optimize for impressive/well-executed over novel/niche. M0
  downgraded from novelty-KILL-gate → light related-work scan (no pivot condition). Added
  "impressiveness" (headline figure + demo) as a co-equal success criterion (§7). `novelty.md` now a
  related-work/borrow reference.
- **D-007 — subscription-native inference.** Target <$100 using the existing $200/mo Claude Max plan
  instead of paid API. **The Claude Code session + subagents ARE the inference engine (marginal $0).**
  Trades accepted: small curated scale (~40–60 trajectories), **Claude-tier panel** (Opus 4.8 /
  Sonnet / Haiku) not cross-provider, semi-manual generation (mitigated by freezing/releasing the
  dataset). Paid-API path demoted to scale-only fallback. Rewrote PROJECT_PLAN §6.
- **R6 — validity note.** Same model family generates + grades; NOT circular (truth = injection, not
  a model); attribution via fresh-context subagents. Documented as a paper limitation.
- ROADMAP M0 + M2 updated (subscription-native; tier-panel; death-spiral-across-tiers hypothesis).

## Evidence produced
- None empirical. Scope + economics reframed.

## Open risks / surprises
- Rate limits are the real constraint now (not $). Generation happens in batches, possibly across
  sessions. Keep N curated-small.
- Owner is ready to COMMIT after this session. Confirm: (a) commit + push the scaffold? public or
  private? (b) Claude-tier panel only, or add a <$50 cross-provider top-up?

## Next session starts here
- [ ] Owner decisions: commit/push (public vs private) + panel scope.
- [ ] M1: write `inject()` + mock-tool env; demo one fault breaking one trace end-to-end (in-session).
- [ ] Light M0 skim of ConstraintRot + ReliabilityBench for borrowable pieces.
