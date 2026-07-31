"""Local-only cron CLI for Horo Agent lite."""

from __future__ import annotations

import argparse
import json

from tools.cronjob_tools import cronjob


def build_parser(subparsers):
    parser = subparsers.add_parser("cron", help="Manage local scheduled tasks")
    sub = parser.add_subparsers(dest="cron_command")

    sub.add_parser("list", help="List scheduled tasks")
    sub.add_parser("status", help="Show local scheduler status")
    tick = sub.add_parser("tick", help="Run due scheduled tasks once")
    tick.add_argument("--limit", type=int, default=None)

    create = sub.add_parser("create", aliases=["add"], help="Create a scheduled task")
    create.add_argument("schedule")
    create.add_argument("prompt", nargs="*")
    create.add_argument("--name")
    create.add_argument("--skill", action="append", dest="skills")

    edit = sub.add_parser("edit", help="Edit a scheduled task")
    edit.add_argument("job_id")
    edit.add_argument("--schedule")
    edit.add_argument("--prompt")
    edit.add_argument("--name")
    edit.add_argument("--skill", action="append", dest="skills")

    run = sub.add_parser("run", help="Run scheduler loop, or trigger a job when job_id is provided")
    run.add_argument("job_id", nargs="?")
    run.add_argument("--interval", type=int, default=60)

    for name in ("pause", "resume", "remove"):
        p = sub.add_parser(name, help=f"{name.title()} a scheduled task")
        p.add_argument("job_id")

    parser.set_defaults(func=cron_command)
    return parser


def _call(**kwargs):
    return json.loads(cronjob(**kwargs))


def cron_command(args: argparse.Namespace) -> None:
    command = getattr(args, "cron_command", None) or "list"
    if command == "list":
        result = _call(action="list", include_disabled=True)
        jobs = result.get("jobs") or []
        if not jobs:
            print("No scheduled jobs.")
            return
        for job in jobs:
            print(f"{job['job_id']}  {job['state']}  {job['schedule']}  {job['name']}")
            print(f"  next: {job.get('next_run_at') or 'n/a'}")
            if job.get("prompt_preview"):
                print(f"  prompt: {job['prompt_preview']}")
        return

    if command == "status":
        from cron.jobs import due_jobs, list_jobs
        from cron.scheduler_provider import resolve_cron_scheduler

        provider = resolve_cron_scheduler()
        jobs = list_jobs(include_disabled=True)
        due = due_jobs()
        print(f"provider: {provider.name}")
        print(f"jobs: {len(jobs)}")
        print(f"due now: {len(due)}")
        print("delivery: local only")
        return

    if command == "tick":
        from cron.scheduler import tick

        result = tick(limit=getattr(args, "limit", None))
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return

    if command in {"create", "add"}:
        prompt = " ".join(getattr(args, "prompt", []) or [])
        result = _call(
            action="create",
            schedule=getattr(args, "schedule", ""),
            prompt=prompt,
            name=getattr(args, "name", None),
            skills=getattr(args, "skills", None),
            deliver="local",
        )
    elif command == "edit":
        result = _call(
            action="update",
            job_id=args.job_id,
            schedule=getattr(args, "schedule", None),
            prompt=getattr(args, "prompt", None),
            name=getattr(args, "name", None),
            skills=getattr(args, "skills", None),
        )
    elif command == "pause":
        result = _call(action="pause", job_id=args.job_id)
    elif command == "resume":
        result = _call(action="resume", job_id=args.job_id)
    elif command == "run":
        job_id = getattr(args, "job_id", None)
        if job_id:
            from cron.scheduler import tick

            _call(action="run", job_id=job_id)
            result = tick(job_id=job_id)
            print(json.dumps(result, indent=2, ensure_ascii=False))
            return
        from cron.scheduler import run_loop

        interval = max(5, int(getattr(args, "interval", 60) or 60))
        print(f"Local cron scheduler running every {interval}s. Press Ctrl+C to stop.")
        try:
            run_loop(interval=interval)
        except KeyboardInterrupt:
            print("Stopped local cron scheduler.")
        return
    elif command == "remove":
        result = _call(action="remove", job_id=args.job_id)
    else:
        raise SystemExit(f"unknown cron command: {command}")

    if not result.get("success"):
        raise SystemExit(result.get("error") or "cron command failed")
    print(json.dumps(result, indent=2, ensure_ascii=False))
