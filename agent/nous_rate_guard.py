"""Disabled Nous rate guard for the lite build."""


def nous_rate_limit_remaining(*args, **kwargs):
    return None


def format_remaining(value):
    return ""


def clear_nous_rate_limit(*args, **kwargs):
    return None


def is_genuine_nous_rate_limit(*args, **kwargs) -> bool:
    return False


def record_nous_rate_limit(*args, **kwargs):
    return None
