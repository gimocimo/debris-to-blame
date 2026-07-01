# Novelty map — debris-to-blame

> **Note (D-006): novelty is deprioritized.** We optimize for *impressive / well-executed*, not for
> *novel / niche* — copying existing ideas is fine. This doc is now a **related-work + what-we-borrow**
> reference, NOT a kill-gate. Nothing below can sink the project; it just tells us whom to cite and
> what to reuse.

*Status: 🟡 M0 (light related-work scan) in progress.* All arxiv IDs below were **verified real on 2026-06-30** by fetching the
abstract pages (titles quoted verbatim). The headline gap-claim is **not yet kill-tested** — that is
the M0 exit condition.

---

## The one-paragraph gap

Automated failure attribution for agentic tool-use is an open problem precisely because **no
benchmark has causal ground truth**: Who&When, TRAIL, and TraceElephant all rely on humans
*annotating* which step "looks" responsible in organically-failed traces, and that label is itself
unverifiable. **debris-to-blame inverts the data-generating process** — we *inject* a typed fault at
a known step into a known-good trajectory, so the blame label is correct by construction. No verified
2026 source does this. The adjacent works each occupy *one* neighbouring tile — attribution-on-
annotated-traces, constraint-survival, compounding-rot, mitigation-in-isolation — but **none unifies
controlled injection (causal labels) with attribution recovery and a cost–quality–detectability
frontier**. That intersection is the claim.

---

## Prior-art kill-list (the 3 nearest rivals)

### 1. Governance Decay / ConstraintRot — [2606.22528](https://arxiv.org/abs/2606.22528)
*"Governance Decay: How Context Compaction Silently Erases Safety Constraints in Long-Horizon LLM
Agents"* — Shiyang Chen, Jun 21 2026 (v1), Jun 27 (v2). **Nearest prior art.**
- **What it occupies:** the constraint-survival-curve idea (violations 0%→30%, peak 59% after
  compaction; survived-vs-dropped 0% vs 38%); a Compaction-Eviction Attack; the *Constraint Pinning*
  mitigation (→0%).
- **How we differ (≥5 axes):** (1) constraint-drop is **one of six** fault types for us, not the whole
  paper; (2) our object is **attribution recoverability**, not violation rate; (3) we have **causal
  ground truth via injection**, they measure an emergent rate; (4) we produce a **blame-gap map**
  (damage × undetectability) they don't; (5) Constraint Pinning is a **C4 baseline** for us, not a
  contribution. **Action:** read in full during M0; cite as the constraint-drop anchor.

### 2. Who&When — [2505.00212](https://arxiv.org/abs/2505.00212)
*"Which Agent Causes Task Failures and When? On Automated Failure Attribution of LLM Multi-Agent
Systems"* — Zhang et al., ICML 2025 Spotlight.
- **What it occupies:** *defines* the attribution task; 127 annotated failure logs; best method 53.5%
  agent / 14.2% step; three attributor methods (all-at-once, step-by-step, binary-search).
- **How we differ:** they **annotate** organic failures (no verifiable ground truth, multi-agent);
  we **inject** (causal ground truth, single-agent tool-use first). Their three methods become our
  **attributor baselines** — we re-measure them against labels that are actually correct.

### 3. TRAIL — [2505.08638](https://arxiv.org/abs/2505.08638)
*"TRAIL: Trace Reasoning and Agentic Issue Localization"* — Deshpande et al. (Patronus AI).
- **What it occupies:** 148 human-annotated traces, formal error taxonomy, OTel spans; best model
  (Gemini-2.5-pro) 11% joint accuracy.
- **How we differ:** same annotation-vs-injection distinction; we add **controlled volume/position**
  (their faults are organic, ours are parameterized), enabling degradation *surfaces* not point
  estimates. Their taxonomy cross-checks our six fault types.
- **Note:** two *stronger* TraceElephant (2604.22708) claims (attribution 65.9%/30.3%; +76%
  observability lever) were **refuted in verification** — do **not** cite those magnitudes.

---

### 4. ReliabilityBench — [2601.06112](https://arxiv.org/abs/2601.06112)
*"ReliabilityBench: Evaluating LLM Agent Reliability Under Production-Like Stress Conditions"* (Jan
2026). **Nearest fault-injection neighbor** (surfaced by the Codex-citation verification pass).
- **What it occupies:** injects faults ("chaos-engineering") + perturbations to measure a reliability
  surface `R(k,ε,λ)` via **pass^k**.
- **How we differ:** they inject to measure *whether* reliability drops under stress; we inject to
  create *causal attribution labels* and measure *whether the fault can be localized* (C1) and *which
  faults are undetectable* (C3, the blame gap). Fault-injection-for-reliability ≠ fault-injection-
  for-attribution-ground-truth. **M0 must confirm they do not also grade attribution against injected
  labels** — if they do, that's a direct hit on C1 (see ROADMAP R5).

## Field map (what's covered vs open)

| Tile | Covered by | Open for us |
|---|---|---|
| Cold long-context rot | Chroma Context Rot; NoLiMa ([2502.05167](https://arxiv.org/abs/2502.05167)) | lift the controlled-length method into agentic tool-use |
| Self-poisoning mechanism | IterResearch ([2511.07327](https://arxiv.org/abs/2511.07327)) | *named*, not *attributed* — we localize it |
| Compounding rot (coding) | SlopCodeBench ([2603.24755](https://arxiv.org/abs/2603.24755)) | domain-specific; general tool-use open |
| Failure taxonomy | HORIZON ([2604.11978](https://arxiv.org/abs/2604.11978)) | taxonomy yes; *controlled injection* no |
| Constraint survival | ConstraintRot ([2606.22528](https://arxiv.org/abs/2606.22528)) | one fault type for us |
| Attribution (annotated) | Who&When, TRAIL, TraceElephant | **attribution with causal labels — OPEN** |
| Reliability via fault injection | ReliabilityBench ([2601.06112](https://arxiv.org/abs/2601.06112)) | injects for **pass^k**, not attribution labels — see kill-list #4 |
| Monitor blind spots | AuditBench ([2602.22755](https://arxiv.org/abs/2602.22755)), SLEIGHT-Bench ([2605.16626](https://arxiv.org/abs/2605.16626)) | our "blame gap" = a measured blind-spot map; cite in their language |
| Tool-use limits / MCP | MCP-Bench (2508.20453), RAG-MCP (2505.03275), MCPToolBench++ (2508.07575) | **under-searched — M0 must deepen** |
| Mitigation (in isolation) | Constraint Pinning, IterResearch O(1) | **unified cost–quality–detectability frontier — OPEN** |

---

## M0 exit checklist
- [ ] Read ConstraintRot 2606.22528 in full; confirm the 5-axis diff holds.
- [ ] Dedicated search: does any 2025–2026 work inject faults to get attribution ground truth?
      (search terms: "synthetic fault injection failure attribution agent", "controlled error
      injection trace localization LLM", "counterfactual fault agent attribution".)
- [ ] Deepen the tool-use-limits / MCP-failure-taxonomy search (flagged under-covered in research).
- [ ] **Read ReliabilityBench 2601.06112 in full** — confirm it does NOT grade attribution against
      injected labels (kill-list #4 / ROADMAP R5). This is the highest-priority new diff.
- [ ] Write the final one-paragraph gap; if closed, trigger §9 D-decision to pivot lead to C4.
