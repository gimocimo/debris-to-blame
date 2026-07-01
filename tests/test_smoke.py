"""Smoke tests — package sanity + the fault manifest (idea space is NOT frozen, D-013)."""

import d2b
from d2b.faults import FaultType

# The v0 manifest: the six fault types we ship experiments for. New types may be ADDED without
# breaking this test — we assert these exist, not that the enum is closed (Codex cut-list, D-013).
V0_MANIFEST = {
    "debris",
    "staleness",
    "contradiction",
    "wrong_tool",
    "constraint_drop",
    "tool_forgetting",
}


def test_version():
    assert d2b.__version__ == "0.0.0"


def test_v0_manifest_present():
    assert V0_MANIFEST <= {f.value for f in FaultType}
