"""Consolidated vertical-slice report with 95% Wilson CIs.

Reads results/*.json (rates) and experiments/decisions/*.json (sample counts), and prints the
Degrade / Attribute / Recover slice with confidence intervals — so the saturated small-n estimates
are shown honestly.  Deterministic, no model calls:  python scripts/report.py
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
R = ROOT / "results"
D = ROOT / "experiments" / "decisions"

import sys  # noqa: E402

sys.path.insert(0, str(ROOT))
from d2b.stats import fmt_rate  # noqa: E402


def _n(path: str, key: str | None = None) -> int:
    obj = json.loads((D / path).read_text())
    data = obj[key] if key else obj
    return len(data)


def main() -> None:
    deg = json.loads((R / "exp01_travel_tempting_constraint_drop.json").read_text())
    att = json.loads((R / "exp02_travel_tempting_attribution.json").read_text())
    rec = json.loads((R / "exp04_travel_tempting_recovery.json").read_text())

    n_h = _n("exp01_travel_tempting.json", "healthy")
    n_d = _n("exp01_travel_tempting.json", "constraint_drop")
    n_bf = att["blind_failed"]["n"]
    n_wf = att["with_policy_failed"]["n"]
    n_br = _n("exp04_blind_repair.json")

    def row(label: str, k: int, n: int) -> str:
        return f"  {label:34} {fmt_rate(k, n)}"

    print("Debris->Blame — vertical slice (constraint_drop, travel_tempting), 95% Wilson CIs\n")
    print("1. DEGRADE  P[books red-eye]")
    print(row("rule present", round(deg["healthy"]["p_fail"] * n_h), n_h))
    print(row("rule dropped", round(deg["constraint_drop"]["p_fail"] * n_d), n_d))
    print("\n2. ATTRIBUTE  correctly blames the fault")
    print(row("trace only (blind)", round(att["blind_failed"]["attributed"] * n_bf), n_bf))
    print(row("trace + policy", round(att["with_policy_failed"]["attributed"] * n_wf), n_wf))
    print("\n3. RECOVER  task recovered")
    print(row("no_repair", round(rec["no_repair"] * n_d), n_d))
    print(row("blind_repair", round(rec["blind_repair"] * n_br), n_br))
    print(row("targeted_repair", round(rec["targeted_repair"] * n_h), n_h))
    print(
        "\nEffects are saturated (0-vs-1) at small n — direction is clear, magnitude is uncertain."
        "\nScaling (faults x tiers x domains, sham controls) tightens these intervals."
    )


if __name__ == "__main__":
    main()
