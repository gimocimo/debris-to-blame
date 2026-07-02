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

from d2b.stats import fisher_p, fmt_rate  # noqa: E402

ORDER = ["healthy", "staleness", "contradiction", "cdrop:0", "cdrop:2", "sham"]
NICE = {"cdrop:0": "cdrop:red-eye", "cdrop:2": "cdrop:refundable"}


def score(files: list[str]) -> dict:
    by: dict[str, dict] = {}
    for f in files:
        st = json.loads(Path(f).read_text())
        cond = st["condition"]
        r = step.replay(st) if st["decisions"] else None
        ok = bool(r and r.result.ok)
        d = by.setdefault(cond, {"k_fail": 0, "n": 0, "variants": set()})
        d["n"] += 1
        d["k_fail"] += 0 if ok else 1
        d["variants"].add(st.get("variant", 0))
    return by


def main() -> None:
    files = sorted(glob(sys.argv[1]))
    by = score(files)
    conds = [c for c in ORDER if c in by] + [c for c in by if c not in ORDER]

    print(f"CONFERENCE_TRIP interactive degradation — {len(files)} rollouts across task variants\n")
    print(f"{'condition':20} {'P[task fails]  (95% Wilson)':32} {'variants':>8}")
    for c in conds:
        d = by[c]
        print(f"{NICE.get(c, c):20} {fmt_rate(d['k_fail'], d['n']):32} {len(d['variants']):>8}")

    if "healthy" in by:
        h = by["healthy"]
        print("\nFisher exact vs healthy:")
        for c in conds:
            if c == "healthy":
                continue
            d = by[c]
            p = fisher_p(h["k_fail"], h["n"], d["k_fail"], d["n"])
            print(f"  {NICE.get(c, c):20} p = {p:.4f}")

    Path("results").mkdir(exist_ok=True)
    out = {
        c: {"k_fail": d["k_fail"], "n": d["n"], "n_variants": len(d["variants"])}
        for c, d in by.items()
    }
    Path("results/conf_degrade_grid.json").write_text(json.dumps(out, indent=2))
    print("\nwrote results/conf_degrade_grid.json")


if __name__ == "__main__":
    main()
