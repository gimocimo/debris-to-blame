"""Score the recovery experiment on CONFERENCE_TRIP — localization enables recovery.

Repairs a constraint_drop failure three ways and reports P[task recovered]:
  no_repair       = the fault, unrepaired          (the binding cdrop:2 cells)
  blind_repair    = a plausible-but-WRONG repair   (this run's br_* rollouts)
  targeted_repair = restore the dropped rule        (the healthy cells)

Reported BOTH pooled and variant-clustered (variants = the independent unit, matching conf_score.py
§1 — pooling reps overstates precision), with a variant-clustered Fisher for targeted vs blind.

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

from d2b.stats import cluster_by_variant, fisher_p, fmt_rate  # noqa: E402

GRID = Path("results/conf_degrade_grid.json")


def blind_recovered_by_variant(files: list[str]) -> dict[int, tuple[int, int]]:
    """{variant: (recovered, n)} for the blind_repair rollouts (recovered = task passed)."""
    pv: dict[int, tuple[int, int]] = {}
    for f in files:
        st = json.loads(Path(f).read_text())
        r = step.replay(st) if st["decisions"] else None
        ok = int(bool(r and r.result.ok))
        v = st.get("variant", 0)
        rk, rn = pv.get(v, (0, 0))
        pv[v] = (rk + ok, rn + 1)
    return pv


def _grid_recovered(grid: dict, cond: str) -> dict[int, tuple[int, int]]:
    """{variant: (recovered, n)} from a grid cell's per-variant fail counts (recovered = n-fail)."""
    cell = grid.get(cond, {})
    return {int(v): (n - k, n) for v, (k, n) in cell.get("per_variant", {}).items()}


def _pooled(pv: dict[int, tuple[int, int]]) -> tuple[int, int]:
    return sum(k for k, _ in pv.values()), sum(n for _, n in pv.values())


def main() -> None:
    br = sorted(glob(sys.argv[1]))
    grid = json.loads(GRID.read_text())
    # targeted = restore the rule = healthy; no_repair = the BINDING cdrop cell (cdrop:2).
    # cdrop:0 (red-eye) is excluded: with sincere agents it is redundant with agent preference, so
    # it does not degrade (0/8) and there is nothing to recover.
    cells = {
        "no_repair": _grid_recovered(grid, "cdrop:2"),
        "blind_repair": blind_recovered_by_variant(br),
        "targeted_repair": _grid_recovered(grid, "healthy"),
    }

    print("CONFERENCE_TRIP recovery — localization enables recovery\n")
    print(f"{'repair policy':16} {'pooled P[recovered] (Wilson)':32} {'variants rec.':>14}")
    clustered = {}
    for name in ("no_repair", "blind_repair", "targeted_repair"):
        k, n = _pooled(cells[name])
        rec_v, nv = cluster_by_variant(cells[name])
        clustered[name] = (rec_v, nv)
        print(f"{name:16} {fmt_rate(k, n):32} {f'{rec_v}/{nv}':>14}")

    tk, tn = _pooled(cells["targeted_repair"])
    bk, bn = _pooled(cells["blind_repair"])
    lift = tk / (tn or 1) - bk / (bn or 1)
    (tv, tnv), (bv, bnv) = clustered["targeted_repair"], clustered["blind_repair"]
    p = fisher_p(tv, tnv, bv, bnv)
    pooled = f"targeted {tk / tn:.2f} vs blind {bk / bn:.2f}"
    print(f"\nLOCALIZATION LIFT = {lift:+.2f} (pooled: {pooled})")
    print(f"variant-clustered: targeted {tv}/{tnv} vs blind {bv}/{bnv}, Fisher p = {p:.4f}")

    Path("results").mkdir(exist_ok=True)
    out = {}
    for name in cells:
        k, n = _pooled(cells[name])
        rec_v, nv = clustered[name]
        out[name] = {"k_ok": k, "n": n, "variants_recovered": rec_v, "n_variants": nv}
    out["_clustered_fisher_targeted_vs_blind"] = p
    Path("results/conf_recovery.json").write_text(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
