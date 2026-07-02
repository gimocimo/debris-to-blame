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

### Headline — the blame-gap map: same damage, different attributability

![blame-gap map](assets/conf_blamegap.png)

On the multi-step **CONFERENCE_TRIP** task (a 10+ step book-then-file-then-send workflow), driven by
**sincere agents** in **real interactive (ReAct) rollouts** across independent task variants, all at
**$0** through subscription subagents. Three faults each break the task ~always — but they are
*attributable* to completely different degrees, which is the whole point:

| fault | damage | blind auditor | + full policy (oracle) | what kind of gap |
|---|---|---|---|---|
| **constraint_drop** (refundable) | 0.88 | **0.00** (de-leak 0.00) | **1.00** | a **deletion gap** — attributable only by re-supplying the exact deleted rule |
| **staleness** (stale quote) | 1.00 | **0.00** | **0.00** | a **deception gap** — the policy does *not* close it; the corrupted quote fools the auditor too |
| **tool_forgetting** (missing tool) | 1.00 | **1.00** | 0.88 | **visible** — the requirement is still stated; no gap |

> Some faults **silently break** an agent and are **invisible in the trace**; whether the reference
> policy makes them attributable **depends on the fault type** — a deletion gap closes, a deception gap
> does not. Dumb baselines (grep/recency) floor at ~0 recall / 100% false-positive, so the LLM
> auditor's oracle result is real work, not token-matching. Recovery follows attribution: restoring
> the correctly localized rule recovers the task in **4/4** variants vs **0/4** for a misdiagnosed
> repair (localization lift **+1.00**, clustered Fisher p = 0.029). ([full results + caveats](docs/results.md))

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
🚧 Active. **M0/M1 done; the full degrade → attribute → recover loop is demonstrated on ONE multi-step
task family** (CONFERENCE_TRIP + 4 variants), with a de-contaminated blame-gap map, dumb-baseline
floor, cross-tier robustness check, and honest variant-level statistics (125 unit tests green). **M2 is not yet
met**: its bar is a measurable attribution gap in **≥3 domains**, and only CONFERENCE_TRIP is wired
into the interactive loop — the other domains are still single-step static fixtures. Next: port a
second domain to the interactive loop; a true cross-provider grader; larger n. See
[`PROJECT_PLAN.md`](PROJECT_PLAN.md) (scope + claims), [`ROADMAP.md`](ROADMAP.md) (milestones),
[`docs/results.md`](docs/results.md) (results + caveats).

### Design constraints
Laptop-scale, **subscription-native** (inference runs through a Claude Code agent + subagents on an
existing Claude Max plan → ~$0). Deterministic mock tool environment; small curated dataset, frozen
and released for reproducibility. Total additional budget < $100.

---
MIT © Guglielmo Cimolai
