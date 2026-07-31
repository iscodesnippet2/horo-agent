"""Local suggestion store for scheduled-task ideas."""

from __future__ import annotations

import contextlib
import json
import secrets
from pathlib import Path
from typing import Any, Iterator

from cron.jobs import create_job
from hermes_constants import get_hermes_home


_store_home_override: Path | None = None


@contextlib.contextmanager
def use_suggestion_store(home: str | Path) -> Iterator[None]:
    global _store_home_override
    previous = _store_home_override
    _store_home_override = Path(home)
    try:
        yield
    finally:
        _store_home_override = previous


def _path() -> Path:
    home = _store_home_override or get_hermes_home()
    return home / "cron" / "suggestions.json"


def _load() -> list[dict[str, Any]]:
    path = _path()
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    if isinstance(data, dict):
        data = data.get("suggestions", [])
    return [item for item in data if isinstance(item, dict)]


def _save(items: list[dict[str, Any]]) -> None:
    path = _path()
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".json.tmp")
    tmp.write_text(
        json.dumps({"suggestions": items}, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    tmp.replace(path)


def list_pending() -> list[dict[str, Any]]:
    return [item for item in _load() if item.get("state", "pending") == "pending"]


def add_suggestion(
    *,
    title: str,
    description: str = "",
    source: str = "local",
    job_spec: dict[str, Any],
    dedup_key: str | None = None,
) -> dict[str, Any] | None:
    items = _load()
    key = dedup_key or f"{source}:{title}:{job_spec.get('schedule')}"
    if any(item.get("dedup_key") == key for item in items):
        return None
    item = {
        "id": "sug_" + secrets.token_hex(5),
        "title": title,
        "description": description,
        "source": source,
        "job_spec": dict(job_spec),
        "dedup_key": key,
        "state": "pending",
    }
    items.append(item)
    _save(items)
    return item


def _resolve_ref(ref: str) -> tuple[int, dict[str, Any]] | tuple[None, None]:
    pending = list_pending()
    text = str(ref or "").strip()
    if text.isdigit():
        index = int(text) - 1
        if 0 <= index < len(pending):
            item = pending[index]
            all_items = _load()
            for all_index, candidate in enumerate(all_items):
                if candidate.get("id") == item.get("id"):
                    return all_index, candidate
    for all_index, item in enumerate(_load()):
        if item.get("id") == text and item.get("state", "pending") == "pending":
            return all_index, item
    return None, None


def accept_suggestion(ref: str, origin: dict[str, Any] | None = None) -> dict[str, Any] | None:
    index, item = _resolve_ref(ref)
    if item is None or index is None:
        return None
    spec = dict(item.get("job_spec") or {})
    spec.pop("origin", None)
    if origin is not None:
        spec["origin"] = origin
    spec["deliver"] = "local"
    job = create_job(**spec)
    items = _load()
    items[index]["state"] = "accepted"
    items[index]["job_id"] = job.get("job_id")
    _save(items)
    return {"name": job.get("name"), "schedule_display": job.get("original_schedule"), **item, "created_job": job}


def dismiss_suggestion(ref: str) -> bool:
    index, item = _resolve_ref(ref)
    if item is None or index is None:
        return False
    items = _load()
    items[index]["state"] = "dismissed"
    _save(items)
    return True


def clear_resolved() -> int:
    items = _load()
    kept = [item for item in items if item.get("state", "pending") == "pending"]
    removed = len(items) - len(kept)
    if removed:
        _save(kept)
    return removed
