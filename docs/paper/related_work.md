# Related work & honest novelty diff (Phase 0, 2026-07-02)

Produced by a verify-and-read workflow (`d2b-prior-art`). **All arXiv IDs below were fetched by
agents; the ones marked ⚠ were surfaced by search and MUST be manually re-verified before citing** —
the agents caught their own WebFetch summaries hallucinating our framing onto other papers, so treat
every "they don't do X" as needing a careful human read of the raw PDF before we rely on it in a paper.

## Our three claims, and how they survive contact with the literature

| # | Our claim | Verdict after prior-art | Nearest prior work |
|---|---|---|---|
| **(1)** | Build attribution labels by **injecting** typed faults into known-good trajectories (label correct **by construction**) | **NOT novel** — already published | AEGIS ⚠, AgenTracer ⚠ (both 2025, multi-agent) |
| **(2)** | **Interactive** harness: fault corrupts only what the agent sees live + **world-state validator** (un-gameable) | **NOT novel as an instrument** — standard/buildable | ReliabilityBench (2601.06112), ToolMaze ⚠ |
| **(3)** | **Finding:** attribution difficulty is **fault-type-structured** — an information-access ladder (trace-only / +reference-policy / +ground-truth-state); a *deletion gap* the policy closes vs a *deception gap* it does **not** vs *visible* faults | **Appears genuinely novel** — no read paper does this | none |

**So the defensible contribution narrows from "method + finding" to "the FINDING", plus a specific
instrument *combination*.** The method (injection→labels) and the instrument (live-corruption +
state-oracle) are each already in the literature; nobody has used them to characterize *when*
attribution is possible and *what information it requires*.

## The papers

**Attribution, labels from ANNOTATION (the pain point we sidestep):**
- **Who&When** (2505.00212, ICML'25 spotlight) — canonical failure-attribution benchmark; 127–184
  multi-agent failure logs, multi-round **human** annotation (Krippendorff α 0.72 agent / **0.64
  step** — noisy). SOTA ~53% agent / **~14% step**. THE benchmark everyone cites; the annotation cost
  + label noise is exactly our motivation.
- **TRAIL** (2505.08638) — span-level error localization over agent traces, **human**-annotated
  organic errors, formal taxonomy; best model ~11% joint accuracy. Static, offline.
- **TELBench / DRIFT** ⚠ (2606.02060) — single-agent ReAct span-level localization, **annotation**-based.

**Injection, but for ROBUSTNESS/RECOVERY (not attribution):**
- **ReliabilityBench** (2601.06112) — **closest on our instrument**: interactive ReAct harness that
  corrupts tool outputs live under a typed-fault schedule (StaleData, SchemaDrift, RateLimit…) +
  **deterministic state oracles** (un-gameable). But pure reliability *scoring* — no blame labels, no
  attribution. Proves our instrument is standard/buildable.
- **ConstraintRot / "Governance Decay"** (2606.22528) — injection, but one fault (constraint eviction
  ≈ our constraint_drop) and robustness framing. Notable: "constraint survives → 0% violation; dropped
  → 38%" — our cdrop degradation, for one fault, no attribution.
- **ToolMaze** ⚠ (2606.05806) — live tool-failure injection for **replanning/recovery**, not attribution.

**Injection → attribution LABELS (the direct threat to claim 1):**
- **AEGIS** ⚠ (2509.14295) — LLM "manipulator" injects context-aware errors into **successful**
  multi-agent trajectories → 9,533-traj labeled dataset (labels by construction), trains attribution
  models. **Direct overlap on our method.** Differs: OFFLINE trajectory editing (not live corruption);
  no world-state validator; MAS role-error modes, not our typed channels; goal = dataset scale +
  training, not a difficulty finding.
- **AgenTracer** ⚠ (2509.03312) — programmatic fault injection into known-good trajectories +
  counterfactual replay → TracerTraj; trains AgenTracer-8B, beats proprietary LLMs on Who&When.
  **Direct overlap on our method** ("decisive error known by construction"). Differs: post-hoc on
  static logs; Ω is task-success reward, not a distinct world-state validator; generic perturbation,
  not a typed taxonomy; **no fault-type-structured difficulty finding** (verified against raw PDF).
- **CAR / Causal Agent Replay** ⚠ (2606.08275) — counterfactual single-agent attribution via
  do-operator + Shapley; validated on **synthetic SCMs**. Shares intervention-as-truth spirit, but
  edits ALREADY-FAILED traces (doesn't mint a test set from known-good ones), no typed taxonomy, no
  difficulty finding.

## Bottom line for the paper

Lead with claim **(3)**, not (1). The one-sentence positioning:

> Prior work uses fault injection to **scale attribution training data** (AEGIS, AgenTracer) or to
> **score robustness** (ReliabilityBench); we use controlled injection as a **measurement instrument**
> to show that failure attribution is *fault-type-structured* — different fault classes require
> fundamentally different information to diagnose (trace / reference-policy / ground-truth-state), and
> in particular a **deception fault is unattributable from the trace and the policy alone**. That
> characterization, not the injection method, is the contribution.

**Immediate risk to close:** claim (3)'s novelty rests on AEGIS / AgenTracer / CAR **not** doing a
fault-type × information-source breakdown. The agents verified this against raw PDFs and caught fetch
hallucinations, but before committing months, **a careful manual read of those three is mandatory** —
if any of them stratify attribution difficulty by fault type, our one remaining novel claim weakens.

## Verification verdict (2026-07-03, workflow `d2b-verify-novelty`) — GO

Two independent deep-readers per paper (raw-text quotes only) + an adjudicator per paper that
re-read the raw PDFs. Result: **all three exist, IDs correct, and NONE pre-empt claim (3).**

| paper | exists / ID correct | pre-empts claim 3? | note |
|---|---|---|---|
| AEGIS (2509.14295) | yes (title verb "Attribution" on arXiv vs "Identification" on HF — same paper) | **no** | attributor input is FIXED (full log + taxonomy); results are Pair/Agent/Error-F1 and by task-domain, never by fault type; no info ladder; no deception gap |
| AgenTracer (2509.03312) | yes | **no** | single generic perturbation Π (not a typed taxonomy); only info contrast is "w/ 𝒢 vs w/o 𝒢" (ground-truth *solution*), not trace→policy→state |
| CAR (2606.08275) | yes | **no** | a causal-attribution *method* (do-op + Shapley), orthogonal; no per-fault-type breakdown |

**Fetch-echo caught:** an AgenTracer WebFetch summary hallucinated "four fault types: deletion,
deception, visible, corrupted observation" — parroting the verifier's own prompt terms; a raw grep
showed **0 hits** for all of them, and the adjudicator discarded the unquoted claim. (This is why the
double-read + raw-PDF adjudication mattered.)

**Residual diligence (do before camera-ready, not blocking now):** (1) AEGIS was verified on v1; it
has later revisions (up to v6) — re-check no per-fault-type/information-ablation analysis was added.
(2) CAR was read via arXiv HTML, not the raw PDF line-by-line — a buried appendix table can't be 100%
excluded. Neither changes the GO.

**Conclusion:** lead the paper with claim (3). The method (injection→labels) and instrument
(live-corruption + state-oracle) are shared prior art; the **fault-type-structured attribution
difficulty finding — especially the deception gap — is ours.**
