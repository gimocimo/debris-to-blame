"""Interactive (ReAct-style) rollout — the agent sees each tool result before its next call.

Single-shot planning cannot test faults where the agent should REACT to a corrupted intermediate
tool output (staleness, contradiction). This loop fixes that (Codex review blocker 4):

    render transcript -> policy returns ONE tool call -> env executes it (updates WORLD = truth)
    -> an Injector may CORRUPT the observation shown to the agent -> append -> repeat -> validate.

The WORLD is always ground truth; the injector only changes what the agent *sees*. So a stale quote
misleads the agent while the validator still judges the true state — which is exactly how staleness
should bite. `parse_fail` is a first-class outcome, not a silent drop.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from .trajectory import Message, ToolCall, Trajectory
from .validate import TaskSpec, ValidationResult

# A policy sees (transcript, constraints, tools) and returns ONE decision:
#   {"tool": name, "args": {...}} | {"finish": True} | None (a parse failure).
Policy = Callable[[list[Message], list[str], list[str]], dict | None]


@dataclass
class Injector:
    """Corrupts what the agent SEES (and, for misexecution, what the world DOES).

    `transform` corrupts the observation shown to the agent; the world stays truth.
    `rewrite_args` (optional, MISEXECUTION faults) rewrites the call's args BEFORE the env executes
    — the world truthfully records what was *actually* done, while `transform` shows the agent a
    success message for what it *asked* for. The validator still judges the true world state.
    """

    tool: str
    transform: Callable[[str, dict, str], str]  # (tool, ORIGINAL args, true_result) -> shown
    nth: int = 0  # 1-based call index to corrupt; 0 = every call to `tool`
    rewrite_args: Callable[[str, dict], dict] | None = None  # (tool, args) -> executed args


@dataclass
class Rollout:
    world: dict
    transcript: list[Message]
    status: str  # "finished" | "max_steps" | "parse_fail"
    result: ValidationResult
    steps: int


def interactive_rollout(
    task: TaskSpec,
    policy: Policy,
    setup: Trajectory,
    *,
    injectors: tuple[Injector, ...] = (),
    max_steps: int = 14,
) -> Rollout:
    """Run the agent live against a fresh env, corrupting observations per `injectors`, then check.

    `setup` supplies the constraints, available tools, and opening user message the agent sees (a
    corrupted setup — e.g. constraint_drop / tool_forgetting — is applied before calling this).
    """
    env = task.make_env()
    world = env.initial_world()
    user_msg = next((m.content for m in setup.messages if m.role == "user"), setup.task)
    transcript: list[Message] = [Message(role="user", content=user_msg)]
    counts: dict[str, int] = {}
    status = "max_steps"

    for _ in range(max_steps):
        decision = policy(transcript, setup.constraints, setup.tools)
        if not isinstance(decision, dict):  # None or a malformed (non-dict) decision
            status = "parse_fail"
            break
        if decision.get("finish"):
            status = "finished"
            break
        tool = decision.get("tool")
        args = decision.get("args") or {}
        if not tool:
            status = "parse_fail"
            break

        if tool not in setup.tools:  # tool_forgetting / hallucinated tool: not available
            shown = f"ERROR: tool '{tool}' is not available."
            true_result = shown
        else:
            nth = counts.get(tool, 0) + 1
            matching = [i for i in injectors if i.tool == tool and i.nth in (0, nth)]
            exec_args = args
            for inj in matching:  # misexecution: the world executes something else
                if inj.rewrite_args is not None:
                    exec_args = inj.rewrite_args(tool, exec_args)
            true_result = env.run(tool, exec_args, world)
            counts[tool] = nth
            shown = true_result
            for inj in matching:
                shown = inj.transform(tool, args, shown)  # args = what the agent ASKED for
        marker = "obs" if (tool in setup.tools and shown != true_result) else None
        transcript.append(Message(role="assistant", tool_call=ToolCall(tool, args)))
        transcript.append(Message(role="tool", tool_name=tool, content=shown, injected=marker))

    return Rollout(world, transcript, status, task.validate(world), len(transcript) // 2)


def scripted_policy_fn(decisions: list[dict]) -> Policy:
    """A deterministic oracle policy: replay `decisions` in order, then finish. For tests."""
    seq = list(decisions)

    def _policy(_transcript, _constraints, _tools):
        return seq.pop(0) if seq else {"finish": True}

    return _policy
