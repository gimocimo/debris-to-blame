# Handoff 0018 — Paper program: prior-art GO, 3 domains, the deception gap replicates

- **Date:** 2026-07-03/04 (Sessions 8–10)
- **Milestone:** M2 exit bar met (domains axis) · M3 delivered cross-domain · **State:** paper program active
- **Decision:** D-019

## What I did
Owner committed to a **full research paper**. Executed Phase 0 (prior-art verification), Phase 1
(two new interactive domains), and E1/E2 (the cross-domain replication test), plus the consolidation
write-up. Two integrity bugs found by the experiments themselves were fixed and re-verified.

## What changed (files / claims / decisions)
- **Paper docs:** `docs/paper/framing.md` (north star: finding-led thesis, C1–C4, E1–E6, threats) and
  `docs/paper/related_work.md` (verified diff vs AEGIS / AgenTracer / CAR / ReliabilityBench /
  Who&When / TRAIL — injection-for-labels and the live-corruption instrument are PRIOR ART; the
  surviving novelty is the fault-type-structured FINDING).
- **New domains:** `d2b/scheduling.py` (slot+room; stale availability hides a double-booking) and
  `d2b/review.py` (PR-merge; stale CI shows green over a red pipeline); `d2b.DOMAINS` registry;
  `step.py`/`attribute.py`/`conf_attr_score.py` domain-aware (backward compatible).
- **Integrity fixes (both regression-free — conference re-scores byte-identically):**
  1. Validator "confirm the *latest* status" failed sincere agents that explore → relaxed to
     **confirmed-at-least-once** (`w["checked"]`).
  2. Staleness injectors emitted a self-labelling "(cached)" tell → corrected to **true deceptions**
     (swap only the value; keep the "(live)" tag). The first audit had shown the tell made staleness
     ~0.5 blind-attributable; all staleness cells were re-audited after the fix.
- **Figures:** `assets/blamegap_map.png` (cross-domain, 3 panels); `make_figure.py` reads the new
  domain-aware `results/conf_attribution.json`.
- **Docs:** README headline → cross-domain two-regime map; `docs/results.md` cross-domain section +
  updated caveats/reproduce; ROADMAP M2 status = met on domains axis (v0.1 still un-tagged).

## Evidence produced (all replay from committed data, $0)
- **Degradation (sincere agents, variant-clustered):** staleness 8/8 and forget 8/8 on ALL 3 domains
  (each p=.029); cdrop 7/8 conference (refundable) / 8/8 scheduling (boardroom, p=.029) / **0/8 null
  review** (approval redundant — D-014). Healthy + sham 0/8 everywhere.
- **The cross-domain blame-gap map** (195 verdicts; `experiments/decisions/conf_attribution_alldomains.json`):
  - **Deception gap replicates 3/3:** staleness blind 0/8 AND oracle 0/8 on stale-price,
    stale-availability, stale-CI. The policy does not close it; needs ground-truth state.
  - **Deletion gap replicates 2/2:** cdrop blind 0, de-leak 0, oracle 1.0 (7/7, 8/8).
  - **Omission is salience-dependent:** forget blind 8/8 (conference, prominent step) vs 1/8 / 0/8
    (scheduling/review); oracle only 0.38–0.88. Verdict inspection suggests it is visible mainly when
    the trace contains the agent's *failed attempt* at the missing tool — Phase-3 validity check.
- 3 rate-limited review-forget oracle audits backfilled → clean n=8 (4/8).
- 167 tests green; ruff clean; pushed.

## Open risks / surprises
- **R2 external validity** still open: 0/22 organic failures elicitable so far (Phase 2). Fallback
  framing exists (labelled-vs-unlabelled staleness contrast = detectability result).
- **Fault map incomplete:** contradiction (2 domains), debris, wrong_tool not yet interactive.
- **Forget-grader validity check** required before the salience claim enters the paper.
- Review domain has no binding cdrop rule (deletion point is 2/2, not 3/3) — acceptable, or design
  a binding drop for review later.
- Cross-tier panel is conference-cdrop only.

## Next session starts here
- [ ] **Phase 3:** forget-salience validity check → wire contradiction (scheduling/review) + debris +
      wrong_tool interactively → degradation pass → attribution-method ladder (add a Who&When-style
      step-by-step auditor) → the methods × fault-types table. Recovery replication on scheduling.
- [ ] **Phase 2:** harder organic-failure elicitation (longer-horizon composite variants, weaker tier);
      formalize the fallback if still zero.
- [ ] **Phase 4 (replanned, $0):** cross-provider grading via the owner's **Codex subscription** —
      prepare a self-contained Codex grader prompt (run `attribute.py` per trace, return verdicts
      JSON); owner runs it; we score with the same `grade_attribution`.
