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

- **Date of last update:** 2026-06-30 (Session 3 — Codex audit adopted + recovery-headline reframe)
- **Lead framing:** **Claim C4 — localization enables recovery** ("agents recover X% more when
  attribution works"), supported by C1 injection-grounded attribution. The measurement floor under
  recoverable long-horizon agents (§2a).
- **Milestones complete:** M0 ✅ · **M1** ✅ (leakage-safe injector, `FaultSite`, real `volume`) ·
  **M1b** ✅ (5 stateful domains + validators + replay/resume harness; 47 tests green)
- **Next milestone:** **M2 — degradation + attribution + recovery (v0.1)** across the 5-domain suite
  on the 3-Claude-tier panel, subscription-native. Needs the model-backed resume `Policy`. Recovery
  (C4) is the headline. First real claim.
- **Scope bar (D-010/D-011):** raised — recovery-headline + 5 domains + validators + sham controls +
  dumb baselines + bootstrap CIs. Cost held at $0 (D-012).
- **Repo health:** scaffold committed + pushed; **public** at `github.com/gimocimo/debris-to-blame`
  (D-008). Smoke tests pass.
- **Headline result so far:** none. No claim is real until M2 lands on a real (Claude-tier) panel.
- **Optimize for:** *impressive, interesting, well-executed* over *novel/niche* (D-006). Copying an
  existing idea is fine; a clean headline figure + a working demo beats a defensible-but-dull gap.
- **Biggest open risk:** now **execution + validity**, not novelty. Chief validity risk: the same
  model family generates and grades (R6, documented limitation) — mitigated because ground truth
  comes from *injection*, not a model, and attribution runs on the redacted `.public` trace in
  fresh-context subagents. Scale (5 domains at $0) is the other risk — rate limits force batching.
- **COMPLETE VERTICAL SLICE (real inference, $0):** exp01 **degradation Δ=+1.00** (constraint_drop:
  dropped→5/5 red-eye vs healthy 0/5; baseline non-tempting Δ=0) → exp02 **blame gap +1.00**
  (trace-only attribution 0/5, with-policy 5/5) → exp04 **recovery**: targeted-repair 1.00 vs
  blind/no-repair 0.00 (**localization lift +1.00**). "Silently breaks → invisible in trace →
  recoverable only once localized." Thesis demonstrated end-to-end on one cell.
- **Latest handoff:** `handoffs/0011-writeup-headline-figure.md` (results section + `assets/headline.png`)

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
