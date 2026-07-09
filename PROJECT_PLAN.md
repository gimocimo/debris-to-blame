# PROJECT_PLAN — debris-to-blame (Debris→Blame)

**The north-star anchor.** This document owns *what we are building and why*. `ROADMAP.md`
owns *how* (experiment mechanics, figures, metrics). `docs/novelty.md` owns *why it is novel*
(prior-art map). `handoffs/` logs *what happened each session*. When in doubt, **this file wins**;
if work diverges from it, either update this file deliberately (with a §9 Decision-Log entry) or
stop and re-align.

> **How to use this doc**
> - **Start of every session:** read §1 (Current Status) + the latest `handoffs/` entry.
> - **End of every session:** write a new `handoffs/NNNN-*.md` (see `handoffs/TEMPLATE.md`),
>   then update §1 here and the §8 traceability matrix if evidence changed.
> - **Any scope/claim/method change:** add a §9 Decision-Log entry. **No silent pivots.**

---

## 1. Current status (pinned — update every session)

- **Date of last update:** 2026-07-04 (Session 10 — cross-domain consolidation; paper program active)
- **Lead framing (updated by D-019):** the paper is **finding-led**: *attribution difficulty is
  fault-type-structured* — an information ladder (trace / +reference-policy / +ground-truth-state)
  with **two robust blame-gap regimes**: a *deletion gap* the exact rule closes and a **deception gap
  the policy does NOT close**. C4 (localization→recovery) is supporting evidence. See
  `docs/paper/framing.md` (north star) + `docs/paper/related_work.md` (novelty diff, verified).
- **Milestones complete:** M0 ✅ · M1 ✅ · M1b ✅ · **M2 exit bar met on the domains axis** (3
  interactive domains, sham-controlled degradation + measured attribution gap; tier panel still
  conference-only — v0.1 NOT tagged) · **M3 delivered cross-domain** (`assets/blamegap_map.png`) ·
  M4 recovery on one domain (lift +1.00, clustered p=.029).
- **Headline result:** **the deception gap replicates 3/3 domains** (staleness: damaging 8/8
  everywhere, attributed 0 blind AND 0 with-policy on stale-price/availability/CI); deletion gap 2/2
  (blind 0, de-leak 0, oracle 1.0); omission salience-dependent. 195 committed verdicts; every number
  replays from committed data at $0.
- **Repo health:** public at `github.com/gimocimo/debris-to-blame`, pushed through the cross-domain
  result; 167 tests green; ruff clean; ~380 subagents of subscription-native inference, $0 total.
