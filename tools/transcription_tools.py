"""Disabled STT tool compatibility shim for the lite build."""

BUILTIN_STT_PROVIDERS = {}


def _disabled(*args, **kwargs):
    raise RuntimeError("Speech-to-text is disabled in the lite build.")


transcribe_audio_tool = _disabled
voice_transcription_tool = _disabled
