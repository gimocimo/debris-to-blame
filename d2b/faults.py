"""Fault taxonomy (v0) + the injector + the leakage-safe public/private split.

`inject()` edits a frozen successful trajectory at a KNOWN locus and returns a `Corruption` holding
BOTH the internally-marked corrupted trajectory AND a private `FaultRecord` (the ground truth).
Attributors must only ever see `Corruption.public` — a redacted trace with the injection markers and
all label metadata stripped — so the answer key can never leak into the input (Codex audit, D-009).

Honesty note (D-009): the injected *site* is known by construction; that it *caused* the failure is
established separately by paired sham controls + the resume actually failing (see ROADMAP). We label
this "known injected-site + causal-effect validation", not "perfect causal labels".
"""

from __future__ import annotations

import copy
from dataclasses import dataclass, field
from enum import StrEnum

from .tools import decoy_tool_names
from .trajectory import Message, ToolCall, Trajectory


class FaultType(StrEnum):
    """The six v0 fault types. This is the *current* idea space, NOT frozen — the benchmark
    *manifest* is what gets frozen, not the enum (Codex cut-list, D-013)."""

    DEBRIS = "debris"  # irrelevant tool output injected into context
    STALENESS = "staleness"  # a superseded tool result lingers, must be recency-overridden
    CONTRADICTION = "contradiction"  # a conflicting retrieval/result is injected
    WRONG_TOOL = "wrong_tool"  # a correct call swapped for a plausible-but-wrong one
    CONSTRAINT_DROP = "constraint_drop"  # a turn-1 policy/constraint evicted (ConstraintRot case)
    TOOL_FORGETTING = "tool_forgetting"  # a needed tool schema is buried under volume


@dataclass(frozen=True)
class FaultSite:
    """Kind-tagged, redaction-stable locus of a fault (replaces the ambiguous raw int, D-009).

    kind: "message" | "constraint" | "tool".
    ref:  message index in the PUBLIC (redacted) trace | constraint index | tool name.
    """

    kind: str
    ref: str


@dataclass(frozen=True)
class FaultSpec:
    """A fully-specified injection request.

    position: where to inject — index in `messages` (insert/modify faults), or in `constraints`
              (constraint_drop), or the step that needs the buried tool (tool_forgetting).
    volume:   severity knob, meaningful for EVERY fault type (see each injector).
    """

    type: FaultType
    position: int
    volume: float = 1.0


@dataclass(frozen=True)
class FaultRecord:
    """The PRIVATE ground-truth label. Never serialized into a public trace."""

    fault_type: FaultType
    site: FaultSite
    volume: float
    extra: dict = field(default_factory=dict)
    sham: bool = False  # a sham is a volume-matched NEUTRAL control (no real fault)

    @property
    def blame_label(self) -> tuple[str, str, str]:
        """(fault_type, site.kind, site.ref) — what an attributor is graded against."""
        return (self.fault_type.value, self.site.kind, self.site.ref)


# meta keys that would leak the answer key; stripped by redact_for_attribution().
LEAKAGE_META_KEYS = {"fault", "blame_label", "dropped_constraint", "buried_step", "corrupted"}


def redact_for_attribution(traj: Trajectory) -> Trajectory:
    """Return a leakage-free copy: injection markers cleared, label metadata removed.

    This is the ONLY trace form an attribution harness may consume. Injected messages become
    indistinguishable from originals (no marker), which also makes the faults realistic.
    """

    t = copy.deepcopy(traj)
    for m in t.messages:
        m.injected = None
    t.meta = {k: v for k, v in t.meta.items() if k not in LEAKAGE_META_KEYS}
    return t


@dataclass
class Corruption:
    """The result of one injection: the internally-marked trace + its private label.

    `.corrupted` retains markers/meta for OUR use (degradation, demo). `.public` is the redacted,
    leakage-free trace attributors see. `.label` is the private ground truth.
    """

    corrupted: Trajectory
    label: FaultRecord

    @property
    def public(self) -> Trajectory:
        return redact_for_attribution(self.corrupted)


_DEBRIS_TEXT = (
    "[web_search] Unrelated result: The 1904 World's Fair in St. Louis popularised the ice-cream "
    "cone. See also: history of waffles, Belgian pastry exports, sugar tariffs (1897)."
)


def inject(traj: Trajectory, spec: FaultSpec) -> Corruption:
    """Return a Corruption (public/private split) with one typed fault at `spec`'s known locus.

    The original is never mutated. `.corrupted.meta` carries internal-only fault info (redacted out
    of `.public`); `.label` is the private FaultRecord graded against.
    """

    t = copy.deepcopy(traj)
    site, extra = _DISPATCH[spec.type](t, spec)
    t.meta["fault"] = {
        "type": spec.type.value,
        "site": [site.kind, site.ref],
        "volume": spec.volume,
    }
    t.meta["corrupted"] = True
    t.meta.update(extra)  # e.g. dropped_constraint / buried_step — internal only, redacted out
    return Corruption(corrupted=t, label=FaultRecord(spec.type, site, spec.volume, extra))


