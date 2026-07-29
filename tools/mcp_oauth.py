"""Disabled MCP OAuth shim for the lite build."""

from contextlib import contextmanager


class OAuthNonInteractiveError(RuntimeError):
    pass


class HermesTokenStorage:
    def __init__(self, *args, **kwargs):
        pass

    def snapshot(self):
        return None

    def restore(self, *args, **kwargs):
        return None


@contextmanager
def force_interactive_oauth(*args, **kwargs):
    raise OAuthNonInteractiveError("MCP OAuth is disabled in the lite build.")


@contextmanager
def suppress_interactive_oauth(*args, **kwargs):
    yield
