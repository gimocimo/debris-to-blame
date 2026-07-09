"""Score the reconcile_long horizon audit — does finding the needle degrade as the trace grows?

Two attribution notions, graded per verdict against the committed ground truth (the trap txn):
  - LOCALIZATION: did the culprit name the exact wrongly-approved transaction id (e.g. T043)?
    (This is what should degrade with horizon — one bad approval among ~N look-alikes.)
  - MECHANISM: did it name the staleness mechanism (stale/cached/...)? Expected ~0 always — the
    stale receipt looks matching, so the deception is unknowable from the trace (horizon-invariant).
Aggregated by batch length N (and reported by trap depth), for the blind and rootcause arms.

  python experiments/long_horizon_score.py experiments/decisions/reconcile_long_audit.json
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import d2b  # noqa: E402
from d2b.detective import _kw  # noqa: E402
from d2b.stats import fmt_rate  # noqa: E402

_STALE_KEYS = ["stale", "cached", "outdated", "superseded", "old receipt", "not live"]


def _trap(variant: int) -> str:
    return d2b.DOMAINS["reconcile_long"]["variants"][variant].data["trap_txn"]


def main() -> None:
    data = json.loads(Path(sys.argv[1]).read_text())["verdicts"]
    # cells[(n, arm)] = [localized, mechanism, detected, count]
    cells: dict = defaultdict(lambda: [0, 0, 0, 0])
    depth: dict = defaultdict(lambda: [0, 0])  # (n, arm, trap_depth) -> [localized, count]
    for v in data:
        n, arm = v["n_txns"], v["arm"]
        culprit = str(v.get("culprit", "")).lower()
        trap = _trap(v["variant"]).lower()
        problem = bool(v.get("problem"))
        localized = problem and _kw(trap, culprit)
        mechanism = problem and any(_kw(k, culprit) for k in _STALE_KEYS)
        c = cells[(n, arm)]
        c[0] += int(localized)
        c[1] += int(mechanism)
        c[2] += int(problem)
        c[3] += 1
        dep = d2b.DOMAINS["reconcile_long"]["variants"][v["variant"]].data["trap_depth"]
        d = depth[(n, arm, dep)]
        d[0] += int(localized)
        d[1] += 1

    print("reconcile_long — attribution vs HORIZON (chance localization = 1/N)\n")
    for arm in ("blind", "rootcause"):
        print(f"=== arm: {arm} ===")
        for n in (8, 24, 48):
            c = cells.get((n, arm))
            if not c:
                continue
            chance = 1.0 / n
            print(f"  N={n:2}  detect {fmt_rate(c[2], c[3]):24}  "
                  f"LOCALIZE {fmt_rate(c[0], c[3]):24}  "
                  f"mechanism {fmt_rate(c[1], c[3]):24}  (chance loc {chance:.3f})")
        print()

    print("Localization by trap depth (rootcause arm):")
    for (n, arm, dep), d in sorted(depth.items()):
        if arm != "rootcause":
            continue
        print(f"  N={n:2} depth={dep:.2f}: localized {d[0]}/{d[1]}")


if __name__ == "__main__":
    main()
