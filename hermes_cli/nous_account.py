"""Disabled Nous Portal account helpers for the lite build."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


TOOL_COVERAGE_CATEGORIES: tuple[str, ...] = ()


@dataclass(frozen=True)
class NousPortalSubscriptionInfo:
    active: bool = False
    status: Optional[str] = None


@dataclass(frozen=True)
class NousPaidServiceAccessInfo:
    active: bool = False
    status: Optional[str] = None


@dataclass(frozen=True)
class NousToolAccessInfo:
    entitled: bool = False
    covered_tools: tuple[str, ...] = ()


@dataclass(frozen=True)
class NousPortalAccountInfo:
    logged_in: bool = False
    inference_credential_present: bool = False
    tool_gateway_entitled: bool = False
    paid_service_access: bool = False
    inference_base_url: Optional[str] = None
    subscription: NousPortalSubscriptionInfo = field(default_factory=NousPortalSubscriptionInfo)
    paid_service: NousPaidServiceAccessInfo = field(default_factory=NousPaidServiceAccessInfo)
    tool_access: NousToolAccessInfo = field(default_factory=NousToolAccessInfo)
    error: Optional[str] = None

    def tool_gateway_entitled_for(self, _tool: str) -> bool:
        return False


def nous_portal_billing_url(account_info: Optional[NousPortalAccountInfo] = None) -> str:
    return ""


def nous_portal_topup_url(account_info: Optional[NousPortalAccountInfo] = None) -> str:
    return ""


def format_nous_portal_entitlement_message(
    account_info: Optional[NousPortalAccountInfo],
    capability: str = "managed tools",
) -> str:
    return f"{capability} is disabled in the lite build."


def reset_nous_portal_account_info_cache() -> None:
    return None


def get_nous_portal_account_info(*, force_fresh: bool = False) -> NousPortalAccountInfo:
    return NousPortalAccountInfo()
