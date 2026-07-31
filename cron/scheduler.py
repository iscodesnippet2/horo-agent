"""Local-only scheduler helpers for Horo Agent lite."""

from __future__ import annotations

import contextlib
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from hermes_constants import get_hermes_home


@contextlib.contextmanager
def _tick_lock() -> Any:
    lock_path = get_hermes_home() / "cron" / ".tick.lock"
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    handle = lock_path.open("a+", encoding="utf-8")
    locked = False
    try:
        try:
            import fcntl

            fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            locked = True
        except (ImportError, BlockingIOError, OSError):
            locked = False
        yield locked
    finally:
        if locked:
            try:
                import fcntl

                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
            except Exception:
                pass
        handle.close()


def cron_delivery_targets() -> list[dict[str, Any]]:
    return []


def _run_dir(job: dict[str, Any], run_id: str) -> Path:
    path = get_hermes_home() / "cron" / "runs" / str(job.get("job_id") or job.get("id")) / run_id
    path.mkdir(parents=True, exist_ok=True)
    return path


def _effective_prompt(job: dict[str, Any]) -> str:
    prompt = str(job.get("prompt") or "").strip()
    skills = [str(item).strip() for item in (job.get("skills") or []) if str(item).strip()]
    if skills:
        prefix = "Scheduled job requested these local skills: " + ", ".join(skills) + "."
        prompt = f"{prefix}\n\n{prompt}" if prompt else prefix
    return prompt


def run_one_job(job: dict[str, Any], *_, **__) -> dict[str, Any]:
    run_id = str(job.get("current_run_id") or ("run_" + datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")))
    out_dir = _run_dir(job, run_id)
    stdout_path = out_dir / "stdout.txt"
    stderr_path = out_dir / "stderr.txt"
    meta_path = out_dir / "meta.json"
    timeout = int(os.getenv("HORO_CRON_JOB_TIMEOUT", "3600"))

    if job.get("no_agent") or job.get("script"):
        error = "script/no_agent cron execution is disabled in horo-agent lite"
        result = {
            "success": False,
            "exit_code": 2,
            "error": error,
            "output_path": str(out_dir),
            "stdout_path": str(stdout_path),
            "stderr_path": str(stderr_path),
        }
        stderr_path.write_text(error + "\n", encoding="utf-8")
        meta_path.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        return result

    prompt = _effective_prompt(job)
    if not prompt:
        error = "agent cron job has no prompt"
        result = {
            "success": False,
            "exit_code": 2,
            "error": error,
            "output_path": str(out_dir),
            "stdout_path": str(stdout_path),
            "stderr_path": str(stderr_path),
        }
        stderr_path.write_text(error + "\n", encoding="utf-8")
        meta_path.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        return result

    env = os.environ.copy()
    env["HERMES_CRON_SESSION"] = "1"
    env["HERMES_SESSION_SOURCE"] = "cron"
    env["HERMES_CRON_JOB_ID"] = str(job.get("job_id") or job.get("id") or "")
    env["HERMES_CRON_RUN_ID"] = run_id

    cmd = [sys.executable, "-m", "hermes_cli.main"]
    if job.get("model"):
        cmd.extend(["--model", str(job["model"])])
    if job.get("provider"):
        cmd.extend(["--provider", str(job["provider"])])
    toolsets = [str(item).strip() for item in (job.get("enabled_toolsets") or []) if str(item).strip()]
    if toolsets:
        cmd.extend(["--toolsets", ",".join(toolsets)])
    cmd.extend(["-z", prompt])

    cwd = str(job.get("workdir") or "").strip()
    if not cwd or not Path(cwd).is_dir():
        cwd = os.getcwd()

    started_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    try:
        with stdout_path.open("w", encoding="utf-8") as stdout, stderr_path.open("w", encoding="utf-8") as stderr:
            proc = subprocess.run(
                cmd,
                cwd=cwd,
                env=env,
                text=True,
                stdout=stdout,
                stderr=stderr,
                timeout=timeout,
            )
        exit_code = proc.returncode
        error = None if exit_code == 0 else f"process exited with {exit_code}"
    except subprocess.TimeoutExpired:
        exit_code = 124
        error = f"process timed out after {timeout}s"
        stderr_path.write_text(error + "\n", encoding="utf-8")
    except Exception as exc:
        exit_code = 1
        error = str(exc)
        stderr_path.write_text(error + "\n", encoding="utf-8")

    result = {
        "success": exit_code == 0,
        "exit_code": exit_code,
        "error": error,
        "output_path": str(out_dir),
        "stdout_path": str(stdout_path),
        "stderr_path": str(stderr_path),
        "started_at": started_at,
        "completed_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
    }
    meta_path.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return result


def tick(job_id: str | None = None, *, limit: int | None = None) -> dict[str, Any]:
    from cron import jobs

    fired: list[dict[str, Any]] = []
    with _tick_lock() as locked:
        if not locked:
            return {"success": True, "locked": False, "fired": fired}
        due = [jobs.get_job(job_id)] if job_id else jobs.due_jobs()
        due = [job for job in due if job]
        if limit is not None:
            due = due[: max(0, limit)]
        for due_job in due:
            run_id = "run_" + datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S") + "_" + str(due_job["job_id"])[-6:]
            claimed = jobs.claim_due_job(due_job["job_id"], run_id=run_id)
            if not claimed:
                continue
            result = run_one_job(claimed)
            completed = jobs.complete_job_run(
                claimed["job_id"],
                run_id=run_id,
                success=bool(result.get("success")),
                exit_code=result.get("exit_code"),
                output_path=result.get("output_path"),
                error=result.get("error"),
            )
            fired.append({"job": completed or claimed, "result": result})
    return {"success": True, "locked": True, "fired": fired}


def run_loop(stop_event: Any = None, *, interval: int = 60) -> None:
    while True:
        tick()
        if stop_event is not None and stop_event.wait(interval):
            return
        if stop_event is None:
            time.sleep(interval)
