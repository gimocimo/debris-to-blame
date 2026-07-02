"""Score a set of interactive CONFERENCE_TRIP rollout state files into a degradation matrix.

Authoritative: replays each state's decisions through the harness (world = truth) and validates.
Aggregates across variants (task-level n), reports Wilson CIs + Fisher-exact vs healthy.

  python experiments/conf_score.py "<glob>"   # e.g. "/tmp/.../g2_*.json"
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

ORDER = ["healthy", "staleness", "contradiction", "cdrop:0", "cdrop:2", "sham",
         "forget:file_expense_report"]
NICE = {"cdrop:0": "cdrop:red-eye", "cdrop:2": "cdrop:refundable",
        "forget:file_expense_report": "forget:expense"}


def score(files: list[str]) -> dict:
    by: dict[str, dict] = {}
    for f in files:
        st = json.loads(Path(f).read_text())
        cond = st["condition"]
        r = step.replay(st) if st["decisions"] else None
        ok = bool(r and r.result.ok)
        d = by.setdefault(cond, {"k_fail": 0, "n": 0, "pv": {}})
        d["n"] += 1
        d["k_fail"] += 0 if ok else 1
        v = st.get("variant", 0)
        pk, pn = d["pv"].get(v, (0, 0))
        d["pv"][v] = (pk + (0 if ok else 1), pn + 1)
    return by


def main() -> None:
    files = sorted(glob(sys.argv[1]))
    by = score(files)
    conds = [c for c in ORDER if c in by] + [c for c in by if c not in ORDER]

    print(f"CONFERENCE_TRIP interactive degradation — {len(files)} rollouts across task variants\n")
    print(f"{'condition':22} {'P[task fails] pooled (95% Wilson)':34} {'variants failing':>16}")
    for c in conds:
        d = by[c]
        aff, nv = cluster_by_variant(d["pv"])
        print(f"{NICE.get(c, c):22} {fmt_rate(d['k_fail'], d['n']):34} {f'{aff}/{nv}':>16}")

    if "healthy" in by:
        h = by["healthy"]
        h_aff, h_nv = cluster_by_variant(h["pv"])
        print("\nVariant-clustered Fisher vs healthy (variants = the independent unit, not reps):")
        for c in conds:
            if c == "healthy":
                continue
            aff, nv = cluster_by_variant(by[c]["pv"])
            p = fisher_p(aff, nv, h_aff, h_nv)
            print(f"  {NICE.get(c, c):22} {aff}/{nv} variants vs {h_aff}/{h_nv}  p = {p:.4f}")

    Path("results").mkdir(exist_ok=True)
    out = {}
    for c, d in by.items():
        aff, nv = cluster_by_variant(d["pv"])
        out[c] = {
            "k_fail": d["k_fail"], "n": d["n"], "n_variants": len(d["pv"]),
            "variants_failing": aff, "per_variant": {str(k): v for k, v in d["pv"].items()},
        }
    Path("results/conf_degrade_grid.json").write_text(json.dumps(out, indent=2))
    print("\nwrote results/conf_degrade_grid.json (with per-variant counts)")


if __name__ == "__main__":
    main()
