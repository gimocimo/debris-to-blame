"""Score de-contaminated attribution verdicts into the HONEST blame-gap map.

Consumes detective verdicts collected in several arms and tiers and grades each against the SPECIFIC
injected fault (grade_attribution). Reports, per fault family:
  blind   — trace only (no reference)
  deleak  — trace + rulebook MINUS the dropped line (cdrop control; should land ~= blind)
  policy  — trace + FULL policy = an ORACLE UPPER BOUND (labelled as such), not a realistic detector
plus the cross-tier grader agreement (R6 lower bound) when Haiku/Sonnet verdicts are present.

  python experiments/conf_attr_score.py experiments/decisions/conf_attribution.json
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from attr_common import record_for  # noqa: E402

import d2b  # noqa: E402
from d2b.detective import grade_attribution  # noqa: E402
from d2b.stats import fmt_rate  # noqa: E402


def _task_for(vr: dict):
    dom = d2b.DOMAINS[vr.get("domain", "conference")]
    return dom["variants"][vr.get("variant", 0)]


def _family(cond: str) -> str:
    if cond.startswith("cdrop:"):
        return "cdrop"
    if cond.startswith("forget:"):
        return "forget"
    return cond


def main() -> None:
    data = json.loads(Path(sys.argv[1]).read_text())
    # cells[domain][family][tier][arm] = {"detect":k, "attr":k, "n":k}
    cells: dict = {}
    for vr in data["verdicts"]:
        cond, arm, tier = vr["condition"], vr.get("arm", "blind"), vr.get("tier", "opus")
        dom = vr.get("domain", "conference")
        rec = record_for(cond, _task_for(vr))
        if rec is None:  # healthy: no fault — 'detect' is a FALSE POSITIVE, nothing to attribute
            g = {"problem": bool(vr["problem"]), "attributed": False}
        else:
            g = grade_attribution({"problem": vr["problem"], "culprit": vr["culprit"]}, rec)
        cell = (
            cells.setdefault(dom, {})
            .setdefault(_family(cond), {})
            .setdefault(tier, {})
            .setdefault(arm, {"detect": 0, "attr": 0, "n": 0})
        )
        cell["n"] += 1
        cell["detect"] += int(g["problem"])
        cell["attr"] += int(g["attributed"])

    print("Cross-domain attribution — the blame-gap map (grades vs the SPECIFIC injected fault)\n")
    for dom in sorted(cells):
        print(f"=== {dom} ===")
        for fam in sorted(cells[dom]):
            print(f"[{fam}]")
            for tier in sorted(cells[dom][fam]):
                for arm in ("blind", "deleak", "policy", "rootcause", "rootcause_policy"):
                    c = cells[dom][fam][tier].get(arm)
                    if not c:
                        continue
                    tag = {"policy": " (ORACLE upper bound)",
                           "rootcause": " (+outcome, causation Q)",
                           "rootcause_policy": " (+outcome +policy)"}.get(arm, "")
                    print(f"  {tier:7} {arm:16} detect {fmt_rate(c['detect'], c['n']):26} "
                          f"attributed {fmt_rate(c['attr'], c['n']):26}{tag}")
            opus = cells[dom][fam].get("opus", {})
            if "blind" in opus and "policy" in opus:
                b, p = opus["blind"], opus["policy"]
                gap = p["attr"] / p["n"] - b["attr"] / b["n"]
                print(f"  -> oracle-vs-blind attribution gap = {gap:+.2f} "
                      f"(blind {b['attr'] / b['n']:.2f} -> oracle {p['attr'] / p['n']:.2f})")
            print()

    Path("results").mkdir(exist_ok=True)
    Path("results/conf_attribution.json").write_text(json.dumps(cells, indent=2))
    print("wrote results/conf_attribution.json (domain-aware)")


if __name__ == "__main__":
    main()
