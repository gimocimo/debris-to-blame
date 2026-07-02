"""Score the recovery experiment on CONFERENCE_TRIP — localization enables recovery.

Repairs a constraint_drop failure three ways and reports P[task recovered]:
  no_repair       = the fault, unrepaired         (reuses the Phase-B cdrop cells)
  blind_repair    = a plausible-but-WRONG repair  (this run's br_* rollouts)
  targeted_repair = restore the dropped rule       (reuses the Phase-B healthy cells)

  python experiments/conf_recover_score.py "<br glob>"
"""

from __future__ import annotations

import json
import sys
from glob import glob
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import step  # noqa: E402

from d2b.stats import fmt_rate  # noqa: E402

GRID = Path("results/conf_degrade_grid.json")


def success_rate(files: list[str]) -> tuple[int, int]:
    k_ok = 0
    for f in files:
        st = json.loads(Path(f).read_text())
        r = step.replay(st) if st["decisions"] else None
        k_ok += int(bool(r and r.result.ok))
    return k_ok, len(files)


def main() -> None:
    br = sorted(glob(sys.argv[1]))
    blind_k, blind_n = success_rate(br)

    grid = json.loads(GRID.read_text())
    # targeted = restore the rule = healthy; no_repair = the BINDING cdrop cell (cdrop:2).
    # cdrop:0 (red-eye) is excluded: with sincere agents it is redundant with agent preference, so
    # it does not degrade (0/8) and there is nothing to recover.
    h = grid["healthy"]
    targeted_k, targeted_n = h["n"] - h["k_fail"], h["n"]
    no_k = no_n = 0
    for c in ("cdrop:2",):
        if c in grid:
            no_k += grid[c]["n"] - grid[c]["k_fail"]
            no_n += grid[c]["n"]

    print("CONFERENCE_TRIP recovery — localization enables recovery\n")
    print(f"{'repair policy':20} {'P[task recovered]  (95% Wilson)':34}")
    print(f"{'no_repair':20} {fmt_rate(no_k, no_n):34}")
    print(f"{'blind_repair':20} {fmt_rate(blind_k, blind_n):34}")
    print(f"{'targeted_repair':20} {fmt_rate(targeted_k, targeted_n):34}")
    lift = targeted_k / targeted_n - blind_k / (blind_n or 1)
    print(f"\nLOCALIZATION LIFT = {lift:+.2f}  "
          f"(targeted {targeted_k / targeted_n:.2f} vs blind {blind_k / (blind_n or 1):.2f})")

    Path("results").mkdir(exist_ok=True)
    out = {
        "no_repair": {"k_ok": no_k, "n": no_n},
        "blind_repair": {"k_ok": blind_k, "n": blind_n},
        "targeted_repair": {"k_ok": targeted_k, "n": targeted_n},
    }
    Path("results/conf_recovery.json").write_text(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
