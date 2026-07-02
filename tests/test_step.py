"""Tests for the interactive-rollout driver's core logic (experiments/step.py)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "experiments"))

import step  # noqa: E402


def _run(condition, decisions):
    state = {"condition": condition, "decisions": decisions}
    return step.replay(state)


HEALTHY = [
    {"tool": "search_flights", "args": {}},
    {"tool": "search_hotels", "args": {}},
    {"tool": "latest_quote", "args": {"flight": "F1", "hotel": "H1"}},
    {"tool": "latest_quote", "args": {"flight": "F4", "hotel": "H1"}},
    {"tool": "book_flight", "args": {"flight": "F4"}},
    {"tool": "book_hotel", "args": {"hotel": "H1"}},
    {"tool": "file_expense_report", "args": {}},
    {"tool": "send_itinerary", "args": {}},
]
GREEDY_F1 = [
    {"tool": "search_flights", "args": {}},
    {"tool": "latest_quote", "args": {"flight": "F1", "hotel": "H1"}},
    {"tool": "book_flight", "args": {"flight": "F1"}},
    {"tool": "book_hotel", "args": {"hotel": "H1"}},
    {"tool": "file_expense_report", "args": {}},
    {"tool": "send_itinerary", "args": {}},
]


def test_healthy_rollout_passes():
    assert _run("healthy", HEALTHY).result.ok


def test_staleness_shows_cached_but_validator_uses_truth():
    r = _run("staleness", GREEDY_F1)
    quote = [m for m in r.transcript if m.tool_name == "latest_quote"][0].content
    assert "$1050" in quote and "cached" in quote  # agent SAW the stale cheap quote
    assert not r.result.ok and "budget" in r.result.reason  # validator caught true $1350


def test_constraint_drop_condition_removes_the_rule_from_the_prompt():
    setup, _ = step.setup_and_injectors("cdrop:2")  # drop "hotel must be refundable"
    assert not any("refundable" in c for c in setup.constraints)


def test_start_prompt_does_not_name_the_condition():
    setup, _ = step.setup_and_injectors("staleness")
    prompt = step.render_initial(setup)
    assert "staleness" not in prompt.lower() and "inject" not in prompt.lower()
