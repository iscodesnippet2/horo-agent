"""Disabled managed-tool gateway helpers for the lite build."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, Optional


MANAGED_FEATURE_COVERAGE_CATEGORY: dict[str, str] = {}


@dataclass(frozen=True)
class NousFeatureState:
    key: str
    label: str
    available: bool = False
    active: bool = False
    managed_by_nous: bool = False
    included_by_default: bool = False
    current_provider: str = ""


@dataclass(frozen=True)
class NousSubscriptionFeatures:
    nous_auth_present: bool = False
    account_info: object | None = None
    features: Dict[str, NousFeatureState] = field(default_factory=dict)

    @property
    def web(self) -> NousFeatureState:
        return self.features.get("web", NousFeatureState("web", "Web"))

    @property
    def browser(self) -> NousFeatureState:
        return self.features.get("browser", NousFeatureState("browser", "Browser"))

    @property
    def image_gen(self) -> NousFeatureState:
        return self.features.get("image_gen", NousFeatureState("image_gen", "Image Generation"))

    @property
    def video_gen(self) -> NousFeatureState:
        return self.features.get("video_gen", NousFeatureState("video_gen", "Video Generation"))

    @property
    def tts(self) -> NousFeatureState:
        return self.features.get("tts", NousFeatureState("tts", "Text-to-Speech"))

    @property
    def stt(self) -> NousFeatureState:
        return self.features.get("stt", NousFeatureState("stt", "Speech-to-Text"))

    def items(self) -> Iterable[NousFeatureState]:
        return self.features.values()


def _has_agent_browser() -> bool:
    try:
        from hermes_constants import agent_browser_runnable

        return bool(agent_browser_runnable())
    except Exception:
        return False


def _local_browser_runnable() -> bool:
    return _has_agent_browser()


def get_nous_subscription_features(config: Optional[dict] = None, *, force_fresh: bool = False) -> NousSubscriptionFeatures:
    return NousSubscriptionFeatures()


def apply_nous_managed_defaults(config: dict, *args, **kwargs) -> list[str]:
    return []


def get_gateway_eligible_tools(config: Optional[dict] = None, *args, **kwargs) -> list[dict]:
    return []


def apply_gateway_defaults(config: dict, tools: Iterable[str] | None = None, *args, **kwargs) -> list[str]:
    return []


def prompt_enable_tool_gateway(*args, **kwargs) -> list[str]:
    return []


def ensure_nous_portal_access(*args, **kwargs) -> bool:
    return False
