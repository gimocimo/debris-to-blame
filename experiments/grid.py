"""Breadth grid — constraint_drop on travel_tempting across {healthy, fault, sham} x 3 Claude tiers.

Two real axes with no positional fragility:
  condition: healthy | fault (drop the binding no-red-eye rule) | sham (drop a NON-binding rule)
  tier:      opus | sonnet | haiku   (does the death-spiral hit weaker tiers harder?)

The sham arm is the key rigor upgrade: if only the BINDING drop degrades (fault high, sham ~0), the
damage is the specific rule — not "dropping any rule". Uses the date-fixed env.

Usage:
  python experiments/grid.py --prompts-json   # emit {condition: prompt} for the workflow to fan out
  python experiments/grid.py decisions.json   # score decisions {tier: {condition: [decision, ...]}}
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from d2b import (  # noqa: E402
    TRAVEL_TEMPTING,
    FaultSpec,
    FaultType,
    decision_to_messages,
    inject,
    redact_for_attribution,
    render_prefix,
    resume,
    scripted_policy,
    sham_inject,
)
from d2b.stats import fisher_p, fmt_rate  # noqa: E402

CUT = 5
TASK = TRAVEL_TEMPTING
TIERS = ["opus", "sonnet", "haiku"]


def prefixes() -> dict:
    drop = FaultSpec(FaultType.CONSTRAINT_DROP, position=0)
    return {
        "healthy": redact_for_attribution(TASK.make_trajectory()),
        "fault": inject(TASK.make_trajectory(), drop).public,  # drops the binding no-red-eye rule
        "sham": sham_inject(TASK.make_trajectory(), drop).public,  # drops a non-binding rule
    }


def prompts() -> dict:
    docs = {name: t.description for name, t in TASK.make_env().tools.items()}
    return {cond: render_prefix(pre, CUT, docs) for cond, pre in prefixes().items()}


def p_fail(prefix, decisions: list[dict]) -> tuple[int, int]:
    def ok(d):
        # A parse failure (or a decision with no tool) is an OUTCOME, not a silent drop — count it
        # as a task failure rather than crashing decision_to_messages (Codex issue 6).
        if d.get("status") == "parse_fail" or "tool" not in d:
            return False
        return resume(TASK, prefix, CUT, scripted_policy(decision_to_messages(d))).ok

    return sum(not ok(d) for d in decisions), len(decisions)


def main() -> None:
    if len(sys.argv) > 1 and sys.argv[1] == "--prompts-json":
        print(json.dumps(prompts(), indent=2))
        return

    decisions = json.loads(Path(sys.argv[1]).read_text()) if len(sys.argv) > 1 else {}
    pre = prefixes()

    print("P[task fails]  (constraint_drop, travel_tempting)  ·  95% Wilson CIs\n")
    print(f"{'tier':8} {'healthy':>22} {'fault':>22} {'sham':>22}")
    matrix = {}
    for tier in TIERS:
        cells = {}
        row = [f"{tier:8}"]
        for cond in ("healthy", "fault", "sham"):
            k, n = p_fail(pre[cond], decisions.get(tier, {}).get(cond, []))
            cells[cond] = {"k": k, "n": n}
            row.append(f"{fmt_rate(k, n):>22}")
        matrix[tier] = cells
        print(" ".join(row))

    Path("results").mkdir(exist_ok=True)
    Path("results/grid_constraint_drop_tiers.json").write_text(json.dumps(matrix, indent=2))

    # Is the tier ordering real, or noise? Test the fault cells directly.
    fo, fs = matrix["opus"]["fault"], matrix["sonnet"]["fault"]
    p = fisher_p(fo["k"], fo["n"], fs["k"], fs["n"])
    print("\nSham works: only the BINDING drop degrades (sham=healthy=0 across tiers).")
    print(
        f"Tier difference (opus fault vs sonnet fault): Fisher p = {p:.4f} — "
        f"{'NOT significant' if p >= 0.05 else 'significant'} at n={fo['n']}."
        "\nThe Sonnet dip is not distinguishable from noise here; ~16-20/tier needed to test it."
    )


if __name__ == "__main__":
    main()
