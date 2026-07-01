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

### M0 — Related-work scan (NEXT, NOT a gate) 🟡
- **Downgraded from novelty-kill to a light scan (D-006).** Novelty is no longer required; we
  optimize for execution + impressiveness. Skim ConstraintRot (2606.22528) and ReliabilityBench
  (2601.06112) enough to *cite and borrow* from them, not to prove we differ.
- Grab any reusable pieces (fault vocab, metrics, task ideas) — copying is fine.
- **Exit:** a short `docs/novelty.md` "related work + what we borrow" note. **No pivot condition** —
  the project proceeds regardless of what exists.

### M1 — Harness + injector (frozen env) ✅ DONE (2026-06-30)
- `d2b/trajectory.py`: Message/ToolCall/Trajectory data model + JSON IO.
- `d2b/tools.py`: deterministic mock-tool environment (flight-booking) + decoy schemas.
- `d2b/faults.py`: `inject(traj, spec)` for all six fault types; ground-truth `blame_label` recorded.
- `d2b/fixtures.py`: a clean successful fixture trajectory.
- `scripts/demo_inject.py`: runnable demo (all 6 faults, zero model calls). `tests/test_inject.py`.
- **Exit met:** inject any fault into any frozen trajectory; 17 tests green; ruff clean; demo runs
  with bare `python3`. NOTE: `replay.py` (deterministic re-execution) deferred to M2, where it pairs
  with resume-live generation — no need for it before real trajectories exist.

### M2 — Degradation + attribution (v0.1, Claude-tier panel)
- **Inference is subscription-native (D-007):** trajectories generated in-session; degradation
  resumed by subagents; attribution by fresh-context subagents. Panel = Opus 4.8 / Sonnet / Haiku.
- exp01: degradation surfaces `D(f,p,v)` per fault type × tier (tests the death-spiral-hits-weaker-
  tiers hypothesis).
- exp02: attribution `A(f,p,v)` — LLM-judge + ≥2 Who&When-style methods vs known labels.
- Metrics: step accuracy, fault-type accuracy, joint accuracy (TRAIL-style); pass^k across tiers.
- Scale: ~40–60 curated trajectories, done in batches within rate limits.
- **Exit:** ≥1 clean degradation curve + a measurable attribution gap on the Claude-tier panel.
  **First real claim.** Tag v0.1.

### M3 — The blame gap (the headline)
- exp03: blame-gap map `damage × (1 − detectability)` per fault type × model family.
- **Exit:** ≥1 high-damage / low-detectability fault across ≥3 families → headline figure.

### M4 — Mitigation Pareto (module, v0.2)
- exp04: for each mitigation (truncation, compaction, RAG-over-history, memory-tool, context-editing,
  sub-agent isolation) measure success-per-1k-tokens AND attribution-recoverability.
- Include provider-native baselines (Constraint Pinning, O(1)-reconstruction).
- **Exit:** one Pareto frontier figure unifying cost / quality / detectability. Tag v0.2.

### M5 — Paper + artifact + leaderboard
- Short paper (workshop-length); release injected test-set + harness; optional public leaderboard
  (RefuseBench-style publishing loop).

### M6 — Recovery probe (the bridge to the "recoverable runtime" vision) — STRETCH
- The bounded gesture at recoverability (D-004), NOT a runtime build. Because injected faults have
  known ground truth, we can close the loop: **detect the fault → roll back to a pre-fault
  checkpoint → resume generation → did task success return?**
- Metrics: **recovery rate**, **irreversible-error rate**, **unnecessary-escalation rate**, cost
  overhead of checkpoint/rollback.
- **Exit:** a recovery-rate number per fault type — the natural sequel-paper hook ("attribution is
  the floor; here's what recovery buys once you have it"). Explicitly out of scope to build a
  general transactional runtime; we replay checkpoints in the mock env only.

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
| exp01 | C2 | degradation surfaces per fault type | ⬜ |
| exp02 | C1 | attribution recovery vs known labels | ⬜ |
| exp03 | C3 | blame-gap map | ⬜ |
| exp04 | C4 | mitigation cost–quality–detectability Pareto | ⬜ |

---

## 5. Risk register

- **R1 — gap already closed.** A 2026 paper may already inject for attribution ground truth. M0 gates
  everything. Mitigation: C4 is a fallback lead.
- **R2 — replay validity.** Injecting into a *frozen* trajectory and replaying may not reflect how a
  live agent would react. Mitigation: validate a subset against live re-runs; report the delta.
- **R3 — LLM-judge attribution circularity.** Using an LLM to attribute faults an LLM caused. Mitigation:
  known ground truth breaks the circularity (we never rely on the judge to *define* truth, only to
  *recover* it).
- **R4 — cost blowup.** Mitigation: Batch API + caching + cached outcomes (see PROJECT_PLAN §6).
- **R5 — ReliabilityBench overlap (2601.06112).** It already injects faults (chaos-engineering) to
  measure reliability. Mitigation: our object is *attribution ground truth + the blame gap*, not
  pass^k under stress; M0 writes the explicit diff. If it turns out they also grade attribution
  against injected labels, escalate — that would be a direct hit on C1.
