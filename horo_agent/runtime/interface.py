"""Runtime protocols for SDK, embedded WebUI, and future HTTP wrappers."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import Protocol

from .types import ControlResult, RunEvent, RunHandle, RunRequest, RunStatus

EventSink = Callable[[RunEvent], None]


class Runtime(Protocol):
    """Small, performance-oriented runtime contract.

    Embedded callers can pass an ``EventSink`` so live token events move directly
    from the agent callback to the UI queue. Durable journals and HTTP replay can
    wrap this protocol later, but they are not required on the hot path.
    """

    def run(self, request: RunRequest, *, event_sink: EventSink | None = None) -> dict: ...
    def start_run(self, request: RunRequest) -> RunHandle: ...
    def events(self, run_id: str, cursor: str | None = None) -> Iterable[RunEvent]: ...
    def status(self, run_id: str) -> RunStatus: ...
    def cancel(self, run_id: str) -> ControlResult: ...
    def respond_approval(self, run_id: str, approval_id: str, choice: str) -> ControlResult: ...
    def respond_clarify(self, run_id: str, clarify_id: str, response: str) -> ControlResult: ...
    def queue_message(self, run_id: str, message: str, mode: str = "queue") -> ControlResult: ...
