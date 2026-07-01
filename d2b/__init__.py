"""debris-to-blame (d2b): controlled fault injection as causal ground truth for agent
failure attribution.

See PROJECT_PLAN.md for scope.
"""

from .faults import FaultSpec, FaultType, inject
from .fixtures import successful_flight_trajectory
from .tools import MockTool, ToolRegistry, demo_registry
from .trajectory import Message, ToolCall, Trajectory

__version__ = "0.0.0"

__all__ = [
    "FaultSpec",
    "FaultType",
    "inject",
    "successful_flight_trajectory",
    "MockTool",
    "ToolRegistry",
    "demo_registry",
    "Message",
    "ToolCall",
    "Trajectory",
]
