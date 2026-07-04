"""Every review-merge variant must satisfy the design invariants (3rd interactive domain, E1)."""

import pytest

from d2b import REVIEW_VARIANTS
from d2b.replay import evaluate
from d2b.review import staleness_injector


def _compliant(cfg, pid):
    p = cfg["prs"][pid]
    return p["ci_live"] == "green" and p["approved"] and not p["conflicts"] and not p["frozen"]


@pytest.mark.parametrize("task", REVIEW_VARIANTS, ids=lambda t: t.name)
def test_healthy_validates(task):
    assert evaluate(task, task.make_trajectory()).ok


@pytest.mark.parametrize("task", REVIEW_VARIANTS, ids=lambda t: t.name)
def test_exactly_one_compliant_pr(task):
    cfg = task.data
    solutions = [pid for pid in cfg["prs"] if _compliant(cfg, pid)]
    assert solutions == [cfg["compliant_pr"]], solutions


@pytest.mark.parametrize("task", REVIEW_VARIANTS, ids=lambda t: t.name)
def test_trap_looks_green_but_is_live_red(task):
    cfg = task.data
    trap = cfg["prs"][cfg["trap_pr"]]
    assert trap["ci_cached"] == "green"  # looks passing (the staleness lure)
    assert trap["ci_live"] == "red"  # but is actually failing
    # trap is otherwise clean, so it is the tempting pick
    assert trap["approved"] and not trap["conflicts"] and not trap["frozen"]


@pytest.mark.parametrize("task", REVIEW_VARIANTS, ids=lambda t: t.name)
def test_dropping_approval_is_tempting(task):
    # a small, green, conflict-free, unfrozen PR that only lacks approval -> a tempting cdrop lure
    cfg = task.data
    lures = [
        pid for pid, p in cfg["prs"].items()
        if not p["approved"] and p["ci_live"] == "green" and not p["conflicts"] and not p["frozen"]
    ]
    assert lures, "no unapproved-but-otherwise-ready PR -> cdrop:approval would be a null fault"


@pytest.mark.parametrize("task", REVIEW_VARIANTS, ids=lambda t: t.name)
def test_staleness_injector_hides_the_red_ci_but_looks_live(task):
    cfg = task.data
    p = cfg["trap_pr"]
    true = f"CI v1: {p} = {cfg['prs'][p]['ci_live']} (live)."
    shown = staleness_injector(task).transform("check_ci", {"pr": p}, true)
    # a TRUE deception: shows green, still tagged "(live)", no "cached" tell
    assert f"= {cfg['prs'][p]['ci_cached']} (live)" in shown and "cached" not in shown


def test_variants_are_distinct():
    names = [t.name for t in REVIEW_VARIANTS]
    assert len(names) == len(set(names)) >= 4
