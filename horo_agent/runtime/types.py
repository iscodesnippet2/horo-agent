"""Stable runtime DTOs shared by WebUI, Python SDK, and future HTTP API."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class RunRequest:
    """Request to start one agent turn.

    The shape intentionally mirrors the existing WebUI adapter request so Phase 1
    can adopt it without changing the hot path. Future SDK fields should be added
    as optional explicit context instead of requiring process-global env state.
    """

    session_id: str
    message: str
    attachments: list[dict[str, Any]] = field(default_factory=list)
    workspace: str | None = None
    profile: str | None = None
    provider: str | None = None
    model: str | None = None
    toolsets: list[str] = field(default_factory=list)
    source: str = "sdk"
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RunHandle:
    """Handle returned immediately after a runtime accepts a run."""

    run_id: str
    session_id: str
    stream_id: str
    status: str = "started"
    started_at: float | None = None
    cursor: str | None = None
    active_controls: list[str] = field(default_factory=list)
    payload: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RunEvent:
    """Canonical live event emitted by an agent runtime."""

    type: str
    payload: dict[str, Any] = field(default_factory=dict)
    run_id: str | None = None
    event_id: str | None = None
    created_at: float | None = None
    seq: int | None = None

    def to_legacy_dict(self) -> dict[str, Any]:
        data = {
            "type": self.type,
            "data": dict(self.payload),
        }
        if self.run_id is not None:
            data["run_id"] = self.run_id
        if self.event_id is not None:
            data["event_id"] = self.event_id
        if self.created_at is not None:
            data["created_at"] = self.created_at
        if self.seq is not None:
            data["seq"] = self.seq
        return data


@dataclass(frozen=True)
class RunEventStream:
    run_id: str
    events: list[dict[str, Any]] = field(default_factory=list)
    cursor: str | None = None
    last_event_id: str | None = None


@dataclass(frozen=True)
class RunStatus:
    run_id: str
    session_id: str | None = None
    status: str = "unknown"
    last_event_id: str | None = None
    terminal_state: str | None = None
    active_controls: list[str] = field(default_factory=list)
    pending_approval_id: str | None = None
    pending_clarify_id: str | None = None


@dataclass(frozen=True, eq=True, unsafe_hash=False)
class ControlResult:
    """Result for runtime control operations.

    ``payload`` deliberately keeps the dataclass unhashable; callers may attach
    nested dict/list response details without surprising hash behavior.
    """

    accepted: bool
    status: str = "accepted"
    event_id: str | None = None
    safe_message: str | None = None
    payload: dict[str, Any] = field(default_factory=dict)


StartRunRequest = RunRequest
RunStartResult = RunHandle
