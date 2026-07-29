"""Disabled MCP OAuth manager shim for the lite build."""


class DisabledOAuthManager:
    def remove(self, *args, **kwargs):
        return None

    def restore_entry(self, *args, **kwargs):
        return None


def get_manager(*args, **kwargs):
    return DisabledOAuthManager()
