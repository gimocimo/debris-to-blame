"""Tests for the multi-step CONFERENCE_TRIP task — healthy validates; failure modes are caught."""

import copy

from d2b import CONFERENCE_TRIP as CT
from d2b import FaultSpec, FaultType, inject
from d2b.env import World
from d2b.replay import evaluate, replay


def test_healthy_validates_and_is_multi_step():
    t = CT.make_trajectory()
    res = evaluate(CT, t)
    assert res.ok, res.reason
    # genuinely multi-step: >=6 distinct tool calls
    calls = {m.tool_call.name for m in t.messages if m.tool_call}
    assert calls >= {"book_flight", "book_hotel", "file_expense_report", "send_itinerary"}


def test_replay_reaches_the_full_committed_state():
    w: World = replay(CT.make_trajectory(), CT.make_env())
    assert w["booked_flight"]["id"] == "F1" and w["booked_hotel"]["id"] == "H1"
    assert w["report_filed"] and w["itinerary_sent"]


def _replace_call(t, name, new_args_id):
    """Return a copy of trajectory t with the first call to `name` rebooked to new_args_id."""
    t = copy.deepcopy(t)
    for m in t.messages:
        if m.tool_call and m.tool_call.name == name:
            m.tool_call.args = {"id": new_args_id}
            break
    return t


def test_red_eye_flight_fails():
    r = evaluate(CT, _replace_call(CT.make_trajectory(), "book_flight", "F2"))
    assert not r.ok and "red-eye" in r.reason


def test_late_arrival_flight_fails():
    r = evaluate(CT, _replace_call(CT.make_trajectory(), "book_flight", "F3"))
    assert not r.ok and "after" in r.reason


def test_non_refundable_hotel_fails():
    r = evaluate(CT, _replace_call(CT.make_trajectory(), "book_hotel", "H2"))
    assert not r.ok and "refundable" in r.reason


def test_far_hotel_fails():
    r = evaluate(CT, _replace_call(CT.make_trajectory(), "book_hotel", "H3"))
    assert not r.ok and "away" in r.reason


def test_missing_expense_report_fails():
    t = copy.deepcopy(CT.make_trajectory())
    t.messages = [
        m for m in t.messages if not (m.tool_call and m.tool_call.name == "file_expense_report")
    ]
    r = evaluate(CT, t)
    assert not r.ok and "expense report" in r.reason


def test_missing_itinerary_fails():
    t = copy.deepcopy(CT.make_trajectory())
    t.messages = [
        m for m in t.messages if not (m.tool_call and m.tool_call.name == "send_itinerary")
    ]
    r = evaluate(CT, t)
    assert not r.ok and "itinerary" in r.reason


def test_wrong_tool_at_book_flight_breaks_it():
    # wrong_tool at the critical step swaps to another in-domain tool -> no flight booked
    t = CT.make_trajectory()
    c = inject(t, FaultSpec(FaultType.WRONG_TOOL, position=CT.critical_step, volume=1))
    assert not evaluate(CT, c.corrupted).ok
