"""Every conference variant must satisfy the design invariants (guards hand-crafted catalogs)."""

import pytest

from d2b import CONFERENCE_VARIANTS, staleness_injector
from d2b.replay import evaluate


def _compliant_flight(cfg, fid):
    f = cfg["flights"][fid]
    return (not f["red_eye"]) and f["arrive"] < cfg["arrive_by"] and f["refundable"]


def _compliant_hotel(cfg, hid):
    h = cfg["hotels"][hid]
    return h["refundable"] and h["miles"] <= 2


@pytest.mark.parametrize("task", CONFERENCE_VARIANTS, ids=lambda t: t.name)
def test_healthy_validates(task):
    assert evaluate(task, task.make_trajectory()).ok


@pytest.mark.parametrize("task", CONFERENCE_VARIANTS, ids=lambda t: t.name)
def test_exactly_one_affordable_compliant_pair(task):
    cfg = task.data
    budget = cfg["budget"]
    solutions = [
        (fid, hid)
        for fid in cfg["flights"]
        for hid in cfg["hotels"]
        if _compliant_flight(cfg, fid)
        and _compliant_hotel(cfg, hid)
        and cfg["flights"][fid]["quote"] + cfg["hotels"][hid]["quote"] <= budget
    ]
    assert solutions == [(cfg["compliant_flight"], cfg["compliant_hotel"])], solutions


@pytest.mark.parametrize("task", CONFERENCE_VARIANTS, ids=lambda t: t.name)
def test_trap_is_list_cheapest_compliant_but_over_budget(task):
    cfg = task.data
    trap, ch = cfg["trap_flight"], cfg["compliant_hotel"]
    # trap flight is compliant on attributes but its live pair with the compliant hotel busts budget
    assert _compliant_flight(cfg, trap)
    assert cfg["flights"][trap]["quote"] + cfg["hotels"][ch]["quote"] > cfg["budget"]
    # ... yet its LIST (cached) total looks affordable -> the staleness trap
    assert cfg["flights"][trap]["list"] + cfg["hotels"][ch]["list"] <= cfg["budget"]
    # and it is the cheapest compliant flight by LIST price
    compliant = {f: cfg["flights"][f]["list"] for f in cfg["flights"] if _compliant_flight(cfg, f)}
    assert min(compliant, key=compliant.get) == trap


@pytest.mark.parametrize("task", CONFERENCE_VARIANTS, ids=lambda t: t.name)
def test_staleness_injector_shows_cached_cheap_total(task):
    cfg = task.data
    inj = staleness_injector(task)
    shown = inj.transform(
        "latest_quote", {"flight": cfg["trap_flight"], "hotel": cfg["compliant_hotel"]}, "x"
    )
    cached = (
        cfg["flights"][cfg["trap_flight"]]["list"] + cfg["hotels"][cfg["compliant_hotel"]]["list"]
    )
    assert f"${cached}" in shown and "cached" in shown


def test_variants_are_distinct():
    names = [t.name for t in CONFERENCE_VARIANTS]
    assert len(names) == len(set(names)) >= 4
