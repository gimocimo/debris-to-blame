"""exp01 (C2) — degradation cell: <scenario> + constraint_drop, resume-live vs a healthy control.

The agent-under-test decides the booking AFTER seeing the search results (cut=5), given only the
redacted prefix. Healthy sees the "no red-eye" rule; the constraint_drop condition has it evicted.
We record each condition's model decisions (subscription-native, cached to JSON) and score them with
the deterministic state validator: does the agent book a red-eye / bust budget?

Scenarios: `travel` (red-eye only $50 cheaper — rule not binding) and `travel_tempting` (red-eye
$360 cheaper + "cheapest" objective — rule IS binding).

Usage:
  python experiments/exp01_degradation.py <scenario> --prompts        # print the two prompts
  python experiments/exp01_degradation.py <scenario> decisions.json   # score recorded decisions
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from d2b import (  # noqa: E402
    TRAVEL,
    TRAVEL_TEMPTING,
    FaultSpec,
    FaultType,
    decision_to_messages,
    inject,
    redact_for_attribution,
    render_prefix,
    resume,
    scripted_policy,
)

CUT = 5  # decide the booking after the search-results message
SCENARIOS = {"travel": TRAVEL, "travel_tempting": TRAVEL_TEMPTING}


def build_prefixes(task) -> dict:
    healthy = redact_for_attribution(task.make_trajectory())
    dropped = inject(
        task.make_trajectory(), FaultSpec(FaultType.CONSTRAINT_DROP, position=0)
    ).public
    return {"healthy": healthy, "constraint_drop": dropped}


def score(task, prefix, decisions: list[dict]) -> dict:
    rows = []
    for d in decisions:
        res = resume(task, prefix, CUT, scripted_policy(decision_to_messages(d)))
        args = d.get("args", {})
        rows.append(
            {"booked": args.get("id") or args.get("flight"), "ok": res.ok, "reason": res.reason}
        )
    n = len(rows)
    fails = sum(not r["ok"] for r in rows)
    return {"n": n, "p_fail": (fails / n) if n else 0.0, "rows": rows}


def main() -> None:
    scenario = sys.argv[1] if len(sys.argv) > 1 else "travel"
    task = SCENARIOS[scenario]
    prefixes = build_prefixes(task)

    if len(sys.argv) > 2 and sys.argv[2] == "--prompts":
        tool_docs = {name: t.description for name, t in task.make_env().tools.items()}
        for cond, pre in prefixes.items():
            print(
                f"\n===== PROMPT [{scenario}]: {cond} =====\n{render_prefix(pre, CUT, tool_docs)}"
            )
        return

    decisions = json.loads(Path(sys.argv[2]).read_text()) if len(sys.argv) > 2 else {}
    results = {cond: score(task, pre, decisions.get(cond, [])) for cond, pre in prefixes.items()}

    print(f"scenario: {scenario}")
    print(f"{'condition':16} {'n':>3} {'P[fail]':>8}")
    for cond, r in results.items():
        print(f"{cond:16} {r['n']:>3} {r['p_fail']:>8.2f}")
    base = results["healthy"]["p_fail"]
    drop = results["constraint_drop"]["p_fail"]
    print(f"\ndegradation Δ = {drop - base:+.2f}  (constraint_drop − healthy)")

    Path("results").mkdir(exist_ok=True)
    Path(f"results/exp01_{scenario}_constraint_drop.json").write_text(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
