"""Local-only cron CLI for Horo Agent lite."""

from __future__ import annotations

import argparse
import json

from tools.cronjob_tools import cronjob


def build_parser(subparsers):
    parser = subparsers.add_parser("cron", help="Manage local scheduled tasks")
    sub = parser.add_subparsers(dest="cron_command")

    sub.add_parser("list", help="List scheduled tasks")

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

    for name in ("pause", "resume", "run", "remove"):
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
        result = _call(action="run", job_id=args.job_id)
    elif command == "remove":
        result = _call(action="remove", job_id=args.job_id)
    else:
        raise SystemExit(f"unknown cron command: {command}")

    if not result.get("success"):
        raise SystemExit(result.get("error") or "cron command failed")
    print(json.dumps(result, indent=2, ensure_ascii=False))
