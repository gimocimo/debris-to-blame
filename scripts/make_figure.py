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

    grid_path = R / "grid_constraint_drop_tiers.json"
    if grid_path.exists():
        _grid_figure(json.loads(grid_path.read_text()))

    conf_path = R / "conf_interactive_degrade.json"
    if conf_path.exists():
        _conf_figure(json.loads(conf_path.read_text()))


def _conf_figure(matrix: dict) -> None:
    labels = {"healthy": "healthy", "staleness": "staleness", "cdrop_2": "cdrop\n(refundable)"}
    order = ["healthy", "staleness", "cdrop_2"]
    vals = [matrix[k]["k_fail"] / matrix[k]["n"] for k in order]
    fig, ax = plt.subplots(figsize=(7, 4.4))
    ax.bar([labels[k] for k in order], vals, color=[GOOD, BAD, BAD], width=0.6)
    ax.set_ylim(0, 1.12)
    ax.set_ylabel("P[task fails]")
    ax.set_title("CONFERENCE_TRIP — interactive rollout degradation (n=3, real agents)")
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
    out = ROOT / "assets" / "conf_degrade.png"
    fig.savefig(out, dpi=140, bbox_inches="tight")
    print(f"wrote {out.relative_to(ROOT)}")


def _grid_figure(matrix: dict) -> None:
    tiers = list(matrix)
    conds = ["healthy", "fault", "sham"]
    colors = {"healthy": GOOD, "fault": BAD, "sham": "#c9a227"}
    fig, ax = plt.subplots(figsize=(8, 4.4))
    w = 0.25
    xs = range(len(tiers))
    for i, cond in enumerate(conds):
        vals = [matrix[t][cond]["k"] / matrix[t][cond]["n"] for t in tiers]
        bars = ax.bar([x + i * w for x in xs], vals, width=w, label=cond, color=colors[cond])
        for b in bars:
            ax.text(
                b.get_x() + w / 2,
                b.get_height() + 0.02,
                f"{b.get_height():.2f}",
                ha="center",
                fontsize=9,
            )
    ax.set_xticks([x + w for x in xs])
    ax.set_xticklabels(tiers)
    ax.set_ylim(0, 1.12)
    ax.set_ylabel("P[task fails]")
    ax.set_title("constraint_drop degradation by Claude tier (sham = drop a non-binding rule)")
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(frameon=False, ncol=3, loc="upper center")
    fig.tight_layout()
    out = ROOT / "assets" / "grid.png"
    fig.savefig(out, dpi=140, bbox_inches="tight")
    print(f"wrote {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
