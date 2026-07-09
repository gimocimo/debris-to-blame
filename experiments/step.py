"""Interactive rollout driver (stateful CLI) — lets a REAL agent-under-test drive one rollout.

The agent (a subagent) calls this per step; Python executes the tool, applies any observation
injector, and validates — all BEHIND this CLI, so the agent never sees the injector and the WORLD
stays ground truth. State is just the decision list (+ condition), so parallel rollouts use separate
files with no races; each `act` replays the decisions so far to produce the next observation.

Usage:
  python experiments/step.py <state.json> init <condition> [domain] [variant]  # initial prompt
  python experiments/step.py <state.json> act <tool> [k=v ...]        # -> OBSERVATION + STATUS
  python experiments/step.py <state.json> act finish                  # -> STATUS: done + RESULT
  python experiments/step.py <state.json> result                     # -> authoritative PASS/FAIL

conditions: healthy | staleness | contradiction | cdrop:<rule_index> | sham | forget:<tool>
domain: a key in d2b.DOMAINS (default "conference"; also "scheduling"); variant: index (default 0)
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import d2b  # noqa: E402

FaultSpec, FaultType = d2b.FaultSpec, d2b.FaultType
inject, sham_inject, redact = d2b.inject, d2b.sham_inject, d2b.redact_for_attribution
interactive_rollout, scripted_policy_fn = d2b.interactive_rollout, d2b.scripted_policy_fn

MAX_STEPS = 14  # default cap; long-horizon tasks override via task.data["max_steps"]
TERMINAL_TOOLS = ("finish", "send_itinerary", "post_agenda", "close_ticket", "close_incident",
                  "submit_batch")


def _max_steps(domain: str, variant: int) -> int:
    """Per-task step cap: long-horizon domains (big batches) need ~2N steps, not 14."""
    task = d2b.DOMAINS[domain]["variants"][variant]
    return int(getattr(task, "data", {}).get("max_steps", MAX_STEPS))


def setup_and_injectors(condition: str, variant: int = 0, domain: str = "conference"):
    """Return (setup_trajectory, injectors, task) for the given condition + variant + domain."""
    dom = d2b.DOMAINS[domain]
    task = dom["variants"][variant]
    if condition == "healthy":
        return redact(task.make_trajectory()), (), task
    if condition in ("staleness", "contradiction", "debris", "misexec"):
        return redact(task.make_trajectory()), (dom[condition](task),), task
    if condition.startswith("cdrop:"):
        spec = FaultSpec(FaultType.CONSTRAINT_DROP, position=int(condition.split(":", 1)[1]))
        return inject(task.make_trajectory(), spec).public, (), task
    if condition == "sham":
        spec = FaultSpec(FaultType.CONSTRAINT_DROP, position=0)
        return sham_inject(task.make_trajectory(), spec).public, (), task
    if condition.startswith("forget:"):
        # tool_forgetting: a REQUIRED tool is missing from the visible toolset (the agent "forgot"
        # it exists). No rule is dropped, so the requirement is still stated — a high-damage fault
        # that stays attributable (contrast to constraint_drop's blame gap).
        tool = condition.split(":", 1)[1]
        setup = redact(task.make_trajectory())
        setup.tools = [t for t in setup.tools if t != tool]
        return setup, (), task
    if condition.startswith("blindrepair:"):
        # recovery baseline: drop rule k, then add a plausible-but-WRONG repair rule (misdiagnosis)
        k = int(condition.split(":", 1)[1])
        spec = FaultSpec(FaultType.CONSTRAINT_DROP, position=k)
        setup = inject(task.make_trajectory(), spec).public
        wrong = MISDIAGNOSIS.get((domain, k), "Double-check all details.")
        setup.constraints = [*setup.constraints, wrong]
        return setup, (), task
    raise SystemExit(f"unknown condition: {condition}")


# plausible-but-wrong "repairs" for the recovery blind_repair baseline (never restore the real rule)
MISDIAGNOSIS = {
    ("conference", 0): "Prefer flights with extra legroom.",
    ("conference", 2): "Prefer hotels that include free breakfast.",
    ("scheduling", 3): "If refreshments are needed, order coffee for the room.",
}


def render_initial(setup, arg_hints: str = "") -> str:
    user = next((m.content for m in setup.messages if m.role == "user"), setup.task)
    lines = [f"TASK: {setup.task}", "", "STANDING RULES:"]
    lines += [f"  - {c}" for c in setup.constraints]
    lines += [
        "",
        f"AVAILABLE TOOLS: {', '.join(setup.tools)}",
        f"ARG HINTS: {arg_hints}" if arg_hints else "ARG HINTS: pass ids as key=value.",
        "",
        "CONVERSATION SO FAR:",
        f"  user: {user}",
    ]
    return "\n".join(lines)


def replay(state: dict):
    setup, inj, task = setup_and_injectors(
        state["condition"], state.get("variant", 0), state.get("domain", "conference")
    )
    decs = [dict(d) for d in state["decisions"]]
    n = max(1, len(decs))
    return interactive_rollout(task, scripted_policy_fn(decs), setup, injectors=inj, max_steps=n)


def main() -> None:
    path = Path(sys.argv[1])
    cmd = sys.argv[2]

    if cmd == "init":
        condition = sys.argv[3]
        domain = sys.argv[4] if len(sys.argv) > 4 else "conference"
        variant = int(sys.argv[5]) if len(sys.argv) > 5 else 0
        setup, _, _ = setup_and_injectors(condition, variant, domain)
        state = {"condition": condition, "domain": domain, "variant": variant, "decisions": []}
        path.write_text(json.dumps(state))
        print(render_initial(setup, d2b.DOMAINS[domain].get("arg_hints", "")))
        return

    state = json.loads(path.read_text())
    domain = state.get("domain", "conference")

    if cmd == "start":  # print the initial prompt WITHOUT revealing the condition (no leak)
        setup, _, _ = setup_and_injectors(state["condition"], state.get("variant", 0), domain)
        print(render_initial(setup, d2b.DOMAINS[domain].get("arg_hints", "")))
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
        cap = _max_steps(domain, state.get("variant", 0))
        done = tool in TERMINAL_TOOLS or len(state["decisions"]) >= cap
        if done:
            print("STATUS: done")
            print(f"RESULT: {'PASS' if r.result.ok else 'FAIL'} — {r.result.reason}")
        else:
            print("STATUS: running (call `finish` once the task is fully complete)")
        return

    raise SystemExit(f"unknown command: {cmd}")


if __name__ == "__main__":
    main()
