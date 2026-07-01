"""exp01 (C2) — first degradation cell: travel + constraint_drop, resume-live vs a healthy control.

The agent-under-test decides the booking AFTER seeing the search results (cut=5), given only the
redacted prefix. Healthy sees the "no red-eye" rule; the constraint_drop condition has that rule
evicted. We record each condition's model decisions (subscription-native, cached to JSON) and score
them with the deterministic state validator: does the agent book a red-eye / bust budget?

Usage:
  python experiments/exp01_degradation.py --prompts        # print the two agent prompts
  python experiments/exp01_degradation.py decisions.json   # score recorded decisions
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from d2b import (  # noqa: E402
    FaultSpec,
    FaultType,
    decision_to_messages,
    inject,
    redact_for_attribution,
    render_prefix,
    resume,
    scripted_policy,
)
from d2b.domains import TRAVEL  # noqa: E402

CUT = 5  # decide the booking after the search-results message


def build_prefixes() -> dict:
    healthy = redact_for_attribution(TRAVEL.make_trajectory())
    dropped = inject(
        TRAVEL.make_trajectory(), FaultSpec(FaultType.CONSTRAINT_DROP, position=0)
    ).public
    return {"healthy": healthy, "constraint_drop": dropped}


def score(prefix, decisions: list[dict]) -> dict:
    rows = []
    for d in decisions:
        res = resume(TRAVEL, prefix, CUT, scripted_policy(decision_to_messages(d)))
        args = d.get("args", {})
        booked = args.get("id") or args.get("flight")
        rows.append({"booked": booked, "ok": res.ok, "reason": res.reason})
    n = len(rows)
    fails = sum(not r["ok"] for r in rows)
    return {"n": n, "p_fail": (fails / n) if n else 0.0, "rows": rows}


def main() -> None:
    prefixes = build_prefixes()
    if len(sys.argv) > 1 and sys.argv[1] == "--prompts":
        for cond, pre in prefixes.items():
            print(f"\n===== PROMPT: {cond} =====\n{render_prefix(pre, CUT)}")
        return

    decisions = json.loads(Path(sys.argv[1]).read_text()) if len(sys.argv) > 1 else {}
    results = {cond: score(pre, decisions.get(cond, [])) for cond, pre in prefixes.items()}

    print(f"{'condition':16} {'n':>3} {'P[fail]':>8}")
    for cond, r in results.items():
        print(f"{cond:16} {r['n']:>3} {r['p_fail']:>8.2f}")
    base = results["healthy"]["p_fail"]
    drop = results["constraint_drop"]["p_fail"]
    print(f"\ndegradation Δ = {drop - base:+.2f}  (constraint_drop − healthy)")

    Path("results").mkdir(exist_ok=True)
    Path("results/exp01_travel_constraint_drop.json").write_text(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