def _check_msg_index(t: Trajectory, pos: int, *, insert: bool) -> None:
    hi = len(t.messages) if insert else len(t.messages) - 1
    if not (0 <= pos <= hi):
        raise ValueError(f"position {pos} out of range for messages (len={len(t.messages)})")


def _inject_debris(t: Trajectory, spec: FaultSpec) -> tuple[FaultSite, dict]:
    # volume = number of debris messages inserted.
    _check_msg_index(t, spec.position, insert=True)
    junk = [
        Message(role="tool", tool_name="web_search", content=_DEBRIS_TEXT, injected="debris")
        for _ in range(max(1, int(spec.volume)))
    ]
    t.messages[spec.position : spec.position] = junk
    return FaultSite("message", str(spec.position)), {}


def _inject_staleness(t: Trajectory, spec: FaultSpec) -> tuple[FaultSite, dict]:
    # volume = staleness magnitude (how wrong the superseded price is).
    _check_msg_index(t, spec.position, insert=True)
    price = 650 + int(130 * spec.volume)
    stale = Message(
        role="tool",
        tool_name="search_flights",
        content=f"[BA112 ${price} dep 09:00 | VS004 $600 dep 23:50 (red-eye)]",
        injected="staleness",
    )
    t.messages.insert(spec.position, stale)
    return FaultSite("message", str(spec.position)), {}


def _inject_contradiction(t: Trajectory, spec: FaultSpec) -> tuple[FaultSite, dict]:
    # volume = contradiction strength (how far the injected budget is from the real $800).
    _check_msg_index(t, spec.position, insert=True)
    budget = max(0, int(800 - 400 * spec.volume))
    contra = Message(
        role="tool",
        tool_name="check_budget",
        content=f"Remaining budget: ${budget}.",
        injected="contradiction",
    )
    t.messages.insert(spec.position, contra)
    return FaultSite("message", str(spec.position)), {}


def _inject_wrong_tool(t: Trajectory, spec: FaultSpec) -> tuple[FaultSite, dict]:
    # Swap the call for a REAL but wrong in-domain tool (realistic, domain-agnostic).
    # volume = semantic distance: near = first alternative, far = last alternative.
    _check_msg_index(t, spec.position, insert=False)
    msg = t.messages[spec.position]
    if msg.role != "assistant" or msg.tool_call is None:
        raise ValueError(f"wrong_tool needs an assistant tool-call at position {spec.position}")
    candidates = [x for x in t.tools if x != msg.tool_call.name]
    if not candidates:
        raise ValueError("wrong_tool needs >=1 alternative tool in trajectory.tools")
    wrong = candidates[0] if spec.volume <= 1 else candidates[-1]
    msg.tool_call.name = wrong
    msg.tool_call.args = {}
    msg.injected = "wrong_tool"
    nxt = t.messages[spec.position + 1] if spec.position + 1 < len(t.messages) else None
    if nxt is not None and nxt.role == "tool":
        nxt.tool_name = wrong
        nxt.content = f"[{wrong}] (unexpected/irrelevant result)"
        nxt.injected = "wrong_tool"
    return FaultSite("message", str(spec.position)), {}


def _inject_constraint_drop(t: Trajectory, spec: FaultSpec) -> tuple[FaultSite, dict]:
    # volume = number of constraints dropped, starting at position.
    if not (0 <= spec.position < len(t.constraints)):
        raise ValueError(f"constraint_drop position {spec.position} out of range")
    dropped = []
    for _ in range(max(1, int(spec.volume))):
        if spec.position < len(t.constraints):
            dropped.append(t.constraints.pop(spec.position))
    _scrub_from_messages(t, dropped)  # so a policy-bearing tool output can't re-leak the rule
    return FaultSite("constraint", str(spec.position)), {"dropped_constraint": dropped}


def _scrub_from_messages(t: Trajectory, rules: list[str]) -> None:
    """Remove dropped-rule text lingering in message contents (e.g. a get_policy tool output)."""
    for m in t.messages:
        if not m.content:
            continue
        for rule in rules:
            if rule in m.content:
                m.content = m.content.replace(rule, "").replace(" |  | ", " | ").strip(" |")
                m.injected = m.injected or "constraint_drop"


