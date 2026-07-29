"""Disabled managed egress/tool gateway for the lite build."""


def is_managed_tool_gateway_enabled(*args, **kwargs) -> bool:
    return False


def managed_tool_gateway_request(*args, **kwargs):
    raise RuntimeError("Managed tool gateway is disabled in the lite build.")
