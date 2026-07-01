"""Demo — inject each of the six faults, show the private label, and prove the public trace is
leakage-free (no injection markers reach an attributor).

Runs with zero model calls / zero cost:  python scripts/demo_inject.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from d2b import (  # noqa: E402
    FaultSpec,
    FaultType,
    Trajectory,
    inject,
    successful_flight_trajectory,
)


def _line(m, idx: int) -> str:
    tag = f"  \033[91m<-- injected ({m.injected})\033[0m" if m.injected else ""
    if m.tool_call:
        body = f"CALL {m.tool_call.name}({m.tool_call.args})"
    elif m.role == "tool":
        body = f"[{m.tool_name}] {m.content}"
    else:
        body = m.content or ""
    return f"    {idx:>2} {m.role:<9} {body}{tag}"


def _show(t: Trajectory, title: str) -> None:
    print(f"\n  {title}")
    print(f"    constraints: {t.constraints}")
    print(f"    tools:       {t.tools}")
    for i, m in enumerate(t.messages):
        print(_line(m, i))


def main() -> None:
    base = successful_flight_trajectory()
    print("=" * 84)
    print("  DEBRIS -> BLAME  ·  M1 injection demo  (deterministic, no model calls)")
    print("=" * 84)
    _show(base, "HEALTHY trajectory (books BA112 — not a red-eye, under budget) ✅")

    specs = [
        FaultSpec(FaultType.DEBRIS, position=3, volume=1),
        FaultSpec(FaultType.STALENESS, position=5, volume=1),
        FaultSpec(FaultType.CONTRADICTION, position=3, volume=1),
        FaultSpec(FaultType.WRONG_TOOL, position=5, volume=2),
        FaultSpec(FaultType.CONSTRAINT_DROP, position=0, volume=1),
        FaultSpec(FaultType.TOOL_FORGETTING, position=5, volume=4),
    ]

    print("\n" + "-" * 84)
    print(
        "  INJECTIONS  (each edit's locus IS the answer key — held PRIVATELY, never in the trace)"
    )
    print("-" * 84)
    for spec in specs:
        c = inject(base, spec)
        _show(c.corrupted, f"{spec.type.value.upper()}  @pos={spec.position} vol={spec.volume}")
        print(f"    private blame_label = {c.label.blame_label}")
        if c.label.extra.get("dropped_constraint"):
            print(f"    dropped: {c.label.extra['dropped_constraint']}")

    print("\n" + "-" * 84)
    print("  LEAKAGE CHECK  (what an attributor actually receives — .public)")
    print("-" * 84)
    c = inject(base, FaultSpec(FaultType.DEBRIS, position=3))
    pub = c.public
    _show(pub, "PUBLIC (redacted) DEBRIS trace — note: no <-- injected markers anywhere")
    leaked = [m for m in pub.messages if m.injected is not None]
    leak_meta = [k for k in pub.meta if k in {"fault", "blame_label", "corrupted"}]
    print(f"\n    markers leaked: {len(leaked)}   label-meta leaked: {leak_meta}   (must be 0/[])")
    print("    original untouched:", base.meta.get("success") is True, "\n")


if __name__ == "__main__":
    main()
