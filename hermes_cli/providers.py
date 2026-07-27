"""
Single source of truth for provider identity in Hermes Agent.

Two data sources, merged at runtime:

1. **models.dev catalog** — 109+ providers with base URLs, env vars, display
   names, and full model metadata (context, cost, capabilities).  This is
   the primary database.

2. **Hermes overlays** — transport type, auth patterns, aggregator flags,
   and additional env vars that models.dev doesn't track.  Small dict,
   maintained here.

3. **User config** (``providers:`` section in config.yaml) — user-defined
   endpoints and overrides.  Merged on top of everything else.

Other modules import from this file.  No parallel registries.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from utils import base_url_host_matches, base_url_hostname

logger = logging.getLogger(__name__)


# -- Hermes overlay ----------------------------------------------------------
# Hermes-specific metadata that models.dev doesn't provide.

@dataclass(frozen=True)
class HermesOverlay:
    """Hermes-specific provider metadata layered on top of models.dev."""

    transport: str = "openai_chat"        # openai_chat | anthropic_messages | codex_responses
    is_aggregator: bool = False
    auth_type: str = "api_key"            # api_key | oauth_device_code | oauth_external | external_process
    extra_env_vars: Tuple[str, ...] = ()  # env vars models.dev doesn't list
    base_url_override: str = ""           # override if models.dev URL is wrong/missing
    base_url_env_var: str = ""            # env var for user-custom base URL


HERMES_OVERLAYS: Dict[str, HermesOverlay] = {
    "custom": HermesOverlay(
        transport="openai_chat",
        auth_type="api_key",
        extra_env_vars=("OPENAI_API_KEY", "CUSTOM_API_KEY"),
        base_url_env_var="OPENAI_BASE_URL",
    ),
    "openai-api": HermesOverlay(
        transport="codex_responses",
        auth_type="api_key",
        base_url_override="https://api.openai.com/v1",
        base_url_env_var="OPENAI_BASE_URL",
    ),
    "lmstudio": HermesOverlay(
        transport="openai_chat",
        auth_type="api_key",
        extra_env_vars=("LM_API_KEY",),
        base_url_override="http://127.0.0.1:1234/v1",
        base_url_env_var="LM_BASE_URL",
    ),
}


# -- Resolved provider -------------------------------------------------------
# The merged result of models.dev + overlay + user config.

@dataclass
class ProviderDef:
    """Complete provider definition — merged from all sources."""

    id: str
    name: str
    transport: str                        # openai_chat | anthropic_messages | codex_responses
    api_key_env_vars: Tuple[str, ...]     # all env vars to check for API key
    base_url: str = ""
    base_url_env_var: str = ""
    is_aggregator: bool = False
    auth_type: str = "api_key"
    doc: str = ""
    source: str = ""                      # "models.dev", "horo", "user-config"


# -- Aliases ------------------------------------------------------------------
# Maps human-friendly / legacy names to canonical provider IDs.
# Uses models.dev IDs where possible.

ALIASES: Dict[str, str] = {
    "custom": "custom",
    "local": "custom",
    "openai": "custom",
    "lmstudio": "lmstudio",
    "lm-studio": "lmstudio",
    "lm_studio": "lmstudio",
    "ollama": "custom",
    "vllm": "custom",
    "llamacpp": "custom",
    "llama.cpp": "custom",
    "llama-cpp": "custom",
}


# -- Display labels -----------------------------------------------------------
# Built dynamically from models.dev + overlays.  Fallback for providers
# not in the catalog.

_LABEL_OVERRIDES: Dict[str, str] = {
    "custom": "Custom OpenAI-compatible",
    "lmstudio": "LM Studio",
    "openai-api": "OpenAI API",
}


# -- Transport → API mode mapping ---------------------------------------------

TRANSPORT_TO_API_MODE: Dict[str, str] = {
    "openai_chat": "chat_completions",
    "anthropic_messages": "anthropic_messages",
    "codex_responses": "codex_responses",
    "bedrock_converse": "bedrock_converse",
}


# -- Helper functions ---------------------------------------------------------

def normalize_provider(name: str) -> str:
    """Resolve aliases and normalise casing to a canonical provider id.

    Returns the canonical id string.  Does *not* validate that the id
    corresponds to a known provider.
    """
    key = name.strip().lower()
    return ALIASES.get(key, key)


def get_provider(name: str) -> Optional[ProviderDef]:
    """Look up an enterprise-lite built-in provider by id or alias.

    In this downstream fork, bundled provider surface is intentionally reduced
    to the small allowlist declared in ``HERMES_OVERLAYS``. models.dev remains
    available for metadata elsewhere, but it must not silently reintroduce
    public providers as first-class built-ins.
    """
    canonical = normalize_provider(name)

    overlay = HERMES_OVERLAYS.get(canonical)
    if overlay is None:
        return None

    # Try to enrich from models.dev when the allowed provider also exists there.
    try:
        from agent.models_dev import get_provider_info as _mdev_provider
        mdev_info = _mdev_provider(canonical)
    except Exception:
        mdev_info = None

    if mdev_info is not None:
        transport = overlay.transport if overlay else "openai_chat"
        is_agg = overlay.is_aggregator if overlay else False
        auth = overlay.auth_type if overlay else "api_key"
        base_url_env = overlay.base_url_env_var if overlay else ""
        base_url_override = overlay.base_url_override if overlay else ""

        env_vars = list(mdev_info.env)
        if overlay and overlay.extra_env_vars:
            for ev in overlay.extra_env_vars:
                if ev not in env_vars:
                    env_vars.append(ev)

        return ProviderDef(
            id=canonical,
            name=mdev_info.name,
            transport=transport,
            api_key_env_vars=tuple(env_vars),
            base_url=base_url_override or mdev_info.api,
            base_url_env_var=base_url_env,
            is_aggregator=is_agg,
            auth_type=auth,
            doc=mdev_info.doc,
            source="models.dev",
        )

    return ProviderDef(
        id=canonical,
        name=_LABEL_OVERRIDES.get(canonical, canonical),
        transport=overlay.transport,
        api_key_env_vars=overlay.extra_env_vars,
        base_url=overlay.base_url_override,
        base_url_env_var=overlay.base_url_env_var,
        is_aggregator=overlay.is_aggregator,
        auth_type=overlay.auth_type,
        source="horo",
    )


def get_label(provider_id: str) -> str:
    """Get a human-readable display name for a provider."""
    canonical = normalize_provider(provider_id)

    # Check label overrides first
    if canonical in _LABEL_OVERRIDES:
        return _LABEL_OVERRIDES[canonical]

    # Try models.dev
    pdef = get_provider(canonical)
    if pdef:
        return pdef.name

    return canonical




def is_aggregator(provider: str) -> bool:
    """Return True when the provider is a multi-model aggregator."""
    provider_norm = normalize_provider(provider or "")
    if provider_norm.startswith("custom:"):
        return True
    pdef = get_provider(provider_norm)
    return pdef.is_aggregator if pdef else False


# Flat-namespace resellers (e.g. opencode-go, opencode-zen) are flagged
# ``is_aggregator=True`` because their live ``/v1/models`` returns bare model
# IDs ("deepseek-v4-flash") rather than ``vendor/model`` routing slugs — the
# model-switch resolver relies on that flag to search their flat catalog
# (see model_switch.py step d). But they are NOT routing aggregators: every
# model they list is a first-party model served under their own subscription,
# not a passthrough route to another provider's endpoint. The picker dedup
# (build_models_payload) must treat them differently from true routers like
# OpenRouter — a reseller's first-party "minimax-m3" must never be stripped
# just because a user's custom proxy also happens to serve a same-named model.
_FLAT_NAMESPACE_RESELLERS: frozenset[str] = frozenset({
    # Use normalized provider IDs: normalize_provider("opencode-zen") -> "opencode".
    "opencode-go",
    "opencode",
})


def is_routing_aggregator(provider: str) -> bool:
    """Return True only for TRUE routing aggregators (e.g. OpenRouter, named
    ``custom:*`` proxies) — those that route bare/vendor-slugged model names
    to *other* providers' endpoints.

    Distinct from :func:`is_aggregator`, which also reports True for
    flat-namespace resellers (opencode-go/zen) whose catalog is entirely
    first-party. Use this gate when the question is "would selecting this
    model silently re-route the call away from the user's intended provider?"
    — i.e. the picker dedup. Resellers answer no: their listed models are
    their own, so their rows must not be deduped against user proxies.
    """
    provider_norm = normalize_provider(provider or "")
    if provider_norm in _FLAT_NAMESPACE_RESELLERS:
        return False
    return is_aggregator(provider_norm)


def host_mandated_api_mode(base_url: str = "") -> Optional[str]:
    """Return the wire protocol a specific endpoint *requires*, or None.

    Some hosts only accept one API mode and reject the others outright:
      - api.openai.com only accepts the Responses API for its (reasoning)
        models when tools + reasoning are in play (chat/completions 400s).
      - api.anthropic.com / ``…/anthropic`` suffixes speak native Messages.
      - Kimi's ``/coding`` endpoint speaks native Messages.
      - AWS Bedrock runtime hosts speak Converse.

    These are *mandatory* — a session carrying a stale api_mode (e.g. a
    /model switch that kept the previous provider's ``chat_completions``)
    must be overridden to the host's required mode, not merely filled in
    when empty. Generic / unknown endpoints return None so an explicitly
    configured api_mode on them is never clobbered.
    """
    if not base_url:
        return None
    url_lower = base_url.rstrip("/").lower()
    hostname = base_url_hostname(base_url)
    # Exact-hostname matching only — never bare substring — so lookalike hosts
    # (api.openai.com.attacker.test) and path-segment spoofs
    # (proxy.test/api.openai.com/v1) are NOT treated as the real endpoint. (#32243)
    if hostname == "api.kimi.com" and "/coding" in url_lower:
        return "anthropic_messages"
    if hostname == "api.anthropic.com" or url_lower.endswith("/anthropic"):
        return "anthropic_messages"
    if hostname == "api.openai.com":
        return "codex_responses"
    if hostname.startswith("bedrock-runtime.") and base_url_host_matches(base_url, "amazonaws.com"):
        return "bedrock_converse"
    return None


def determine_api_mode(provider: str, base_url: str = "") -> str:
    """Determine the API mode (wire protocol) for a provider/endpoint.

    Resolution order:
      1. Host-mandated mode (special endpoints that only accept one protocol).
      2. Known provider → transport → TRANSPORT_TO_API_MODE.
      3. Direct provider checks (bedrock).
      4. Default: 'chat_completions'.
    """
    mandated = host_mandated_api_mode(base_url)
    if mandated is not None:
        return mandated

    pdef = get_provider(provider)
    if pdef is not None:
        return TRANSPORT_TO_API_MODE.get(pdef.transport, "chat_completions")

    # Direct provider checks for providers not in HERMES_OVERLAYS
    if provider == "bedrock":
        return "bedrock_converse"

    return "chat_completions"


# -- Provider from user config ------------------------------------------------

def resolve_user_provider(name: str, user_config: Dict[str, Any]) -> Optional[ProviderDef]:
    """Resolve a provider from the user's config.yaml ``providers:`` section.

    Args:
        name: Provider name as given by the user.
        user_config: The ``providers:`` dict from config.yaml.

    Returns:
        ProviderDef if found, else None.
    """
    if not user_config or not isinstance(user_config, dict):
        return None

    entry = user_config.get(name)
    if not isinstance(entry, dict):
        return None

    # Extract fields
    display_name = entry.get("name", "") or name
    api_url = entry.get("api", "") or entry.get("url", "") or entry.get("base_url", "") or ""
    key_env = entry.get("key_env", "") or ""
    transport = entry.get("transport", "openai_chat") or "openai_chat"

    env_vars: List[str] = []
    if key_env:
        env_vars.append(key_env)

    return ProviderDef(
        id=name,
        name=display_name,
        transport=transport,
        api_key_env_vars=tuple(env_vars),
        base_url=api_url,
        is_aggregator=False,
        auth_type="api_key",
        source="user-config",
    )


def custom_provider_slug(display_name: str) -> str:
    """Build a canonical slug for a custom_providers entry.

    Matches the convention used by runtime_provider and credential_pool
    (``custom:<normalized-name>``).  Centralised here so all call-sites
    produce identical slugs.
    """
    return "custom:" + display_name.strip().lower().replace(" ", "-")


def resolve_custom_provider(
    name: str,
    custom_providers: Optional[List[Dict[str, Any]]],
) -> Optional[ProviderDef]:
    """Resolve a provider from the user's config.yaml ``custom_providers`` list."""
    if not custom_providers or not isinstance(custom_providers, list):
        return None

    requested = (name or "").strip().lower()
    if not requested:
        return None

    # If the stored provider is the bare string "custom" (corrupt state
    # from a prior model-switch bug), fall back to the first custom
    # provider entry so existing configs self-heal.  (GH #17478)
    bare_custom_fallback = requested == "custom"
    first_valid: Optional[Tuple[str, str, Tuple[str, ...]]] = None

    for entry in custom_providers:
        if not isinstance(entry, dict):
            continue

        display_name = (entry.get("name") or "").strip()
        api_url = (
            entry.get("base_url", "")
            or entry.get("url", "")
            or entry.get("api", "")
            or ""
        ).strip()
        if not display_name or not api_url:
            continue

        key_env = (entry.get("key_env") or "").strip()
        env_vars: List[str] = []
        if key_env:
            env_vars.append(key_env)

        # Stash the first valid entry for bare-"custom" fallback
        if first_valid is None:
            first_valid = (display_name, api_url, tuple(env_vars))

        slug = custom_provider_slug(display_name)
        if requested not in {display_name.lower(), slug}:
            continue

        return ProviderDef(
            id=slug,
            name=display_name,
            transport="openai_chat",
            api_key_env_vars=tuple(env_vars),
            base_url=api_url,
            is_aggregator=False,
            auth_type="api_key",
            source="user-config",
        )

    # Self-heal: bare "custom" matched nothing — return first valid entry
    if bare_custom_fallback and first_valid:
        dname, aurl, denv = first_valid
        slug = custom_provider_slug(dname)
        return ProviderDef(
            id=slug,
            name=dname,
            transport="openai_chat",
            api_key_env_vars=denv,
            base_url=aurl,
            is_aggregator=False,
            auth_type="api_key",
            source="user-config",
        )

    return None


def resolve_provider_full(
    name: str,
    user_providers: Optional[Dict[str, Any]] = None,
    custom_providers: Optional[List[Dict[str, Any]]] = None,
) -> Optional[ProviderDef]:
    """Full resolution chain for enterprise-lite.

    Resolution order:
      1. user-defined providers from config.yaml (raw name wins)
      2. built-in allowlist from ``HERMES_OVERLAYS``
      3. user-defined providers again via canonical name
      4. saved custom providers from config.yaml

    Public models.dev providers are intentionally *not* revived here.
    """
    canonical = normalize_provider(name)
    raw = name.strip().lower()

    if user_providers:
        user_pdef = resolve_user_provider(raw, user_providers)
        if user_pdef is not None:
            return user_pdef

    pdef = get_provider(canonical)
    if pdef is not None:
        return pdef

    if user_providers:
        user_pdef = resolve_user_provider(canonical, user_providers)
        if user_pdef is not None:
            return user_pdef
        user_pdef = resolve_user_provider(raw, user_providers)
        if user_pdef is not None:
            return user_pdef

    custom_pdef = resolve_custom_provider(name, custom_providers)
    if custom_pdef is not None:
        return custom_pdef

    return None
