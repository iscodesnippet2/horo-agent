"""Local cron job store used by the air-gapped lite build."""

from __future__ import annotations

import contextlib
import json
import re
import secrets
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

from croniter import croniter

from hermes_constants import get_hermes_home


_store_home_override: Path | None = None


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(dt: datetime | None = None) -> str:
    return (dt or _now()).replace(microsecond=0).isoformat()


def _parse_iso(value: Any) -> datetime | None:
    text = str(value or "").strip()
    if not text:
        return None
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _cron_dir() -> Path:
    home = _store_home_override or get_hermes_home()
    return home / "cron"


def _jobs_path() -> Path:
    return _cron_dir() / "jobs.json"


@contextlib.contextmanager
def use_cron_store(home: str | Path) -> Iterator[None]:
    global _store_home_override
    previous = _store_home_override
    _store_home_override = Path(home)
    try:
        yield
    finally:
        _store_home_override = previous


def _load_jobs() -> list[dict[str, Any]]:
    path = _jobs_path()
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    if isinstance(data, dict):
        data = data.get("jobs", [])
    return [job for job in data if isinstance(job, dict)]


def _save_jobs(jobs: list[dict[str, Any]]) -> None:
    path = _jobs_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".json.tmp")
    tmp.write_text(
        json.dumps({"jobs": jobs}, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    tmp.replace(path)


def _normalize_schedule(schedule: str) -> str:
    text = str(schedule or "").strip()
    if not text:
        raise ValueError("schedule is required")
    lower = text.lower()
    if lower.startswith("every "):
        value = lower[6:].strip()
        match = re.fullmatch(r"(\d+)\s*(m|min|mins|minute|minutes|h|hr|hrs|hour|hours|d|day|days)", value)
        if not match:
            raise ValueError("unsupported interval; use cron syntax or 'every 2h'")
        amount = int(match.group(1))
        unit = match.group(2)
        if amount <= 0:
            raise ValueError("schedule interval must be positive")
        if unit.startswith("m"):
            return f"*/{amount} * * * *"
        if unit.startswith("h"):
            return f"0 */{amount} * * *"
        return f"0 0 */{amount} * *"
    fields = text.split()
    if len(fields) != 5:
        raise ValueError("schedule must be a 5-field cron expression or 'every <n>m|h|d'")
    return text


def _next_run(schedule: str, base: datetime | None = None) -> str:
    return croniter(schedule, base or _now()).get_next(datetime).replace(microsecond=0).isoformat()


def _skills_list(values: Any) -> list[str]:
    if values is None:
        return []
    if isinstance(values, str):
        raw = re.split(r"[\n,]", values)
    else:
        raw = values
    result: list[str] = []
    for item in raw:
        text = str(item or "").strip()
        if text and text not in result:
            result.append(text)
    return result


def _job_matches(job: dict[str, Any], ref: str) -> bool:
    return ref in {str(job.get("id", "")), str(job.get("job_id", "")), str(job.get("name", ""))}


def _format_job(job: dict[str, Any]) -> dict[str, Any]:
    out = dict(job)
    out.setdefault("id", out.get("job_id"))
    out.setdefault("job_id", out.get("id"))
    out.setdefault("name", out.get("job_id"))
    out.setdefault("state", "paused" if out.get("paused") else "enabled")
    out.setdefault("deliver", "local")
    out.setdefault("skills", [])
    prompt = str(out.get("prompt") or "")
    out["prompt_preview"] = prompt[:120] + ("..." if len(prompt) > 120 else "")
    out["repeat"] = out.get("repeat") or out.get("schedule")
    return out


def _find_job_index(jobs: list[dict[str, Any]], job_id: str) -> int | None:
    ref = str(job_id or "").strip()
    for index, job in enumerate(jobs):
        if _job_matches(job, ref):
            return index
    return None


def list_jobs(include_disabled: bool = False) -> list[dict[str, Any]]:
    jobs = [_format_job(job) for job in _load_jobs()]
    if not include_disabled:
        jobs = [job for job in jobs if job.get("state") != "paused"]
    return jobs


def get_job(job_id: str) -> dict[str, Any] | None:
    ref = str(job_id or "").strip()
    for job in _load_jobs():
        if _job_matches(job, ref):
            return _format_job(job)
    return None


def due_jobs(now: datetime | None = None) -> list[dict[str, Any]]:
    now = now or _now()
    jobs: list[dict[str, Any]] = []
    for job in _load_jobs():
        if job.get("state", "enabled") == "paused":
            continue
        if job.get("running"):
            continue
        next_run = _parse_iso(job.get("next_run_at"))
        if next_run is not None and next_run <= now:
            jobs.append(_format_job(job))
    return jobs


def create_job(
    *,
    prompt: str = "",
    schedule: str,
    name: str | None = None,
    deliver: str | None = "local",
    repeat: int | None = None,
    skills: Any = None,
    model: str | None = None,
    provider: str | None = None,
    base_url: str | None = None,
    script: str | None = None,
    context_from: Any = None,
    enabled_toolsets: Any = None,
    workdir: str | None = None,
    no_agent: bool = False,
) -> dict[str, Any]:
    normalized_schedule = _normalize_schedule(schedule)
    if deliver and deliver != "local":
        raise ValueError("horo-agent lite only supports local cron delivery")
    job_id = "job_" + secrets.token_hex(6)
    job = {
        "id": job_id,
        "job_id": job_id,
        "name": (name or "").strip() or job_id,
        "prompt": prompt or "",
        "schedule": normalized_schedule,
        "original_schedule": schedule,
        "deliver": "local",
        "repeat": repeat,
        "skills": _skills_list(skills),
        "context_from": _skills_list(context_from),
        "enabled_toolsets": _skills_list(enabled_toolsets),
        "model": model,
        "provider": provider,
        "base_url": base_url,
        "script": script,
        "workdir": workdir,
        "no_agent": bool(no_agent),
        "state": "enabled",
        "created_at": _iso(),
        "updated_at": _iso(),
        "last_run_at": None,
        "last_status": None,
        "next_run_at": _next_run(normalized_schedule),
    }
    jobs = _load_jobs()
    jobs.append(job)
    _save_jobs(jobs)
    return _format_job(job)


def update_job(job_id: str, updates: dict[str, Any] | None = None, **kwargs) -> dict[str, Any] | None:
    changes = dict(updates or {})
    changes.update({k: v for k, v in kwargs.items() if v is not None})
    if "deliver" in changes and changes["deliver"] and changes["deliver"] != "local":
        raise ValueError("horo-agent lite only supports local cron delivery")
    jobs = _load_jobs()
    for index, job in enumerate(jobs):
        if not _job_matches(job, str(job_id)):
            continue
        if "schedule" in changes and changes["schedule"]:
            job["schedule"] = _normalize_schedule(changes["schedule"])
            job["original_schedule"] = changes["schedule"]
            job["next_run_at"] = _next_run(job["schedule"])
        for key in (
            "prompt",
            "name",
            "repeat",
            "model",
            "provider",
            "base_url",
            "script",
            "workdir",
            "no_agent",
        ):
            if key in changes:
                job[key] = changes[key]
        for key in ("skills", "context_from", "enabled_toolsets"):
            if key in changes:
                job[key] = _skills_list(changes[key])
        job["deliver"] = "local"
        job["updated_at"] = _iso()
        jobs[index] = job
        _save_jobs(jobs)
        return _format_job(job)
    return None


def pause_job(job_id: str, reason: str | None = None) -> dict[str, Any] | None:
    job = update_job(job_id, {"state": "paused", "paused_reason": reason})
    if job:
        jobs = _load_jobs()
        for stored in jobs:
            if _job_matches(stored, str(job_id)):
                stored["state"] = "paused"
                stored["paused_reason"] = reason
                stored["updated_at"] = _iso()
        _save_jobs(jobs)
        return get_job(job_id)
    return None


def resume_job(job_id: str) -> dict[str, Any] | None:
    jobs = _load_jobs()
    for stored in jobs:
        if _job_matches(stored, str(job_id)):
            stored["state"] = "enabled"
            stored["paused_reason"] = None
            stored["next_run_at"] = _next_run(stored["schedule"])
            stored["updated_at"] = _iso()
            _save_jobs(jobs)
            return _format_job(stored)
    return None


def trigger_job(job_id: str) -> dict[str, Any] | None:
    jobs = _load_jobs()
    for stored in jobs:
        if _job_matches(stored, str(job_id)):
            stored["next_run_at"] = _iso()
            stored["last_status"] = "queued"
            stored["updated_at"] = _iso()
            _save_jobs(jobs)
            return _format_job(stored)
    return None


def claim_due_job(job_id: str, run_id: str | None = None) -> dict[str, Any] | None:
    jobs = _load_jobs()
    index = _find_job_index(jobs, str(job_id))
    if index is None:
        return None
    job = jobs[index]
    if job.get("state", "enabled") == "paused" or job.get("running"):
        return None
    next_run = _parse_iso(job.get("next_run_at"))
    if next_run is None or next_run > _now():
        return None
    run_id = run_id or ("run_" + secrets.token_hex(6))
    job["running"] = True
    job["current_run_id"] = run_id
    job["last_run_at"] = _iso()
    job["last_status"] = "running"
    job["updated_at"] = _iso()
    jobs[index] = job
    _save_jobs(jobs)
    return _format_job(job)


def complete_job_run(
    job_id: str,
    *,
    run_id: str,
    success: bool,
    exit_code: int | None = None,
    output_path: str | None = None,
    error: str | None = None,
) -> dict[str, Any] | None:
    jobs = _load_jobs()
    index = _find_job_index(jobs, str(job_id))
    if index is None:
        return None
    job = jobs[index]
    status = "success" if success else "failed"
    job["running"] = False
    job["current_run_id"] = None
    job["last_status"] = status
    job["last_exit_code"] = exit_code
    job["last_error"] = error
    job["last_output_path"] = output_path
    job["last_completed_at"] = _iso()
    job["next_run_at"] = _next_run(job["schedule"], _now())
    job["updated_at"] = _iso()
    history = list(job.get("run_history") or [])
    history.append({
        "run_id": run_id,
        "status": status,
        "exit_code": exit_code,
        "output_path": output_path,
        "error": error,
        "completed_at": job["last_completed_at"],
    })
    job["run_history"] = history[-20:]
    jobs[index] = job
    _save_jobs(jobs)
    return _format_job(job)


def remove_job(job_id: str) -> dict[str, Any] | None:
    jobs = _load_jobs()
    kept: list[dict[str, Any]] = []
    removed: dict[str, Any] | None = None
    for job in jobs:
        if removed is None and _job_matches(job, str(job_id)):
            removed = job
        else:
            kept.append(job)
    if removed is None:
        return None
    _save_jobs(kept)
    return _format_job(removed)


def referenced_skill_names() -> set[str]:
    names: set[str] = set()
    for job in _load_jobs():
        names.update(_skills_list(job.get("skills")))
        skill = str(job.get("skill") or "").strip()
        if skill:
            names.add(skill)
    return names


def rewrite_skill_refs(mapping: dict[str, str], *_, **__) -> dict[str, Any]:
    rewrites: list[dict[str, str]] = []
    jobs = _load_jobs()
    for job in jobs:
        skills = _skills_list(job.get("skills"))
        replaced = [mapping.get(skill, skill) for skill in skills]
        if replaced != skills:
            job["skills"] = replaced
            job["updated_at"] = _iso()
            rewrites.append({"job_id": str(job.get("job_id")), "from": ",".join(skills), "to": ",".join(replaced)})
    if rewrites:
        _save_jobs(jobs)
    return {"rewrites": rewrites, "jobs_updated": len(rewrites), "jobs_scanned": len(jobs)}
