"""SDK-first runtime interface for embedded and future remote Horo Agent use."""

from __future__ import annotations

from .embedded import EmbeddedRuntime
from .interface import EventSink, Runtime
from .types import (
    ControlResult,
    RunEvent,
    RunEventStream,
    RunHandle,
    RunRequest,
    RunStartResult,
    RunStatus,
    StartRunRequest,
)

__all__ = [
    "ControlResult",
    "EmbeddedRuntime",
    "EventSink",
    "RunEvent",
    "RunEventStream",
    "RunHandle",
    "RunRequest",
    "RunStartResult",
    "RunStatus",
    "Runtime",
    "StartRunRequest",
]
