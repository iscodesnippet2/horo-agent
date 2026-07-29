"""Disabled MCP dashboard OAuth shim for the lite build."""

from contextlib import contextmanager
from dataclasses import dataclass, field
import time


@dataclass
class DashboardOAuthFlow:
    flow_id: str = ""
    server_name: str = ""
    profile: str | None = None
    hermes_home: str = ""
    redirect_uri: str = ""
    reconnect_live: bool = False
    created_at: float = field(default_factory=time.time)
    worker_done: bool = False
    approved: bool = False
    error: str | None = None
    tools: list[dict] = field(default_factory=list)

    def mark_approved(self) -> None:
        self.approved = True

    def mark_error(self, message: str) -> None:
        self.error = message

    def mark_worker_done(self) -> None:
        self.worker_done = True


@contextmanager
def dashboard_oauth_flow(*args, **kwargs):
    raise RuntimeError("MCP OAuth is disabled in the lite build.")
