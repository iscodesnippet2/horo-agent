"""Empty cron blueprint catalog for the lite build."""

from __future__ import annotations


CATALOG: list[dict] = []


class BlueprintFillError(ValueError):
    pass


def blueprint_catalog_entry(item: dict) -> dict:
    return dict(item)


def get_blueprint(name: str) -> dict | None:
    return None


def fill_blueprint(_blueprint: dict, _values: dict) -> dict:
    raise BlueprintFillError("cron blueprints are not bundled in horo-agent lite")
