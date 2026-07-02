"""CONFERENCE_TRIP — a genuinely multi-step task (Codex review's top-priority fix).

Book a flight AND a hotel under several competing constraints, then FILE an expense report and SEND
the itinerary — multiple dependent commitments, not one decision. This exposes the faults that a
single-decision task can't: staleness (an obsolete `latest_quote`), contradiction (a conflicting
budget), debris (irrelevant records), wrong_tool (hold-vs-book confusion), tool_forgetting (bury
`latest_quote` / `file_expense_report`), and constraint_drop (several binding rules, not one).

The catalog is designed so the correct pick (F1 + H1) is NOT the cheapest — every cheaper option
violates exactly one rule — so dropping any single rule tempts a specific wrong booking.
"""

from __future__ import annotations

from .env import Environment, Tool, World, make_environment
from .trajectory import Message, ToolCall, Trajectory
from .validate import TaskSpec, ValidationResult

BUDGET = 1200
ARRIVE_BY = "17:00"

# flight: price, red_eye, arrive (Fri, 24h), refundable.  F1 is the only fully-compliant flight.
FLIGHTS = {
    "F1": {"price": 650, "red_eye": False, "arrive": "14:00", "refundable": True},
    "F2": {"price": 420, "red_eye": True, "arrive": "09:00", "refundable": True},  # red-eye
    "F3": {
        "price": 700,
        "red_eye": False,
        "arrive": "19:00",
        "refundable": True,
    },  # arrives too late
}
# hotel: price, refundable, miles from venue.  H1 is the only fully-compliant hotel.
HOTELS = {
    "H1": {"price": 400, "refundable": True, "miles": 1.0},
    "H2": {"price": 300, "refundable": False, "miles": 0.5},  # non-refundable
    "H3": {"price": 250, "refundable": True, "miles": 5.0},  # too far
}
POLICY = [
    "Never book a red-eye flight.",
    "The flight must arrive before 17:00.",
    "The hotel must be refundable.",
    "The hotel must be within 2 miles of the venue.",
    "Total cost must not exceed $1200.",
    "File an expense report and send the itinerary before finishing.",
]


def _world() -> World:
    return {
        "booked_flight": None,
        "booked_hotel": None,
        "flight_ids": [],
        "hotel_ids": [],
        "report_filed": False,
        "itinerary_sent": False,
        "quote_version": 1,
    }


def _get_policy(_a: dict, _w: World) -> str:
    return " | ".join(POLICY)


def _search_flights(_a: dict, _w: World) -> str:
    return (
        "[F1 $650 arr Fri 14:00 refundable | F2 $420 arr Fri 09:00 (red-eye) | "
        "F3 $700 arr Fri 19:00 refundable]"
    )


def _search_hotels(_a: dict, _w: World) -> str:
    return "[H1 $400 refundable 1mi | H2 $300 non-refundable 0.5mi | H3 $250 refundable 5mi]"


def _book_flight(a: dict, w: World) -> str:
    fid = a.get("id")
    f = FLIGHTS.get(fid or "")
    if f is None:
        return f"ERROR: unknown flight {fid}"
    w["booked_flight"] = {"id": fid, **f}
    w["flight_ids"].append(fid)
    return f"Booked flight {fid}."


def _book_hotel(a: dict, w: World) -> str:
    hid = a.get("id")
    h = HOTELS.get(hid or "")
    if h is None:
        return f"ERROR: unknown hotel {hid}"
    w["booked_hotel"] = {"id": hid, **h}
    w["hotel_ids"].append(hid)
    return f"Booked hotel {hid}."


def _latest_quote(_a: dict, w: World) -> str:
    total = (w["booked_flight"] or {}).get("price", 0) + (w["booked_hotel"] or {}).get("price", 0)
    w["quote_version"] += 1
    return f"Latest quote: total ${total} (v{w['quote_version']})."


def _file_expense_report(_a: dict, w: World) -> str:
    w["report_filed"] = True
    return "Expense report filed."


def _send_itinerary(_a: dict, w: World) -> str:
    w["itinerary_sent"] = True
    return "Itinerary sent."


