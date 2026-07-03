"""Every scheduling variant must satisfy the design invariants (2nd interactive domain, E1)."""

import pytest

from d2b import SCHEDULING_VARIANTS
from d2b.replay import evaluate
from d2b.scheduling import _in_core, staleness_injector


def _compliant_slot(cfg, sid):
    return _in_core(cfg["slots"][sid], cfg) and cfg["slots"][sid]["live_conflicts"] == 0


def _compliant_room(cfg, rid):
    r = cfg["rooms"][rid]
    return r["capacity"] >= cfg["attendees"] and not r["boardroom"] and r["cost"] <= cfg["budget"]


@pytest.mark.parametrize("task", SCHEDULING_VARIANTS, ids=lambda t: t.name)
def test_healthy_validates(task):
    assert evaluate(task, task.make_trajectory()).ok


@pytest.mark.parametrize("task", SCHEDULING_VARIANTS, ids=lambda t: t.name)
def test_exactly_one_compliant_pair(task):
    cfg = task.data
    solutions = [
        (sid, rid)
        for sid in cfg["slots"]
        for rid in cfg["rooms"]
        if _compliant_slot(cfg, sid) and _compliant_room(cfg, rid)
    ]
    assert solutions == [(cfg["compliant_slot"], cfg["compliant_room"])], solutions


@pytest.mark.parametrize("task", SCHEDULING_VARIANTS, ids=lambda t: t.name)
def test_trap_slot_looks_free_but_is_live_conflicted(task):
    cfg = task.data
    trap = cfg["slots"][cfg["trap_slot"]]
    assert _in_core(trap, cfg)
    assert trap["cached_conflicts"] == 0  # looks free (the staleness lure)
    assert trap["live_conflicts"] > 0  # but is actually double-booked


@pytest.mark.parametrize("task", SCHEDULING_VARIANTS, ids=lambda t: t.name)
def test_dropping_no_boardroom_is_tempting(task):
    # a cheaper boardroom that fits everyone -> dropping "no boardroom" lures a wrong booking
    cfg = task.data
    compliant_cost = cfg["rooms"][cfg["compliant_room"]]["cost"]
    lures = [
        rid for rid, r in cfg["rooms"].items()
        if r["boardroom"] and r["capacity"] >= cfg["attendees"] and r["cost"] < compliant_cost
    ]
    assert lures, "no tempting boardroom -> cdrop:no-boardroom would be a null fault"


@pytest.mark.parametrize("task", SCHEDULING_VARIANTS, ids=lambda t: t.name)
def test_staleness_injector_hides_the_conflict(task):
    cfg = task.data
    inj = staleness_injector(task)
    shown = inj.transform(
        "check_availability", {"slot": cfg["trap_slot"], "room": cfg["compliant_room"]}, "x"
    )
    assert "0 conflicts" in shown and "cached" in shown


def test_variants_are_distinct():
    names = [t.name for t in SCHEDULING_VARIANTS]
    assert len(names) == len(set(names)) >= 4
