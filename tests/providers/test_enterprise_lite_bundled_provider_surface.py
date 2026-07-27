from pathlib import Path
import sys

import providers as provider_registry


def test_bundled_provider_surface_reduced_to_custom(monkeypatch):
    repo_bundled = Path(__file__).resolve().parents[2] / "plugins" / "model-providers"
    assert repo_bundled.is_dir()

    for key in list(sys.modules):
        if key.startswith("plugins.model_providers."):
            del sys.modules[key]

    monkeypatch.setattr(provider_registry, "_BUNDLED_PLUGINS_DIR", repo_bundled)
    monkeypatch.setattr(provider_registry, "_user_plugins_dir", lambda: None)
    monkeypatch.setattr(provider_registry, "_REGISTRY", {})
    monkeypatch.setattr(provider_registry, "_ALIASES", {})
    monkeypatch.setattr(provider_registry, "_discovered", False)

    profiles = provider_registry.list_providers()
    names = sorted(profile.name for profile in profiles)

    assert names == ["custom"]
    assert provider_registry.get_provider_profile("custom") is not None
    assert provider_registry.get_provider_profile("openrouter") is None
    assert provider_registry.get_provider_profile("anthropic") is None
    assert provider_registry.get_provider_profile("nvidia") is None
