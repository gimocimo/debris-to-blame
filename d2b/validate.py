"""TaskSpec + deterministic validators.

A `TaskSpec` bundles a domain: how to build its stateful environment, its healthy successful
trajectory, a deterministic `validate(world) -> ValidationResult`, and the `critical_step` — the
message index whose tool call is load-bearing for success (a natural high-damage injection site).
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from .env import Environment, World
from .trajectory import Trajectory


@dataclass
class ValidationResult:
    ok: bool
    reason: str = ""


@dataclass
class TaskSpec:
    name: str
    goal: str
    make_env: Callable[[], Environment]
    make_trajectory: Callable[[], Trajectory]
    validate: Callable[[World], ValidationResult]
    critical_step: int  # message index of the tool call the task hinges on
    # Optional domain-aware sham plan, e.g. {"constraint_drop_index": 7} = the inert (non-binding)
    # rule to drop for a constraint_drop sham. The trajectory also stamps its meta.
    sham_plan: dict | None = None
