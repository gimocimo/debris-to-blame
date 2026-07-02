"""Dumb, $0, deterministic attributor baselines — the floor the LLM detective must beat.

Each baseline reads a reconstructed rollout trace and emits a {problem, culprit} verdict, graded by
the SAME grade_attribution the LLM detective is graded by. We report, per baseline:
  recall    — attributed rate on FAILED faulty traces  (did it name the real fault?)
  false-pos — flagged-a-problem rate on healthy/sham    (does it cry wolf?)
A baseline that "attributes" a fault only by crying wolf on everything is exposed by its FP rate.

  python experiments/attr_baselines.py "experiments/decisions/states/*.json"
"""

from __future__ import annotations

import json
import sys
from glob import glob
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import attribute  # noqa: E402
import step  # noqa: E402
from attr_common import record_for  # noqa: E402

from d2b.detective import grade_attribution  # noqa: E402
from d2b.stats import fmt_rate  # noqa: E402

# a plausible dumb lexicon a grep-based auditor might use (deliberately imprecise)
_LEXICON = [
    "red-eye", "non-refundable", "cached", "stale", "surged", "over budget", "expense report",
]


def _tool_steps(traj) -> list[tuple[int, str, str]]:
    """(index, tool_name, observation_text) for each executed tool call in the trace."""
    out = []
    msgs = traj.messages
    for i, m in enumerate(msgs):
        if m.tool_call is not None:
            obs = ""
            if i + 1 < len(msgs) and msgs[i + 1].role == "tool":
                obs = msgs[i + 1].content or ""
            out.append((i, m.tool_call.name, obs))
    return out


def random_baseline(traj, idx: int) -> dict:
    """Blame a pseudo-random tool step (deterministic in idx — no RNG)."""
    steps = _tool_steps(traj)
    if not steps:
        return {"problem": False, "culprit": "none"}
    i, name, _ = steps[(idx * 7 + 3) % len(steps)]
    return {"problem": True, "culprit": f"{name} at step {i}"}


def recency_baseline(traj) -> dict:
    """Blame the last action before the episode ended."""
    steps = _tool_steps(traj)
    if not steps:
        return {"problem": False, "culprit": "none"}
    i, name, _ = steps[-1]
    return {"problem": True, "culprit": f"{name} at step {i}"}


def keyword_baseline(traj) -> dict:
    """Flag + name the first suspicious token found anywhere in the trace text (grep auditor)."""
    text = "\n".join((m.content or "") for m in traj.messages).lower()
    for tok in _LEXICON:
        if tok in text:
            return {"problem": True, "culprit": f"trace mentions {tok}"}
    return {"problem": False, "culprit": "none"}


BASELINES = {"random": random_baseline, "recency": recency_baseline, "keyword": keyword_baseline}


def _verdict(name: str, traj, idx: int) -> dict:
    return random_baseline(traj, idx) if name == "random" else BASELINES[name](traj)


def main() -> None:
    files = sorted(glob(sys.argv[1]))
    # tallies[name] = {"faulty":[att,n], "clean":[fp,n]}
    tallies = {b: {"faulty": [0, 0], "clean": [0, 0]} for b in BASELINES}
    for idx, f in enumerate(files):
        st = json.loads(Path(f).read_text())
        cond = st["condition"]
        r = step.replay(st) if st["decisions"] else None
        failed = bool(r and not r.result.ok)
        traj, task, _ = attribute.reconstruct(st)
        rec = record_for(cond, task)
        clean = cond in ("healthy", "sham")
        for b in BASELINES:
            v = _verdict(b, traj, idx)
            if clean:
                tallies[b]["clean"][0] += int(bool(v["problem"]))
                tallies[b]["clean"][1] += 1
            elif failed and rec is not None:
                g = grade_attribution(v, rec)
                tallies[b]["faulty"][0] += int(g["attributed"])
                tallies[b]["faulty"][1] += 1

    print("Dumb attributor baselines (the floor the LLM detective must beat)\n")
    print(f"{'baseline':10} {'recall on faulty (attributed)':34} {'false-pos on healthy/sham':30}")
    out = {}
    for b in BASELINES:
        fa, cl = tallies[b]["faulty"], tallies[b]["clean"]
        print(f"{b:10} {fmt_rate(fa[0], fa[1]):34} {fmt_rate(cl[0], cl[1]):30}")
        out[b] = {"recall": fa, "false_pos": cl}
    Path("results").mkdir(exist_ok=True)
    Path("results/conf_attr_baselines.json").write_text(json.dumps(out, indent=2))
    print("\nwrote results/conf_attr_baselines.json")


if __name__ == "__main__":
    main()
