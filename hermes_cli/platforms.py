"""Lite platform labels.

The upstream project used this module for gateway and messaging surfaces.  The
lite build keeps only local surfaces, but some skill-configuration views still
import the shared label helpers.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PlatformInfo:
    label: str


PLATFORMS = {
    "cli": PlatformInfo("Command line"),
    "desktop": PlatformInfo("Desktop"),
    "web": PlatformInfo("Web UI"),
    "api_server": PlatformInfo("API server"),
}


def platform_label(platform: str) -> str:
    info = PLATFORMS.get(platform)
    return info.label if info is not None else platform.replace("_", " ").title()
