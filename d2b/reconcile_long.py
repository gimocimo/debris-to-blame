"""RECONCILE_LONG — the accumulation loop stretched to a REAL horizon (tens/hundreds of steps).

Same shape and validator as `reconcile`, but the batch has N transactions (N up to ~48 → ~100
interactive steps), and the single stale-receipt TRAP sits at a controllable DEPTH in the batch.
This makes **fault→symptom distance a variable**: the auditor must localize one bad approval among
~N look-alikes in a long trace. The experiment asks whether the blame gap WIDENS as the needle is
buried deeper and the horizon grows (does long-horizon attribution degrade?).

Reuses `make_reconcile` (already N-generic); this module only builds the long cfgs and a length ×
depth variant sweep. cfg carries `n_txns`, `trap_depth` (fractional), and `max_steps` so the
interactive driver and the scorer can stratify by horizon.
"""

from __future__ import annotations

from .reconcile import _BASE_POLICY, make_reconcile

# allowed (reconciling) categories cycled through the batch; the blocked one only ever blocks
_ALLOWED = ["meals", "transport", "lodging", "software", "supplies", "travel", "training"]
_BLOCKED_CAT = "alcohol"
# trap depths (as a fraction of the batch) used across the 4 sub-variants of each length
_DEPTH_FRACS = [0.15, 0.4, 0.65, 0.9]


def _amount(i: int, salt: int) -> int:
    return 40 + ((i * 13 + salt * 7) % 200) // 5 * 5  # deterministic, 40..235 in $5 steps


def _long_cfg(name: str, n: int, trap_frac: float, salt: int) -> dict:
    """One long batch: N txns, exactly one stale TRAP at `trap_frac` depth, two blocked-category
    txns offset from it, the rest reconcile."""
    trap_idx = min(n - 1, max(0, int(round(trap_frac * (n - 1)))))
    # two blocked txns placed away from the trap (wrap around), so `good` is well populated
    blocked_idx = {(trap_idx + n // 3) % n, (trap_idx + 2 * n // 3) % n} - {trap_idx}
    tx: dict = {}
    for i in range(n):
        tid = f"T{i + 1:03d}"
        amt = _amount(i, salt)
        if i == trap_idx:
            # deception: cached receipt matches the charge, live receipt is short by $20+salt
            tx[tid] = {
                "amount": amt,
                "live_receipt": amt - (20 + salt % 15),
                "cached_receipt": amt,
                "category": _ALLOWED[i % len(_ALLOWED)],
            }
        elif i in blocked_idx:
            tx[tid] = {
                "amount": amt,
                "live_receipt": amt,
                "cached_receipt": amt,
                "category": _BLOCKED_CAT,
            }
        else:
            tx[tid] = {
                "amount": amt,
                "live_receipt": amt,
                "cached_receipt": amt,
                "category": _ALLOWED[i % len(_ALLOWED)],
            }
    return {
        "name": name,
        "blocked_categories": [_BLOCKED_CAT],
        "transactions": tx,
        "trap_txn": f"T{trap_idx + 1:03d}",
        "policy": list(_BASE_POLICY),
        "n_txns": n,
        "trap_depth": round(trap_idx / (n - 1), 2),
        "max_steps": 2 * n + 10,  # list + N*(check+decide) + submit, with slack
    }


# Length sweep: three horizons, 4 independent sub-variants each (trap depth spans early→late so
# depth varies within a length-cell, and each length has >=4 variants for variant-clustered stats).
_LENGTHS = [8, 24, 48]
LONG_VARIANTS_CFG = [
    _long_cfg(f"reconcile_n{n}_v{v}", n, _DEPTH_FRACS[v], salt=v + 1)
    for n in _LENGTHS
    for v in range(4)
]

RECONCILE_LONG_VARIANTS = [make_reconcile(c) for c in LONG_VARIANTS_CFG]
