"""Model-backed resume: render the agent-under-test's prompt, parse its decision.

The agent-under-test sees ONLY the redacted `.public` prefix (leakage-free) — never the fault or the
label. We render that prefix to a prompt; the model (a subscription-native subagent, orchestrated
outside Python) returns its next tool call as JSON; we turn that into continuation Messages the
replay harness executes against the stateful env. This is how real inference enters the otherwise
deterministic pipeline at $0.
"""

from __future__ import annotations

import json

from .trajectory import Message, ToolCall, Trajectory


def render_prefix(traj: Trajectory, cut: int) -> str:
    """Render the redacted prefix [:cut] as the prompt the agent-under-test sees."""
    lines = [f"TASK: {traj.task}", ""]
    if traj.constraints:
        lines.append("STANDING RULES:")
        lines += [f"  - {c}" for c in traj.constraints]
        lines.append("")
    lines.append(f"AVAILABLE TOOLS: {', '.join(traj.tools)}")
    lines.append("")
    lines.append("CONVERSATION SO FAR:")
    for m in traj.messages[:cut]:
        if m.tool_call is not None:
            lines.append(f"  assistant -> CALL {m.tool_call.name}({m.tool_call.args})")
        elif m.role == "tool":
            lines.append(f"  tool [{m.tool_name}]: {m.content}")
        else:
            lines.append(f"  {m.role}: {m.content}")
    return "\n".join(lines)


def parse_decision(text: str) -> dict:
    """Extract the first JSON object from a model response (tolerant of surrounding prose)."""
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("no JSON object found in model response")
    return json.loads(text[start : end + 1])


def decision_to_messages(decision: dict) -> list[Message]:
    """Turn a decision {"tool","args"} (or {"calls":[...]}) into continuation Messages."""
    calls = decision.get("calls") or [decision]
    return [
        Message(role="assistant", tool_call=ToolCall(c["tool"], c.get("args", {}))) for c in calls
    ]
