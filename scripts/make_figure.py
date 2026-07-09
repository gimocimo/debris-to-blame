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

    gpath = R / "conf_degrade_grid.json"
    apath = R / "conf_attribution.json"
    if gpath.exists():
        _degrade_grid_figure(json.loads(gpath.read_text()))
    if gpath.exists() and apath.exists():
        _blamegap_map_figure(json.loads(gpath.read_text()), json.loads(apath.read_text()))
    rpath = R / "conf_recovery.json"
    if rpath.exists():
        _recovery_figure(json.loads(rpath.read_text()))


def _bars(ax, labels, vals, colors, title):
    ax.bar(labels, vals, color=colors, width=0.62)
    ax.set_ylim(0, 1.12)
    ax.set_yticks([0, 0.5, 1.0])
    ax.set_title(title, fontsize=10)
    ax.spines[["top", "right"]].set_visible(False)
    for p in ax.patches:
        ax.text(p.get_x() + p.get_width() / 2, p.get_height() + 0.02, f"{p.get_height():.2f}",
                ha="center", fontsize=9, fontweight="bold")


def _blamegap_map_figure(deg: dict, att: dict) -> None:
    """The money figure: the CROSS-DOMAIN blame-gap map (att = domain-aware conf_attribution.json).

    One panel per fault family; x = domains; bars = blind / de-leak / oracle attributed-rate.
    Shows the two regimes: the deletion gap (closed only by the exact rule) and the deception gap
    (NOT closed by the policy), replicated across domains; forget is salience-dependent.
    """
    domains = ["conference", "scheduling", "review"]
    fams = [("staleness", "staleness (deception)"), ("cdrop", "constraint_drop (deletion)"),
            ("forget", "tool_forgetting (omission)")]
    arms = [("blind", BAD, "blind (trace only)"), ("deleak", "#e08a3c", "de-leak (policy − rule)"),
            ("policy", GOOD, "oracle (+ full policy)")]

    def rate(dom: str, fam: str, arm: str) -> float | None:
        c = att.get(dom, {}).get(fam, {}).get("opus", {}).get(arm)
        return (c["attr"] / c["n"]) if c else None

    fig, axes = plt.subplots(1, 3, figsize=(13.5, 4.2), sharey=True)
    fig.suptitle("Cross-domain blame-gap map — attributed rate by auditor information "
                 "(3 domains, sincere agents)", fontsize=11, y=1.04)
    w = 0.26
    for ax, (fam, title) in zip(axes, fams, strict=True):
        xs = list(range(len(domains)))
        for i, (arm, color, label) in enumerate(arms):
            vals = [rate(d, fam, arm) for d in domains]
            pos = [x + (i - 1) * w for x in xs]
            bars = ax.bar([p for p, v in zip(pos, vals, strict=True) if v is not None],
                          [v for v in vals if v is not None], width=w, color=color,
                          label=label if fam == "staleness" else None)
            for b in bars:
                ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.03,
                        f"{b.get_height():.2f}", ha="center", fontsize=8, fontweight="bold")
        # mark cells with no data (fault null on that domain)
        for x in xs:
            if rate(domains[x], fam, "blind") is None and rate(domains[x], fam, "policy") is None:
                ax.text(x, 0.06, "fault null\n(no failures)", ha="center", fontsize=8,
                        color="#6b7280")
        ax.set_xticks(xs)
        ax.set_xticklabels(domains)
        ax.set_ylim(0, 1.18)
        ax.set_yticks([0, 0.5, 1.0])
        ax.set_title(title, fontsize=10)
        ax.spines[["top", "right"]].set_visible(False)
    fig.legend(frameon=False, ncol=3, loc="upper center", bbox_to_anchor=(0.5, 0.97), fontsize=9)
    fig.tight_layout(rect=(0, 0, 1, 0.9))
    out = ROOT / "assets" / "blamegap_map.png"
    fig.savefig(out, dpi=140, bbox_inches="tight")
    print(f"wrote {out.relative_to(ROOT)}")


def _recovery_figure(rec: dict) -> None:
    order = ["no_repair", "blind_repair", "targeted_repair"]
    labels = ["no\nrepair", "blind repair\n(wrong rule)", "targeted repair\n(restore rule)"]
    vals = [rec[c]["k_ok"] / rec[c]["n"] for c in order]
    fig, ax = plt.subplots(figsize=(6.8, 4.4))
    _bars(ax, labels, vals, [BAD, BAD, GOOD],
          "Recovery on cdrop:refundable — localization enables recovery\nP[task recovered]")
    fig.tight_layout()
    out = ROOT / "assets" / "conf_recovery.png"
    fig.savefig(out, dpi=140, bbox_inches="tight")
    print(f"wrote {out.relative_to(ROOT)}")


def _degrade_grid_figure(m: dict) -> None:
    order = ["healthy", "staleness", "contradiction", "cdrop:0", "cdrop:2", "sham",
             "forget:file_expense_report"]
    nice = {"cdrop:0": "cdrop\nred-eye", "cdrop:2": "cdrop\nrefundable",
            "forget:file_expense_report": "forget\nexpense"}
    order = [c for c in order if c in m]
    vals = [m[c]["k_fail"] / m[c]["n"] for c in order]
    colors = [
        "#c9a227" if c in ("healthy", "sham") else BAD if v >= 0.75 else "#e08a3c"
        for c, v in zip(order, vals, strict=True)
    ]
    colors[order.index("healthy")] = GOOD
    fig, ax = plt.subplots(figsize=(10, 4.6))
    ax.bar([nice.get(c, c) for c in order], vals, color=colors, width=0.62)
    ax.set_ylim(0, 1.16)
    ax.set_ylabel("P[task fails]")
    n = m[order[0]]["n"]
    ax.set_title(f"CONFERENCE_TRIP degradation by fault — sincere agents "
                 f"(n={n}/cond across 4 task variants)")
    ax.spines[["top", "right"]].set_visible(False)
    for c, p in zip(order, ax.patches, strict=True):
        vf = m[c].get("variants_failing")
        nv = m[c].get("n_variants")
        tag = f"\n{vf}/{nv} var" if vf is not None and nv else ""
        ax.text(p.get_x() + p.get_width() / 2, p.get_height() + 0.02,
                f"{p.get_height():.2f}{tag}", ha="center", fontsize=9, fontweight="bold")
    fig.tight_layout()
    out = ROOT / "assets" / "conf_grid.png"
    fig.savefig(out, dpi=140, bbox_inches="tight")
    print(f"wrote {out.relative_to(ROOT)}")


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
