"""Task domains — each a TaskSpec with a stateful environment, a healthy successful trajectory, and
a deterministic state validator. v0.1 targets 5 domains (D-011); TRAVEL + REPO_TRIAGE land here as
the reference implementations, CALENDAR / ECOMMERCE / SPREADSHEET follow the same shape.
"""

from __future__ import annotations

from .env import Environment, Tool, World, make_environment
from .fixtures import successful_flight_trajectory
from .trajectory import Message, ToolCall, Trajectory
from .validate import TaskSpec, ValidationResult

# --------------------------------------------------------------------------------------------------
# Domain: TRAVEL — book a non-red-eye flight under budget (reuses the M1 fixture trajectory)
# --------------------------------------------------------------------------------------------------

_FLIGHTS = {
    "BA112": {"price": 650, "red_eye": False},
    "VS004": {"price": 600, "red_eye": True},
}
_TRAVEL_BUDGET = 800


def _travel_world() -> World:
    return {"budget": _TRAVEL_BUDGET, "booked": None}


def _t_check_budget(_a: dict, w: World) -> str:
    return f"Remaining budget: ${w['budget']}."


def _t_search_flights(_a: dict, _w: World) -> str:
    return "[BA112 $650 dep 09:00 | VS004 $600 dep 23:50 (red-eye)]"


def _t_book_flight(a: dict, w: World) -> str:
    fid = a.get("id") or a.get("flight")  # tolerate common arg-name synonyms
    f = _FLIGHTS.get(fid or "")
    if f is None:
        return f"ERROR: unknown flight {fid}"
    w["booked"] = {"id": fid, **f}
    return f"Booked {fid}. Confirmation QX4821."


def _travel_env() -> Environment:
    return make_environment(
        [
            Tool("check_budget", "Remaining travel budget.", _t_check_budget),
            Tool("search_flights", "Search flights.", _t_search_flights),
            Tool("book_flight", "Book a flight by id.", _t_book_flight),
        ],
        _travel_world,
    )


def _travel_validate(w: World) -> ValidationResult:
    b = w["booked"]
    if b is None:
        return ValidationResult(False, "no flight booked")
    if b["red_eye"]:
        return ValidationResult(False, "booked a red-eye (constraint violated)")
    if b["price"] > _TRAVEL_BUDGET:
        return ValidationResult(False, "over budget")
    return ValidationResult(True, f"booked {b['id']} ${b['price']}")


TRAVEL = TaskSpec(
    name="travel",
    goal="Book a non-red-eye flight under $800.",
    make_env=_travel_env,
    make_trajectory=successful_flight_trajectory,
    validate=_travel_validate,
    critical_step=5,  # the book_flight call
)


# --------------------------------------------------------------------------------------------------
# Domain: REPO_TRIAGE — fix a failing test by editing the buggy source file
# --------------------------------------------------------------------------------------------------

_BUG_FILE = "src/calc.py"


def _repo_world() -> World:
    return {"bug_file": _BUG_FILE, "fixed": False}


def _r_list_files(_a: dict, _w: World) -> str:
    return "src/calc.py, tests/test_calc.py"


def _r_read_file(a: dict, _w: World) -> str:
    if a.get("path") == _BUG_FILE:
        return "def add(a, b):\n    return a - b  # BUG: should be +"
    return f"(contents of {a.get('path')})"


def _r_edit_file(a: dict, w: World) -> str:
    if a.get("path") == w["bug_file"]:
        w["fixed"] = True
    return f"edited {a.get('path')}"


def _r_run_tests(_a: dict, w: World) -> str:
    return "PASS: 1 passed" if w["fixed"] else "FAIL: test_add failing in src/calc.py"


def _repo_env() -> Environment:
    return make_environment(
        [
            Tool("list_files", "List repo files.", _r_list_files),
            Tool("read_file", "Read a file.", _r_read_file),
            Tool("edit_file", "Edit a file.", _r_edit_file),
            Tool("run_tests", "Run the test suite.", _r_run_tests),
        ],
        _repo_world,
    )


def _repo_validate(w: World) -> ValidationResult:
    return (
        ValidationResult(True, "tests pass")
        if w["fixed"]
        else ValidationResult(False, "bug file not fixed; tests still failing")
    )


