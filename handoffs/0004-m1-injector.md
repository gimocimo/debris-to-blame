# Handoff 0004 — M1 injector + mock env + demo

- **Date:** 2026-06-30 (Session 2, cont.)
- **Milestone:** M1 · **State:** DONE

## What I did
- Closed M0 as a light related-work scan (borrow-list in `docs/novelty.md`; non-gating, no pivot).
- Built M1 end-to-end.

## What changed (files / claims / decisions)
- `d2b/trajectory.py` — Message / ToolCall / Trajectory data model ("memory = a list of messages")
  with JSON round-trip.
- `d2b/tools.py` — deterministic mock flight-booking tools (cost $0, reproducible) + decoy schemas.
- `d2b/faults.py` — `inject(traj, spec)` implementing all six faults; records `blame_label` by
  construction; never mutates the original. Switched enum to `StrEnum` (UP042).
- `d2b/fixtures.py` — clean successful fixture trajectory (respects both constraints, books BA112).
- `scripts/demo_inject.py` — runnable demo, self-contained (`python3 scripts/demo_inject.py`).
- `tests/test_inject.py` — 9 tests (round-trip, per-fault, immutability, JSON survival).

## Evidence produced
- **17 tests green, ruff clean, formatted.** Demo prints all 6 corrupted trajectories + their
  ground-truth labels. Still ZERO model calls / $0 (fixture-based).
- Fixed a repro bug: removed non-deterministic `hash()` from the mock `book_flight` output.

## Open risks / surprises
- None new. The one design choice to revisit in M2: `position` semantics differ slightly across
  fault families (message-index vs constraint-index) — documented in `FaultSpec`, fine for now.

## Next session starts here (M2)
- [ ] Generate ~40–60 real successful trajectories subscription-native (this session / subagents).
- [ ] Add `d2b/replay.py` (deterministic re-exec) + resume-live generation from the injection point.
- [ ] exp01 (degradation D(f,p,v) per fault × Claude tier) + exp02 (attribution vs known labels).
