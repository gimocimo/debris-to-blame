"""Trajectory data model — the object faults are injected into.

An agent's "memory" is just a list of messages re-sent to the model each turn (PROJECT_PLAN §5).
A Trajectory captures that list plus the two things some faults act on but that don't live inside
the message stream: the standing `constraints` (system rules) and the available `tools` (schemas).

Pure stdlib on purpose — the whole M1 machinery runs with no dependencies and no model calls.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ToolCall:
    """A tool invocation emitted by an assistant step."""

    name: str
    args: dict = field(default_factory=dict)


@dataclass
class Message:
    """One turn in the trajectory.

    role: "system" | "user" | "assistant" | "tool".
    content:   free text (system/user/assistant-text/tool-result payload).
    tool_call: set on assistant steps that call a tool.
    tool_name: set on "tool" messages (which tool produced this result).
    injected:  None for original messages; the fault-type string if this message was injected.
    """

    role: str
    content: str | None = None
    tool_call: ToolCall | None = None
    tool_name: str | None = None
    injected: str | None = None

    def to_dict(self) -> dict:
        d: dict = {"role": self.role}
        if self.content is not None:
            d["content"] = self.content
        if self.tool_call is not None:
            d["tool_call"] = {"name": self.tool_call.name, "args": self.tool_call.args}
        if self.tool_name is not None:
            d["tool_name"] = self.tool_name
        if self.injected is not None:
            d["injected"] = self.injected
        return d

    @staticmethod
    def from_dict(d: dict) -> Message:
        tc = d.get("tool_call")
        return Message(
            role=d["role"],
            content=d.get("content"),
            tool_call=ToolCall(tc["name"], tc.get("args", {})) if tc else None,
            tool_name=d.get("tool_name"),
            injected=d.get("injected"),
        )


@dataclass
class Trajectory:
    """A full agent run. `constraints` and `tools` are the loci for constraint_drop /
    tool_forgetting; `messages` is the locus for the insert/modify faults. `meta` records
    provenance and, once a fault is injected, the FaultSpec that produced this (corrupted) copy.
    """

    task: str
    messages: list[Message] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)
    tools: list[str] = field(default_factory=list)
    meta: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "task": self.task,
            "constraints": list(self.constraints),
            "tools": list(self.tools),
            "messages": [m.to_dict() for m in self.messages],
            "meta": self.meta,
        }

    @staticmethod
    def from_dict(d: dict) -> Trajectory:
        return Trajectory(
            task=d["task"],
            messages=[Message.from_dict(m) for m in d.get("messages", [])],
            constraints=list(d.get("constraints", [])),
            tools=list(d.get("tools", [])),
            meta=dict(d.get("meta", {})),
        )

    def save(self, path: str | Path) -> None:
        Path(path).write_text(json.dumps(self.to_dict(), indent=2))

    @staticmethod
    def load(path: str | Path) -> Trajectory:
        return Trajectory.from_dict(json.loads(Path(path).read_text()))
