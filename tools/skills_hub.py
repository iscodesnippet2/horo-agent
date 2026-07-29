"""Disabled remote Skills Hub backend for the lite build."""

from dataclasses import dataclass, field
from pathlib import Path

SKILLS_DIR = Path.home() / ".hermes" / "skills"


@dataclass
class SkillMeta:
    name: str = ""
    description: str = ""
    source: str = "disabled"
    identifier: str = ""
    trust_level: str = "disabled"
    repo: str | None = None
    tags: list[str] = field(default_factory=list)


@dataclass
class SkillBundle(SkillMeta):
    files: dict[str, str | bytes] = field(default_factory=dict)


class HubLockFile:
    def __init__(self, path: str | Path | None = None):
        self.path = Path(path) if path else SKILLS_DIR / ".hub" / "lock.json"

    def list_installed(self):
        return []


def create_source_router(*args, **kwargs):
    return []


def parallel_search_sources(*args, **kwargs):
    return [], {}, []


def quarantine_bundle(*args, **kwargs):
    raise RuntimeError("Remote Skills Hub discovery is disabled in the lite build.")


def bundle_content_hash(*args, **kwargs):
    return ""
