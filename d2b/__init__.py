"""debris-to-blame (d2b): controlled fault injection as causal ground truth for agent
failure attribution.

See PROJECT_PLAN.md for scope.
"""

# Registry of interactive multi-step domains: name -> {variants, per-domain observation injectors}.
# step.py drives any registered domain; new domains only need to register here.
from . import conference as _conference  # noqa: E402
from . import review as _review  # noqa: E402
from . import scheduling as _scheduling  # noqa: E402
from .agent import decision_to_messages, parse_decision, render_prefix
from .conference import (
    CONFERENCE_TRIP,
    CONFERENCE_VARIANTS,
    contradiction_injector,
    make_conference,
    sham_note_injector,
    staleness_injector,
)
from .domains import (
    ALL_DOMAINS,
    CALENDAR,
    ECOMMERCE,
    REPO_TRIAGE,
    SPREADSHEET,
    TRAVEL,
    TRAVEL_TEMPTING,
)
from .env import Environment, Tool, World, make_environment
from .faults import (
    Corruption,
    FaultRecord,
    FaultSite,
    FaultSpec,
    FaultType,
    inject,
    redact_for_attribution,
    sham_inject,
)
from .fixtures import successful_flight_trajectory
from .replay import Policy, evaluate, replay, replay_tail_policy, resume, scripted_policy
from .review import REVIEW_TASK, REVIEW_VARIANTS, make_review
from .rollout import Injector, Rollout, interactive_rollout, scripted_policy_fn
from .scheduling import SCHEDULING_TASK, SCHEDULING_VARIANTS, make_scheduling
from .tools import MockTool, ToolRegistry, demo_registry
from .trajectory import Message, ToolCall, Trajectory
from .validate import TaskSpec, ValidationResult

DOMAINS = {
    "conference": {
        "variants": CONFERENCE_VARIANTS,
        "staleness": _conference.staleness_injector,
        "contradiction": _conference.contradiction_injector,
        "sham": _conference.sham_note_injector,
        "debris": _conference.debris_injector,
        "misexec": _conference.misexec_injector,
        "arg_hints": (
            "latest_quote & book_flight take flight=<id>; book_hotel takes hotel=<id>; "
            "search_flights/search_hotels/file_expense_report/send_itinerary take no args."
        ),
    },
    "scheduling": {
        "variants": SCHEDULING_VARIANTS,
        "staleness": _scheduling.staleness_injector,
        "contradiction": _scheduling.contradiction_injector,
        "sham": _scheduling.sham_note_injector,
        "debris": _scheduling.debris_injector,
        "misexec": _scheduling.misexec_injector,
        "arg_hints": (
            "check_availability takes slot=<id> room=<id>; book_slot takes slot=<id>; "
            "book_room takes room=<id>; list_slots/list_rooms/send_invites/post_agenda: no args."
        ),
    },
    "review": {
        "variants": REVIEW_VARIANTS,
        "staleness": _review.staleness_injector,
        "contradiction": _review.contradiction_injector,
        "sham": _review.sham_note_injector,
        "debris": _review.debris_injector,
        "misexec": _review.misexec_injector,
        "arg_hints": (
            "check_ci & merge_pr take pr=<id>; "
            "list_prs/notify_author/close_ticket take no args."
        ),
    },
}

__version__ = "0.0.0"

__all__ = [
    # injection
    "Corruption",
    "FaultRecord",
    "FaultSite",
    "FaultSpec",
    "FaultType",
    "inject",
    "sham_inject",
    "redact_for_attribution",
    # trajectory
    "Message",
    "ToolCall",
    "Trajectory",
    "successful_flight_trajectory",
    # stateful env + domains + replay
    "Environment",
    "Tool",
    "World",
    "make_environment",
    "TaskSpec",
    "ValidationResult",
    "evaluate",
    "replay",
    "resume",
    "replay_tail_policy",
    "scripted_policy",
    "Policy",
    "render_prefix",
    "parse_decision",
    "decision_to_messages",
    "ALL_DOMAINS",
    "TRAVEL",
    "REPO_TRIAGE",
    "CALENDAR",
    "ECOMMERCE",
    "SPREADSHEET",
    "TRAVEL_TEMPTING",
    "CONFERENCE_TRIP",
    "CONFERENCE_VARIANTS",
    "make_conference",
    "SCHEDULING_TASK",
    "SCHEDULING_VARIANTS",
    "make_scheduling",
    "REVIEW_TASK",
    "REVIEW_VARIANTS",
    "make_review",
    "DOMAINS",
    # interactive rollout (multi-step, reacts to corrupted observations)
    "interactive_rollout",
    "Injector",
    "Rollout",
    "scripted_policy_fn",
    "staleness_injector",
    "contradiction_injector",
    "sham_note_injector",
    # legacy stateless demo tools (M1)
    "MockTool",
    "ToolRegistry",
    "demo_registry",
]
