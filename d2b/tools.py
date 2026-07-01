"""Mock deterministic tool environment.

Tool calls cost $0 and return fixed outputs, so trajectories are perfectly reproducible and
`resume-live` (M2) is cheap and safe (no real bookings, no flaky APIs). M1 only needs the registry
to (a) ground the fixture trajectory and (b) supply plausible-but-wrong tools for the wrong_tool
fault and decoy schemas for tool_forgetting.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass


@dataclass
class MockTool:
    """A deterministic tool: name, one-line description, and a pure fn from args to a string."""

    name: str
    description: str
    fn: Callable[[dict], str]

    def run(self, args: dict) -> str:
        return self.fn(args)


class ToolRegistry:
    def __init__(self, tools: list[MockTool] | None = None):
        self._tools: dict[str, MockTool] = {t.name: t for t in (tools or [])}

    def add(self, tool: MockTool) -> None:
        self._tools[tool.name] = tool

    def get(self, name: str) -> MockTool | None:
        return self._tools.get(name)

    def names(self) -> list[str]:
        return list(self._tools)

    def run(self, name: str, args: dict) -> str:
        tool = self._tools.get(name)
        if tool is None:
            return f"ERROR: unknown tool '{name}'"
        return tool.run(args)


def demo_registry() -> ToolRegistry:
    """A tiny flight-booking environment used by the fixture trajectory and the demo."""

    return ToolRegistry(
        [
            MockTool(
                "search_flights",
                "Search flights for a route and date.",
                lambda a: "[BA112 $650 dep 09:00 | VS004 $600 dep 23:50 (red-eye)]",
            ),
            MockTool(
                "book_flight",
                "Book a flight by its id.",
                lambda a: f"Booked {a.get('id', '?')}. Confirmation QX4821.",
            ),
            MockTool(
                "check_budget",
                "Return the remaining travel budget in USD.",
                lambda a: "Remaining budget: $800.",
            ),
            # Plausible-but-wrong neighbours, used by the wrong_tool fault:
            MockTool("check_weather", "Get the weather forecast.", lambda a: "Sunny, 18C."),
            MockTool("search_hotels", "Search hotels.", lambda a: "[Hilton $210/night]"),
        ]
    )


def decoy_tool_names(n: int) -> list[str]:
    """Deterministic decoy tool schemas for the tool_forgetting fault (buries the real tool)."""
    return [f"legacy_util_{i:02d}" for i in range(n)]
