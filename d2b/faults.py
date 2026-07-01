"""Fault taxonomy (v0) + the injector.

The taxonomy pins the *vocabulary* (PROJECT_PLAN §5); `inject()` is the operator Phi(tau, spec) that
edits a frozen successful trajectory at a KNOWN locus — so the blame label is correct by design.

Insert/modify faults act on `Trajectory.messages`; `constraint_drop` acts on `constraints`;
`tool_forgetting` acts on `tools`. `position` indexes the relevant list (documented per fault).
"""

from __future__ import annotations

import copy
from dataclasses import dataclass
from enum import StrEnum

from .tools import decoy_tool_names
from .trajectory import Message, Trajectory


class FaultType(StrEnum):
    """The six v0 fault types. Adding/removing a member requires a PROJECT_PLAN §9 decision."""

    DEBRIS = "debris"  # irrelevant tool output injected into context
    STALENESS = "staleness"  # a superseded tool result lingers, must be recency-overridden
    CONTRADICTION = "contradiction"  # a conflicting retrieval/result is injected
    WRONG_TOOL = "wrong_tool"  # a correct call swapped for a plausible-but-wrong one
    CONSTRAINT_DROP = "constraint_drop"  # a turn-1 policy/constraint evicted (ConstraintRot case)
    TOOL_FORGETTING = "tool_forgetting"  # a needed tool schema is buried under volume


@dataclass(frozen=True)
class FaultSpec:
    """A fully-specified injection. The (type, position) pair IS the ground-truth blame label.

    position semantics by type:
      debris/staleness/contradiction : index in `messages` where the fault message is inserted.
      wrong_tool                     : index in `messages` of the assistant step to corrupt.
      constraint_drop                : index in `constraints` of the rule to evict.
      tool_forgetting                : index in `messages` of the step that needs the buried tool.
    volume: fault-specific magnitude (# debris msgs or # decoy tools; see each injector).
    """

    type: FaultType
    position: int
    volume: float = 1.0

    @property
    def blame_label(self) -> tuple[str, int]:
        """The causal ground-truth label this injection guarantees by construction."""
        return (self.type.value, self.position)


_DEBRIS_TEXT = (
    "[web_search] Unrelated result: The 1904 World's Fair in St. Louis popularised the ice-cream "
    "cone. See also: history of waffles, Belgian pastry exports, sugar tariffs (1897)."
)


def inject(traj: Trajectory, spec: FaultSpec) -> Trajectory:
    """Return a corrupted deep copy of `traj` with one typed fault at `spec`'s known locus.

    The original is never mutated. The returned trajectory records the fault in `.meta["fault"]`
    and the ground-truth label in `.meta["blame_label"]`.
    """

    t = copy.deepcopy(traj)
    _DISPATCH[spec.type](t, spec)
    t.meta["fault"] = {"type": spec.type.value, "position": spec.position, "volume": spec.volume}
    t.meta["blame_label"] = list(spec.blame_label)
    t.meta["corrupted"] = True
    return t


def _check_msg_index(t: Trajectory, pos: int, *, insert: bool) -> None:
    hi = len(t.messages) if insert else len(t.messages) - 1
    if not (0 <= pos <= hi):
        raise ValueError(f"position {pos} out of range for messages (len={len(t.messages)})")


def _inject_debris(t: Trajectory, spec: FaultSpec) -> None:
    _check_msg_index(t, spec.position, insert=True)
    junk = [
        Message(role="tool", tool_name="web_search", content=_DEBRIS_TEXT, injected="debris")
        for _ in range(max(1, int(spec.volume)))
    ]
    t.messages[spec.position : spec.position] = junk


def _inject_staleness(t: Trajectory, spec: FaultSpec) -> None:
    _check_msg_index(t, spec.position, insert=True)
    stale = Message(
        role="tool",
        tool_name="search_flights",
        content="[BA112 $780 dep 09:00 | VS004 $600 dep 23:50 (red-eye)]",  # superseded price
        injected="staleness",
    )
    t.messages.insert(spec.position, stale)


def _inject_contradiction(t: Trajectory, spec: FaultSpec) -> None:
    _check_msg_index(t, spec.position, insert=True)
    contra = Message(
        role="tool",
        tool_name="check_budget",
        content="Remaining budget: $400.",  # contradicts the real $800
        injected="contradiction",
    )
    t.messages.insert(spec.position, contra)


def _inject_wrong_tool(t: Trajectory, spec: FaultSpec) -> None:
    _check_msg_index(t, spec.position, insert=False)
    msg = t.messages[spec.position]
    if msg.role != "assistant" or msg.tool_call is None:
        raise ValueError(f"wrong_tool needs an assistant tool-call at position {spec.position}")
    msg.tool_call.name = "check_weather"  # plausible-but-wrong neighbour
    msg.tool_call.args = {}
    msg.injected = "wrong_tool"
    nxt = t.messages[spec.position + 1] if spec.position + 1 < len(t.messages) else None
    if nxt is not None and nxt.role == "tool":
        nxt.tool_name = "check_weather"
        nxt.content = "Sunny, 18C."
        nxt.injected = "wrong_tool"


def _inject_constraint_drop(t: Trajectory, spec: FaultSpec) -> None:
    if not (0 <= spec.position < len(t.constraints)):
        raise ValueError(f"constraint_drop position {spec.position} out of range")
    t.meta["dropped_constraint"] = t.constraints.pop(spec.position)


def _inject_tool_forgetting(t: Trajectory, spec: FaultSpec) -> None:
    # Bury the real tools under `volume` decoy schemas (prepend so real tools sink down the list).
    t.tools[:0] = decoy_tool_names(max(1, int(spec.volume)))
    t.meta["buried_step"] = spec.position


_DISPATCH = {
    FaultType.DEBRIS: _inject_debris,
    FaultType.STALENESS: _inject_staleness,
    FaultType.CONTRADICTION: _inject_contradiction,
    FaultType.WRONG_TOOL: _inject_wrong_tool,
    FaultType.CONSTRAINT_DROP: _inject_constraint_drop,
    FaultType.TOOL_FORGETTING: _inject_tool_forgetting,
}
