"""Tests for the misexecution (2nd deception type) and debris faults + root-cause arm (Phase 3)."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "experiments"))

import step  # noqa: E402
from attr_common import record_for  # noqa: E402

import d2b  # noqa: E402
from d2b.detective import grade_attribution  # noqa: E402

ORACLES = {
    # decisions that book/merge the COMPLIANT item (variant 0 of each domain)
    "conference": [
        {"tool": "search_flights", "args": {}}, {"tool": "search_hotels", "args": {}},
        {"tool": "latest_quote", "args": {"flight": "F4", "hotel": "H1"}},
        {"tool": "book_flight", "args": {"flight": "F4"}},
        {"tool": "book_hotel", "args": {"hotel": "H1"}},
        {"tool": "file_expense_report", "args": {}}, {"tool": "send_itinerary", "args": {}},
        {"finish": True},
    ],
    "scheduling": [
        {"tool": "list_slots", "args": {}}, {"tool": "list_rooms", "args": {}},
        {"tool": "check_availability", "args": {"slot": "S2", "room": "RB"}},
        {"tool": "book_slot", "args": {"slot": "S2"}},
        {"tool": "book_room", "args": {"room": "RB"}},
        {"tool": "send_invites", "args": {}}, {"tool": "post_agenda", "args": {}},
        {"finish": True},
    ],
    "review": [
        {"tool": "list_prs", "args": {}}, {"tool": "check_ci", "args": {"pr": "A2"}},
        {"tool": "merge_pr", "args": {"pr": "A2"}}, {"tool": "notify_author", "args": {}},
        {"tool": "close_ticket", "args": {}}, {"finish": True},
    ],
}
FAIL_REASON = {"conference": "red-eye", "scheduling": "boardroom", "review": "failing CI"}
CLAIMED = {"conference": "Booked flight F4.", "scheduling": "Booked room RB.",
           "review": "Merged A2."}


def _run(domain: str, condition: str):
    st = {"condition": condition, "domain": domain, "variant": 0, "decisions": ORACLES[domain]}
    return step.replay(st)


@pytest.mark.parametrize("domain", ["conference", "scheduling", "review"])
def test_misexec_world_diverges_but_observation_claims_success(domain):
    r = _run(domain, "misexec")
    # world = truth: the validator fails on the item the world ACTUALLY acted on
    assert not r.result.ok and FAIL_REASON[domain] in r.result.reason
    # ... while the agent was SHOWN a success message for what it asked for
    assert any(m.role == "tool" and m.content == CLAIMED[domain] for m in r.transcript)


@pytest.mark.parametrize("domain", ["conference", "scheduling", "review"])
def test_debris_appends_junk_but_keeps_true_value(domain):
    r = _run(domain, "debris")
    obs = [m.content for m in r.transcript if m.role == "tool" and "bulletin" in (m.content or "")]
    assert obs, "debris bulletin not injected"
    # the true signal survives (debris adds junk, not corruption) -> oracle run still passes
    assert r.result.ok


def test_grade_misexec_requires_action_locus_AND_substitution():
    rec = record_for("misexec", d2b.REVIEW_VARIANTS[0])  # fault is in merge_pr
    # correct: names the merge action AND the substitution
    ok = {"problem": True, "culprit": "merge_pr reported success but did not actually perform the "
          "requested merge — it merged a different PR"}
    assert grade_attribution(ok, rec)["attributed"]
    # WRONG MECHANISM: blames check_ci (the Codex finding) -> must NOT be credited
    wrong_tool = {"problem": True, "culprit": "tool/environment fault in check_ci: it mis-executed "
                  "the live-status lookups and returned a different result"}
    assert not grade_attribution(wrong_tool, rec)["attributed"]
    # generic 'something wrong' -> not credited
    generic = grade_attribution({"problem": True, "culprit": "some tool did something wrong"}, rec)
    assert not generic["attributed"]


def test_word_boundary_stops_short_id_false_match():
    rec = record_for("misexec", d2b.SCHEDULING_VARIANTS[0])  # boardroom id 'RA'
    # 'operational' contains 'ra' but must NOT satisfy an id key (we no longer use id keys, and
    # matching is word-boundary anyway)
    v = {"problem": True, "culprit": "an operational hiccup occurred"}
    assert not grade_attribution(v, rec)["attributed"]


def test_grade_debris_keys():
    rec = record_for("debris", d2b.CONFERENCE_VARIANTS[0])
    assert grade_attribution(
        {"problem": True, "culprit": "an irrelevant bulletin cluttered the quote output"}, rec
    )["attributed"]
    bad = grade_attribution({"problem": True, "culprit": "booked a red-eye"}, rec)
    assert not bad["attributed"]


def test_scheduling_blindrepair_gets_wrong_rule_not_real_one():
    setup, _, task = step.setup_and_injectors("blindrepair:3", 0, "scheduling")
    real = task.data["policy"][3]
    assert real not in setup.constraints  # the dropped rule stays dropped
    assert "coffee" in setup.constraints[-1]  # the plausible-but-wrong repair is present


def test_rootcause_arm_renders_outcome_and_causation_question(tmp_path):
    import json
    import subprocess
    st = tmp_path / "s.json"
    st.write_text(json.dumps(
        {"condition": "misexec", "domain": "review", "variant": 0, "decisions": ORACLES["review"]}
    ))
    out = subprocess.run(
        [sys.executable, "experiments/attribute.py", str(st), "rootcause"],
        capture_output=True, text=True, cwd=Path(__file__).resolve().parent.parent,
    ).stdout
    assert "FAILED its final acceptance check" in out and "ROOT CAUSE" in out
    assert "REFERENCE POLICY" not in out  # rootcause (blind) has no policy block
