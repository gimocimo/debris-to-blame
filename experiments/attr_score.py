"""Score conference attribution verdicts into the blame gap (blind vs with-policy).

Grades each detective verdict against the SPECIFIC dropped rule (grade_attribution), then reports
detection + correct-attribution rates for blind vs with-policy.

  python experiments/attr_score.py experiments/decisions/conf_attribution.json
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from d2b import FaultRecord, FaultSite, FaultType  # noqa: E402
from d2b.conference import VARIANTS  # noqa: E402
from d2b.detective import grade_attribution  # noqa: E402
from d2b.stats import fmt_rate  # noqa: E402

# rule text by dropped index (constant across variants for indices 0 and 2)
RULE = {0: VARIANTS[0]["policy"][0], 2: VARIANTS[0]["policy"][2]}


def _record(condition: str) -> FaultRecord:
    k = int(condition.split(":", 1)[1])
    return FaultRecord(FaultType.CONSTRAINT_DROP, FaultSite("constraint", str(k)), 1.0,
                       {"dropped_constraint": [RULE[k]]})


def main() -> None:
    data = json.loads(Path(sys.argv[1]).read_text())
    by_mode: dict[str, dict] = {}
    for v in data["verdicts"]:
        verdict = {"problem": v["problem"], "culprit": v["culprit"]}
        g = grade_attribution(verdict, _record(v["condition"]))
        m = by_mode.setdefault(v["mode"], {"detect": 0, "attr": 0, "n": 0})
        m["n"] += 1
        m["detect"] += int(g["problem"])
        m["attr"] += int(g["attributed"])

    print("CONFERENCE_TRIP attribution — blame gap on the multi-step task\n")
    print(f"{'mode':14} {'detect (flagged a problem)':30} {'correctly attributed':24}")
    for mode in ("blind", "policy"):
        if mode not in by_mode:
            continue
        m = by_mode[mode]
        print(f"{mode:14} {fmt_rate(m['detect'], m['n']):30} {fmt_rate(m['attr'], m['n']):24}")

    b, p = by_mode.get("blind"), by_mode.get("policy")
    if b and p:
        lift = p["attr"] / p["n"] - b["attr"] / b["n"]
        print(f"\nBLAME GAP (attribution lift from policy) = {lift:+.2f}"
              f"  (blind {b['attr'] / b['n']:.2f} -> with-policy {p['attr'] / p['n']:.2f})")

    Path("results").mkdir(exist_ok=True)
    Path("results/conf_attribution.json").write_text(json.dumps(by_mode, indent=2))


if __name__ == "__main__":
    main()
