"""Stateful mock tool environment.

Unlike the M1 stateless demo tools, these tools READ AND WRITE a `World` (a plain dict), so a
domain's success can be judged on the resulting *state* — not on the model's prose (Codex audit:
"validate final state, not prose"). Deterministic: replaying the same tool calls yields the same
world, which keeps degradation/attribution/recovery cheap and reproducible.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

World = dict  # mutable domain state; JSON-friendly


@dataclass
class Tool:
    """A stateful tool: name, description, and fn(args, world) -> output (may mutate world)."""

    name: str
    description: str
    fn: Callable[[dict, World], str]

    def run(self, args: dict, world: World) -> str:
        return self.fn(args, world)


@dataclass
class Environment:
    """A registry of stateful tools plus a factory for the initial world."""

    tools: dict[str, Tool]
    world_factory: Callable[[], World]

    def initial_world(self) -> World:
        return self.world_factory()

    def names(self) -> list[str]:
        return list(self.tools)

    def run(self, name: str, args: dict, world: World) -> str:
        tool = self.tools.get(name)
        if tool is None:
            return f"ERROR: unknown tool '{name}'"
        return tool.run(args, world)


def make_environment(tools: list[Tool], world_factory: Callable[[], World]) -> Environment:
    return Environment({t.name: t for t in tools}, world_factory)
