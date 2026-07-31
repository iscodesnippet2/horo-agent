"""Lite-compatible streaming TTS shims.

The lite build removes streaming/cloud TTS providers, but a few interactive
paths still use the interruption markers and sentence chunker API. Keep those
imports available so voice-disabled and air-gapped runs degrade cleanly.
"""

from __future__ import annotations

import re
import threading
from collections.abc import Iterable


SPEECH_INTERRUPTED_NOTE = (
    "Note: the previous spoken response was interrupted by the user. Continue "
    "from the interruption point without repeating unnecessary context."
)

SENTENCE_BOUNDARY_RE = re.compile(r"(?<=[.!?…:])\s+")

_speech_interrupted = threading.Event()


def mark_speech_interrupted() -> None:
    """Record a one-shot speech interruption marker."""
    _speech_interrupted.set()


def take_speech_interrupted() -> bool:
    """Return and clear the one-shot speech interruption marker."""
    interrupted = _speech_interrupted.is_set()
    if interrupted:
        _speech_interrupted.clear()
    return interrupted


def resolve_streaming_provider(_config: dict | None = None):
    """No streaming TTS provider is bundled in the air-gapped lite build."""
    return None


class SentenceChunker:
    """Small sentence chunker compatible with the removed streaming module."""

    def __init__(self) -> None:
        self.buf = ""

    def feed(self, text: str) -> Iterable[str]:
        self.buf += text
        parts = SENTENCE_BOUNDARY_RE.split(self.buf)
        if len(parts) <= 1:
            return []
        self.buf = parts[-1]
        return [part.strip() for part in parts[:-1] if part.strip()]

    def flush(self) -> Iterable[str]:
        text = self.buf.strip()
        self.buf = ""
        return [text] if text else []
