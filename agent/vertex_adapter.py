"""Disabled Vertex adapter for the lite build."""


def get_vertex_config(*args, **kwargs):
    return {}


def has_vertex_credentials(*args, **kwargs) -> bool:
    return False
