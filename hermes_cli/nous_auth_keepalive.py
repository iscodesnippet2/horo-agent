"""Disabled Nous auth keepalive for the lite build."""


def start_nous_auth_keepalive(*args, **kwargs):
    return None
