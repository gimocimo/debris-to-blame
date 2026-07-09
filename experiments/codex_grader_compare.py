"""Direction B scorer: Codex judge vs the deterministic grader on the same Claude verdicts.

Reads the reference key (our deterministic per-id grade) and Codex's judge verdicts, then reports:
  - overall agreement % and Cohen's kappa on the binary `attributed` decision
  - the disagreements, listed
  - the blame-gap map recomputed under Codex's grades (does the deception/deletion gap survive?)

  python experiments/codex_grader_compare.py \
      experiments/decisions/codex_grader_refkey.json \
      experiments/decisions/codex_grader_verdicts.json
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path


def _kappa(a: list[bool], b: list[bool]) -> float:
    n = len(a)
    if not n:
        return float("nan")
    po = sum(x == y for x, y in zip(a, b, strict=True)) / n
    pa1, pb1 = sum(a) / n, sum(b) / n
    pe = pa1 * pb1 + (1 - pa1) * (1 - pb1)
    return (po - pe) / (1 - pe) if pe != 1 else 1.0


def _family(cond: str) -> str:
    if cond.startswith("cdrop:"):
        return "cdrop"
    if cond.startswith("forget:"):
        return "forget"
    return cond


def main() -> None:
    ref = json.loads(Path(sys.argv[1]).read_text())
    cdx = {v["id"]: bool(v["attributed"])
           for v in json.loads(Path(sys.argv[2]).read_text())["verdicts"]}

    det_list, cdx_list, missing, disagree = [], [], [], []
    # cells[domain][family][arm] = [det_count, cdx_count, n]
    cells: dict = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: [0, 0, 0])))
    for rid, r in ref.items():
        if rid not in cdx:
            missing.append(rid)
            continue
        d, c = r["det_attributed"], cdx[rid]
        det_list.append(d)
        cdx_list.append(c)
        if d != c:
            disagree.append((rid, d, c))
        cell = cells[r["domain"]][_family(r["condition"])][r["arm"]]
        cell[0] += int(d)
        cell[1] += int(c)
        cell[2] += 1

    n = len(det_list)
    agree = sum(x == y for x, y in zip(det_list, cdx_list, strict=True))
    print(f"Direction B — Codex-judge vs deterministic grader on {n} Claude verdicts "
          f"({len(missing)} missing)")
    kap = _kappa(det_list, cdx_list)
    print(f"  agreement: {agree}/{n} = {agree / n:.3f}   Cohen's kappa = {kap:.3f}\n")

    if disagree:
        print(f"  {len(disagree)} disagreements (id: deterministic -> codex):")
        for rid, d, c in disagree:
            print(f"    {rid}: det={int(d)} codex={int(c)}")
        print()

    print("Blame-gap map recomputed under Codex grades (det | codex attributed rate):")
    for dom in sorted(cells):
        print(f"=== {dom} ===")
        for fam in sorted(cells[dom]):
            parts = []
            for arm in ("blind", "deleak", "policy", "rootcause"):
                c = cells[dom][fam].get(arm)
                if c:
                    parts.append(f"{arm} {c[0]}/{c[2]}|{c[1]}/{c[2]}")
            print(f"  [{fam}] " + "   ".join(parts))
    if missing:
        print(f"\nWARNING: {len(missing)} ids had no Codex verdict (excluded).")


if __name__ == "__main__":
    main()
