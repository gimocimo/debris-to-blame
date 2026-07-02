# ROADMAP — debris-to-blame

*How* we build the vision in `PROJECT_PLAN.md`. This file owns experiment mechanics, metrics, and
figures. Milestone-gated; each milestone ends with a `handoffs/NNNN-*.md` entry.

---

## 0. Problem statement (formal)

A successful agent trajectory is a sequence of steps `τ = (s_1, …, s_T)` (tool calls + outputs +
model turns) that completes task `g`. We define a **fault injector** `Φ(τ, f, p, v) → τ'` that
inserts a fault of **type** `f`, at **position** `p`, with **volume** `v`, producing a perturbed
trajectory `τ'` whose **ground-truth blame label is (f, p) by construction**.

Two measurements over `τ'`:

1. **Degradation** `D(f,p,v) = P[ task g fails | τ' ]` — does the fault break the run?
2. **Attribution** `A(f,p,v) = P[ attributor(τ') recovers (f, p) ]` — can the failure be localized?

The **blame gap** is the region where `D` is high but `A` is low — faults that silently break agents.

---

## 1. Literature anchors (ALL arxiv IDs verified 2026-06-30 — see `docs/novelty.md`)

| Theme | Anchor works | What we take |
|---|---|---|
| Failure attribution (the open gap) | Who&When (2505.00212, ICML Spotlight), TRAIL (2505.08638), TraceElephant (2604.22708) | The attribution task + their attributor methods as baselines; we supply the missing causal labels |
| Constraint survival (nearest prior art) | Governance Decay / ConstraintRot (2606.22528) | `constraint_drop` becomes ONE fault type; Constraint Pinning is a C4 mitigation baseline |
| Self-poisoning / compounding rot | IterResearch (2511.07327), SlopCodeBench (2603.24755) | Mechanism naming (suffocation/contamination); O(1)-reconstruction as a C4 baseline |
| Static context-rot (cold) | Chroma Context Rot, NoLiMa (2502.05167) | The controlled-length methodology we lift into the agentic setting |
| Failure taxonomy | HORIZON (2604.11978) | Fault-type vocabulary cross-check |
| Tool-use limits / MCP | MCP-Bench (2508.20453), RAG-MCP (2505.03275), MCPToolBench++ (2508.07575) | `wrong_tool` / `tool_forgetting` realism; M0 must search this angle deeper (flagged under-covered) |
| Reliability via fault injection (NEAREST NEIGHBOR) | ReliabilityBench (2601.06112) | injects faults for **pass^k under stress** — we injects for **attribution ground truth**; diff owed in novelty.md |
| Monitor blind spots (blame-gap framing) | AuditBench (2602.22755, "tool-to-agent gap"), SLEIGHT-Bench (2605.16626, 11 blind-spot classes) | cite the blame gap in the field's own language |
| Dependability horizon (narrative) | METR Time Horizons (~14.5h@50%, ~2.5–3.5h@80%; reward-hack confound) | the "capability > dependability" motivation |

---

## 2. Milestones

### M0 — Related-work scan (NOT a gate) ✅ DONE (2026-06-30)
- Closed as a light, non-gating scan (D-006). Borrow-list written in `docs/novelty.md`; no pivot.

### M1 — Harness + injector (frozen env) ✅ DONE (2026-06-30)
- `d2b/trajectory.py`: Message/ToolCall/Trajectory data model + JSON IO.
- `d2b/tools.py`: deterministic mock-tool environment (flight-booking) + decoy schemas.
- `d2b/faults.py`: `inject(traj, spec)` for all six fault types; ground-truth `blame_label` recorded.
- `d2b/fixtures.py`: a clean successful fixture trajectory.
- `scripts/demo_inject.py`: runnable demo (all 6 faults, zero model calls). `tests/test_inject.py`.
- **Exit met:** inject any fault into any frozen trajectory; 17 tests green; ruff clean; demo runs
  with bare `python3`. NOTE: `replay.py` (deterministic re-execution) deferred to M2, where it pairs
  with resume-live generation — no need for it before real trajectories exist.

### M1b — Domains + validators + resume (foundation for v0.1) ✅ DONE (2026-06-30)
- **5-domain suite (D-011):** travel, repo-triage, calendar, ecommerce, spreadsheet — each with a
  **stateful `Environment`** (`d2b/env.py`), a hand-authored successful trajectory, and a
  deterministic state **validator** (`d2b/validate.py: TaskSpec`).
- `d2b/replay.py`: deterministic `replay`/`evaluate` (static) + the `resume`/`Policy` interface for
  resume-live (M2 wires the model; an oracle policy tests the harness at $0).
- `wrong_tool` generalized to swap for a real in-domain tool (domain-agnostic, more realistic).
- **Exit met:** all 5 domains — healthy trajectory validates ✅, `wrong_tool` at the critical step
  breaks the state validator ✅, context-only faults leave static replay valid (documents the
  two-mode design) ✅. 47 tests green; ruff clean. Only the model-backed resume policy is left → M2.

### M2 — Degradation + attribution (v0.1) — 3 Claude tiers, subscription-native
- **Inference (D-007/D-012):** trajectories generated in-session; degradation resumed by subagents;
  attribution by **fresh-context subagents on the redacted `.public` trace**. Panel = 3 tiers.
