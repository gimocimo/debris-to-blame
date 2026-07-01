# debris-to-blame

**Controlled fault injection as causal ground truth for agent failure attribution.**

Automated failure attribution — saying *which step* of an agent's tool-use trajectory caused a
failure — is the hardest open problem in agent observability. The best methods reach only ~14%
step-level accuracy ([Who&When, ICML 2025](https://arxiv.org/abs/2505.00212)) and the best model
scores 11% on trace debugging ([TRAIL](https://arxiv.org/abs/2505.08638)) — because real failure
traces have **no verifiable ground truth**. A human has to *guess* which step is to blame.

**debris-to-blame inverts the data-generating process.** We take known-successful agent
trajectories, **inject typed faults at controlled positions and volumes**, and now *we know exactly
which step is to blame, by construction*. That gives the field its missing causal labels — and lets
us measure three things no existing benchmark unifies:

- **Degradation** — which fault types actually *break* agents (decoupled from task difficulty).
- **Attribution** — which broken runs can be *localized* back to the injected fault.
- **The blame gap** — faults that are **high-damage but invisible to attribution**. The dangerous quadrant.

The same harness then scores mitigations (truncation, compaction, RAG-over-history, memory tools,
context editing, sub-agent isolation) on a **cost–quality–detectability** frontier.

### Fault taxonomy (v0)
`debris` · `staleness` · `contradiction` · `wrong_tool` · `constraint_drop` · `tool_forgetting`

### Status
🚧 Scaffold. See [`PROJECT_PLAN.md`](PROJECT_PLAN.md) for scope, [`ROADMAP.md`](ROADMAP.md) for
milestones, and [`docs/novelty.md`](docs/novelty.md) for the prior-art map. **M0 (novelty kill)** is
the next milestone — no empirical claim is real until M2.

### Design constraints
Laptop-scale. Deterministic frozen/mocked tool environment; Batch API + prompt caching + cached
inference outcomes keep cost <$1k.

---
MIT © Guglielmo Cimolai
