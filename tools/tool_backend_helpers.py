"""Lite-build backend helpers.

Cloud and managed Nous backends are removed. The remaining helpers keep older
call sites importable while forcing local/internal backends only.
"""


def managed_nous_tools_enabled(*args, **kwargs) -> bool:
    return False


def nous_tool_gateway_unavailable_message(*args, **kwargs) -> str:
    return "Managed Nous Tool Gateway is disabled in the lite build."


def normalize_browser_cloud_provider(provider):
    return None


def fal_key_is_configured(*args, **kwargs) -> bool:
    return False
