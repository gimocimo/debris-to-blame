# debris-to-blame

**Controlled fault injection as ground truth for agent failure attribution — and recovery.**

Automated failure attribution — saying *which step* of an agent's tool-use trajectory caused a
failure — is the hardest open problem in agent observability. The best methods reach only ~14%
step-level accuracy ([Who&When, ICML 2025](https://arxiv.org/abs/2505.00212)) and the best model
scores 11% on trace debugging ([TRAIL](https://arxiv.org/abs/2505.08638)) — because real failure
traces have **no verifiable ground truth**. A human has to *guess* which step is to blame.

**debris-to-blame inverts the data-generating process.** We take known-successful agent
trajectories and **inject typed faults at known positions and severities**, so the blame label is
**known by construction** (that the fault *caused* the failure is confirmed separately, by paired
sham controls + the resume actually failing). That gives the field its missing labels — and lets us
measure four things no existing benchmark unifies:

- **Degradation** — which fault types actually *break* agents (vs. a same-volume sham control).
- **Attribution** — which broken runs can be *localized* back to the injected fault.
- **The blame gap** — faults that are **high-damage but invisible to attribution**. The dangerous quadrant.
- **Recovery (headline)** — *do agents recover measurably more when attribution is correct?* We close
  the loop: detect → roll back to a pre-fault checkpoint → resume → validate.

Attributors only ever see a **redacted `.public` trace** (injection markers + labels stripped), so
the answer key can never leak into the input. A later module scores mitigations (truncation,
constraint pinning, memory/context-editing) on a cost–quality–detectability frontier.

### Fault manifest (v0 — not frozen)
`debris` · `staleness` · `contradiction` · `wrong_tool` · `constraint_drop` · `tool_forgetting`
— each with a real `volume` severity knob.

### Headline — two blame-gap regimes, replicated across five domains

![cross-domain blame-gap map](assets/blamegap_map.png)

Multi-step tasks (booking a trip / scheduling a meeting / merging a PR / triaging an incident down a
dependency chain / reconciling a ~14-txn batch), driven by **sincere agents** in **real interactive
(ReAct) rollouts**, 4 independent variants per domain, all at **$0** through subscription subagents.
The last two domains deliberately break the shared pick-then-finalize *task shape*. The faults below
each break the task ~always — but *what an auditor needs in order to blame them correctly* is a
property of the **fault type**, and it replicates across all five:

| regime | blind | + full policy (oracle) | closes only with | replicates |
|---|---|---|---|---|
| **deception gap** (staleness: stale price / availability / CI / service-health / receipt) | **0.00** | **0.00** | **ground-truth world state** | **5/5 domains** |
| **deletion gap** (constraint_drop; de-leak control ≈0) | **≈0.00** | **0.88–1.00** | the exact deleted rule | 3/3 domains where it bites |
| omission (tool_forgetting) | salience-dependent (0.00 → 1.00) | can *drop* (oracle exonerates) | the **causation question** (root-cause 5/5) | 5/5 damaging, unevenly visible |

> The sharp claim is the **deception gap**: for a whole class of faults, *more rule/spec observability
> does not help* — the corrupted observation fools the auditor exactly as it fooled the agent, so
> post-hoc attribution needs re-verifiable **world state**, not better logs. The two new shapes add a
> limit: outcome-informed **root-cause** reasoning recovers deceptions on pick-then-finalize tasks but
> **fails on a diagnostic chain and an accumulation loop** (staleness 3/8 and 0/8), where an honest
> alternative explanation is equally available. Dumb baselines (grep/recency) always cry wolf (100%
> false-positive) and get ~0–0.19 recall; the LLM auditor has 0 false-positives. Recovery follows
> attribution: restoring the correctly localized rule recovers **4/4** variants vs **0/4** for a
> misdiagnosed repair (lift **+1.00**, p = 0.029, two domains).
> ([full results + caveats](docs/results.md))

<details><summary>Method note — why "sincere agents" and "oracle upper bound" matter</summary>

An earlier pass drove rollouts with *scripted oracle* policies and reported `constraint_drop 8/8,
p = 0.0002` + a `blame gap +0.88`. Re-collecting with **sincere** agents overturned it: dropping "no
red-eye" causes **zero** failures (capable agents avoid red-eyes anyway — the rule was redundant), and
the `with-policy` arm is an **oracle upper bound** (the auditor handed the full spec), not a realistic
detector. The `de-leak` control (rulebook minus the deleted line ⇒ still 0.00) is what proves the
deletion gap is real rather than an artifact of handing over the answer. See
[docs/results.md](docs/results.md).

</details>

<details><summary>The original proof-of-mechanism (single travel cell, n=5)</summary>

![headline](assets/headline.png)

The first vertical slice: the same loop on one fault (`constraint_drop`, travel), 5 samples/cell.
Saturated 0-vs-1 effects — a proof of mechanism on one base trajectory, superseded by the multi-step
canonical dataset above.

</details>

### Demo (zero model calls, ~instant)
```
python3 scripts/demo_inject.py     # each fault corrupting a clean trace + its private label
python3 scripts/make_figure.py     # regenerate the figure above from results/
```

### Status
🚧 Active — now a paper program (see [`docs/paper/framing.md`](docs/paper/framing.md)). **M0/M1 done.
M2's exit bar (sham-controlled degradation + a measured attribution gap in ≥3 domains) is exceeded**:
**five** multi-step domains (conference, scheduling, review, incident, reconcile) are wired into the
interactive loop, with the deception gap replicating **5/5** and the deletion gap **3/3** where it
bites (220 unit tests green; every number replays from committed data; audited by an external Codex
review, findings fixed). Honest partials: the cross-*tier* panel exists only for conference cdrop;
recovery is one domain; long-horizon (tens–hundreds of steps) and external validity remain open.
Next: full 6-fault map + attribution-method re-ranking (Phase 3), external validity (Phase 2),
cross-provider grader (Phase 4). See [`PROJECT_PLAN.md`](PROJECT_PLAN.md) (decision log),
[`ROADMAP.md`](ROADMAP.md) (milestones), [`docs/results.md`](docs/results.md) (results + caveats).

### Design constraints
Laptop-scale, **subscription-native** (inference runs through a Claude Code agent + subagents on an
existing Claude Max plan → ~$0). Deterministic mock tool environment; small curated dataset, frozen
and released for reproducibility. Total additional budget < $100.

---
MIT © Guglielmo Cimolai
