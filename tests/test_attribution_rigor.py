"""Tests for the de-contaminated attribution rig: de-leak arm, generalized grader, baselines,
variant clustering, and the tool_forgetting condition."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "experiments"))

import attr_baselines  # noqa: E402
import attribute  # noqa: E402
import step  # noqa: E402
from attr_common import record_for  # noqa: E402

import d2b  # noqa: E402
from d2b.detective import grade_attribution  # noqa: E402
from d2b.stats import cluster_by_variant  # noqa: E402

TASK = d2b.CONFERENCE_VARIANTS[0]
REDEYE_RULE = "Never book a red-eye flight."


def _state(condition: str, variant: int = 0) -> dict:
    return {"condition": condition, "variant": variant,
            "decisions": [{"tool": "search_flights", "args": {}}]}


def test_reconstruct_blind_hides_dropped_rule_oracle_shows_it():
    traj, task, dropped = attribute.reconstruct(_state("cdrop:0"))
    assert dropped == REDEYE_RULE
    # blind view (the agent's own standing rules) no longer contains the dropped rule
    assert REDEYE_RULE not in traj.constraints
    # oracle policy still holds it; de-leaked rulebook (policy minus index 0) does not
    assert REDEYE_RULE in task.data["policy"]
    deleaked = [r for i, r in enumerate(task.data["policy"]) if i != 0]
    assert REDEYE_RULE not in deleaked
    assert len(deleaked) == len(task.data["policy"]) - 1


def test_grade_attribution_staleness_via_attr_keys():
    rec = record_for("staleness", TASK)
    assert grade_attribution({"problem": True, "culprit": "acted on a stale cached quote"}, rec)[
        "attributed"
    ]
    # naming an unrelated step does NOT count
    assert not grade_attribution({"problem": True, "culprit": "book_flight at step 9"}, rec)[
        "attributed"
    ]


def test_grade_attribution_tool_forgetting():
    rec = record_for("forget:file_expense_report", TASK)
    assert grade_attribution({"problem": True, "culprit": "never filed the expense report"}, rec)[
        "attributed"
    ]
    bad = grade_attribution({"problem": True, "culprit": "booked a red-eye"}, rec)
    assert not bad["attributed"]


def test_sham_record_correct_when_not_flagged():
    rec = record_for("sham", TASK)
    assert grade_attribution({"problem": False, "culprit": "none"}, rec)["correct"]
    assert not grade_attribution({"problem": True, "culprit": "something"}, rec)["correct"]


def test_keyword_baseline_fires_and_redeye_tell_is_in_every_listing():
    # a stale latest_quote leaves a "(cached)" tell in the trace
    stale_state = {"condition": "staleness", "variant": 0, "decisions": [
        {"tool": "search_flights", "args": {}},
        {"tool": "latest_quote", "args": {"flight": "F1", "hotel": "H1"}},
    ]}
    traj, _task, _ = attribute.reconstruct(stale_state)
    text = "\n".join((m.content or "") for m in traj.messages).lower()
    assert "cached" in text  # staleness tell survives redaction (an honest caveat we surface)
    # the grep baseline fires, but note "red-eye" is a tell present in EVERY flight listing —
    # so keyword attribution is imprecise (high false-positive), which its FP column exposes
    assert attr_baselines.keyword_baseline(traj)["problem"]
    assert "red-eye" in text
    for v in (attr_baselines.random_baseline(traj, 0), attr_baselines.recency_baseline(traj)):
        assert set(v) == {"problem", "culprit"}


def test_cluster_by_variant_counts_affected():
    # 3 variants fully fail, 1 fully passes -> 3 of 4 affected
    pv = {0: (2, 2), 1: (2, 2), 2: (2, 2), 3: (0, 2)}
    assert cluster_by_variant(pv) == (3, 4)
    assert cluster_by_variant({0: (0, 2), 1: (0, 2)}) == (0, 2)


def test_forget_condition_removes_tool():
    setup, injectors, _task = step.setup_and_injectors("forget:file_expense_report", 0)
    assert "file_expense_report" not in setup.tools
    assert "book_flight" in setup.tools  # only the forgotten tool is gone
    assert injectors == ()
