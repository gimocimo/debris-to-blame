"""Hand-authored fixture trajectory — a clean, successful flight-booking run.

Deliberately small and legible: it respects both constraints (no red-eye, under budget) and books
the correct flight. Every fault type has something meaningful to corrupt here. Real trajectories
(M2) are generated subscription-native; this fixture lets the M1 machinery + demo run with zero
model calls.
"""

from __future__ import annotations

from .trajectory import Message, ToolCall, Trajectory


def successful_flight_trajectory() -> Trajectory:
    return Trajectory(
        task="Book a flight NYC->London next Friday, under $800.",
        constraints=[
            "Never book a red-eye flight.",
            "Never exceed the stated budget.",
        ],
        tools=["check_budget", "search_flights", "book_flight"],
        messages=[
            Message(role="user", content="Book me NYC->London next Friday, under $800."),
            Message(role="assistant", tool_call=ToolCall("check_budget")),
            Message(role="tool", tool_name="check_budget", content="Remaining budget: $800."),
            Message(role="assistant", tool_call=ToolCall("search_flights", {"to": "LON"})),
            Message(
                role="tool",
                tool_name="search_flights",
                content="[BA112 $650 dep 09:00 | VS004 $600 dep 23:50 (red-eye)]",
            ),
            Message(
                role="assistant",
                content="BA112 is $650, 09:00 (not a red-eye), within the $800 budget. Booking it.",
                tool_call=ToolCall("book_flight", {"id": "BA112"}),
            ),
            Message(
                role="tool", tool_name="book_flight", content="Booked BA112. Confirmation QX4821."
            ),
            Message(
                role="assistant",
                content="Done — booked BA112, $650, 09:00 (not a red-eye), within budget.",
            ),
        ],
        meta={"source": "fixture", "success": True},
    )
