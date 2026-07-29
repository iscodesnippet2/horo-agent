"""Disabled TTS tool compatibility shim for the lite build."""

BUILTIN_TTS_PROVIDERS = {}


def _disabled(*args, **kwargs):
    raise RuntimeError("Text-to-speech is disabled in the lite build.")


text_to_speech_tool = _disabled
_get_provider = _disabled


def _load_tts_config(*args, **kwargs):
    return {}


def _resolve_max_text_length(*args, **kwargs):
    return 0


def _strip_markdown_for_tts(text):
    return text
