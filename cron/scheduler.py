"""Local-only scheduler helpers for Horo Agent lite."""

from __future__ import annotations

from typing import Any


def cron_delivery_targets() -> list[dict[str, Any]]:
    return []


def run_one_job(job: dict[str, Any], *_, **__) -> dict[str, Any]:
    return {
        "success": False,
        "job": job,
        "error": "local cron execution is not wired in this lite build yet",
    }
