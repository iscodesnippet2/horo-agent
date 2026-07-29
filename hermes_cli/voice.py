"""Disabled voice CLI helpers for the lite build."""


def format_voice_record_key_for_status(*args, **kwargs):
    return "disabled"


def voice_command(*args, **kwargs) -> int:
    print("Voice mode is disabled in the lite build.")
    return 1