def _inject_tool_forgetting(t: Trajectory, spec: FaultSpec) -> tuple[FaultSite, dict]:
    # volume = number of decoy schemas prepended (buries the real tools deeper).
    _check_msg_index(t, spec.position, insert=False)
    t.tools[:0] = decoy_tool_names(max(1, int(spec.volume)))
    return FaultSite("message", str(spec.position)), {"buried_step": spec.position}


_DISPATCH = {
    FaultType.DEBRIS: _inject_debris,
    FaultType.STALENESS: _inject_staleness,
    FaultType.CONTRADICTION: _inject_contradiction,
    FaultType.WRONG_TOOL: _inject_wrong_tool,
    FaultType.CONSTRAINT_DROP: _inject_constraint_drop,
    FaultType.TOOL_FORGETTING: _inject_tool_forgetting,
}


# --------------------------------------------------------------------------------------------------
# Sham controls: a volume-matched NEUTRAL perturbation of the same shape as each fault. Comparing
# fault-vs-sham (not fault-vs-healthy) isolates the SPECIFIC fault from generic context perturbation
# (e.g. "extra message", "longer tool list") — a paired control (Codex audit, D-009).
# --------------------------------------------------------------------------------------------------

_SHAM_TEXT = "[note] Confirming the request parameters are unchanged; proceeding as planned."


def _sham_insert(t: Trajectory, spec: FaultSpec) -> tuple[FaultSite, dict]:
    # Same #messages as debris/staleness/contradiction, but benign on-task content (no junk).
    _check_msg_index(t, spec.position, insert=True)
    n = max(1, int(spec.volume)) if spec.type is FaultType.DEBRIS else 1
    notes = [
        Message(role="tool", tool_name="note", content=_SHAM_TEXT, injected="sham")
        for _ in range(n)
    ]
    t.messages[spec.position : spec.position] = notes
    return FaultSite("message", str(spec.position)), {}


def _sham_wrong_tool(t: Trajectory, spec: FaultSpec) -> tuple[FaultSite, dict]:
    # Re-issue the SAME (correct) call as a redundant duplicate — matched shape, no wrong tool.
    _check_msg_index(t, spec.position, insert=False)
    msg = t.messages[spec.position]
    if msg.role != "assistant" or msg.tool_call is None:
        raise ValueError(
            f"wrong_tool sham needs an assistant tool-call at position {spec.position}"
        )
    dup = Message(
        role="assistant",
        tool_call=ToolCall(msg.tool_call.name, dict(msg.tool_call.args)),
        injected="sham",
    )
    t.messages.insert(spec.position, dup)
    return FaultSite("message", str(spec.position)), {}


def _sham_constraint_drop(t: Trajectory, spec: FaultSpec) -> tuple[FaultSite, dict]:
    # Drop a genuinely NON-binding rule — isolates "the binding rule mattered" from "dropping any
    # rule". Prefer the domain's inert rule (meta["sham_constraint_index"]); else a heuristic.
    if len(t.constraints) < 2:
        raise ValueError("constraint_drop sham needs >=2 constraints (a non-target one to drop)")
    idx = t.meta.get("sham_constraint_index")
    if not (isinstance(idx, int) and 0 <= idx < len(t.constraints)):
        idx = len(t.constraints) - 1  # safe default: the last rule (never position-dependent)
    dropped = t.constraints.pop(idx)
    return FaultSite("constraint", str(idx)), {"dropped_constraint": [dropped]}


def _sham_tool_forgetting(t: Trajectory, spec: FaultSpec) -> tuple[FaultSite, dict]:
    # Add the same #decoy tools but APPEND them (real tools stay prominent) — matched, no burial.
    _check_msg_index(t, spec.position, insert=False)
    t.tools += decoy_tool_names(max(1, int(spec.volume)))
    return FaultSite("message", str(spec.position)), {"buried_step": spec.position}


_SHAM_DISPATCH = {
    FaultType.DEBRIS: _sham_insert,
    FaultType.STALENESS: _sham_insert,
    FaultType.CONTRADICTION: _sham_insert,
    FaultType.WRONG_TOOL: _sham_wrong_tool,
    FaultType.CONSTRAINT_DROP: _sham_constraint_drop,
    FaultType.TOOL_FORGETTING: _sham_tool_forgetting,
}


def sham_inject(traj: Trajectory, spec: FaultSpec) -> Corruption:
    """Volume-matched NEUTRAL control for `spec`'s fault type. label.sham=True; no real fault."""
    t = copy.deepcopy(traj)
    site, extra = _SHAM_DISPATCH[spec.type](t, spec)
    t.meta["fault"] = {"type": f"sham:{spec.type.value}", "site": [site.kind, site.ref]}
    t.meta["corrupted"] = True
    t.meta.update(extra)
    return Corruption(
        corrupted=t, label=FaultRecord(spec.type, site, spec.volume, extra, sham=True)
    )
