"""M1 tests — injection, kind-tagged labels, per-fault volume, and the leakage-free guarantee."""

import copy

import pytest

from d2b import (
    FaultSpec,
    FaultType,
    Trajectory,
    inject,
    redact_for_attribution,
    successful_flight_trajectory,
)
from d2b.faults import LEAKAGE_META_KEYS


def test_fixture_is_clean_and_successful():
    t = successful_flight_trajectory()
    assert t.meta["success"] is True
    assert "Never book a red-eye flight." in t.constraints
    assert all(m.injected is None for m in t.messages)


def test_inject_never_mutates_original():
    base = successful_flight_trajectory()
    snapshot = copy.deepcopy(base.to_dict())
    inject(base, FaultSpec(FaultType.DEBRIS, position=3))
    assert base.to_dict() == snapshot


@pytest.mark.parametrize("ftype", list(FaultType))
def test_blame_label_is_kind_tagged(ftype):
    base = successful_flight_trajectory()
    pos = 0 if ftype is FaultType.CONSTRAINT_DROP else 5 if ftype is FaultType.WRONG_TOOL else 3
    c = inject(base, FaultSpec(ftype, position=pos, volume=1))
    kind, ref = c.label.site.kind, c.label.site.ref
    assert c.label.blame_label == (ftype.value, kind, ref)
    assert kind in {"message", "constraint", "tool"}


# ---- the leakage-free guarantee (Codex audit, D-009) -------------------------------------------


@pytest.mark.parametrize("ftype", list(FaultType))
def test_public_trace_has_no_leakage(ftype):
    base = successful_flight_trajectory()
    pos = 0 if ftype is FaultType.CONSTRAINT_DROP else 5 if ftype is FaultType.WRONG_TOOL else 3
    pub = inject(base, FaultSpec(ftype, position=pos, volume=2)).public
    assert all(m.injected is None for m in pub.messages)  # no injection markers
    assert not (set(pub.meta) & LEAKAGE_META_KEYS)  # no label metadata
    # and it must not accidentally serialize a marker either:
    assert "injected" not in pub.to_dict()["messages"][pos] if pos < len(pub.messages) else True


def test_redact_is_idempotent_and_pure():
    base = successful_flight_trajectory()
    c = inject(base, FaultSpec(FaultType.STALENESS, position=5))
    once = redact_for_attribution(c.corrupted)
    twice = redact_for_attribution(once)
    assert once.to_dict() == twice.to_dict()
    assert any(m.injected == "staleness" for m in c.corrupted.messages)  # original marks intact


# ---- volume is a real severity knob for every fault type ----------------------------------------


def test_debris_volume_controls_count():
    base = successful_flight_trajectory()
    c = inject(base, FaultSpec(FaultType.DEBRIS, position=3, volume=3))
    assert sum(m.injected == "debris" for m in c.corrupted.messages) == 3


def test_staleness_volume_controls_price():
    base = successful_flight_trajectory()
    low = inject(base, FaultSpec(FaultType.STALENESS, position=5, volume=1)).corrupted.messages[5]
    high = inject(base, FaultSpec(FaultType.STALENESS, position=5, volume=3)).corrupted.messages[5]
    assert "$780" in low.content and "$1040" in high.content


def test_contradiction_volume_controls_strength():
    base = successful_flight_trajectory()
    low = inject(base, FaultSpec(FaultType.CONTRADICTION, position=3, volume=1)).corrupted.messages[
        3
    ]
    high = inject(
        base, FaultSpec(FaultType.CONTRADICTION, position=3, volume=2)
    ).corrupted.messages[3]
    assert "$400" in low.content and "$0" in high.content


def test_wrong_tool_swaps_to_a_real_in_domain_tool():
    base = successful_flight_trajectory()  # tools = [check_budget, search_flights, book_flight]
    near = inject(base, FaultSpec(FaultType.WRONG_TOOL, position=5, volume=1)).corrupted
    far = inject(base, FaultSpec(FaultType.WRONG_TOOL, position=5, volume=3)).corrupted
    # pos 5 = book_flight; candidates = [check_budget, search_flights]
    assert near.messages[5].tool_call.name == "check_budget"  # nearest alternative
    assert far.messages[5].tool_call.name == "search_flights"  # farthest alternative
    assert near.messages[5].tool_call.name != far.messages[5].tool_call.name


def test_constraint_drop_volume_drops_multiple():
    base = successful_flight_trajectory()
    c = inject(base, FaultSpec(FaultType.CONSTRAINT_DROP, position=0, volume=2))
    assert c.corrupted.constraints == []
    assert len(c.label.extra["dropped_constraint"]) == 2


def test_tool_forgetting_volume_controls_burial_depth():
    base = successful_flight_trajectory()
    c = inject(base, FaultSpec(FaultType.TOOL_FORGETTING, position=5, volume=5))
    assert len(c.corrupted.tools) == len(base.tools) + 5
    assert c.corrupted.tools.index("book_flight") >= 5


def test_wrong_tool_rejects_non_toolcall_step():
    base = successful_flight_trajectory()
    with pytest.raises(ValueError):
        inject(base, FaultSpec(FaultType.WRONG_TOOL, position=0))


def test_json_round_trip_survives_injection():
    base = successful_flight_trajectory()
    c = inject(base, FaultSpec(FaultType.STALENESS, position=5))
    restored = Trajectory.from_dict(c.corrupted.to_dict())
    assert restored.to_dict() == c.corrupted.to_dict()
