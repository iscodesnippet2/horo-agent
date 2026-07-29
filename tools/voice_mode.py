"""Disabled voice mode compatibility shim for the lite build."""


def transcribe_recording(*args, **kwargs):
    raise RuntimeError("Voice mode is disabled in the lite build.")
