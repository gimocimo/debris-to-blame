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
    # cells[(n, arm)] = [genuine_loc, mechanism, named_trap_raw, detected, count]
    cells: dict = defaultdict(lambda: [0, 0, 0, 0, 0])
    for v in data:
        n, arm = v["n_txns"], v["arm"]
        culprit = str(v.get("culprit", "")).lower()
        trap = _trap(v["variant"]).lower()
        problem = bool(v.get("problem"))
        named_trap = problem and _kw(trap, culprit)  # names the trap txn (may be confabulation)
        mechanism = problem and any(_kw(k, culprit) for k in _STALE_KEYS)  # names 'stale'
        genuine = named_trap and mechanism  # right item AND right reason (real localization)
        c = cells[(n, arm)]
        c[0] += int(genuine)
        c[1] += int(mechanism)
        c[2] += int(named_trap)
        c[3] += int(problem)
        c[4] += 1

    print("reconcile_long — attribution vs HORIZON (chance = 1/N)")
    print("  genuine LOCALIZE = names the trap txn AND the stale mechanism; "
          "named-trap(raw) may be confabulation\n")
    for arm in ("blind", "rootcause"):
        print(f"=== arm: {arm} ===")
        for n in (8, 24, 48):
            c = cells.get((n, arm))
            if not c:
                continue
            print(f"  N={n:2}  detect {fmt_rate(c[3], c[4]):22}  "
                  f"genuine-LOC {fmt_rate(c[0], c[4]):22}  "
                  f"mechanism {fmt_rate(c[1], c[4]):22}  "
                  f"named-trap(raw) {c[2]}/{c[4]}  (chance {1.0 / n:.3f})")
        print()

    out = {f"{n}:{arm}": {"genuine_loc": c[0], "mechanism": c[1], "named_trap_raw": c[2],
                          "detect": c[3], "n": c[4], "chance": 1.0 / n}
           for (n, arm), c in cells.items()}
    Path("results").mkdir(exist_ok=True)
    Path("results/reconcile_long_horizon.json").write_text(json.dumps(out, indent=2))
    print("\nwrote results/reconcile_long_horizon.json")


if __name__ == "__main__":
    main()
