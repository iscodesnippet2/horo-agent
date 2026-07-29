"""Disabled TTS provider protocol for the lite build."""


class TTSProvider:
    name = "disabled"

    def synthesize(self, *args, **kwargs):
        raise RuntimeError("Text-to-speech providers are disabled in the lite build.")
