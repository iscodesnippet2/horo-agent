"""Disabled billing usage model for the lite build."""


def build_usage_model(*args, **kwargs):
    return None


def fetch_usage_model(*args, **kwargs):
    return None
