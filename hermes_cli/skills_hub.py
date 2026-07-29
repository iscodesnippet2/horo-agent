"""Disabled remote Skills Hub commands for the lite build."""


def skills_command(*args, **kwargs) -> int:
    print("Remote Skills Hub discovery is disabled in the lite build.")
    return 1


def handle_skills_slash(*args, **kwargs):
    return "Remote Skills Hub discovery is disabled in the lite build."


def _resolve_source_meta_and_bundle(*args, **kwargs):
    raise RuntimeError("Remote Skills Hub discovery is disabled in the lite build.")
