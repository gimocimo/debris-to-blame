"""debris-to-blame (d2b): controlled fault injection as causal ground truth for agent
failure attribution.

See PROJECT_PLAN.md for scope.
"""

from .domains import ALL_DOMAINS, CALENDAR, ECOMMERCE, REPO_TRIAGE, SPREADSHEET, TRAVEL
from .env import Environment, Tool, World, make_environment
from .faults import (
    Corruption,
    FaultRecord,
    FaultSite,
    FaultSpec,
    FaultType,
    inject,
    redact_for_attribution,
)
from .fixtures import successful_flight_trajectory
from .replay import Policy, evaluate, replay, replay_tail_policy, resume
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
    "Policy",
    "ALL_DOMAINS",
    "TRAVEL",
    "REPO_TRIAGE",
    "CALENDAR",
    "ECOMMERCE",
    "SPREADSHEET",
    # legacy stateless demo tools (M1)
    "MockTool",
    "ToolRegistry",
    "demo_registry",
]
