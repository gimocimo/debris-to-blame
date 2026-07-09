"""Invariants for the INCIDENT domain (diagnostic chain: root cause upstream of the alert)."""

import pytest

from d2b import INCIDENT_VARIANTS
from d2b.incident import staleness_injector
from d2b.replay import evaluate


@pytest.mark.parametrize("task", INCIDENT_VARIANTS, ids=lambda t: t.name)
def test_healthy_validates(task):
    assert evaluate(task, task.make_trajectory()).ok


@pytest.mark.parametrize("task", INCIDENT_VARIANTS, ids=lambda t: t.name)
def test_exactly_one_root_and_it_is_the_hidden_trap(task):
    cfg = task.data
    roots = [s for s, d in cfg["services"].items() if d["root"]]
    assert roots == [cfg["root"]]
    root = cfg["services"][cfg["root"]]
    assert root["live"] == "down"  # the root is actually broken
    assert root["cached"] == "healthy"  # ... but reads healthy when stale (the deception)
    assert root["upstream"] is None  # nothing upstream is breaking it


@pytest.mark.parametrize("task", INCIDENT_VARIANTS, ids=lambda t: t.name)
def test_symptom_is_far_from_cause(task):
    cfg = task.data
    assert cfg["alert_service"] != cfg["root"]  # the alert fires downstream of the cause
    assert cfg["services"][cfg["alert_service"]]["live"] == "degraded"


@pytest.mark.parametrize("task", INCIDENT_VARIANTS, ids=lambda t: t.name)
def test_one_healthy_payments_redline(task):
    cfg = task.data
    red = [s for s, d in cfg["services"].items() if d["redline"]]
    assert len(red) == 1
    assert cfg["services"][red[0]]["live"] == "healthy"  # touching it is purely harmful


@pytest.mark.parametrize("task", INCIDENT_VARIANTS, ids=lambda t: t.name)
def test_staleness_hides_the_down_root_but_looks_live(task):
    cfg = task.data
    root = cfg["root"]
    true = f"{root}: status=down, depends_on=none (live)."
    shown = staleness_injector(task).transform("check", {"service": root}, true)
    assert "status=healthy" in shown and "(live)" in shown and "cached" not in shown


def test_variants_distinct():
    names = [t.name for t in INCIDENT_VARIANTS]
    assert len(names) == len(set(names)) >= 4
