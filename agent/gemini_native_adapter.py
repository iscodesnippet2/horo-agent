"""Disabled Gemini native adapter for the lite build."""


def is_native_gemini_base_url(*args, **kwargs) -> bool:
    return False


def bare_gemini_model_id(model):
    return model


def probe_gemini_tier(*args, **kwargs):
    return None


class GeminiNativeClient:
    def __init__(self, *args, **kwargs):
        raise RuntimeError("Gemini provider is disabled; use an internal OpenAI-compatible endpoint.")


class AsyncGeminiNativeClient(GeminiNativeClient):
    pass
