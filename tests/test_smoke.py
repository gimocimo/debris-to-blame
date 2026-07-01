"""Smoke tests — keep the scaffold honest until M1 lands real logic."""

import d2b
from d2b.faults import FaultSpec, FaultType


def test_version():
    assert d2b.__version__ == "0.0.0"


def test_fault_taxonomy_frozen():
    # The six v0 fault types are the frozen contract (PROJECT_PLAN §5).
    assert {f.value for f in FaultType} == {
        "debris",
        "staleness",
        "contradiction",
        "wrong_tool",
        "constraint_drop",
        "tool_forgetting",
    }


def test_blame_label_is_type_and_position():
    spec = FaultSpec(type=FaultType.WRONG_TOOL, position=7, volume=2.0)
    assert spec.blame_label == ("wrong_tool", 7)
