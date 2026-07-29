"""Disabled STT registry for the lite build."""


def register_provider(*args, **kwargs):
    raise RuntimeError("Speech-to-text providers are disabled in the lite build.")


def list_providers():
    return []
