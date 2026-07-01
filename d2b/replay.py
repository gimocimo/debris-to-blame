"""Deterministic replay + the resume-live interface.

`replay` executes a trajectory's literal tool calls against a fresh world → final state. `evaluate`
validates that state. This is enough to catch *call-changing* faults (e.g. wrong_tool) statically.

*Context-driven* faults (debris, staleness, contradiction, constraint_drop, tool_forgetting) don't
change the recorded calls, so they only bite when a MODEL re-decides — that is `resume`, whose
`Policy` is wired to a subscription-native subagent in M2. Here we ship the interface plus a
deterministic oracle policy so the resume harness itself is testable at $0.
"""

from __future__ import annotations

from collections.abc import Callable

from .env import Environment, World
from .trajectory import Message, Trajectory
from .validate import TaskSpec, ValidationResult

# A policy sees the prefix + live environment and returns the continuation messages (M2: a model).
Policy = Callable[[Trajectory, Environment], list[Message]]


def _apply(env: Environment, world: World, messages: list[Message]) -> None:
    for m in messages:
        if m.role == "assistant" and m.tool_call is not None:
            env.run(m.tool_call.name, m.tool_call.args, world)


def replay(traj: Trajectory, env: Environment) -> World:
    """Execute the trajectory's literal tool calls against a fresh world; return the final state."""
    world = env.initial_world()
    _apply(env, world, traj.messages)
    return world


def evaluate(task: TaskSpec, traj: Trajectory) -> ValidationResult:
    """Replay `traj` in the task's environment and validate the resulting state."""
    return task.validate(replay(traj, task.make_env()))


def resume(task: TaskSpec, traj: Trajectory, cut: int, policy: Policy) -> ValidationResult:
    """Resume-live: run the prefix [:cut], let `policy` continue, then validate the final state."""
    env = task.make_env()
    world = env.initial_world()
    prefix = list(traj.messages[:cut])
    _apply(env, world, prefix)
    prefix_traj = Trajectory(
        task=traj.task, messages=prefix, constraints=traj.constraints, tools=traj.tools
    )
    _apply(env, world, policy(prefix_traj, env))
    return task.validate(world)


def scripted_policy(continuation: list[Message]) -> Policy:
    """A policy that plays back a recorded continuation (e.g. a model's captured tool calls)."""

    tail = list(continuation)

    def _policy(_prefix: Trajectory, _env: Environment) -> list[Message]:
        return tail

    return _policy


def replay_tail_policy(original: Trajectory, cut: int) -> Policy:
    """A deterministic oracle policy: replay the original trajectory's messages after `cut`.

    Used to test the resume harness structurally; M2 replaces it with a model-backed policy.
    """

    tail = list(original.messages[cut:])

    def _policy(_prefix: Trajectory, _env: Environment) -> list[Message]:
        return tail

    return _policy
