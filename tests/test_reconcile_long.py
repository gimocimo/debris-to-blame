"""Invariants for RECONCILE_LONG (the accumulation loop at a real horizon; fault depth varies)."""

import pytest

from d2b import RECONCILE_LONG_VARIANTS
from d2b.reconcile import _reconciles, staleness_injector
from d2b.replay import evaluate


@pytest.mark.parametrize("task", RECONCILE_LONG_VARIANTS, ids=lambda t: t.name)
def test_healthy_validates(task):
    assert evaluate(task, task.make_trajectory()).ok


@pytest.mark.parametrize("task", RECONCILE_LONG_VARIANTS, ids=lambda t: t.name)
def test_batch_is_long_and_scales(task):
    cfg = task.data
    assert cfg["n_txns"] == len(cfg["transactions"])
    # a real horizon: the healthy trajectory is ~2N interactive turns
    assert len(task.make_trajectory().messages) >= 2 * cfg["n_txns"]
    assert cfg["max_steps"] >= 2 * cfg["n_txns"]


@pytest.mark.parametrize("task", RECONCILE_LONG_VARIANTS, ids=lambda t: t.name)
def test_exactly_one_trap_and_it_is_hidden_by_staleness(task):
    cfg = task.data
    trap = cfg["trap_txn"]
    d = cfg["transactions"][trap]
    assert d["cached_receipt"] == d["amount"]  # looks fine cached
    assert d["live_receipt"] != d["amount"]  # ... but the live receipt does not match
    assert not _reconciles(cfg, trap)  # so it must NOT be approved
    true = (f"{trap}: charge ${d['amount']}, receipt ${d['live_receipt']}, "
            f"category {d['category']} (live).")
    shown = staleness_injector(task).transform("check_receipt", {"txn": trap}, true)
    assert f"receipt ${d['amount']}" in shown and "(live)" in shown and "cached" not in shown


@pytest.mark.parametrize("task", RECONCILE_LONG_VARIANTS, ids=lambda t: t.name)
def test_many_reconcilers_and_a_couple_blocked(task):
    cfg = task.data
    good = [t for t in cfg["transactions"] if _reconciles(cfg, t)]
    blocked = [t for t, d in cfg["transactions"].items()
               if d["category"] in cfg["blocked_categories"]]
    assert len(good) >= 4 and cfg["trap_txn"] not in good
    assert len(blocked) >= 1  # blocked-category txns exist (cdrop:blocked is a real fault here)


def test_lengths_and_depths_span_a_range():
    ns = sorted({t.data["n_txns"] for t in RECONCILE_LONG_VARIANTS})
    depths = sorted({t.data["trap_depth"] for t in RECONCILE_LONG_VARIANTS})
    assert ns == [8, 24, 48]  # a genuine horizon sweep
    assert min(depths) < 0.2 and max(depths) > 0.8  # trap depth spans early -> late
    assert len({t.name for t in RECONCILE_LONG_VARIANTS}) == 12