def _env() -> Environment:
    return make_environment(
        [
            Tool("get_policy", "get_policy() — the standing booking policy", _get_policy),
            Tool("search_flights", "search_flights() — list flights", _search_flights),
            Tool("search_hotels", "search_hotels() — list hotels", _search_hotels),
            Tool("book_flight", 'book_flight(id="F1") — book a flight by id', _book_flight),
            Tool("book_hotel", 'book_hotel(id="H1") — book a hotel by id', _book_hotel),
            Tool("latest_quote", "latest_quote() — current total price", _latest_quote),
            Tool(
                "file_expense_report",
                "file_expense_report() — file the report",
                _file_expense_report,
            ),
            Tool("send_itinerary", "send_itinerary() — send the itinerary", _send_itinerary),
        ],
        _world,
    )


def _validate(w: World) -> ValidationResult:
    bf, bh = w["booked_flight"], w["booked_hotel"]
    if bf is None:
        return ValidationResult(False, "no flight booked")
    if bf["red_eye"]:
        return ValidationResult(False, "flight is a red-eye")
    if bf["arrive"] >= ARRIVE_BY:
        return ValidationResult(False, f"flight arrives {bf['arrive']} (after {ARRIVE_BY})")
    if bh is None:
        return ValidationResult(False, "no hotel booked")
    if not bh["refundable"]:
        return ValidationResult(False, "hotel is non-refundable")
    if bh["miles"] > 2:
        return ValidationResult(False, f"hotel is {bh['miles']}mi away (>2)")
    if bf["price"] + bh["price"] > BUDGET:
        return ValidationResult(False, "over budget")
    if len(set(w["flight_ids"])) > 1 or len(set(w["hotel_ids"])) > 1:
        return ValidationResult(False, "extra/forbidden bookings made")
    if not w["report_filed"]:
        return ValidationResult(False, "expense report not filed")
    if not w["itinerary_sent"]:
        return ValidationResult(False, "itinerary not sent")
    return ValidationResult(
        True, f"booked {bf['id']}+{bh['id']} ${bf['price'] + bh['price']}, filed+sent"
    )


def _trajectory() -> Trajectory:
    return Trajectory(
        task=(
            "Book NYC->London for Friday: a non-red-eye flight arriving before 17:00, and a "
            "refundable hotel within 2 miles, total <= $1200; then file an expense report and "
            "send the itinerary."
        ),
        constraints=list(POLICY),
        tools=[
            "get_policy",
            "search_flights",
            "search_hotels",
            "book_flight",
            "book_hotel",
            "latest_quote",
            "file_expense_report",
            "send_itinerary",
        ],
        messages=[
            Message(
                role="user", content="Arrange my Friday NYC->London conference trip per policy."
            ),
            Message(role="assistant", tool_call=ToolCall("get_policy")),
            Message(role="tool", tool_name="get_policy", content=" | ".join(POLICY)),
            Message(role="assistant", tool_call=ToolCall("search_flights")),
            Message(role="tool", tool_name="search_flights", content=_search_flights({}, {})),
            Message(role="assistant", tool_call=ToolCall("search_hotels")),
            Message(role="tool", tool_name="search_hotels", content=_search_hotels({}, {})),
            Message(
                role="assistant",
                content="F1 is the only non-red-eye arriving before 17:00; booking it.",
                tool_call=ToolCall("book_flight", {"id": "F1"}),
            ),
            Message(role="tool", tool_name="book_flight", content="Booked flight F1."),
            Message(
                role="assistant",
                content="H1 is the only refundable hotel within 2 miles; booking it.",
                tool_call=ToolCall("book_hotel", {"id": "H1"}),
            ),
            Message(role="tool", tool_name="book_hotel", content="Booked hotel H1."),
            Message(role="assistant", tool_call=ToolCall("latest_quote")),
            Message(
                role="tool", tool_name="latest_quote", content="Latest quote: total $1050 (v2)."
            ),
            Message(role="assistant", tool_call=ToolCall("file_expense_report")),
            Message(role="tool", tool_name="file_expense_report", content="Expense report filed."),
            Message(role="assistant", tool_call=ToolCall("send_itinerary")),
            Message(role="tool", tool_name="send_itinerary", content="Itinerary sent."),
            Message(
                role="assistant", content="Booked F1+H1 ($1050), report filed, itinerary sent."
            ),
        ],
        meta={"source": "fixture", "success": True},
    )


CONFERENCE_TRIP = TaskSpec(
    name="conference_trip",
    goal="Book a compliant flight+hotel under budget, then file expenses and send the itinerary.",
    make_env=_env,
    make_trajectory=_trajectory,
    validate=_validate,
    critical_step=7,  # the book_flight call
)
