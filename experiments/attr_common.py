"""Shared attribution helpers: build the ground-truth FaultRecord for a rollout condition.

Both the detective scorer (conf_attr_score) and the dumb-baseline ladder (attr_baselines) grade a
`culprit` against the SAME record via d2b.detective.grade_attribution, so the two are comparable.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from d2b import FaultRecord, FaultSite, FaultType  # noqa: E402

# Distinguishing tokens the culprit must name to count as correctly attributing each fault. For
# constraint_drop we derive them from the dropped rule text instead (see grade_attribution).
_ATTR_KEYS = {
    "staleness": ["stale", "cached", "surged", "outdated", "superseded"],
    # deliberately NOT "budget"/"note" (too generic — they match any over-budget failure narrative,
    # which would credit the contradiction fault for a plain budget miss). Must name the fabricated
    # note that RAISED/INFLATED the cap.
    "contradiction": ["raised", "inflated", "contradict", "conflicting", "fabricated", "hiked"],
    "debris": ["debris", "irrelevant", "noise", "bulletin", "clutter", "unrelated", "junk"],
}


def record_for(condition: str, task) -> FaultRecord | None:
    """The private ground-truth label for a rollout condition (None = no fault: healthy)."""
    if condition == "healthy":
        return None
    if condition == "sham":
        return FaultRecord(
            FaultType.CONSTRAINT_DROP, FaultSite("constraint", "sham"), 1.0, sham=True
        )
    if condition.startswith("cdrop:"):
        k = int(condition.split(":", 1)[1])
        rule = task.data["policy"][k]
        return FaultRecord(
            FaultType.CONSTRAINT_DROP, FaultSite("constraint", str(k)), 1.0,
            {"dropped_constraint": [rule]},
        )
    if condition.startswith("forget:"):
        tool = condition.split(":", 1)[1]
        keys = [w for w in tool.split("_") if len(w) > 3]
        return FaultRecord(
            FaultType.TOOL_FORGETTING, FaultSite("tool", tool), 1.0, {"attr_keys": keys},
        )
    if condition == "staleness":
        return FaultRecord(
            FaultType.STALENESS, FaultSite("message", "quote"), 1.0,
            {"attr_keys": _ATTR_KEYS["staleness"]},
        )
    if condition == "contradiction":
        return FaultRecord(
            FaultType.CONTRADICTION, FaultSite("message", "quote"), 1.0,
            {"attr_keys": _ATTR_KEYS["contradiction"]},
        )
    if condition == "debris":
        return FaultRecord(
            FaultType.DEBRIS, FaultSite("message", "check"), 1.0,
            {"attr_keys": _ATTR_KEYS["debris"]},
        )
    if condition == "misexec":
        cfg = task.data
        # STRICT (Codex audit finding 1): the culprit must (A) name the misexecuted ACTION locus —
        # the booking/merge step, NOT the check/quote tool — AND (B) a substitution concept. This
        # rejects wrong-mechanism verdicts that blame check_ci/latest_quote for a book/merge fault.
        if "flights" in cfg:
            action = ["book_flight", "book_hotel", "booked flight", "booked hotel", "booking step",
                      "booking-side", "booking-path", "booking path", "booking-step"]
        elif "rooms" in cfg:
            action = ["book_room", "book_slot", "booked room", "booked slot", "booking step",
                      "booking-step"]
        else:
            action = ["merge_pr", "the requested merge", "merge step", "merge tool", "merge action",
                      "merging step", "merge-step"]
        # full inflected forms (word-boundary matching requires whole words, not truncated stems)
        substitution = [
            "instead", "different", "other than", "not the requested", "did not actually perform",
            "did not perform the requested", "substituted", "substitution", "mismatch",
            "discrepancy", "diverged", "divergence", "divergent", "silently executed",
            "silent misexecution", "misexecution", "misexecuted", "mis-execution", "mis-executed",
            "did not reflect", "actually executed", "actually merged", "actually booked",
            "non-compliant", "something other", "something else", "did not match",
        ]
        return FaultRecord(
            FaultType.WRONG_TOOL, FaultSite("tool", "book/merge"), 1.0,
            {"match_groups": [action, substitution]},
        )
    raise SystemExit(f"no record mapping for condition: {condition}")
