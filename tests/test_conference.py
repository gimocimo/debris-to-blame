"""CONFERENCE_TRIP (redesigned) — healthy validates; validator loopholes closed; staleness bites;
constraint_drop no longer leaks via a policy tool; interactive rollout works."""

from d2b import CONFERENCE_TRIP as CT
from d2b import (
    FaultSpec,
    FaultType,
    ToolCall,
    inject,
    interactive_rollout,
    scripted_policy_fn,
    sham_inject,
    staleness_injector,
)
from d2b.replay import evaluate, replay

# --- static (healthy + validator gameability) ----------------------------------------------------


def test_healthy_validates_and_is_multi_step():
    t = CT.make_trajectory()
    r = evaluate(CT, t)
    assert r.ok, r.reason
    assert "F4+H1" in r.reason  # the compliant+affordable pick, not list-cheapest F1
    calls = {m.tool_call.name for m in t.messages if m.tool_call}
    assert {
        "latest_quote",
        "book_flight",
        "book_hotel",
        "file_expense_report",
        "send_itinerary",
    } <= calls


def test_no_get_policy_tool():
    assert "get_policy" not in CT.make_env().names()  # so constraint_drop can't be re-leaked


def _decisions_from(traj):
    return [
        {"tool": m.tool_call.name, "args": m.tool_call.args}
        for m in traj.messages
        if m.tool_call is not None
    ]


def _rollout(decisions, injectors=(), setup=None):
    return interactive_rollout(
        CT, scripted_policy_fn(decisions), setup or CT.make_trajectory(), injectors=injectors
    )


def test_interactive_healthy_validates():
    r = _rollout(_decisions_from(CT.make_trajectory()))
    assert r.status == "finished" and r.result.ok, r.result.reason


def test_duplicate_booking_is_rejected():
    # book the correct flight twice -> "must book exactly one flight"
    dec = _decisions_from(CT.make_trajectory())
    dec.insert(
        dec.index({"tool": "book_flight", "args": {"flight": "F4"}}) + 1,
        {"tool": "book_flight", "args": {"flight": "F4"}},
    )
    r = _rollout(dec)
    assert not r.result.ok and "exactly one flight" in r.result.reason


def test_file_before_booking_is_rejected():
    # file the report first, before any booking -> out-of-order
    dec = [{"tool": "file_expense_report", "args": {}}] + _decisions_from(CT.make_trajectory())
    r = _rollout(dec)
    assert not r.result.ok


def test_parse_fail_is_an_outcome_not_a_crash():
    r = interactive_rollout(CT, scripted_policy_fn([None]), CT.make_trajectory())
    assert r.status == "parse_fail" and not r.result.ok


# --- staleness now BITES (the core review fix) ---------------------------------------------------


def test_staleness_lures_agent_into_over_budget_booking():
    # A greedy agent trusts the cached (cheap-looking) quote and books list-cheapest F1+H1.
    greedy = [
        {"tool": "search_flights", "args": {}},
        {"tool": "search_hotels", "args": {}},
        {"tool": "latest_quote", "args": {"flight": "F1", "hotel": "H1"}},  # sees stale $1050
        {"tool": "book_flight", "args": {"flight": "F1"}},
        {"tool": "book_hotel", "args": {"hotel": "H1"}},
        {"tool": "file_expense_report", "args": {}},
        {"tool": "send_itinerary", "args": {}},
    ]
    # The validator uses TRUTH (fails on budget regardless); the KEY check is what the agent SAW.
    stale = _rollout(greedy, injectors=(staleness_injector(),))
    # the agent's observation was the stale cheap total, disguised as live ...
    quote_obs = [m for m in stale.transcript if m.tool_name == "latest_quote"][0].content
    assert "1050" in quote_obs and "(live)" in quote_obs and "cached" not in quote_obs
    # ... but truth (validator) catches the over-budget F1+H1 booking:
    assert not stale.result.ok and "budget" in stale.result.reason


def test_latest_quote_is_authoritative_truth_regardless_of_injection():
    # world tracks the TRUE surged total even when the agent is shown a stale one
    r = _rollout(
        [{"tool": "latest_quote", "args": {"flight": "F1", "hotel": "H1"}}],
        injectors=(staleness_injector(),),
    )
    assert r.world["latest"]["total"] == 1350  # truth: F1 surged to 950 + H1 400


# --- constraint_drop no longer leaks; sham drops the inert rule ----------------------------------


def test_constraint_drop_removes_rule_everywhere():
    t = CT.make_trajectory()
    # drop "The hotel must be refundable." (index 2)
    c = inject(t, FaultSpec(FaultType.CONSTRAINT_DROP, position=2))
    assert not any("refundable" in cstr for cstr in c.public.constraints)
    # and it does not linger in any message content (no policy tool re-leak)
    assert not any(
        "hotel must be refundable" in (m.content or "").lower() for m in c.public.messages
    )


def test_conference_sham_drops_the_inert_rule():
    t = CT.make_trajectory()
    c = sham_inject(t, FaultSpec(FaultType.CONSTRAINT_DROP, position=0))
    dropped = c.label.extra["dropped_constraint"][0]
    assert "rental car" in dropped and "electric" in dropped  # the designated inert rule
    assert "Never book a red-eye flight." in c.corrupted.constraints  # binding rules survive


def test_wrong_tool_at_critical_step_breaks_it():
    t = CT.make_trajectory()
    c = inject(t, FaultSpec(FaultType.WRONG_TOOL, position=CT.critical_step, volume=1))
    assert not evaluate(CT, c.corrupted).ok


def test_replay_reaches_committed_state():
    w = replay(CT.make_trajectory(), CT.make_env())
    assert w["booked_flight"]["id"] == "F4" and w["booked_hotel"]["id"] == "H1"
    assert w["report_filed"] and w["itinerary_sent"] and w["latest"]["fid"] == "F4"


def test_toolcall_import_ok():
    assert ToolCall("book_flight", {"flight": "F4"}).name == "book_flight"


def test_grade_attribution_distinguishes_the_specific_rule():
    from d2b.detective import grade_attribution

    # drop "The hotel must be refundable." -> distinguishing token 'refundable'
    rec = inject(CT.make_trajectory(), FaultSpec(FaultType.CONSTRAINT_DROP, position=2)).label
    good = grade_attribution({"problem": True, "culprit": "dropped the refundable-hotel rule"}, rec)
    assert good["attributed"]
    # blaming a DIFFERENT rule must not count as attributed
    assert not grade_attribution({"problem": True, "culprit": "a red-eye was booked"}, rec)[
        "attributed"
    ]
    assert not grade_attribution({"problem": True, "culprit": "some policy was dropped"}, rec)[
        "attributed"
    ]


def test_grade_attribution_sham_is_correct_when_not_flagged():
    from d2b.detective import grade_attribution

    rec = sham_inject(CT.make_trajectory(), FaultSpec(FaultType.CONSTRAINT_DROP, position=0)).label
    assert grade_attribution({"problem": False, "culprit": "none"}, rec)[
        "correct"
    ]  # no false-alarm
    assert not grade_attribution({"problem": True, "culprit": "x"}, rec)["correct"]  # flagged sham
