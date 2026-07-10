"""Build the full 5-domain AUDITOR manifest — every (committed failed state, arm) to re-audit.

Used by the model×effort robustness matrix (and the cross-family Codex packs): each auditor config
diagnoses this identical canonical trace set, so results compare across models/efforts/families.
Covers the four damaging faults per domain (staleness / misexecution / forget / binding
constraint_drop where it bites), on the load-bearing arms (blind / policy / rootcause; + de-leak).

  python experiments/gen_auditor_manifest.py  # writes decisions/auditor_manifest_5domain.json
"""

from __future__ import annotations

import json
from pathlib import Path

DEC = Path("experiments/decisions")
NC_ARMS = ["blind", "policy", "rootcause"]  # non-deletion faults
CDROP_ARMS = ["blind", "deleak", "policy"]

# (domain, states_dir, {condition_file_stem: arms}); only FAILING faults are audited.
DOMAINS = [
    ("conference", "states", {
        "staleness": NC_ARMS, "misexec": NC_ARMS,
        "forget-file_expense_report": NC_ARMS, "cdrop-2": CDROP_ARMS}),
    ("scheduling", "states_scheduling", {
        "staleness": NC_ARMS, "misexec": NC_ARMS,
        "forget-post_agenda": NC_ARMS, "cdrop-3": CDROP_ARMS}),
    ("review", "states_review", {
        "staleness": NC_ARMS, "misexec": NC_ARMS, "forget-close_ticket": NC_ARMS}),  # cdrop null
    ("incident", "states_incident", {
        "staleness": NC_ARMS, "misexec": NC_ARMS, "forget-close_incident": NC_ARMS}),  # cdrop n/a
    ("reconcile", "states_reconcile", {
        "staleness": NC_ARMS, "misexec": NC_ARMS,
        "forget-submit_batch": NC_ARMS, "cdrop-1": CDROP_ARMS}),
]


def main() -> None:
    manifest = []
    for domain, sdir, conds in DOMAINS:
        for stem, arms in conds.items():
            for v in range(4):
                for rep in (1, 2):
                    f = DEC / sdir / f"{stem}_v{v}_{rep}.json"
                    if not f.exists():
                        raise SystemExit(f"missing committed state: {f}")
                    st = json.loads(f.read_text())
                    for arm in arms:
                        manifest.append({
                            "file": str(f), "arm": arm, "domain": domain,
                            "condition": st["condition"], "variant": v,
                        })
    out = DEC / "auditor_manifest_5domain.json"
    out.write_text(json.dumps(manifest, indent=0))
    from collections import Counter
    by = Counter((m["domain"], m["condition"].split(":")[0].split("-")[0]) for m in manifest)
    print(f"wrote {len(manifest)} (state, arm) audits -> {out}")
    for k in sorted(by):
        print(f"  {k[0]:12} {k[1]:12} {by[k]}")


if __name__ == "__main__":
    main()
