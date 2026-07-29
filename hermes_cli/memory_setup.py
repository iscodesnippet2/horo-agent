"""Disabled external memory setup helpers for the lite build."""

_CANCELLED = object()


def _prompt(*args, **kwargs):
    return _CANCELLED


def _curses_select(*args, **kwargs):
    return _CANCELLED


def _print_cancelled_setup(*args, **kwargs) -> None:
    print("External memory setup is disabled in the lite build.")


def memory_command(*args, **kwargs) -> int:
    print("External memory providers are disabled in the lite build.")
    return 1
