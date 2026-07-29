"""Disabled Azure identity adapter for the lite build."""


def is_token_provider(*args, **kwargs) -> bool:
    return False
