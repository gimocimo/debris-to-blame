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
def test_staleness_injector_swaps_in_cheap_total_but_looks_live(task):
    cfg = task.data
    f, h = cfg["trap_flight"], cfg["compliant_hotel"]
    live = cfg["flights"][f]["quote"] + cfg["hotels"][h]["quote"]
    cached = cfg["flights"][f]["list"] + cfg["hotels"][h]["list"]
    true = f"Quote v2: {f}+{h} = ${live} (live)."
    shown = staleness_injector(task).transform("latest_quote", {"flight": f, "hotel": h}, true)
    # a TRUE deception: cheap cached total, still tagged "(live)", no self-labelling "cached" tell
    assert f"${cached}" in shown and "(live)" in shown and "cached" not in shown


def test_variants_are_distinct():
    names = [t.name for t in CONFERENCE_VARIANTS]
    assert len(names) == len(set(names)) >= 4
