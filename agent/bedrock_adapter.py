"""Disabled Bedrock adapter for the lite build."""


def _disabled(*args, **kwargs):
    raise RuntimeError("Bedrock provider is disabled; use an internal OpenAI-compatible endpoint.")


def has_aws_credentials(*args, **kwargs) -> bool:
    return False


def resolve_aws_auth_env_var(*args, **kwargs):
    return None


def resolve_bedrock_region(*args, **kwargs):
    return None


def bedrock_model_ids_or_none(*args, **kwargs):
    return None


def discover_bedrock_models(*args, **kwargs):
    return []


def get_bedrock_context_length(*args, **kwargs):
    return None


def invalidate_runtime_client(*args, **kwargs):
    return None


call_converse = _disabled
convert_messages_to_converse = _disabled
convert_tools_to_converse = _disabled
build_converse_kwargs = _disabled
normalize_converse_response = _disabled
