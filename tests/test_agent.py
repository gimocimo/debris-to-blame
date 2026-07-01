"""M2 tests — render/parse/scripted-policy plumbing for the model-backed resume."""

from d2b import (
    TRAVEL,
    decision_to_messages,
    evaluate,
    parse_decision,
    render_prefix,
    resume,
    scripted_policy,
)


def test_render_prefix_is_leakage_free_and_shows_options():
    pre = render_prefix(TRAVEL.make_trajectory(), cut=5)
    assert "TASK:" in pre and "AVAILABLE TOOLS:" in pre
    assert "BA112" in pre and "red-eye" in pre  # the agent can see the options
    assert "injected" not in pre and "blame_label" not in pre  # no leakage


def test_parse_decision_tolerates_prose():
    d = parse_decision('Sure! Here is my choice:\n{"tool": "book_flight", "args": {"id": "BA112"}}')
    assert d["tool"] == "book_flight" and d["args"]["id"] == "BA112"


def test_scripted_policy_resume_matches_a_good_booking():
    # A model that books the non-red-eye BA112 should pass the validator.
    decision = {"tool": "book_flight", "args": {"id": "BA112"}}
    res = resume(
        TRAVEL, TRAVEL.make_trajectory(), 5, scripted_policy(decision_to_messages(decision))
    )
    assert res.ok


def test_scripted_policy_resume_catches_a_red_eye_booking():
    # Booking the red-eye VS004 should FAIL the validator (this is the degradation signal).
    decision = {"tool": "book_flight", "args": {"id": "VS004"}}
    res = evaluate_via_resume(decision)
    assert not res.ok


def evaluate_via_resume(decision):
    return resume(
        TRAVEL, TRAVEL.make_trajectory(), 5, scripted_policy(decision_to_messages(decision))
    )


def test_evaluate_helper_and_domain_still_consistent():
    assert evaluate(TRAVEL, TRAVEL.make_trajectory()).ok
