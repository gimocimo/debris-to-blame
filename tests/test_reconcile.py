"""Invariants for the RECONCILE domain (per-item validation loop over a batch)."""

import pytest

from d2b import RECONCILE_VARIANTS
from d2b.reconcile import _reconciles, staleness_injector
from d2b.replay import evaluate


@pytest.mark.parametrize("task", RECONCILE_VARIANTS, ids=lambda t: t.name)
def test_healthy_validates(task):
    assert evaluate(task, task.make_trajectory()).ok


@pytest.mark.parametrize("task", RECONCILE_VARIANTS, ids=lambda t: t.name)
def test_trap_looks_reconciled_cached_but_not_live(task):
    cfg = task.data
    trap = cfg["transactions"][cfg["trap_txn"]]
    assert trap["cached_receipt"] == trap["amount"]  # looks fine by the cached receipt
    assert trap["live_receipt"] != trap["amount"]  # ... but the live receipt does not match
    assert not _reconciles(cfg, cfg["trap_txn"])  # so it must NOT be approved


@pytest.mark.parametrize("task", RECONCILE_VARIANTS, ids=lambda t: t.name)
def test_there_is_a_blocked_category_txn_and_some_valid_ones(task):
    cfg = task.data
    blocked = [
        t for t, d in cfg["transactions"].items() if d["category"] in cfg["blocked_categories"]
    ]
    valid = [t for t in cfg["transactions"] if _reconciles(cfg, t)]
    assert blocked, "no blocked-category transaction (cdrop:blocked would be a null fault)"
    assert len(valid) >= 2  # a real batch: several to approve, plus traps to flag
    assert cfg["trap_txn"] not in valid


@pytest.mark.parametrize("task", RECONCILE_VARIANTS, ids=lambda t: t.name)
def test_staleness_makes_the_trap_receipt_appear_to_match(task):
    cfg = task.data
    trap = cfg["trap_txn"]
    d = cfg["transactions"][trap]
    true = (f"{trap}: charge ${d['amount']}, receipt ${d['live_receipt']}, "
            f"category {d['category']} (live).")
    shown = staleness_injector(task).transform("check_receipt", {"txn": trap}, true)
    assert f"receipt ${d['amount']}" in shown and "(live)" in shown and "cached" not in shown


def test_variants_distinct():
    names = [t.name for t in RECONCILE_VARIANTS]
    assert len(names) == len(set(names)) >= 4
