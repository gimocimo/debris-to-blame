"""exp04 (C4, HEADLINE) — recovery: does repairing the fault recover the task? Localization matters.

We take the SAME failure (constraint_drop -> the agent booked the red-eye) and repair it three ways,
then let the agent re-decide and check the state validator:

  no_repair        : leave the dropped context as-is (baseline)                     -> expect ~0
  blind_repair     : act on the blind auditor's MISDIAGNOSIS (add a date-check)      -> expect ~0
  targeted_repair  : restore the dropped 'no red-eye' rule (correct localization)    -> expect high

recovery_rate = P[task valid after re-deciding]. no_repair/targeted reuse exp01 decisions; only
blind_repair needs a fresh batch (the agent must react to the misdiagnosis repair).

Usage:
  python experiments/exp04_recovery.py --prompts             # print the blind_repair prompt
  python experiments/exp04_recovery.py blind_decisions.json  # score recovery
"""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from d2b import (  # noqa: E402
    TRAVEL_TEMPTING,
    FaultSpec,
    FaultType,
    decision_to_messages,
    inject,
    redact_for_attribution,
    render_prefix,
    resume,
    scripted_policy,
)

CUT = 5
TASK = TRAVEL_TEMPTING
MISDIAGNOSIS = "Before booking, verify the flight departs on the requested Friday."
EXP01 = "experiments/decisions/exp01_travel_tempting.json"


def build_prefixes():
    healthy = redact_for_attribution(TASK.make_trajectory())  # targeted repair (rule restored)
    dropped = inject(
        TASK.make_trajectory(), FaultSpec(FaultType.CONSTRAINT_DROP, position=0)
    ).public
    blind = copy.deepcopy(dropped)  # blind repair: add the misdiagnosis, NOT the real rule
    blind.constraints = [*blind.constraints, MISDIAGNOSIS]
    return {"targeted_repair": healthy, "no_repair": dropped, "blind_repair": blind}


def recovery_rate(prefix, decisions: list[dict]) -> float:
    if not decisions:
        return 0.0
    oks = [
        resume(TASK, prefix, CUT, scripted_policy(decision_to_messages(d))).ok for d in decisions
    ]
    return sum(oks) / len(oks)


def main() -> None:
    prefixes = build_prefixes()
    if len(sys.argv) > 1 and sys.argv[1] == "--prompts":
        docs = {name: t.description for name, t in TASK.make_env().tools.items()}
        print(
            "##### blind_repair prompt #####\n" + render_prefix(prefixes["blind_repair"], CUT, docs)
        )
        return

    blind_decisions = json.loads(Path(sys.argv[1]).read_text()) if len(sys.argv) > 1 else []
    exp01 = json.loads(Path(EXP01).read_text())
    decisions = {
        "targeted_repair": exp01["healthy"],
        "no_repair": exp01["constraint_drop"],
        "blind_repair": blind_decisions,
    }

    print(f"{'repair policy':28} {'n':>3} {'recovery':>9}")
    rates = {}
    for name in ("no_repair", "blind_repair", "targeted_repair"):
        rates[name] = recovery_rate(prefixes[name], decisions[name])
        print(f"{name:28} {len(decisions[name]):>3} {rates[name]:>9.2f}")

    print(
        f"\nLOCALIZATION LIFT = {rates['targeted_repair'] - rates['blind_repair']:+.2f}  "
        f"(targeted {rates['targeted_repair']:.2f} vs blind {rates['blind_repair']:.2f})"
    )
    Path("results").mkdir(exist_ok=True)
    Path("results/exp04_travel_tempting_recovery.json").write_text(json.dumps(rates, indent=2))


if __name__ == "__main__":
    main()