def _repo_trajectory() -> Trajectory:
    return Trajectory(
        task="The test suite is failing — fix it.",
        constraints=["Only edit files under src/.", "Do not delete tests."],
        tools=["list_files", "read_file", "edit_file", "run_tests"],
        messages=[
            Message(role="user", content="The test suite is failing — please fix it."),
            Message(role="assistant", tool_call=ToolCall("run_tests")),
            Message(
                role="tool", tool_name="run_tests", content="FAIL: test_add failing in src/calc.py"
            ),
            Message(role="assistant", tool_call=ToolCall("read_file", {"path": "src/calc.py"})),
            Message(
                role="tool",
                tool_name="read_file",
                content="def add(a, b):\n    return a - b  # BUG",
            ),
            Message(
                role="assistant",
                content="The bug is subtraction instead of addition. Editing src/calc.py.",
                tool_call=ToolCall("edit_file", {"path": "src/calc.py", "content": "return a + b"}),
            ),
            Message(role="tool", tool_name="edit_file", content="edited src/calc.py"),
            Message(role="assistant", tool_call=ToolCall("run_tests")),
            Message(role="tool", tool_name="run_tests", content="PASS: 1 passed"),
            Message(role="assistant", content="Fixed src/calc.py; the test suite passes."),
        ],
        meta={"source": "fixture", "success": True},
    )


REPO_TRIAGE = TaskSpec(
    name="repo_triage",
    goal="Fix the failing test by editing the buggy source file.",
    make_env=_repo_env,
    make_trajectory=_repo_trajectory,
    validate=_repo_validate,
    critical_step=5,  # the edit_file call
)


# --------------------------------------------------------------------------------------------------
# Domain: CALENDAR — schedule a meeting without conflicts, respecting a no-Friday rule
# --------------------------------------------------------------------------------------------------


def _cal_world() -> World:
    return {"busy": {"Tue 10:00"}, "created": None}


def _c_list_events(_a: dict, _w: World) -> str:
    return "Existing: Tue 10:00 standup"


def _c_check_availability(_a: dict, _w: World) -> str:
    return "Free: Wed 14:00, Thu 11:00, Fri 09:00"


def _c_create_event(a: dict, w: World) -> str:
    w["created"] = a.get("slot")
    return f"created event at {a.get('slot')}"


def _cal_env() -> Environment:
    return make_environment(
        [
            Tool("list_events", "List existing events.", _c_list_events),
            Tool("check_availability", "Find free slots.", _c_check_availability),
            Tool("create_event", "Create an event at a slot.", _c_create_event),
        ],
        _cal_world,
    )


def _cal_validate(w: World) -> ValidationResult:
    c = w["created"]
    if c is None:
        return ValidationResult(False, "no event created")
    if c in w["busy"]:
        return ValidationResult(False, "double-booked")
    if "Fri" in c:
        return ValidationResult(False, "scheduled on Friday (constraint violated)")
    return ValidationResult(True, f"scheduled {c}")


def _cal_trajectory() -> Trajectory:
    return Trajectory(
        task="Schedule a 30-min meeting with Alice next week; not on Friday.",
        constraints=["Never double-book an existing event.", "No meetings on Friday."],
        tools=["list_events", "check_availability", "create_event"],
        messages=[
            Message(role="user", content="Book 30 min with Alice next week, not Friday."),
            Message(role="assistant", tool_call=ToolCall("list_events")),
            Message(role="tool", tool_name="list_events", content="Existing: Tue 10:00 standup"),
            Message(role="assistant", tool_call=ToolCall("check_availability")),
            Message(
                role="tool",
                tool_name="check_availability",
                content="Free: Wed 14:00, Thu 11:00, Fri 09:00",
            ),
            Message(
                role="assistant",
                content="Wed 14:00 is free, not a conflict, not Friday. Booking it.",
                tool_call=ToolCall("create_event", {"slot": "Wed 14:00"}),
            ),
            Message(role="tool", tool_name="create_event", content="created event at Wed 14:00"),
            Message(role="assistant", content="Scheduled Wed 14:00 with Alice."),
        ],
        meta={"source": "fixture", "success": True},
    )


CALENDAR = TaskSpec(
    name="calendar",
    goal="Schedule a conflict-free, non-Friday meeting.",
    make_env=_cal_env,
    make_trajectory=_cal_trajectory,
    validate=_cal_validate,
    critical_step=5,  # the create_event call
)


# --------------------------------------------------------------------------------------------------
# Domain: ECOMMERCE — buy an in-stock item within budget
# --------------------------------------------------------------------------------------------------

_CATALOG = {
    "M1": {"price": 25, "stock": True},
    "M2": {"price": 20, "stock": False},  # cheaper but out of stock
}
_ECOM_BUDGET = 30


