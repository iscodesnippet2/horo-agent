"""Scheduler provider shim for local-only cron management."""

from __future__ import annotations


class LocalCronScheduler:
    def fire_due(self, *_args, **_kwargs) -> bool:
        return False


def resolve_cron_scheduler() -> LocalCronScheduler:
    return LocalCronScheduler()
