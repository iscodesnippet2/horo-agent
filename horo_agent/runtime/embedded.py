"""Embedded runtime facade over the existing ``AIAgent`` conversation API."""

from __future__ import annotations

import time
import uuid
from collections.abc import Callable, Iterable
from typing import Any

from .interface import EventSink
from .types import ControlResult, RunEvent, RunHandle, RunRequest, RunStatus


class EmbeddedRuntime:
    """Thin SDK facade for in-process agent execution.

    Phase 1 keeps this deliberately small: it wraps an injected agent factory and
    forwards to ``AIAgent.run_conversation`` without changing the agent loop. The
    optional event sink is callback-first to avoid putting a journal/replay layer
    on the live token path.
    """

    def __init__(self, *, agent_factory: Callable[[RunRequest], Any] | None = None):
        self._agent_factory = agent_factory
        self._runs: dict[str, RunStatus] = {}

    def run(self, request: RunRequest, *, event_sink: EventSink | None = None) -> dict:
        run_id = str(request.metadata.get("run_id") or uuid.uuid4().hex)
        self._runs[run_id] = RunStatus(
            run_id=run_id,
            session_id=request.session_id,
            status="running",
            active_controls=["cancel"],
        )
        self._emit(event_sink, RunEvent("run.started", {"session_id": request.session_id}, run_id=run_id))
        try:
            agent = self._build_agent(request)

            def _stream_callback(delta: str) -> None:
                self._emit(event_sink, RunEvent("message.delta", {"text": delta}, run_id=run_id))

            kwargs = {
                "user_message": request.message,
                "conversation_history": list(request.metadata.get("conversation_history") or []),
                "task_id": request.session_id,
                "stream_callback": _stream_callback if event_sink is not None else None,
            }
            system_message = request.metadata.get("system_message")
            if system_message is not None:
                kwargs["system_message"] = system_message
            persist_user_message = request.metadata.get("persist_user_message")
            if persist_user_message is not None:
                kwargs["persist_user_message"] = persist_user_message

            result = agent.run_conversation(**kwargs)
            self._runs[run_id] = RunStatus(
                run_id=run_id,
                session_id=request.session_id,
                status="completed",
                terminal_state="completed",
                active_controls=[],
            )
            self._emit(event_sink, RunEvent("run.completed", {"result": result}, run_id=run_id))
            return result
        except Exception as exc:
            self._runs[run_id] = RunStatus(
                run_id=run_id,
                session_id=request.session_id,
                status="failed",
                terminal_state="failed",
                active_controls=[],
            )
            self._emit(event_sink, RunEvent("run.failed", {"error": str(exc)}, run_id=run_id))
            raise

    def start_run(self, request: RunRequest) -> RunHandle:
        run_id = str(request.metadata.get("run_id") or uuid.uuid4().hex)
        handle = RunHandle(
            run_id=run_id,
            session_id=request.session_id,
            stream_id=run_id,
            status="accepted",
            started_at=time.time(),
            active_controls=["cancel"],
        )
        self._runs[run_id] = RunStatus(
            run_id=run_id,
            session_id=request.session_id,
            status="accepted",
            active_controls=["cancel"],
        )
        return handle

    def events(self, run_id: str, cursor: str | None = None) -> Iterable[RunEvent]:
        return ()

    def status(self, run_id: str) -> RunStatus:
        return self._runs.get(run_id, RunStatus(run_id=run_id))

    def cancel(self, run_id: str) -> ControlResult:
        status = self._runs.get(run_id)
        if status is None or status.status not in {"accepted", "running"}:
            return ControlResult(False, status="not-active", safe_message="Run is not active.")
        self._runs[run_id] = RunStatus(
            run_id=run_id,
            session_id=status.session_id,
            status="cancelled",
            terminal_state="cancelled",
            active_controls=[],
        )
        return ControlResult(True, status="cancelled")

    def respond_approval(self, run_id: str, approval_id: str, choice: str) -> ControlResult:
        return ControlResult(False, status="unsupported", safe_message="Approval is not wired for EmbeddedRuntime yet.")

    def respond_clarify(self, run_id: str, clarify_id: str, response: str) -> ControlResult:
        return ControlResult(False, status="unsupported", safe_message="Clarify is not wired for EmbeddedRuntime yet.")

    def queue_message(self, run_id: str, message: str, mode: str = "queue") -> ControlResult:
        return ControlResult(False, status="unsupported", safe_message="Queue is not wired for EmbeddedRuntime yet.")

    def _build_agent(self, request: RunRequest) -> Any:
        if self._agent_factory is not None:
            return self._agent_factory(request)
        from run_agent import AIAgent

        kwargs: dict[str, Any] = {}
        if request.model:
            kwargs["model"] = request.model
        if request.provider:
            kwargs["provider"] = request.provider
        return AIAgent(**kwargs)

    @staticmethod
    def _emit(event_sink: EventSink | None, event: RunEvent) -> None:
        if event_sink is not None:
            event_sink(event)