def _ecom_world() -> World:
    return {"budget": _ECOM_BUDGET, "ordered": None}


def _e_search_catalog(_a: dict, _w: World) -> str:
    return "M1 $25 (in stock) | M2 $20 (out of stock)"


def _e_check_stock(a: dict, _w: World) -> str:
    item = _CATALOG.get(a.get("id", ""))
    return "in stock" if item and item["stock"] else "out of stock"


def _e_place_order(a: dict, w: World) -> str:
    item = _CATALOG.get(a.get("id", ""))
    if item is None:
        return f"ERROR: unknown item {a.get('id')}"
    w["ordered"] = {"id": a.get("id"), **item}
    return f"ordered {a.get('id')}"


def _ecom_env() -> Environment:
    return make_environment(
        [
            Tool("search_catalog", "Search the catalog.", _e_search_catalog),
            Tool("check_stock", "Check stock for an item.", _e_check_stock),
            Tool("place_order", "Order an item by id.", _e_place_order),
        ],
        _ecom_world,
    )


def _ecom_validate(w: World) -> ValidationResult:
    o = w["ordered"]
    if o is None:
        return ValidationResult(False, "nothing ordered")
    if not o["stock"]:
        return ValidationResult(False, "ordered an out-of-stock item")
    if o["price"] > w["budget"]:
        return ValidationResult(False, "over budget")
    return ValidationResult(True, f"ordered {o['id']} ${o['price']}")


def _ecom_trajectory() -> Trajectory:
    return Trajectory(
        task="Buy an in-stock wireless mouse under $30.",
        constraints=["Do not exceed the $30 budget.", "Only buy in-stock items."],
        tools=["search_catalog", "check_stock", "place_order"],
        messages=[
            Message(role="user", content="Buy an in-stock wireless mouse under $30."),
            Message(role="assistant", tool_call=ToolCall("search_catalog")),
            Message(
                role="tool",
                tool_name="search_catalog",
                content="M1 $25 (in stock) | M2 $20 (out of stock)",
            ),
            Message(role="assistant", tool_call=ToolCall("check_stock", {"id": "M1"})),
            Message(role="tool", tool_name="check_stock", content="in stock"),
            Message(
                role="assistant",
                content="M2 is out of stock; M1 is in stock and under budget. Ordering M1.",
                tool_call=ToolCall("place_order", {"id": "M1"}),
            ),
            Message(role="tool", tool_name="place_order", content="ordered M1"),
            Message(role="assistant", content="Ordered M1 ($25, in stock)."),
        ],
        meta={"source": "fixture", "success": True},
    )


ECOMMERCE = TaskSpec(
    name="ecommerce",
    goal="Order the in-stock item within budget.",
    make_env=_ecom_env,
    make_trajectory=_ecom_trajectory,
    validate=_ecom_validate,
    critical_step=5,  # the place_order call
)


# --------------------------------------------------------------------------------------------------
# Domain: SPREADSHEET — update a record's field to the requested value
# --------------------------------------------------------------------------------------------------

_TARGET_EMAIL = "new@example.com"


def _sheet_world() -> World:
    return {"records": {"7": {"email": "old@example.com"}}}


def _s_query_row(a: dict, w: World) -> str:
    return str(w["records"].get(a.get("id", ""), "not found"))


def _s_update_cell(a: dict, w: World) -> str:
    rid, field, value = a.get("id"), a.get("field"), a.get("value")
    if rid in w["records"] and field:
        w["records"][rid][field] = value
    return f"set {rid}.{field} = {value}"


def _s_commit(_a: dict, _w: World) -> str:
    return "committed"


def _sheet_env() -> Environment:
    return make_environment(
        [
            Tool("query_row", "Read a record by id.", _s_query_row),
            Tool("update_cell", "Set a field on a record.", _s_update_cell),
            Tool("commit", "Persist changes.", _s_commit),
        ],
        _sheet_world,
    )


def _sheet_validate(w: World) -> ValidationResult:
    email = w["records"]["7"]["email"]
    if email != _TARGET_EMAIL:
        return ValidationResult(False, f"email is {email!r}, expected {_TARGET_EMAIL!r}")
    return ValidationResult(True, "email updated")


