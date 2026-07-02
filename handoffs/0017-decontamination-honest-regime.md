# Handoff 0017 — De-contamination to the honest regime (steps 1–7 + Codex re-review)

- **Date:** 2026-07-02 (Session 7)
- **Milestone:** M2/M3 (degradation + attribution + blame-gap map) · **State:** partially met — one domain
- **Decision:** D-018

## What I did
A self-run "next steps" review (adversarially verified in-code) found that the previous session's
headline was **contaminated**: `attribute.py` handed the detective the full policy *including the
dropped rule* (so `blind→with-policy 0→0.88` largely measured answer-copying), and the degradation
surface was collected with **scripted-oracle** policies told to take the trap. I executed all seven
recommended fixes and **re-collected a canonical sincere-agent dataset**, then ran a final adversarial
self-review and fixed its 3 (minor/nit) findings.

## What changed (files / claims / decisions)
- **New harness:** `experiments/attribute.py` de-leak arm; `experiments/attr_baselines.py` (dumb
  attributor floor); `experiments/attr_common.py` (`record_for`); `d2b/stats.cluster_by_variant`;
  `experiments/step.py` `forget:<tool>` (tool_forgetting); `experiments/conf_attr_score.py`
  (multi-arm/tier scorer); `d2b/detective.grade_attribution` generalized via `attr_keys`.
- **Canonical dataset (committed, replayable, $0):** `experiments/decisions/states/` (56 rollouts),
  `.../conf_attribution.json` (107 detective verdicts), `.../recovery2/` (8), `.../organic_*` (22).
- **Removed** the superseded `experiments/attr_score.py` and the orphaned `assets/conf_headline.png`.
- **Docs de-inflated:** README leads with the blame-gap **map** (not `+0.88`); `docs/results.md` marks
  the scripted/travel numbers **SUPERSEDED**; **M2's ≥3-domain bar explicitly NOT claimed met**
  (only CONFERENCE_TRIP is wired; the other 5 domains are single-step static fixtures). PROJECT_PLAN
  D-018; ROADMAP M2 = PARTIALLY MET.

## Evidence produced (all reproduce from committed data — no model calls)
- **Degradation** (`conf_score.py`, variant-clustered): staleness **8/8 (4/4 var, p=0.029)**,
  forget:expense **8/8 (4/4, p=0.029)**, cdrop:refundable **7/8 (3/4, p=0.14)**, **cdrop:red-eye 0/8
  NULL** (rule redundant with agent preference — the scripted 8/8 was an artifact; validates D-014),
  contradiction 1/8, sham 0/8. Figure `assets/conf_grid.png`.
- **Blame-gap map** (`conf_attr_score.py`): `assets/conf_blamegap.png`.
  - cdrop:refundable — **deletion gap**: blind 0, **de-leak 0** (rulebook minus the line ⇒ no help),
    oracle **1.0** (labelled UPPER BOUND). Only re-supplying the exact rule attributes it.
  - staleness — **deception gap**: blind 0 **and** oracle 0 (the cached quote deceives the auditor
    too; needs ground-truth state, not the policy).
  - forget:expense — **visible**: blind **1.0**, no gap.
  - healthy/sham: 0.00 false-positive (auditor is precise). Dumb baselines: ~0 recall / 100% FP.
- **Cross-tier** (R6 lower bound): Haiku/Sonnet/Opus all blind 0 → oracle 1.0 on cdrop.
- **Recovery** (`conf_recover_score.py`): pooled 0.12 / 0.00 / 1.00; variant-clustered **targeted 4/4
  vs blind 0/4, p=0.029**, localization lift **+1.00**. Figure `assets/conf_recovery.png`.
- **External validity:** honest **null** — 0/22 organic failures elicitable (Haiku on healthy + a
  tight-margin `conference_hard` variant); documented as R2-open + a structural face-validity argument.
- 125 unit tests green, ruff clean.

## Open risks / surprises
- **The headline reversed, honestly.** Scripted `cdrop 8/8 p=0.0002` + `blame gap +0.88` were
  artifacts. The sincere-agent result is richer: a fault-type-resolved observability map.
- **M2 is NOT closed** — one task family only. The ≥3-domain bar needs a second domain ported to the
  interactive `step.py` loop (the other domains are static single-step fixtures).
- **Oracle arm is an upper bound**, not a realistic detector; the de-leak control and dumb baselines
  bound the realistic number from below.
- **R6/R2 partly open:** grader is Claude-only (bounded across tiers, not cross-provider); organic
  comparison not yet possible at toy scale.

## Next session starts here
- [ ] **Port a 2nd domain** (e.g. calendar or ecommerce) from a static fixture to `step.py`'s
      interactive loop — the real M2 gate.
- [ ] Grow the blame-gap map to the remaining faults (debris, wrong_tool) on CONFERENCE_TRIP.
- [ ] A true **cross-provider** grader once a small API budget is sanctioned (bounds R6 properly).
- [ ] Larger n per variant to tighten cdrop:refundable (currently p=0.14).

---

## Codex re-review prompt (paste this to Codex)

> You are reviewing the public repo **debris-to-blame** after a de-contamination pass (commit range
> `883eee8..HEAD`, decision **D-018**). The project injects typed faults into known-good agent
> trajectories to create causal ground truth for failure attribution. A prior "blame gap +0.88" was
> found to be contaminated (the detective was handed the dropped rule) and the degradation used
> scripted-oracle policies; both were re-done with **sincere agents** and a de-leak control.
>
> Please verify, adversarially and with the code/data in front of you:
> 1. **No residual leakage/contamination.** In `experiments/attribute.py`, confirm `blind` reveals no
>    dropped rule, `deleak` excludes **only** the dropped line, and `policy` (oracle) is honestly
>    labelled an upper bound. Confirm the detective never sees injection markers or label metadata
>    (`d2b/faults.py:redact_for_attribution`).
> 2. **Scorer correctness.** In `experiments/conf_attr_score.py` + `attr_common.py` +
>    `d2b/detective.py:grade_attribution`, confirm each verdict is graded against the *specific* fault
>    and no credit is given for the wrong fault. (We tightened the `contradiction` keys after review —
>    check they can't be earned by a generic over-budget narrative.)
> 3. **Statistical honesty.** Confirm degradation and recovery are reported at the **variant** level
>    (reps of one variant are correlated), the pooled `p=0.0002` is retired, and no doc quotes the old
>    contaminated `+0.88` or scripted `8/8` as a live result.
> 4. **Docs match data.** Every quantitative claim in `README.md` and `docs/results.md` should match
>    the committed `results/*.json`. Confirm **M2's ≥3-domain bar is NOT claimed met** (only
>    CONFERENCE_TRIP is wired into the interactive loop).
> 5. **Reproducibility.** Run the `docs/results.md` "Reproduce" block; every headline number should
>    reproduce from committed data with no model calls. Run `uv run --extra dev pytest -q` (125 tests)
>    and `uv run --extra dev ruff check .`.
> 6. **The three-cornered claim.** Is the "deletion gap (cdrop, closed by oracle) vs deception gap
>    (staleness, NOT closed by policy) vs visible (forget)" framing supported by the data, or
>    over-stated? Is the dumb-baseline floor (~0 recall / 100% FP) a fair control?
>
> Report blockers/majors/minors with file:line and a concrete repro. An empty list is a valid result.
