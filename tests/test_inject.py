"""M1 tests — injection round-trips, ground-truth labels, and original-immutability per fault."""

import copy

import pytest

from d2b import FaultSpec, FaultType, Trajectory, inject, successful_flight_trajectory


def test_fixture_is_clean_and_successful():
    t = successful_flight_trajectory()
    assert t.meta["success"] is True
    assert "Never book a red-eye flight." in t.constraints
    assert all(m.injected is None for m in t.messages)


def test_inject_never_mutates_original():
    base = successful_flight_trajectory()
    snapshot = copy.deepcopy(base.to_dict())
    inject(base, FaultSpec(FaultType.DEBRIS, position=3))
    assert base.to_dict() == snapshot  # original untouched


@pytest.mark.parametrize("ftype", list(FaultType))
def test_blame_label_matches_spec(ftype):
    base = successful_flight_trajectory()
    pos = 0 if ftype is FaultType.CONSTRAINT_DROP else 5 if ftype is FaultType.WRONG_TOOL else 3
    spec = FaultSpec(ftype, position=pos, volume=2)
    corrupted = inject(base, spec)
    assert tuple(corrupted.meta["blame_label"]) == spec.blame_label
    assert corrupted.meta["corrupted"] is True


def test_debris_inserts_volume_messages_and_marks_them():
    base = successful_flight_trajectory()
    n = len(base.messages)
    corrupted = inject(base, FaultSpec(FaultType.DEBRIS, position=3, volume=3))
    assert len(corrupted.messages) == n + 3
    injected = [m for m in corrupted.messages if m.injected == "debris"]
    assert len(injected) == 3


def test_wrong_tool_swaps_the_call():
    base = successful_flight_trajectory()
    assert base.messages[5].tool_call.name == "book_flight"
    corrupted = inject(base, FaultSpec(FaultType.WRONG_TOOL, position=5))
    assert corrupted.messages[5].tool_call.name == "check_weather"
    assert corrupted.messages[5].injected == "wrong_tool"


def test_wrong_tool_rejects_non_toolcall_step():
    base = successful_flight_trajectory()
    with pytest.raises(ValueError):
        inject(base, FaultSpec(FaultType.WRONG_TOOL, position=0))  # position 0 is a user message


def test_constraint_drop_removes_the_rule():
    base = successful_flight_trajectory()
    corrupted = inject(base, FaultSpec(FaultType.CONSTRAINT_DROP, position=0))
    assert "Never book a red-eye flight." not in corrupted.constraints
    assert corrupted.meta["dropped_constraint"] == "Never book a red-eye flight."


def test_tool_forgetting_buries_real_tools():
    base = successful_flight_trajectory()
    corrupted = inject(base, FaultSpec(FaultType.TOOL_FORGETTING, position=5, volume=5))
    assert len(corrupted.tools) == len(base.tools) + 5
    assert "book_flight" in corrupted.tools  # still present, just buried
    assert corrupted.tools.index("book_flight") >= 5  # sunk below the decoys


def test_json_round_trip_survives_injection():
    base = successful_flight_trajectory()
    corrupted = inject(base, FaultSpec(FaultType.STALENESS, position=5))
    restored = Trajectory.from_dict(corrupted.to_dict())
    assert restored.to_dict() == corrupted.to_dict()
    assert tuple(restored.meta["blame_label"]) == ("staleness", 5)
