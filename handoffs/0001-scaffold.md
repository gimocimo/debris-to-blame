# Handoff 0001 — scaffold

- **Date:** 2026-06-30 (Session 0)
- **Milestone:** M0 — novelty kill · **State:** in progress (not started in earnest)

## What I did
- Ran a deep-research pass (5 angles, 22 sources, 25 claims adversarially verified) over the
  context-rot / observability / tool-use-limits space.
- Verified 7 load-bearing arxiv IDs against their abstract pages (all real). Corrected SlopCodeBench
  figures (36 problems / 196 checkpoints / 14.8% best, not 20/93/17.2%) and TRAIL's title.
- Chose the project: **Debris→Blame** — controlled fault injection as causal ground truth for
  failure attribution. Wrote the anti-drift docs.

## What changed (files / claims / decisions)
- Created scaffold: `PROJECT_PLAN.md`, `ROADMAP.md`, `docs/novelty.md`, `README.md`,
  `pyproject.toml`, `LICENSE`, `.gitignore`, `handoffs/`, `d2b/` skeleton, `tests/test_smoke.py`.
- Decisions logged: D-000 (lead = C1 injection-grounded attribution, NOT standalone constraint
  survival — ConstraintRot 2606.22528 already occupies that), D-001 (naming/stack), D-002
  (single-agent first). See `PROJECT_PLAN.md §9`.

## Evidence produced
- None empirical. Scaffold + verified literature map only.

## Open risks / surprises
- **ConstraintRot (2606.22528) landed days ago** and occupies the original constraint-survival hook
  → forced the repositioning to attribution as the lead. This is the central risk: M0 must prove the
  injection-for-attribution gap is genuinely unoccupied.
- The tool-use-limits / MCP-failure angle was **under-searched** in the research pass — M0 owes it a
  dedicated search before we lean on `wrong_tool` / `tool_forgetting` realism.

## Next session starts here (M0)
- [ ] Read ConstraintRot 2606.22528 in full; confirm the 5-axis diff in `docs/novelty.md`.
- [ ] Dedicated prior-art search: does any 2025–2026 work inject faults to get attribution ground truth?
- [ ] Deepen the tool-use-limits / MCP-failure-taxonomy search.
- [ ] Write the final one-paragraph gap; if closed, log a D-decision pivoting the lead to C4.
- [ ] Owner decision: make the GitHub repo public and push the scaffold? (currently private + uncommitted)
