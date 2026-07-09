# Paper framing — north star (v1, 2026-07-03)

The one document every later phase is measured against. Locked after the Phase-0 prior-art GO
([related_work.md](related_work.md)). If an experiment doesn't serve a contribution or defuse a
threat below, it is out of scope.

## Working title
**"When can you blame the right step? Fault-type-structured failure attribution for LLM agents."**

## Thesis (one sentence)
Using controlled fault injection as a *measurement instrument*, we show that **agent failure
attribution is not one problem but several: which information an auditor needs to localize blame is
determined by the fault type** — and in particular some faults (deceptions) are unattributable from
the execution trace and the reference policy alone.

## The finding, precisely (this is the contribution)
For a failed multi-step agent episode, define an **information ladder** available to an auditor:
`trace-only` ⊂ `trace + reference policy` ⊂ `trace + ground-truth world state`. Then attribution
success is **fault-type-structured**:
- **Visible faults** (e.g. a required tool/step omitted): attributable from the **trace alone**.
- **Deletion faults** (a governing rule was removed): invisible in the trace; attributable only once
  the **reference policy** is restored — the *deletion gap*.
- **Deception faults** (a corrupted observation the agent acted on): invisible in the trace **and not
  recovered by the reference policy**, because the corruption misleads the auditor as much as the
  agent; attributable only with **ground-truth state** — the *deception gap*.

The deception gap is the sharp, novel claim: **more observability of the rules does not help; you need
observability of the world.** It has a direct safety/oversight implication — logging traces and specs
is insufficient for a whole class of failures; you must retain re-verifiable ground truth.

**Phase-3 refinement (2026-07-04): the ladder gained an OUTCOME rung and a second deception type.**
Misexecution (deceptive confirmation) is blind-0 AND oracle-0; an outcome-informed *root-cause*
auditor recovers it **15/40** (across 5 domains) by inference ("visible decisions compliant + run
failed ⇒ a tool lied") — **but only when the failure symptom implicates the action tool** (conference
7/8, scheduling 6/8, review 2/8, and **0/8 on the incident chain and reconcile loop**). The same
framing closes the omission gap (**forget 40/40** — a culpability-question artifact) and recovers
staleness partially (**18/40**: conference 8/8, scheduling 7/8, review 3/8, but **0/8 on both new
shapes** — root-cause recovery of deceptions is task-shape-dependent, failing where an honest
alternative explanation for the same symptom is equally available). Final ladder: trace → +outcome →
+policy → +state, with fault types on different rungs. Caveats: the root-cause arm bundles
outcome-knowledge with the causation question (dissection = future work); cdrop×root-cause is an unrun
cell; misexec is graded strictly (action-locus + substitution) after a Codex audit caught a lenient
grader inflating it to 23/24. All incident/reconcile cells re-audited from committed states (an
earlier non-committed render put incident-forget-oracle at a dramatic 1/8; it is 7/8 on committed
data — the "oracle exonerates" instance did not replay, so it is not claimed).

**Cross-domain status (2026-07-04).** Two regimes are ROBUST across domains: the **deception gap**
replicates **3/3** (staleness: blind 0, oracle 0 on stale-price / availability / CI) and the
**deletion gap** replicates **2/2** (cdrop: blind 0, de-leak 0, oracle 1.0). The **"visible" category
is NOT clean**: forget is caught blind only when the missing step is *salient* (conference's
expense-report, 8/8) and is missed on minor steps (scheduling/review, ~0) even with the policy. So the
honest framing is **two distinct blame-gap regimes** (deletion vs deception, separated by what
information closes them), plus a softer, salience-dependent "omission" case — not a clean three-way
taxonomy. (Methodological note: the staleness injector was corrected mid-phase to a *true* deception —
no self-labelling "(cached)" tell — after the first audit showed the tell made it partly attributable;
the labelled-vs-unlabelled contrast is itself reportable.)

## Positioning (defensible after Phase-0 verification)
- **Injection→attribution-labels** (AEGIS 2509.14295, AgenTracer 2509.03312): they inject faults to
  **scale training data / train a tracer**. We inject as a **controlled instrument to characterize
  *when* attribution is possible**. Shared mechanism, different scientific goal; neither stratifies by
  fault type or by auditor information.
