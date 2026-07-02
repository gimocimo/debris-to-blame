"""Tests for sham controls — volume-matched neutral perturbations with no real fault."""

import pytest

from d2b import TRAVEL_TEMPTING, FaultSpec, FaultType, sham_inject
from d2b.domains import REPO_TRIAGE


def _traj():
    return TRAVEL_TEMPTING.make_trajectory()


@pytest.mark.parametrize("ftype", list(FaultType))
def test_sham_is_marked_and_not_a_real_fault(ftype):
    t = _traj()
    pos = 0 if ftype is FaultType.CONSTRAINT_DROP else 5 if ftype is FaultType.WRONG_TOOL else 3
    c = sham_inject(t, FaultSpec(ftype, position=pos, volume=2))
    assert c.label.sham is True
    assert not any(m.injected for m in c.public.messages)  # redacted public trace has no markers


def test_debris_sham_matches_volume_but_is_benign():
    t = _traj()
    c = sham_inject(t, FaultSpec(FaultType.DEBRIS, position=3, volume=3))
    shams = [m for m in c.corrupted.messages if m.injected == "sham"]
    assert len(shams) == 3  # same count as debris volume
    assert all("Unrelated" not in (m.content or "") for m in shams)  # benign, not junk


def test_wrong_tool_sham_keeps_the_correct_call():
    t = _traj()
    c = sham_inject(t, FaultSpec(FaultType.WRONG_TOOL, position=5, volume=2))
    # a redundant duplicate of book_flight, NOT a swap to another tool
    dup = c.corrupted.messages[5]
    assert dup.tool_call.name == "book_flight"


def test_constraint_drop_sham_drops_a_nontarget_rule():
    t = _traj()  # constraints: [no-red-eye (0, binding), no-overbudget (1, non-binding)]
    c = sham_inject(t, FaultSpec(FaultType.CONSTRAINT_DROP, position=0, volume=1))
    # the binding no-red-eye rule SURVIVES; a different (last) rule is dropped
    assert "Never book a red-eye flight." in c.corrupted.constraints
    assert c.label.extra["dropped_constraint"] == ["Never exceed the stated budget."]


def test_tool_forgetting_sham_appends_not_buries():
    t = _traj()
    c = sham_inject(t, FaultSpec(FaultType.TOOL_FORGETTING, position=5, volume=5))
    assert len(c.corrupted.tools) == len(t.tools) + 5
    assert c.corrupted.tools.index("book_flight") < 5  # real tools stay prominent (not buried)


def test_constraint_drop_sham_needs_two_constraints():
    # repo_triage has 2 constraints, ok; a 1-constraint trajectory would raise.
    c = sham_inject(REPO_TRIAGE.make_trajectory(), FaultSpec(FaultType.CONSTRAINT_DROP, 0))
    assert c.label.sham is True
