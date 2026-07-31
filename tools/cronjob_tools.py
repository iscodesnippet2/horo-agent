"""Cron job management tool for local-only Horo Agent lite."""

from __future__ import annotations

import json
from typing import Any

from tools.registry import registry


CRONJOB_SCHEMA = {
    "name": "cronjob",
    "description": (
        "Create, list, update, pause, resume, run, or remove local scheduled "
        "jobs. Horo Agent lite stores cron jobs locally and only supports "
        "local delivery."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": ["create", "list", "update", "pause", "resume", "run", "remove"],
            },
            "job_id": {"type": "string"},
            "schedule": {"type": "string"},
            "prompt": {"type": "string"},
            "name": {"type": "string"},
            "deliver": {"type": "string", "enum": ["local"]},
            "repeat": {"type": "integer"},
            "skills": {"type": "array", "items": {"type": "string"}},
            "include_disabled": {"type": "boolean"},
            "reason": {"type": "string"},
        },
        "required": ["action"],
    },
}


def _json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False)


def cronjob(**kwargs) -> str:
    from cron import jobs

    action = str(kwargs.get("action") or "").strip().lower()
    try:
        if action == "list":
            return _json({
                "success": True,
                "jobs": jobs.list_jobs(bool(kwargs.get("include_disabled"))),
            })
        if action == "create":
            job = jobs.create_job(
                schedule=kwargs.get("schedule") or "",
                prompt=kwargs.get("prompt") or "",
                name=kwargs.get("name"),
                deliver=kwargs.get("deliver") or "local",
                repeat=kwargs.get("repeat"),
                skills=kwargs.get("skills"),
            )
            return _json({"success": True, **job})
        job_id = kwargs.get("job_id")
        if not job_id:
            return _json({"success": False, "error": "job_id is required"})
        if action == "update":
            job = jobs.update_job(
                str(job_id),
                schedule=kwargs.get("schedule"),
                prompt=kwargs.get("prompt"),
                name=kwargs.get("name"),
                deliver=kwargs.get("deliver") or None,
                repeat=kwargs.get("repeat"),
                skills=kwargs.get("skills"),
            )
            return _json({"success": bool(job), "job": job, "error": None if job else "job not found"})
        if action == "pause":
            job = jobs.pause_job(str(job_id), kwargs.get("reason"))
            return _json({"success": bool(job), "job": job, "error": None if job else "job not found"})
        if action == "resume":
            job = jobs.resume_job(str(job_id))
            return _json({"success": bool(job), "job": job, "error": None if job else "job not found"})
        if action == "run":
            job = jobs.trigger_job(str(job_id))
            return _json({"success": bool(job), "job": job, "error": None if job else "job not found"})
        if action == "remove":
            job = jobs.remove_job(str(job_id))
            return _json({"success": bool(job), "removed_job": job, "error": None if job else "job not found"})
        return _json({"success": False, "error": f"unknown action: {action}"})
    except Exception as exc:
        return _json({"success": False, "error": str(exc)})


def _handle_cronjob(args: dict[str, Any], **_kwargs) -> str:
    return cronjob(**(args or {}))


registry.register(
    name="cronjob",
    toolset="cronjob",
    schema=CRONJOB_SCHEMA,
    handler=_handle_cronjob,
    emoji="⏰",
    max_result_size_chars=50_000,
)
