"""Disabled account usage helpers for the lite build."""


def fetch_account_usage(*args, **kwargs):
    return None


def render_account_usage_lines(*args, **kwargs):
    return ["Account usage is disabled in the lite build."]


def redeem_codex_reset_credit(*args, **kwargs):
    return False
