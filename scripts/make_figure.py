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

    hpath = R / "reconcile_long_horizon.json"
    if hpath.exists():
        _horizon_figure(json.loads(hpath.read_text()))

    mpath = R / "auditor_matrix.json"
    if mpath.exists():
        _matrix_figure(json.loads(mpath.read_text()))


def _matrix_figure(m: dict) -> None:
    """Model×effort auditor matrix: does the staleness deception gap survive across configs?

    Grouped bars per config: staleness blind / oracle / root-cause attributed rate. Blind and oracle
    stay ≈0 for every model at every effort (the gap is model/effort-invariant); only root-cause
    recovery varies — and by MODEL (Fable > Opus ≈ Sonnet), not by effort."""
    configs = sorted(m, key=lambda t: (t.split(":")[0], t.split(":")[1]))

    def rate(tier, key):
        c = m[tier].get(key)
        return (c["attr"] / c["n"]) if c else 0.0

    fig, ax = plt.subplots(figsize=(9.5, 4.6))
    xs = list(range(len(configs)))
    w = 0.26
    series = [("staleness:blind", BAD, "blind (trace only)"),
              ("staleness:policy", GOOD, "oracle (+ full policy)"),
              ("staleness:rootcause", "#7c3aed", "root-cause (+ outcome)")]
    for i, (key, color, label) in enumerate(series):
        vals = [rate(t, key) for t in configs]
        bars = ax.bar([x + (i - 1) * w for x in xs], vals, width=w, color=color, label=label)
        for b in bars:
            ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.02, f"{b.get_height():.2f}",
                    ha="center", fontsize=7.5, fontweight="bold")
    ax.set_xticks(xs)
    ax.set_xticklabels(configs, rotation=18, ha="right", fontsize=9)
    ax.set_ylim(0, 1.12)
    ax.set_yticks([0, 0.5, 1.0])
    ax.set_ylabel("staleness attributed rate")
    ax.set_title("The deception gap is model × effort invariant\n"
                 "blind & oracle ≈ 0 for every config; only root-cause recovery varies — by MODEL, "
                 "not effort")
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(frameon=False, ncol=3, loc="upper center", fontsize=8.5)
    fig.tight_layout()
    out = ROOT / "assets" / "auditor_matrix.png"
    fig.savefig(out, dpi=140, bbox_inches="tight")
    print(f"wrote {out.relative_to(ROOT)}")


def _horizon_figure(h: dict) -> None:
    """reconcile_long: attributing one stale approval in an N-txn trace (needle in a long trace).

    x = horizon N (log); y = rate. Blind detect ≈ 0 (deception invisible at any length); root-cause
    recovers only the MECHANISM in the abstract ("a receipt was stale") at a low, horizon-flat rate,
    and GENUINE localization (right txn AND reason) is 0 at every N — the needle is unfindable.
    The raw named-trap line is confabulation-inflated (auditor invents a false 'blocked' theory that
    coincidentally hits the trap) and only at the shortest horizon."""
    ns = sorted({int(k.split(":")[0]) for k in h})

    def series(arm: str, field: str):
        return [h[f"{n}:{arm}"][field] / h[f"{n}:{arm}"]["n"] for n in ns]

    fig, ax = plt.subplots(figsize=(7.4, 4.6))
    ax.plot(ns, series("rootcause", "mechanism"), "-o", color="#e08a3c", lw=2,
            label="root-cause names 'stale' mechanism (abstract)")
    ax.plot(ns, series("rootcause", "genuine_loc"), "-o", color="#7c3aed", lw=2,
            label="root-cause GENUINE localization (txn + reason)")
    ax.plot(ns, series("rootcause", "named_trap_raw"), "--^", color="#b8a3e0", lw=1.4,
            label="named trap txn (raw; incl. confabulation)")
    ax.plot(ns, series("blind", "detect"), "-s", color=BAD, lw=1.6,
            label="blind detects any problem")
    ax.plot(ns, [1.0 / n for n in ns], ":", color="#6b7280", lw=1.5, label="chance = 1/N")
    ax.set_xscale("log")
    ax.set_xticks(ns)
    ax.set_xticklabels([str(n) for n in ns])
    ax.set_ylim(-0.03, 1.02)
    ax.set_xlabel("batch length N (≈ 2N interactive steps)")
    ax.set_ylabel("rate over 8 traces/length")
    ax.set_title("reconcile_long — a stale needle in a long trace is unlocalizable\n"
                 "blind sees nothing; root-cause recovers only 'a receipt was stale', not which")
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(frameon=False, fontsize=8, loc="upper right")
    fig.tight_layout()
    out = ROOT / "assets" / "reconcile_long_horizon.png"
    fig.savefig(out, dpi=140, bbox_inches="tight")
    print(f"wrote {out.relative_to(ROOT)}")


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
    domains = ["conference", "scheduling", "review", "incident", "reconcile"]
    fams = [("staleness", "staleness\n(deceptive data)"),
            ("misexec", "misexecution\n(deceptive confirmation)"),
            ("cdrop", "constraint_drop\n(deletion)"), ("forget", "tool_forgetting\n(omission)")]
    arms = [("blind", BAD, "blind (trace only)"), ("deleak", "#e08a3c", "de-leak (policy − rule)"),
            ("policy", GOOD, "oracle (+ full policy)"),
            ("rootcause", "#7c3aed", "root-cause (+ outcome, causation question)")]

    def rate(dom: str, fam: str, arm: str) -> float | None:
        c = att.get(dom, {}).get(fam, {}).get("opus", {}).get(arm)
        return (c["attr"] / c["n"]) if c else None

    fig, axes = plt.subplots(1, 4, figsize=(20.5, 4.4), sharey=True)
    fig.suptitle("Cross-domain blame-gap map — attributed rate by auditor information "
                 "(5 domains, sincere agents)", fontsize=11, y=1.04)
    w = 0.2
    for ax, (fam, title) in zip(axes, fams, strict=True):
        xs = list(range(len(domains)))
        for i, (arm, color, label) in enumerate(arms):
            vals = [rate(d, fam, arm) for d in domains]
            pos = [x + (i - 1.5) * w for x in xs]
            bars = ax.bar([p for p, v in zip(pos, vals, strict=True) if v is not None],
                          [v for v in vals if v is not None], width=w, color=color,
                          label=label if fam.startswith("staleness") else None)
            for b in bars:
                ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.03,
                        f"{b.get_height():.2f}", ha="center", fontsize=7.5, fontweight="bold")
        # mark cells with no data (fault null on that domain)
        for x in xs:
            if rate(domains[x], fam, "blind") is None and rate(domains[x], fam, "policy") is None:
                ax.text(x, 0.06, "fault null\n(no failures)", ha="center", fontsize=8,
                        color="#6b7280")
        ax.set_xticks(xs)
        ax.set_xticklabels(domains, rotation=20, ha="right", fontsize=8.5)
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