- **Injection→robustness** (ReliabilityBench 2601.06112, ConstraintRot 2606.22528, ToolMaze): live
  typed-fault injection with state oracles, but they **score success**, not attribution.
- **Attribution via annotation** (Who&When 2505.00212, TRAIL 2505.08638, TELBench): labels from
  **human annotation of organic failures** (α≈0.64 step-level; ~14% SOTA step accuracy). We replace
  the noisy label source with by-construction injection labels — and go beyond a benchmark to a
  structured *observability* result.
- **Causal attribution methods** (CAR 2606.08275): a do-operator/Shapley scoring method on an
  orthogonal axis; no fault-type/information stratification.

## Contributions (in priority order)
1. **C1 — the observability ladder finding** (the deception gap). The headline.
2. **C2 — the instrument that makes it measurable:** interactive live-corruption of only what the
   agent sees + an un-gameable world-state validator + a **typed fault taxonomy** (6 channels) crossed
   with **auditor information tiers** — the specific combination none of the prior works have.
3. **C3 — a re-ranking of attribution methods against clean labels:** dumb baselines + an LLM auditor
   + the oracle upper bound, showing what the field's accuracy *really* is once label noise is removed,
   and that the ranking is fault-type-dependent.
4. **C4 — localization → recovery:** repairing the correctly-localized fault recovers the task; a
   misdiagnosis does not (gated on C1).

## Load-bearing experiments (each MUST succeed or the claim narrows)
| # | Experiment | Why it's load-bearing | Status |
|---|---|---|---|
| E1 | The ladder holds on **≥3 task domains**, not one | generality — without it, "one toy" | **DONE (exceeded)** — **5** domains wired + collected (conference, scheduling, review, incident, reconcile); last two break the shared pick-then-finalize shape (diagnostic chain + accumulation loop) |
| E2 | The **deception gap** replicates for staleness across domains | the sharp claim can't be a single dot | **DONE** — replicates **5/5** (blind 0, oracle 0 on stale price / availability / CI / service-health / receipt). New limit surfaced: outcome-informed root-cause recovery is *task-shape-dependent* (staleness recovered 8/8 conf, 7/8 sched, but **0/8 on both** the diagnostic chain and the accumulation loop) |
| E3 | **External validity:** injected-fault failures resemble organic ones (or a measured characterization of the gap) | the premise the whole method rests on | **ADDRESSED (characterized)** — 2/28 organic failures elicited (xhard); 6/6 blind-attributable → agent-caused failures are trace-visible; environment faults are the blame-gap regime and are un-elicitable by definition (their realism is an infrastructure fact) |
| E4 | **Method comparison** (baselines vs LLM auditor vs oracle) with clean labels, per fault type | C3; the reviewer's money table | **DONE** — random/recency/keyword + stepwise (Who&When-style) + all-at-once blind + oracle + root-cause, per fault family; ranking is fault-type-dependent; step-walking cannot fix deception blindness |
| E5 | **Cross-provider grader** — the ladder isn't a same-family artifact | kills R6 | within-Claude done; cross-provider open (Phase 4, needs paid budget) |
| E6 | **Power:** variant-clustered significance at n large enough that the map isn't noise | honest stats | staleness/forget p=0.029; cdrop p=0.14 (need more n) |

## Threats to validity (must be addressed, not hidden)
- **R2 external validity** (biggest): do injected faults look organic? → E3. If unresolved, we frame
  as face-validity-by-construction and scope the claim to "diagnosability structure," not "predicts
  real failures."
- **R6 same-family generate+grade:** grader is Claude → E5 (cross-provider).
- **Oracle = upper bound, not a detector:** always reported as such; de-leak control + dumb baselines
  bound the realistic number from below.
- **Small n / one task family:** → E1, E6.
- **Prior-art overlap on method:** handled by leading with C1, not the injection method (Phase-0 GO).

## Target venue (tentative)
A dataset-and-benchmarks / evaluation track or an agents/reliability workshop
(e.g. NeurIPS D&B, an ICLR/ICML workshop on agents or evaluation). Decide after E1–E3 land.

## Scope OUT (guard against sprawl)
- Not building a runtime / recoverable agent-OS (declared out earlier).
- Not a new attribution *algorithm* (CAR occupies that; we measure, not out-score).
- Mitigation frontier (C5/Phase 5) is a **stretch**, not required for the core paper.
