# Handoff 0019 — External Codex audit adopted (9 findings fixed; misexec regraded)

- **Date:** 2026-07-05 (Session 12)
- **Milestone:** hardening pass on M2/M3 results · **State:** audit-clean, paper-ready pending Phase 4
- **Decision:** D-020

## What I did
The owner ran a full adversarial Codex review (prompted by `docs/paper/codex_audit_prompt.md`). It
returned 9 findings; I verified each with my own repro and fixed all of them. The headline finding
changed honestly.

## The blocker and how it changed the result
Codex found the **misexecution root-cause 23/24** was inflated by a lenient substring grader: it
credited verdicts that blamed the *wrong* tool (`check_ci`) for a `merge_pr` fault, and short item IDs
(`RA`) matched inside ordinary words. Fixed:
- `grade_attribution` now does **word-boundary** matching and supports `match_groups` (AND-of-ORs).
- misexec requires naming the **action locus** (`book_flight`/`book_room`/`merge_pr`) **and** a
  substitution concept.

**Honest re-grade: misexec root-cause 23/24 → 15/24** (conference 7/8, scheduling 6/8, review 2/8).
This is a *better* finding: root-cause inference localizes misexecution only when the failure symptom
implicates the action tool; on review, "the CI check was stale" is an equally available (and wrong)
hypothesis, so auditors blame `check_ci`. Outcome-informed attribution degrades to the most
**available** fault story. Only misexec moved — staleness/forget/cdrop are byte-identical under the
stricter grader (they never relied on loose matching), which is itself reassuring.

## The other 8 fixes
2. `conf_recover_score` takes an explicit grid path + cdrop condition and **fails loudly on n=0**
   (the docs' multi-domain reproduce order had clobbered the mutable grid → a bogus 0/0 table).
3. Moved scheduling recovery states out of `states_scheduling/` (→ `recovery_scheduling/`); added
   condition guards to `conf_score` and `attr_baselines` so repair states can't corrupt/crash them.
4. `attr_baselines` now takes multiple domain globs; the honest floor is **structured, not flat** —
   recency recall 0.19 (it catches `forget` by naming the last tool), keyword FP domain-dependent
   (100% conference / 0% scheduling+review). Docs' "~0 recall / 100% FP" corrected.
5. `conf_attr_score` now prints the **root-cause arms** (the method table depended on them).
6. Replaced 3 **hand-transcribed** backfill verdicts with **raw re-audit captures** (review forget
   oracle 4/8 → honest **3/8**); raw outputs committed (`reaudit_review_forget_policy.json`).
7. Added a **multiplicity / fragility** caveat: at n=4, `4/4 vs 0/4` is the minimum Fisher p=.0286 and
   one flipped variant → .143; no multiple-comparisons correction → p-values are **descriptive**.
8. Refreshed stale counts: **200** rollout states / **363** verdicts / **182** tests; "one task
   family" → "three".
9. `grade_attribution.correct` now == `attributed` for faulty records (was a foot-gun).

Codex confirmed CLEAN: no residual answer-key leakage, de-leak removes only the dropped rule, the
misexecution world-model is coherent (world executes rewritten args, shows original-request obs),
organic data checks out (2/28; the 6 verdicts name the true mechanism), and the prior-art IDs resolve.

## Final numbers (all replay from committed data, tier=opus)
- Attribution (blind / oracle / root-cause): staleness 0 / 0 / **18/24**; misexec 0 / 0 / **15/24**;
  cdrop 0 / (de-leak 0) / **15/15**; forget 9 / 13 / **24/24**. healthy/sham FP 0.
- Degradation unchanged; recovery +1.00 on conference AND scheduling.
- 182 tests green, ruff clean, pushed (commit `bce02c9`).

## Next session starts here
- [ ] **Phase 4** (owner action): run `docs/paper/codex_grader_prompt.md` in Codex → cross-provider
      verdicts → score with the same grader; agreement ⇒ ladder is task-structural, not family-specific.
- [ ] Optional dissection cells: cdrop×root-cause; separate outcome-knowledge from the causation
      question in the root-cause arm.
- [ ] Human-adjudicate a verdict sample to validate the keyword grader end-to-end (Codex's suggested
      next hardening step).
- [ ] **Phase 6** — paper draft from `docs/paper/framing.md`.
