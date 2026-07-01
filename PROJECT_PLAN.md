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

- **Date of last update:** 2026-06-30 (Session 2 — subscription-native + novelty deprioritized)
- **Lead framing:** Claim C1 — *injection-grounded attribution* (see §3), positioned as **the
  measurement floor under recoverable long-horizon agents** (see §2a).
- **Milestones complete:** M0 (light related-work scan) ✅ · **M1 (injector + mock env + demo)** ✅
- **Next milestone:** **M2 — degradation + attribution (v0.1)** on a Claude-tier panel,
  subscription-native. First real empirical claim.
- **Repo health:** scaffold committed + pushed; **public** at `github.com/gimocimo/debris-to-blame`
  (D-008). Smoke tests pass.
- **Headline result so far:** none. No claim is real until M2 lands on a real (Claude-tier) panel.
- **Optimize for:** *impressive, interesting, well-executed* over *novel/niche* (D-006). Copying an
  existing idea is fine; a clean headline figure + a working demo beats a defensible-but-dull gap.
- **Biggest open risk:** now **execution + validity**, not novelty. Chief validity risk: the same
  model family generates and grades — mitigated because ground truth comes from *injection*, not a
  model, and attribution runs in fresh-context subagents (R6).
- **Latest handoff:** `handoffs/0004-m1-injector.md`

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

A paper is cited for a **claim**, not an artifact. We carry four; we **lead with C1**.

- **Claim C1 — injection-grounded attribution (LEAD).** Controlled fault injection yields *causal*
  ground truth for failure attribution, where all prior benchmarks (Who&When 2505.00212, TRAIL
  2505.08638, TraceElephant 2604.22708) rely on post-hoc human *annotation*. We release the first
  attribution test-set with by-construction labels and re-measure SOTA attributors against it.
- **Claim C2 — fault-resolved degradation.** Holding the task constant and varying only the injected
  fault (type × volume × position) decouples *rot* from *difficulty* — the controlled-injection
  wedge. We report P[failure] surfaces per fault type, extending the static context-rot literature
  (Chroma, NoLiMa 2502.05167) into the agentic tool-use setting.
- **Claim C3 — the "blame gap" (the novel framing).** Cross degradation (C2) with detectability
  (C1) to expose faults that **break runs but evade attribution**: damage × (1 − detectability).
  This quadrant is, to our knowledge, un-named in the literature and is the safety-relevant payoff.
- **Claim C4 — unified mitigation frontier (module).** Score truncation / compaction / RAG-over-
  history / memory-tool / context-editing / sub-agent-isolation on one frontier of *success-per-
  token × attribution-recoverability* — which no single benchmark unifies today.

---

## 4. Scope — IN vs OUT (the anti-drift contract)

**IN (we build this):**
- A deterministic, mock/frozen **tool-use environment** + **fault injector** (typed, parameterized
  by position and volume) operating on **frozen successful trajectories**.
- An **attribution harness** that runs existing attributors (LLM-judge, Who&When all-at-once /
  step-by-step / binary-search methods, trace-fed long-context models) against injected ground truth.
- **Degradation curves** (C2), the **blame-gap map** (C3), and the **mitigation Pareto** (C4).
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
- **The "recoverable runtime" / agent-OS itself** (transactions, checkpointing, permission &
  information-flow enforcement). Explicitly DECLINED as a build (D-003): it is a systems megaproject,
  not a laptop-scale measured claim, and it contradicts "avoid another agent framework." We measure
  the primitive it depends on and gesture at recovery via the bounded **M6 recovery-probe** only.
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
                          C4 Pareto    = success/token × recoverability under each mitigation
```

**Fault taxonomy (v0 — frozen in `d2b/faults.py`):**
`debris` (irrelevant tool output), `staleness` (superseded result lingers), `contradiction`
(conflicting retrieval), `wrong_tool` (plausible-wrong call swap), `constraint_drop` (policy evicted
— the ConstraintRot special case), `tool_forgetting` (schema buried under volume).

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
- **Scale = small & curated** (~40–60 trajectories, 6 faults, few positions) — rate limits forbid
  thousands of automated calls; done in batches across sessions. A hand-curated eval set is a
  feature, not a weakness.
- **Panel = Claude tiers** (Opus 4.8 / Sonnet / Haiku via model-switch), which doubles as a real
  research axis: *does the self-poisoning death-spiral hit weaker tiers harder?* Cross-provider
  (GPT/Gemini/DeepSeek) is **not** available from the subscription — optional API top-up (<$50) only
  if a cross-provider supplementary panel is wanted.
- **Reproducibility** preserved by freezing + releasing the trajectory dataset + injector + analysis;
  users replay the artifact deterministically even though generation was subscription-native.

Fallback (if we ever want to scale past rate limits): the old paid-API path — Batch API (50% off) +
prompt caching (~0.1× reads) + cached outcomes — still applies, but is **not** needed for v0.1/v0.2.

---

## 7. Success criteria

- **M2 (v0.1):** at least one fault type shows a statistically clean degradation curve AND a
  measurable attribution-recovery gap vs the known label, on a real model panel (not synthetic).
- **Paper-ready:** the blame-gap map (C3) shows ≥1 fault type that is high-damage + low-detectability
  across ≥3 model families — the headline figure.
- **Artifact:** the test-set + harness are reproducible from a single `make` / script with cached
  outcomes checked in.
- **Impressiveness (D-006, co-equal with the above):** a striking single headline figure (the blame-
  gap map), a runnable demo ("watch one fault break a trace + see who catches it"), and a clean README
  are first-class deliverables — we optimize for a reviewer's "oh, that's cool," not for niche novelty.

**Metrics vocabulary (dependability-native — `pass@1` is dead).** We adopt the reliability-era
metrics so the work is legible to the METR/Anthropic evals audience: **pass^k** (task succeeds on
all k independent resamples — reliability, not luck), **recovery rate** (fraction of injected faults
a detect→rollback loop recovers, measured in M6), **irreversible-error rate**, and
**unnecessary-escalation rate**. These slot directly onto the degradation and blame-gap maps.

---

## 8. Traceability matrix (claim → evidence → status)

| Claim | Needs (evidence) | Experiment | Status |
|---|---|---|---|
| C1 injection-grounded attribution | attributor accuracy vs known label, per method | exp02 | ⬜ not started |
| C2 fault-resolved degradation | P[fail] surface per fault type | exp01 | ⬜ not started |
| C3 blame gap | damage × (1−detectability) map | exp03 | ⬜ not started |
| C4 mitigation frontier | success/token × recoverability per mitigation | exp04 | ⬜ not started |
| novelty | no prior injection-grounded attribution bench | M0 / `docs/novelty.md` | 🟡 in progress |

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
