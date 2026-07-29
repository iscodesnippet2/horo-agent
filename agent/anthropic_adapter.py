"""Disabled Anthropic adapter for the lite build."""


def _disabled(*args, **kwargs):
    raise RuntimeError("Anthropic provider is disabled; use an internal OpenAI-compatible endpoint.")


def _is_oauth_token(*args, **kwargs) -> bool:
    return False


def _forbids_sampling_params(*args, **kwargs) -> bool:
    return False


def _model_name_is_kimi_family(*args, **kwargs) -> bool:
    return False


def sanitize_anthropic_kwargs(kwargs):
    return kwargs


def resolve_anthropic_token(*args, **kwargs):
    return None


def read_claude_code_credentials(*args, **kwargs):
    return None


def read_hermes_oauth_credentials(*args, **kwargs):
    return None


def refresh_anthropic_oauth_pure(*args, **kwargs):
    return None


def _refresh_oauth_token(*args, **kwargs):
    return None


def _write_claude_code_credentials(*args, **kwargs):
    return None


def _get_hermes_oauth_file(*args, **kwargs):
    return None


def build_anthropic_client(*args, **kwargs):
    return _disabled()


def build_anthropic_bedrock_client(*args, **kwargs):
    return _disabled()


def build_anthropic_kwargs(*args, **kwargs):
    return _disabled()


def create_anthropic_message(*args, **kwargs):
    return _disabled()


def convert_messages_to_anthropic(*args, **kwargs):
    return _disabled()


def convert_tools_to_anthropic(*args, **kwargs):
    return _disabled()


def _to_plain_data(value):
    return value


def _sanitize_replay_block(value):
    return value


_COMMON_BETAS = []
_OAUTH_ONLY_BETAS = []
_CONTEXT_1M_BETA = ""
