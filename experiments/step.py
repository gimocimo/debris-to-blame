"""Interactive rollout driver (stateful CLI) — lets a REAL agent-under-test drive one rollout.

The agent (a subagent) calls this per step; Python executes the tool, applies any observation
injector, and validates — all BEHIND this CLI, so the agent never sees the injector and the WORLD
stays ground truth. State is just the decision list (+ condition), so parallel rollouts use separate
files with no races; each `act` replays the decisions so far to produce the next observation.

Usage:
  python experiments/step.py <state.json> init <condition>        # -> prints the initial prompt
  python experiments/step.py <state.json> act <tool> [k=v ...]    # -> prints OBSERVATION + STATUS
  python experiments/step.py <state.json> act finish              # -> STATUS: done + RESULT
  python experiments/step.py <state.json> result                 # -> authoritative PASS/FAIL

conditions: healthy | staleness | contradiction | cdrop:<rule_index> | sham
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import d2b  # noqa: E402

CT = d2b.CONFERENCE_TRIP
FaultSpec, FaultType = d2b.FaultSpec, d2b.FaultType
inject, sham_inject, redact = d2b.inject, d2b.sham_inject, d2b.redact_for_attribution
interactive_rollout, scripted_policy_fn = d2b.interactive_rollout, d2b.scripted_policy_fn
staleness_injector, contradiction_injector = d2b.staleness_injector, d2b.contradiction_injector

MAX_STEPS = 14


def setup_and_injectors(condition: str):
    if condition == "healthy":
        return redact(CT.make_trajectory()), ()
    if condition == "staleness":
        return redact(CT.make_trajectory()), (staleness_injector(),)
    if condition == "contradiction":
        return redact(CT.make_trajectory()), (contradiction_injector(),)
    if condition.startswith("cdrop:"):
        spec = FaultSpec(FaultType.CONSTRAINT_DROP, position=int(condition.split(":", 1)[1]))
        return inject(CT.make_trajectory(), spec).public, ()
    if condition == "sham":
        spec = FaultSpec(FaultType.CONSTRAINT_DROP, position=0)
        return sham_inject(CT.make_trajectory(), spec).public, ()
    raise SystemExit(f"unknown condition: {condition}")


def render_initial(setup) -> str:
    user = next((m.content for m in setup.messages if m.role == "user"), setup.task)
    lines = [f"TASK: {setup.task}", "", "STANDING RULES:"]
    lines += [f"  - {c}" for c in setup.constraints]
    lines += [
        "",
        f"AVAILABLE TOOLS: {', '.join(setup.tools)}",
        "ARG HINTS: latest_quote & book_flight take flight=<id>; book_hotel takes hotel=<id>; "
        "search_flights/search_hotels/file_expense_report/send_itinerary take no args.",
        "",
        "CONVERSATION SO FAR:",
        f"  user: {user}",
    ]
    return "\n".join(lines)


def replay(state: dict):
    setup, inj = setup_and_injectors(state["condition"])
    decs = [dict(d) for d in state["decisions"]]
    n = max(1, len(decs))
    return interactive_rollout(CT, scripted_policy_fn(decs), setup, injectors=inj, max_steps=n)


def main() -> None:
    path = Path(sys.argv[1])
    cmd = sys.argv[2]

    if cmd == "init":
        condition = sys.argv[3]
        setup, _ = setup_and_injectors(condition)
        path.write_text(json.dumps({"condition": condition, "decisions": []}))
        print(render_initial(setup))
        return

    state = json.loads(path.read_text())

    if cmd == "start":  # print the initial prompt WITHOUT revealing the condition (no leak)
        setup, _ = setup_and_injectors(state["condition"])
        print(render_initial(setup))
        return

    if cmd == "result":
        r = replay(state) if state["decisions"] else None
        ok = bool(r and r.result.ok)
        reason = r.result.reason if r else "no actions taken"
        print(f"RESULT: {'PASS' if ok else 'FAIL'} — {reason}")
        return

    if cmd == "act":
        parts = " ".join(sys.argv[3:]).split()  # robust to quoting (act tool k=v OR act "tool k=v")
        tool = parts[0] if parts else ""
        if tool == "finish":
            state["decisions"].append({"finish": True})
        else:
            args = {}
            for kv in parts[1:]:
                if "=" in kv:
                    k, v = kv.split("=", 1)
                    args[k] = v
            state["decisions"].append({"tool": tool, "args": args})
        path.write_text(json.dumps(state))

        r = replay(state)
        obs = next((m for m in reversed(r.transcript) if m.role == "tool"), None)
        print("OBSERVATION:", obs.content if obs else "(no tool observation yet)")
        done = tool in ("finish", "send_itinerary") or len(state["decisions"]) >= MAX_STEPS
        if done:
            print("STATUS: done")
            print(f"RESULT: {'PASS' if r.result.ok else 'FAIL'} — {r.result.reason}")
        else:
            print("STATUS: running (call `finish` once the task is fully complete)")
        return

    raise SystemExit(f"unknown command: {cmd}")


if __name__ == "__main__":
    main()
