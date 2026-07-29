"""Disabled STT provider protocol for the lite build."""


class TranscriptionProvider:
    name = "disabled"

    def transcribe(self, *args, **kwargs):
        raise RuntimeError("Speech-to-text providers are disabled in the lite build.")
