"""Status command for the horo lite CLI."""

from __future__ import annotations

import sys
from pathlib import Path

from hermes_cli.colors import Colors, color
from hermes_cli.config import get_env_path, load_config
from hermes_cli.runtime_provider import resolve_requested_provider

PROJECT_ROOT = Path(__file__).parent.parent.resolve()


def check_mark(ok: bool) -> str:
    return color("✓", Colors.GREEN) if ok else color("✗", Colors.RED)


def _configured_model_label(config: dict) -> str:
    model_cfg = config.get("model")
    if isinstance(model_cfg, dict):
        model = (model_cfg.get("default") or model_cfg.get("name") or "").strip()
    elif isinstance(model_cfg, str):
        model = model_cfg.strip()
    else:
        model = ""
    return model or "(not set)"


def show_status(args) -> None:
    """Show local-only status for the lite build."""
    print()
    print(color("┌─────────────────────────────────────────────────────────┐", Colors.CYAN))
    print(color("│                   Horo Agent Lite Status                │", Colors.CYAN))
    print(color("└─────────────────────────────────────────────────────────┘", Colors.CYAN))

    try:
        config = load_config()
    except Exception:
        config = {}

    env_path = get_env_path()
    print()
    print(color("◆ Environment", Colors.CYAN, Colors.BOLD))
    print(f"  Project:      {PROJECT_ROOT}")
    print(f"  Python:       {sys.version.split()[0]}")
    print(f"  .env file:    {check_mark(env_path.exists())} {'exists' if env_path.exists() else 'not found'}")

    print()
    print(color("◆ Model", Colors.CYAN, Colors.BOLD))
    print(f"  Model:        {_configured_model_label(config)}")
    print(f"  Provider:     {resolve_requested_provider() or 'custom/local'}")

    terminal = config.get("terminal", {}) if isinstance(config.get("terminal"), dict) else {}
    print()
    print(color("◆ Terminal", Colors.CYAN, Colors.BOLD))
    print(f"  Backend:      {terminal.get('backend', 'local')}")
    print(f"  Working dir:  {terminal.get('cwd', '.')}")
    print(f"  Timeout:      {terminal.get('timeout', 60)}s")

    browser = config.get("browser", {}) if isinstance(config.get("browser"), dict) else {}
    print()
    print(color("◆ Browser", Colors.CYAN, Colors.BOLD))
    print(f"  Provider:     {browser.get('cloud_provider', 'local') or 'local'}")
    print(f"  Headed:       {'yes' if browser.get('headed') else 'no'}")
    print(f"  Private URLs: {'yes' if browser.get('allow_private_urls') else 'no'}")

    print()
    print(color("◆ Lite Build", Colors.CYAN, Colors.BOLD))
    print("  External messaging, cloud TTS/STT, managed Nous gateway, OAuth,")
    print("  cloud memory providers, and remote Skills Hub are disabled.")
