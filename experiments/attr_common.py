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


def _misexec_wrong_item(cfg: dict) -> str:
    """The item the world ACTUALLY acted on under misexec (mirrors the domain misexec_injector)."""
    if "flights" in cfg:
        return next(f for f, d in cfg["flights"].items() if d["red_eye"])
    if "rooms" in cfg:
        return next(r for r, d in cfg["rooms"].items() if d["boardroom"])
    return cfg["trap_pr"]


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
        wrong = _misexec_wrong_item(task.data)
        # the culprit must name the SUBSTITUTION: the wrongly-executed item or the mismatch itself
        keys = [wrong.lower(), "wrong", "instead", "mismatch", "misexecut", "substitut",
                "different", "not the requested"]
        return FaultRecord(
            FaultType.WRONG_TOOL, FaultSite("tool", "book/merge"), 1.0, {"attr_keys": keys},
        )
    raise SystemExit(f"no record mapping for condition: {condition}")
