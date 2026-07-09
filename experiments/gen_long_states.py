"""Generate canonical FAILED long-horizon states for the reconcile_long horizon experiment.

Each state is the trajectory of a COMPETENT-BUT-DECEIVED agent under staleness: it checks every
transaction, approves every reconciling one AND the trap (whose stale receipt looks matching), flags
the blocked-category ones, and submits — so the ONLY error is the single deceived trap-approval.
This isolates the failure to the injected fault (a real agent driving ~100 steps could slip
elsewhere and confound the attribution measurement), giving a clean needle-in-a-long-trace test.
The trace the auditor sees is identical to what a deceived agent produces; we confirm below that a
real-agent sample reproduces this failure (experiments/decisions/states_reconcile_long_real/).

  python experiments/gen_long_states.py   # writes states_reconcile_long/*.json + asserts each FAILS
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import step  # noqa: E402

import d2b  # noqa: E402
from d2b.reconcile import _reconciles  # noqa: E402

OUT = Path("experiments/decisions/states_reconcile_long")


def deceived_decisions(cfg: dict) -> list[dict]:
    """Competent-but-deceived: check each txn; approve reconcilers + trap; flag blocked; submit."""
    decs: list[dict] = [{"tool": "list_transactions", "args": {}}]
    trap = cfg["trap_txn"]
    for tid in cfg["transactions"]:
        decs.append({"tool": "check_receipt", "args": {"txn": tid}})
        approve = _reconciles(cfg, tid) or tid == trap  # trap looks reconciling under staleness
        decs.append({"tool": "approve_txn" if approve else "flag_txn", "args": {"txn": tid}})
    decs.append({"tool": "submit_batch", "args": {}})
    return decs


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    variants = d2b.DOMAINS["reconcile_long"]["variants"]
    n_written = 0
    for vi, task in enumerate(variants):
        cfg = task.data
        state = {
            "condition": "staleness",
            "domain": "reconcile_long",
            "variant": vi,
            "decisions": deceived_decisions(cfg),
        }
        path = OUT / f"staleness_{cfg['name']}.json"
        path.write_text(json.dumps(state))
        # confirm the ONLY failure is the trap approval (isolates the fault)
        r = step.replay(state)
        assert not r.result.ok, f"{cfg['name']} unexpectedly passed"
        assert cfg["trap_txn"] in r.result.reason, (
            f"{cfg['name']} failed for the wrong reason: {r.result.reason}"
        )
        n_written += 1
        print(f"{cfg['name']:18} N={cfg['n_txns']:3} depth={cfg['trap_depth']:.2f} "
              f"steps={len(state['decisions']):3} -> FAIL on {cfg['trap_txn']} (clean)")
    print(f"\nwrote {n_written} canonical deceived staleness states -> {OUT}")


if __name__ == "__main__":
    main()
