"""Scheduler provider shim for local-only cron management."""

from __future__ import annotations


class LocalCronScheduler:
    name = "local"

    def fire_due(self, *_args, **_kwargs) -> bool:
        from cron.scheduler import tick

        job_id = _args[0] if _args else _kwargs.get("job_id")
        result = tick(job_id=job_id)
        return bool(result.get("fired"))

    def start(self, stop_event, interval: int = 60) -> None:
        from cron.scheduler import run_loop

        run_loop(stop_event, interval=interval)


def resolve_cron_scheduler() -> LocalCronScheduler:
    return LocalCronScheduler()
