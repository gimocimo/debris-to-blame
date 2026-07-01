"""Render the headline figure (the vertical slice) from the cached result JSONs.

Writes assets/headline.png. Deterministic, no model calls:  python scripts/make_figure.py
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
R = ROOT / "results"
GOOD, BAD = "#3a923a", "#c23b52"


def main() -> None:
    deg = json.loads((R / "exp01_travel_tempting_constraint_drop.json").read_text())
    att = json.loads((R / "exp02_travel_tempting_attribution.json").read_text())
    rec = json.loads((R / "exp04_travel_tempting_recovery.json").read_text())

    fig, axes = plt.subplots(1, 3, figsize=(13.5, 4.4))
    fig.suptitle(
        "Debris→Blame  ·  one fault (constraint_drop, travel), 5 samples/cell, $0 inference\n"
        "A dropped rule silently breaks the agent — invisible in the trace — "
        "recoverable only once localized.",
        fontsize=11,
        y=1.06,
    )

    # 1. Degrade
    ax = axes[0]
    vals = [deg["healthy"]["p_fail"], deg["constraint_drop"]["p_fail"]]
    ax.bar(["rule\npresent", "rule\ndropped"], vals, color=[GOOD, BAD], width=0.6)
    ax.set_title("1. Degrade\nP[books the red-eye]")

    # 2. Attribute (correct attribution of the real fault)
    ax = axes[1]
    vals = [att["blind_failed"]["attributed"], att["with_policy_failed"]["attributed"]]
    ax.bar(["trace\nonly", "trace +\npolicy"], vals, color=[BAD, GOOD], width=0.6)
    ax.set_title("2. Attribute\ncorrectly blames the fault")

    # 3. Recover
    ax = axes[2]
    vals = [rec["no_repair"], rec["blind_repair"], rec["targeted_repair"]]
    ax.bar(
        ["no\nrepair", "blind\nrepair", "targeted\nrepair"],
        vals,
        color=[BAD, BAD, GOOD],
        width=0.6,
    )
    ax.set_title("3. Recover\ntask recovered")

    for ax in axes:
        ax.set_ylim(0, 1.08)
        ax.set_yticks([0, 0.5, 1.0])
        ax.spines[["top", "right"]].set_visible(False)
        for p in ax.patches:
            ax.text(
                p.get_x() + p.get_width() / 2,
                p.get_height() + 0.02,
                f"{p.get_height():.2f}",
                ha="center",
                fontsize=10,
                fontweight="bold",
            )

    fig.tight_layout()
    out = ROOT / "assets" / "headline.png"
    out.parent.mkdir(exist_ok=True)
    fig.savefig(out, dpi=140, bbox_inches="tight")
    print(f"wrote {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