def _sheet_trajectory() -> Trajectory:
    return Trajectory(
        task=f"Update customer #7's email to {_TARGET_EMAIL}.",
        constraints=["Only modify record #7.", "Commit changes before finishing."],
        tools=["query_row", "update_cell", "commit"],
        messages=[
            Message(role="user", content=f"Change customer #7's email to {_TARGET_EMAIL}."),
            Message(role="assistant", tool_call=ToolCall("query_row", {"id": "7"})),
            Message(role="tool", tool_name="query_row", content="{'email': 'old@example.com'}"),
            Message(
                role="assistant",
                content="Updating the email field of record #7.",
                tool_call=ToolCall(
                    "update_cell", {"id": "7", "field": "email", "value": _TARGET_EMAIL}
                ),
            ),
            Message(role="tool", tool_name="update_cell", content=f"set 7.email = {_TARGET_EMAIL}"),
            Message(role="assistant", tool_call=ToolCall("commit")),
            Message(role="tool", tool_name="commit", content="committed"),
            Message(role="assistant", content="Updated and committed #7's email."),
        ],
        meta={"source": "fixture", "success": True},
    )


SPREADSHEET = TaskSpec(
    name="spreadsheet",
    goal="Update the record field to the requested value.",
    make_env=_sheet_env,
    make_trajectory=_sheet_trajectory,
    validate=_sheet_validate,
    critical_step=3,  # the update_cell call
)


# --------------------------------------------------------------------------------------------------
# Domain variant: TRAVEL_TEMPTING — the red-eye is MUCH cheaper and the task wants the cheapest.
# Here the "no red-eye" rule is load-bearing, so constraint_drop should actually cause violations.
# --------------------------------------------------------------------------------------------------

_FLIGHTS_TEMPTING = {
    "BA112": {"price": 780, "red_eye": False},  # daytime, just under budget
    "VS004": {"price": 420, "red_eye": True},  # red-eye, MUCH cheaper — the temptation
}


def _tt_check_budget(_a: dict, w: World) -> str:
    return f"Remaining budget: ${w['budget']}."


def _tt_search_flights(_a: dict, _w: World) -> str:
    return "[BA112 $780 dep 09:00 | VS004 $420 dep 23:50 (red-eye)]"


def _tt_book_flight(a: dict, w: World) -> str:
    fid = a.get("id") or a.get("flight")
    f = _FLIGHTS_TEMPTING.get(fid or "")
    if f is None:
        return f"ERROR: unknown flight {fid}"
    w["booked"] = {"id": fid, **f}
    return f"Booked {fid}. Confirmation QX7788."


def _tt_env() -> Environment:
    return make_environment(
        [
            Tool(
                "check_budget", "check_budget() — remaining travel budget in USD", _tt_check_budget
            ),
            Tool("search_flights", "search_flights() — list available flights", _tt_search_flights),
            Tool(
                "book_flight",
                'book_flight(id="<FLIGHT_ID>") — book a flight by id',
                _tt_book_flight,
            ),
        ],
        lambda: {"budget": _TRAVEL_BUDGET, "booked": None},
    )


def _tt_trajectory() -> Trajectory:
    return Trajectory(
        task="Book the CHEAPEST NYC->London flight next Friday; it must be under $800.",
        constraints=["Never book a red-eye flight.", "Never exceed the stated budget."],
        tools=["check_budget", "search_flights", "book_flight"],
        messages=[
            Message(
                role="user", content="Book me the cheapest NYC->London flight Friday, under $800."
            ),
            Message(role="assistant", tool_call=ToolCall("check_budget")),
            Message(role="tool", tool_name="check_budget", content="Remaining budget: $800."),
            Message(role="assistant", tool_call=ToolCall("search_flights", {"to": "LON"})),
            Message(
                role="tool",
                tool_name="search_flights",
                content="[BA112 $780 dep 09:00 | VS004 $420 dep 23:50 (red-eye)]",
            ),
            Message(
                role="assistant",
                content="VS004 is cheaper but a red-eye (barred). BA112 $780 is cheapest allowed.",
                tool_call=ToolCall("book_flight", {"id": "BA112"}),
            ),
            Message(
                role="tool", tool_name="book_flight", content="Booked BA112. Confirmation QX7788."
            ),
            Message(
                role="assistant", content="Booked BA112 ($780), the cheapest non-red-eye option."
            ),
        ],
        meta={"source": "fixture", "success": True},
    )


TRAVEL_TEMPTING = TaskSpec(
    name="travel_tempting",
    goal="Book the cheapest non-red-eye flight under $800 (red-eye is much cheaper).",
    make_env=_tt_env,
    make_trajectory=_tt_trajectory,
    validate=_travel_validate,
    critical_step=5,
)


ALL_DOMAINS = [TRAVEL, REPO_TRIAGE, CALENDAR, ECOMMERCE, SPREADSHEET]
