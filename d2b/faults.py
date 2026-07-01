"""Fault taxonomy (v0) — the typed faults we inject into frozen successful trajectories.

This module pins the *vocabulary* (PROJECT_PLAN.md §5). The injector itself (Phi) lands in M1;
this is the frozen contract it must implement, kept here so the taxonomy can't silently drift.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class FaultType(str, Enum):
    """The six v0 fault types. Adding/removing a member requires a PROJECT_PLAN §9 decision."""

    DEBRIS = "debris"  # irrelevant tool output injected into context
    STALENESS = "staleness"  # a superseded tool result lingers, must be recency-overridden
    CONTRADICTION = "contradiction"  # a conflicting retrieval/result is injected
    WRONG_TOOL = "wrong_tool"  # a correct call swapped for a plausible-but-wrong one
    CONSTRAINT_DROP = "constraint_drop"  # a turn-1 policy/constraint is evicted (ConstraintRot case)
    TOOL_FORGETTING = "tool_forgetting"  # a needed tool schema is buried under volume


@dataclass(frozen=True)
class FaultSpec:
    """A fully-specified injection. The (type, position) pair IS the ground-truth blame label.

    Attributes
    ----------
    type:      which fault to inject.
    position:  step index in the frozen trajectory at which the fault is introduced.
    volume:    fault-type-specific magnitude (e.g. #debris tokens/items, #buried tools).
    """

    type: FaultType
    position: int
    volume: float = 1.0

    @property
    def blame_label(self) -> tuple[str, int]:
        """The causal ground-truth label this injection guarantees by construction."""
        return (self.type.value, self.position)
