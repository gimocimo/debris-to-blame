"""debris-to-blame (d2b): controlled fault injection as causal ground truth for agent
failure attribution.

See PROJECT_PLAN.md for scope.
"""

from .agent import decision_to_messages, parse_decision, render_prefix
from .conference import CONFERENCE_TRIP
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
from .tools import MockTool, ToolRegistry, demo_registry
from .trajectory import Message, ToolCall, Trajectory
from .validate import TaskSpec, ValidationResult

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
    # legacy stateless demo tools (M1)
    "MockTool",
    "ToolRegistry",
    "demo_registry",
]
