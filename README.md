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

### First result — the whole thesis on one cell

![headline](assets/headline.png)

A proof-of-mechanism run of the complete loop on one fault (`constraint_drop`, travel domain), with
real inference through subscription subagents at **$0**, 5 samples per cell:

| stage | result | reading |
|---|---|---|
| **1. Degrade** (exp01) | P[fail] `0.00 → 1.00` | drop the "no red-eye" rule → the agent silently books the cheaper red-eye |
| **2. Attribute** (exp02) | correct blame `0.00 → 1.00` (w/ policy) | a **trace-only** auditor can't see the violation — a deletion leaves no trace |
| **3. Recover** (exp04) | recovery `0.00` blind → `1.00` targeted | the task recovers **only** when the fault is correctly localized |

> A dropped constraint **silently breaks** the agent, is **invisible in the trace**, and is
> **recoverable only once you can localize it.** ([full results + caveats](docs/results.md))

**Honest caveat:** these effects are saturated (0-vs-1) at n=5, one tier, one fault, one domain —
a convincing *proof of mechanism*, not yet a paper claim. Scaling (faults × tiers × domains, sham
controls, bootstrap CIs) is the next milestone.

### Demo (zero model calls, ~instant)
```
python3 scripts/demo_inject.py     # each fault corrupting a clean trace + its private label
python3 scripts/make_figure.py     # regenerate the figure above from results/
```

### Status
🚧 Early. **M0 (related-work scan) and M1 (leakage-safe injector + mock env + demo, 25 tests) done.**
Next: **M2 — degradation + attribution + recovery (v0.1)** across 5 task domains on a 3-Claude-tier
panel. No empirical claim is real until M2. See [`PROJECT_PLAN.md`](PROJECT_PLAN.md) (scope + claims),
[`ROADMAP.md`](ROADMAP.md) (milestones), [`docs/novelty.md`](docs/novelty.md) (related work).

### Design constraints
Laptop-scale, **subscription-native** (inference runs through a Claude Code agent + subagents on an
existing Claude Max plan → ~$0). Deterministic mock tool environment; small curated dataset, frozen
and released for reproducibility. Total additional budget < $100.

---
MIT © Guglielmo Cimolai