- exp01 (C2): degradation surfaces `D(f,p,v)` per fault × tier × domain, **each vs a paired sham
  control**; **bootstrap CIs** by base trajectory. Tests the death-spiral-hits-weaker-tiers axis.
- exp02 (C1): attribution vs known labels — **dumb baselines first** (recency / first-anomaly /
  random / diff-oracle / counterfactual-ablation), then LLM/Who&When-style methods. Metrics: step /
  type / joint accuracy (TRAIL-style).
- Scale: ~40–60 curated trajectories across 5 domains, batched within rate limits.
- **Exit:** ≥1 sham-controlled degradation curve + a measurable attribution gap in ≥3 domains.
  **First real claim.**
- **Status (2026-07-02, D-018): PARTIALLY MET — on ONE domain only.** On the multi-step CONFERENCE_TRIP
  task (+4 variants) we have a sham-controlled, variant-clustered degradation surface AND a
  de-contaminated, dumb-baseline-anchored, cross-tier attribution map (M3's blame-gap map is effectively
  delivered here too). **What is NOT met: the ≥3-domain bar.** The other five domains remain single-step
  static fixtures, not wired into the interactive rollout. **M2 stays OPEN until a second (then third)
  domain is ported to `step.py`'s interactive loop.** Do not describe M2/v0.1 as closed.

### M3 — The blame gap (v0.1)
- exp03 (C3): blame-gap map `damage × (1 − detectability)` per fault × tier.
- **Exit:** ≥1 high-damage / low-detectability fault across ≥3 tiers → one headline figure.

### M4 — Recovery (v0.1 HEADLINE, D-010)
- exp04 (C4): close the loop — detect → roll back to a pre-fault checkpoint → resume → validate.
  Compare **correct-localization rollback vs blind/random rollback**.
- Metrics: **recovery rate**, irreversible-error rate, unnecessary-escalation rate, rollback cost.
- **Exit:** "agents recover X% more when attribution is correct," across ≥3 tiers. Tag v0.1. This is
  the money result. Replay-based rollback in the mock env only — NOT a runtime.

### M5 — Mitigation frontier (v0.2 module, TRIMMED — D-013)
- exp05 (C5): truncation, constraint pinning, structured memory/context-editing only (not all six).
  Measure success-per-1k-tokens × attribution-recoverability. Baselines: Constraint Pinning,
  O(1)-reconstruction. **Exit:** one frontier figure. Tag v0.2.

### M6 — Paper + artifact
- Short paper (workshop-length); release the leakage-free test-set + harness. Optional leaderboard
  (RefuseBench-style) stays OUT for now.

---

## 3. Metrics (frozen vocabulary)

- **Degradation:** `D = P[task fail | fault]`, reported as surfaces over (volume, position) per type.
- **Attribution:** step-accuracy, type-accuracy, joint-accuracy — all vs the *known injected* label.
- **Blame gap:** per fault type, `gap = ΔP[fail] · (1 − joint-accuracy)`.
- **Pareto:** success-per-1k-context-tokens (x) vs attribution-recoverability (y), per mitigation.
- **Dependability metrics (D-003):** `pass^k` (success on all k resamples), `recovery rate`,
  `irreversible-error rate`, `unnecessary-escalation rate`. Report these instead of bare `pass@1`.

---

## 4. Experiments index

| id | claim | one-line | status |
|---|---|---|---|
| exp01 | C2 | degradation surfaces per fault, vs sham control, bootstrap CIs | ⬜ |
| exp02 | C1 | attribution vs known labels: dumb baselines + LLM methods | ⬜ |
| exp03 | C3 | blame-gap map | ⬜ |
| exp04 | C4 | recovery: correct-localization vs blind rollback (HEADLINE) | ⬜ |
| exp05 | C5 | mitigation frontier (v0.2, trimmed to 3) | ⬜ |

---

## 5. Risk register

- **R1 — novelty (RETIRED).** Deprioritized (D-006); non-gating. No longer a project risk.
- **R2 — replay validity.** Injecting into a *frozen* trajectory and resuming may not reflect how a
  live agent would react. Mitigation: validate a subset against fully-live re-runs; report the delta.
- **R3 — same-family generate+grade circularity (documented limitation, R6/D-012).** Generator and
  attributor are both Claude. Mitigation: truth comes from *injection* (not a model); attribution
  reads only the redacted `.public` trace in fresh-context subagents; leakage-free enforced by test.
  A <$50 cross-provider smoke test is a v0.2 option to quantify residual bias.
- **R7 — answer leakage (RESOLVED, M1/D-009).** Fixed by the public/private split
  (`redact_for_attribution`); a per-fault test asserts `.public` carries no markers or label meta.
- **R4 — cost blowup.** Mitigation: Batch API + caching + cached outcomes (see PROJECT_PLAN §6).
- **R5 — ReliabilityBench overlap (2601.06112).** It already injects faults (chaos-engineering) to
  measure reliability. Mitigation: our object is *attribution ground truth + the blame gap*, not
  pass^k under stress; M0 writes the explicit diff. If it turns out they also grade attribution
  against injected labels, escalate — that would be a direct hit on C1.