- **Biggest open risks:** **R2 external validity** (organic failures not yet elicitable — Phase 2) and
  fault-map completeness (contradiction/debris/wrong_tool not yet interactive — Phase 3). R6 grader
  circularity to be closed via Codex-as-cross-provider-grader (Phase 4, $0 via owner's subscription).
- **Latest handoff:** `handoffs/0018-crossdomain-deception-gap.md`

---

## 2. Vision (one paragraph)

Automated **failure attribution** — saying *which step* of an agent's tool-use trajectory caused a
failure — is the single hardest open problem in agent observability: the best methods reach only
~14% step-level accuracy because real failure traces have **no causal ground truth** (a human has
to *guess* the culprit step, and can't verify the guess). **debris-to-blame** fixes this at the
source: we take known-successful agent trajectories, **inject typed faults at controlled positions**
(debris, staleness, contradiction, wrong-tool, constraint-drop, tool-forgetting), and now *we know
exactly which step is to blame by construction*. This turns attribution into a benchmark with
**perfect labels**, and lets us measure two things no existing benchmark unifies: (A) which fault
types actually **break** agents (degradation, decoupled from task difficulty), and (B) which broken
runs are **invisible to attribution** — the dangerous "blame gap" of high-damage, low-detectability
faults. The same harness then scores mitigations on a **cost–quality–detectability** frontier.

---

## 2a. Why now — the dependability frontier (narrative altitude)

The June-2026 frontier has moved from *"can an agent do impressive work once?"* to *"can an agent
stay reliable and corrigible over long, messy horizons?"* Capability is outrunning dependability:
METR clocks a ~14.5h **50%**-success horizon (Opus 4.6) but only ~2.5–3.5h at **80%** reliability —
and even that is confounded by agents gaming the eval harness. The vision everyone now points at is
a *recoverable runtime* that **diagnoses its first fatal mistake and rolls it back**. But you cannot
roll back what you cannot **localize** — and localization (failure attribution) sits at ~14%
step-accuracy. **debris-to-blame builds the measurement floor that vision stands on:** the causal
ground truth needed to measure, then improve, the diagnose-and-recover primitive. We measure the
primitive; we do **not** build the runtime (see §4 OUT / D-003). This altitude connects our "blame
gap" to the monitor-blind-spot literature in the field's own language (AuditBench's "tool-to-agent
gap" 2602.22755; SLEIGHT-Bench's 11 blind-spot classes 2605.16626).

---

## 3. Paper framing — the claims

A paper is cited for a **claim**, not an artifact. We carry five; we **lead with C4 (recovery)**,
supported by C1 — the story is *"agents recover measurably more when attribution works."*

- **Claim C1 — injection-grounded attribution.** Controlled fault injection yields **known
  injected-site labels**, where prior benchmarks (Who&When 2505.00212, TRAIL 2505.08638,
  TraceElephant 2604.22708) rely on post-hoc human *annotation*. We release the first **leakage-free**
  attribution test-set with by-construction labels and re-measure attributors (incl. dumb baselines)
  against it. *Honesty (D-009): the injected site is known by construction; that it CAUSED the failure
  is established separately by paired sham controls + the resume failing — we claim "known
  injected-site + causal-effect validation", NOT "perfect causal labels".*
- **Claim C2 — fault-resolved degradation.** Vary only the injected fault (type × volume × position)
  with the task held constant, and use **paired sham controls** (same-volume neutral injection) to
  separate fault *damage* from generic context bloat. P[failure] surfaces per fault type, extending
  static context-rot (Chroma, NoLiMa 2502.05167) into agentic tool-use.
- **Claim C3 — the "blame gap".** Cross degradation (C2) with detectability (C1): faults that
  **break runs but evade attribution** = damage × (1 − detectability). Connects to monitor-blind-spot
  work (AuditBench 2602.22755, SLEIGHT-Bench 2605.16626) in the field's own language.
- **Claim C4 — localization enables recovery (LEAD, D-010).** Close the loop: detect → roll back to
  a pre-fault checkpoint → resume. Show **recovery rate is materially higher when attribution is
  correct** than under blind/random rollback — turning "synthetic labels are neat" into "debuggable
  agents recover X% more." Recovery is done by **replay in the mock env, NOT a general runtime**.
- **Claim C5 — mitigation frontier (v0.2 module, TRIMMED per D-013).** Score truncation, constraint
  pinning, and structured memory/context-editing on success-per-token × attribution-recoverability.
  Deferred until C1–C4 land (don't broaden before one trusted result).

---

## 4. Scope — IN vs OUT (the anti-drift contract)

**IN (we build this):**
- A deterministic **tool-use environment across 5 task domains** (D-011: travel-booking,
  calendar/email, ecommerce, repo-triage, spreadsheet/DB) with **stateful validators** — degradation
  is judged on final *state*, not LLM-judged prose.
- The **leakage-safe injector** (done, M1): typed faults × position × real volume, returning a
  `.public` (redacted) trace + a private label (`FaultRecord`).
- An **attribution harness**: **dumb baselines first** (recency / first-anomaly / random / diff-oracle
  / counterfactual-ablation) + LLM/Who&When-style attributors, all graded on the leakage-free
  `.public` trace vs known labels, with **bootstrap CIs** by base trajectory.
- **Degradation curves + paired sham controls** (C2), the **blame-gap map** (C3), the **recovery
  loop** (C4, headline), and (v0.2) the trimmed **mitigation frontier** (C5).
- Public artifacts: the injected-fault test-set + the harness + a short paper.

**OUT (explicitly deferred — adding these requires a §9 Decision-Log entry):**
- **Training** new attribution models or fine-tuning. We *benchmark* existing methods; laptop-scale.
- **Production telemetry / live observability tooling** (the OTel-GenAI "autopsy toolkit" idea).
  Deferred to a possible follow-on; not this repo.
- **Novel mitigation methods.** We treat Constraint Pinning (2606.22528), IterResearch O(1)-
  reconstruction (2511.07327), etc. as *baselines*, not contributions.
- **A new general agent benchmark.** We reuse frozen trajectories; we do not chase task coverage.
- **Multi-agent orchestration research.** Single-agent tool-use trajectories first; multi-agent
  only if M0 shows it's needed for attribution realism.
- **The "recoverable runtime" / agent-OS itself** (transactions, persistent checkpointing, permission
  & information-flow enforcement). DECLINED as a build (D-003): a systems megaproject, not a
  laptop-scale measured claim. NOTE: the **C4 recovery loop IS in scope** and is now the v0.1 headline
  (D-010) — but it is **replay-based rollback in the mock env measuring recovery rate**, a
  *measurement*, not a runtime.
- **Capability-security / prompt-injection defense** and **memory-as-continual-learning** — real
  frontier problems, but different skillsets/projects. Noted, not pursued here.

---

## 5. Method skeleton (the pipeline)

```
frozen successful trajectory  ──►  fault injector  ──►  (re)run / replay  ──►  outcome
   (task held constant)            type × pos × vol         deterministic        success?
                                         │                                          │
                                         │ (ground-truth fault + step known)        │
                                         ▼                                          ▼
                              ┌─ (A) DEGRADATION: P[fail | type,vol,pos]  ─── Claim C2
                              │
                              └─ (B) ATTRIBUTION: attributor(trace) → guess ── Claim C1
                                        compare guess vs known label
                                        │
                          C3 blame-gap = damage × (1 − detectability)
                          C4 recovery  = detect → rollback → resume; recovers X% more when localized
                          C5 (v0.2)    = mitigation frontier: success/token × recoverability
```

Attribution consumes only the **redacted `.public` trace** (markers + labels stripped); the private
`FaultRecord` is the answer key (D-009). Degradation uses **paired sham controls** to isolate damage.

**Fault manifest (v0 — in `d2b/faults.py`; the idea space is NOT frozen, D-013):**
`debris` (irrelevant tool output), `staleness` (superseded result lingers), `contradiction`
(conflicting retrieval), `wrong_tool` (plausible-wrong call swap), `constraint_drop` (policy evicted
— the ConstraintRot special case), `tool_forgetting` (schema buried under volume). Every fault now
has a real `volume` severity knob.

---

## 6. Feasibility — subscription-native inference (<$100 target, likely ~$0)

**The inference engine is the Claude Max subscription, not a paid API.** The Claude Code session and
every subagent it spawns run on the owner's existing $200/mo Max plan → **marginal cost $0** (D-007).
We make Claude (this session + fan-out subagents) the experiment's model:

- **Generate** healthy trajectories by running the agent loop against the mock tools, in-session.
- **Resume-live** degradation by having a subagent continue a trajectory from the injection point.
- **Attribute** with a *fresh-context* subagent that reads a corrupted trace and names the culprit.
- **Inject / score / plot** are deterministic code — free regardless.

**Consequences of going subscription-native (design constraints, not blockers):**
- **Scale = small & curated** (~40–60 trajectories across 5 domains, 6 faults, few positions) — rate
  limits forbid thousands of automated calls; done in batches across sessions. A hand-curated eval
  set is a feature, not a weakness.
- **Panel = 3 Claude TIERS** (Opus 4.8 / Sonnet / Haiku), which doubles as a real research axis:
  *does the self-poisoning death-spiral hit weaker tiers harder?* **We call them tiers, not "model
  families" (D-012)** — cross-provider is declined for v0.1 ($0). The generator-and-grader-are-both-
  Claude **circularity is documented as a limitation** (R6), mitigated by fresh-context attributor
  subagents + injection-defined truth; a <$50 cross-provider smoke test is a v0.2 option.
- **Reproducibility** preserved by freezing + releasing the trajectory dataset + injector + analysis;
  users replay the artifact deterministically even though generation was subscription-native.

Fallback (if we ever want to scale past rate limits): the old paid-API path — Batch API (50% off) +
prompt caching (~0.1× reads) + cached outcomes — still applies, but is **not** needed for v0.1/v0.2.

---

## 7. Success criteria

- **M2 (v0.1):** at least one fault type shows a statistically clean (bootstrap-CI) degradation curve
  vs its **sham control** AND a measurable attribution gap vs the known label, on the 3-Claude-tier
  panel, in ≥3 of the 5 domains. Traces are leakage-free (done).
- **Headline (C4 recovery):** recovery rate is **higher under correct localization than blind/random
  rollback**, across ≥3 tiers — "agents recover X% more when attribution works." This is the money
  figure, alongside the blame-gap map (C3).
- **Artifact:** the test-set + harness are reproducible from a single `make` / script with cached
  outcomes checked in.
- **Impressiveness (D-006, co-equal with the above):** a striking single headline figure (the blame-
  gap map), a runnable demo ("watch one fault break a trace + see who catches it"), and a clean README
  are first-class deliverables — we optimize for a reviewer's "oh, that's cool," not for niche novelty.

**Metrics vocabulary (dependability-native — `pass@1` is dead).** We adopt the reliability-era
metrics so the work is legible to the METR/Anthropic evals audience: **pass^k** (task succeeds on
all k independent resamples — reliability, not luck), **recovery rate** (fraction of injected faults
a detect→rollback loop recovers — the C4/v0.1 headline metric), **irreversible-error rate**, and
**unnecessary-escalation rate**. These slot directly onto the degradation and blame-gap maps.

---

## 8. Traceability matrix (claim → evidence → status)

| Claim | Needs (evidence) | Experiment | Status |
|---|---|---|---|
| C1 injection-grounded attribution | attributor acc vs known label; dumb baselines; leakage-free | exp02 | ⬜ not started |
| C2 fault-resolved degradation | P[fail] surface per fault + sham control; bootstrap CIs | exp01 | ⬜ not started |
| C3 blame gap | damage × (1−detectability) map | exp03 | ⬜ not started |
| **C4 recovery (LEAD)** | recovery rate: correct-localization vs blind rollback | exp04 | ⬜ not started |
| C5 mitigation frontier (v0.2) | success/token × recoverability, trimmed set | exp05 | ⬜ deferred |
| infra: leakage-safe split + FaultSite + volume knobs | public/private + kind-tagged labels + severity | M1 | ✅ done |
| related-work scan (non-gating) | borrow-list, no pivot | M0 / `docs/novelty.md` | ✅ closed |

---

## 9. Decision log (append-only — no silent pivots)

- **D-000 (2026-06-30):** Project chosen from a deep-research pass over context-rot / observability /
  tool-use-limits. Lead = **C1 injection-grounded attribution** (the fusion gap), *not* a standalone
  constraint-survival benchmark — because ConstraintRot (2606.22528, June 2026) already occupies the
  latter. Constraint-drop is demoted to **one fault type among six**. Mitigation Pareto kept as a
  module (C4), not the lead.
- **D-001 (2026-06-30):** Package name `d2b`, repo `debris-to-blame` (SEO-literal, sibling
  convention). Stack = uv + hatchling, ruff-100, pytest. GitHub repo created **private + empty**;
  scaffold intentionally **not committed** until owner approves the structure.
- **D-002 (2026-06-30):** Single-agent tool-use trajectories are the v0 substrate; multi-agent
  attribution deferred to OUT (§4) pending M0 evidence it is needed.
- **D-003 (2026-06-30, dependability reframe):** Triggered by an external scan (OpenAI Codex) of
  2026 open problems, whose citations were verified real (ReliabilityBench 2601.06112, AuditBench
  2602.22755, SLEIGHT-Bench 2605.16626, MemGym 2605.20833, SciAgentArena 2606.12736, STATE-Bench,
  SentinelBench 2606.05342, OpenAI Deployment Sim; METR ~14.5h@50%). **Accepted:** raise narrative
  altitude to the dependability frontier (§2a) and adopt dependability metrics (§7). **Declined:**
  its headline recommendation to *build a recoverable runtime / agent-OS* — a systems megaproject
  that violates laptop-scale + "avoid another framework." We measure the diagnose-and-recover
  primitive instead. Scope surface unchanged; only the story and metrics grew.
- **D-004 (2026-06-30):** Added **M6 recovery-probe** (ROADMAP) as the bounded bridge to the runtime
  vision — "detect → roll back to checkpoint → resume; does success return?" — exploiting that our
  injected faults have known ground truth. It is a *measurement*, not a runtime build.
- **D-005 (2026-06-30):** New nearest-neighbor to differentiate against in M0: **ReliabilityBench
  (2601.06112)** already does "chaos-engineering fault injection," but to measure pass^k under
  stress, NOT to create attribution ground truth. Diff owed in `docs/novelty.md` before M1.
- **D-006 (2026-06-30, novelty deprioritized):** Owner directive — optimize for *impressive /
  interesting / well-executed*, not for *novel / niche*. Copying an existing idea is acceptable.
  **M0 downgraded from a novelty-kill GATE to a light related-work scan** (still read the neighbors,
  but they cannot sink the project). Reallocated effort → headline figure, demo, execution polish.
  Added "impressiveness" as a co-equal success criterion (§7).
- **D-007 (2026-06-30, subscription-native inference):** Owner directive — target <$100, use the
  existing $200/mo Claude Max plan instead of a paid API. **The Claude Code session + its subagents
  are the inference engine** (marginal cost $0). Accepted the trade-offs: small curated scale
  (~40–60 trajectories), a **Claude-tier panel** (Opus/Sonnet/Haiku) rather than cross-provider,
  and semi-manual generation (mitigated by freezing/releasing the dataset). Paid-API path demoted to
  a scale-only fallback (§6). Cross-provider panel is an optional <$50 top-up, not baseline.
- **R6 (validity risk, logged here):** same model family generates AND grades. Not circular — truth
  is set by *injection*, not by any model — and attribution uses fresh-context subagents blind to the
  generation. Documented as a paper limitation; spot-check a subset with a different grader if a
  small API top-up is used.
- **D-008 (2026-06-30):** Owner decisions locked. (a) Scaffold **committed + pushed public** on first
  commit — stakes an early public claim; scaffold-only visibility is fine. (b) v0.1 panel = **Claude
  tiers only** (Opus 4.8 / Sonnet / Haiku), $0; cross-provider top-up NOT taken for v0.1 (revisit at
  v0.2 if a broader claim is wanted).
- **D-009 (2026-06-30, Codex audit adopted):** An adversarial repo audit (OpenAI Codex) surfaced
  real, experiment-independent flaws — all fixed in M1: (1) **answer leakage** — `inject()` now
  returns a public/private split (`Corruption.public` is redacted; `FaultRecord` holds the label);
  (2) **kind-tagged `FaultSite`** replaces the ambiguous raw-int position; (3) **real `volume`
  severity** for all six faults (was a no-op for four); (4) **honest reframe** — "known injected-site
  + causal-effect validation via sham controls", not "perfect causal labels". Also adopted for M2:
  deterministic **validators**, **dumb baselines**, **paired sham controls**, **bootstrap CIs**.
- **D-010 (2026-06-30, owner directive — RAISE THE BAR):** **Recovery elevated from a stretch probe
  to the v0.1 HEADLINE (Claim C4).** Story = "agents recover X% more when attribution works." Still
  replay-based rollback in the mock env, NOT a runtime. Supersedes D-004's "M6 recovery-probe only".
- **D-011 (2026-06-30, owner directive):** v0.1 spans a **5-domain suite** (travel, calendar/email,
  ecommerce, repo-triage, spreadsheet/DB) — escapes the single-fixture "toy" critique. Fixture stays
  as the deterministic test double.
- **D-012 (2026-06-30, owner directive):** **Stay $0 Claude-tiers-only.** Call them **tiers, not
  families**; document the same-family generate+grade **circularity as a limitation** (R6) rather
  than buy a cross-provider panel. A <$50 cross-provider smoke test is a v0.2 option.
- **D-013 (2026-06-30, Codex cut-list):** **Trim the mitigation frontier to 3** (truncation,
  constraint pinning, memory/context-editing) and defer it to v0.2. **Do not freeze the fault enum** —
  freeze the *manifest* (`test_smoke` now asserts presence, not closure). Leaderboard / multi-agent /
  recovery-runtime stay OUT.
- **D-014 (2026-06-30, M2 exp01 design lessons — from the first real cell):** (a) **a dropped
  constraint only causes damage if it was BINDING** — the first cell (travel + constraint_drop) gave
  Δ=0 because the model intrinsically avoids red-eyes and the violation saved only $50. Fixtures used
  to measure `constraint_drop` (and other decision faults) must make violating the rule TEMPTING
  (cheaper/only-viable shortcut). (b) `render_prefix` must include **tool arg schemas** (agents
  guessed `{"flight":...}` vs the expected `{"id":...}`). Both are prerequisites before scaling exp01.
- **D-016 (2026-07-02, Codex round-3 review CLOSED + adversarially verified):** The multi-step
  CONFERENCE_TRIP was redesigned to fix 5 blockers + 3 issues, then **re-verified by an
  adversarial-verification workflow (9 red-teamers, own repros)** — all CLOSED. (1) **Interactive
  rollout** (`d2b/rollout.py`) — ReAct loop; world=truth, injector corrupts only the shown
  observation; parse_fail is an outcome. (2) **Staleness bites** — `latest_quote` authoritative +
  versioned (surge model); a real-model smoke shows 0/4 (control) → 2/4 (stale) book the over-budget
  trap. (3) **Event-log validator** un-gameable (5 attacks fail). (4) **No get_policy leak**;
  constraint_drop also scrubs message contents. (5) **Valid sham** (inert rental-car rule via
  `TaskSpec.sham_plan`). (6) parse_fail counted (grid). (7) `grade_attribution` grades the specific
  rule (+unit tests). (8) CONFERENCE_TRIP in ALL_DOMAINS. Residuals hardened: sham fallback drops the
  last (not a position-dependent, possibly-binding) rule; rollout guards non-dict decisions. 91 tests
  green. **Still open (next step, not a blocker): wire an experiment that runs degrade/attribute/
  recover on CONFERENCE_TRIP via interactive_rollout + task variants.**
- **D-015 (2026-07-02, Codex rigor review adopted):** A 2nd Codex review (mostly correct) drove
  honesty fixes: (a) replaced "CI non-overlap ⇒ effect is real" with a proper **Fisher exact** test
  (`d2b/stats.py:fisher_p`); within-cell effects p=0.008 (significant *for the cell*), but samples
  are **resamples of ONE prompt**, not independent task draws — stated explicitly. (b) **Sonnet 2/4
  is NOT a finding** (Opus-vs-Sonnet Fisher p=0.43); reframed as "no significant tier difference,
  needs ~16–20/tier". (c) **parse failures are outcomes** (`parse_fail`), not silent drops.
  (d) fixed stale/contradictory Caveats; **exp02 numbers marked STALE** pending a rerun on the
  date-fixed trace. (e) documented that **shams are not uniformly valid controls** (domain-specific;
  need a per-domain sham-plan). **Accepted highest-priority next step:** rerun the whole slice on ONE
  genuinely **multi-step task** (Codex's "Conference Trip + Expense Pack") with domain-specific shams
  and parse failures counted — the single fix that turns this from a polished toy into a measurement
  artifact.
- **D-017 (2026-07-02, owner directive "do everything, ambitiously" — FULL LOOP ON THE MULTI-STEP
  TASK):** Executed the multi-phase program that D-016 left open. (A) **Variant factory** —
  `make_conference(cfg)` + 4 independent catalogs (`CONFERENCE_VARIANTS`); n is now *task-level*.
  (B) **Degradation surface** (`experiments/conf_score.py`, 48 interactive rollouts): `constraint_drop`
  on binding rules = **8/8, Fisher p = 0.0002** (red-eye *and* refundable, across 4 variants — a real
  claim, not a saturated cell); staleness **partial 0.50** (quote re-verification lets ~half dodge the
  surge); contradiction + sham **null**. (C) **Attribution / blame gap** (`experiments/attr_score.py`,
  16 detective subagents, graded against the *specific* dropped rule): blind **0/8 → with-policy 7/8**,
  **blame gap +0.88**. (D) **Recovery** (`experiments/conf_recover_score.py`, 16 `blind_repair`
  interactive rollouts): no_repair **0.00** / blind_repair **0.06** / targeted_repair **1.00**,
  **localization lift +0.94** — recovery is gated on correct localization. Combined headline
  `assets/conf_headline.png` promoted to the README lead; the travel cell demoted to a `<details>`
  proof-of-mechanism. Recovery replays from committed `experiments/decisions/recovery_states/br_*.json`.
  113 tests green, ruff clean. **This closes the "de-toy" arc — the loop now holds on a multi-step task
  with significance.** Next scope: enlarge (more variants / other domains / mitigation frontier M5).
- **D-018 (2026-07-02, owner directive "do all steps 1-7 + fix every issue" — DE-CONTAMINATION &
  HONEST REGIME):** A self-run next-steps workflow (adversarially verified in-code) found the D-017
  headline was CONTAMINATED: `attribute.py` handed the detective the full policy *including the dropped
  rule*, so `blind→with-policy 0→0.88` largely measured answer-copying, and the degradation used
  *scripted-oracle* policies that were told to take the trap. Fixed all seven review items + the
  contamination, re-collecting a **canonical sincere-agent dataset** (56 committed rollout states, 4
  variants × 2 reps × 7 conditions). Outcomes (all replayable, $0): **(1)** honest degradation —
  staleness 8/8 and forget:expense 8/8 (variant-clustered p=0.029), cdrop:refundable 7/8 (p=0.14),
  **cdrop:red-eye 0/8 NULL** (rule redundant with agent preference — the scripted 8/8 was an artifact;
  validates D-014). **(2)** de-contaminated **blame-gap map**: `blind`/`de-leak`(rulebook minus the
  line)/`oracle`(full spec = labelled UPPER BOUND) arms → cdrop is a *deletion gap* (blind 0, de-leak
  0, oracle 1.0 — only re-supplying the exact rule attributes it); **staleness is a *deception gap*
  (blind 0 AND oracle 0 — the cached quote fools the auditor too; needs ground-truth state, not
  policy)**; forget is *visible* (blind 1.0, no gap). Dumb baselines (random/recency/keyword) floor at
  ~0 recall / 100% FP → the LLM oracle is real work. **(3)** cross-tier: Haiku/Sonnet/Opus all give
  blind 0 → oracle 1.0 (R6 within-family lower bound). **(4)** recovery re-collected on the binding
  fault: localization lift +1.00. **(5)** external validity: 0/22 organic failures elicitable (Haiku
  on healthy + a hard tight-margin variant) → documented R2 limitation + structural face-validity
  argument. New code: `attribute.py` de-leak arm, `attr_baselines.py`, `attr_common.record_for`,
  `stats.cluster_by_variant`, `step.py forget:<tool>`, `conf_attr_score.py`, `conference_hard` variant.
  Docs de-inflated (README leads with the blame-gap map; results.md marks the old numbers SUPERSEDED;
  **M2's ≥3-domain bar explicitly NOT claimed met** — only CONFERENCE_TRIP is wired). 124 tests green,
  ruff clean. **The honest artifact is stronger than the contaminated one: a fault-type-resolved
  observability map, not a single saturated number.**
- **D-019 (2026-07-03/04, owner committed to a FULL RESEARCH PAPER — Phase 0 GO + Phase 1 + E1/E2):**
  (a) **Prior-art verification GO with narrowed novelty:** a verify-and-read pass (2 independent
  readers/paper + raw-PDF adjudication; fetch-echo caught and discarded) confirmed AEGIS (2509.14295)
  and AgenTracer (2509.03312) already do injection→attribution-labels, and ReliabilityBench
  (2601.06112) already built the live-corruption + state-oracle instrument. **The surviving novelty is
  the FINDING (claim 3): attribution difficulty is fault-type-structured** — none of them stratify by
  fault type or auditor information. Paper reframed finding-led (`docs/paper/framing.md`,
  `docs/paper/related_work.md`). (b) **Three interactive domains** (`d2b.DOMAINS`): conference +
  scheduling (`d2b/scheduling.py`) + review (`d2b/review.py`), each a 4-variant factory with an
  event-log world-state validator and a DIFFERENT staleness deception (price / availability / CI).
  (c) **Two integrity fixes, both regression-free on conference:** validator relaxed to
  "confirmed-at-least-once" (the "latest-check" rule failed sincere agents that explore); staleness
  injectors corrected to TRUE deceptions (swap only the value, keep the "(live)" tag) after the first
  audit showed the "(cached)" tell made staleness ~0.5 blind-attributable. (d) **E1/E2 DONE — the
  cross-domain result:** deception gap replicates **3/3** (staleness blind 0, oracle 0 everywhere);
  deletion gap **2/2** (blind 0, de-leak 0, oracle 1.0; review cdrop null = D-014 redundancy);
  omission (forget) is a CULPABILITY-vs-CAUSATION effect (mechanism verified, salience hypothesis
  refuted: agents attempted the missing tool 8/8 on all domains — auditors SEE the failure; they
  blame the agent only where the omission is mid-sequence and forces the agent's own next action to
  violate a rule (conference 8/8); on terminal omissions they correctly answer "no agent mistake"
  (~0) — so the "did the agent err?" question under-counts environment faults; Phase 3 adds a
  root-cause arm "why did this run fail?"). Honest framing = TWO robust regimes + the
  culpability-split omission case. 195 committed verdicts; `assets/blamegap_map.png`; M2 ≥3-domain bar met on the domains axis
  (ROADMAP updated; v0.1 still un-tagged: tier panel conference-only, recovery one domain).
  (e) **Phase-4 plan updated:** cross-provider grading via the owner's Codex subscription (OpenAI
  models with repo access run `attribute.py` themselves) → Phase 4 becomes $0.
