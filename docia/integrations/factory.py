"""
Docia Provider Factory for Vision Language Model Integration

Factory pattern for creating Vision Language Model provider instances.
"""

from typing import Union

from .base import BaseProvider
from .openai import OpenAIProvider
from .openrouter import OpenRouterProvider
from ..core.config import DociaConfig


def create_provider(config: DociaConfig) -> BaseProvider:
    """
    Create Vision Language Model provider based on configuration

    Args:
        config: Docia intelligence configuration

    Returns:
        Configured Vision Language Model provider instance

    Raises:
        ValueError: If provider is not supported
    """
    if config.provider == "openai":
        return OpenAIProvider(config)
    elif config.provider == "openrouter":
        return OpenRouterProvider(config)
    else:
        raise ValueError(f"Unsupported provider: {config.provider}")


def get_available_providers() -> list[str]:
    """Get list of available Vision Language Model provider names"""
    return ["openai", "openrouter"]


def validate_provider_config(provider: str, config: DociaConfig) -> bool:
    """
    Validate Vision Language Model provider configuration

    Args:
        provider: Vision Language Model provider name
        config: Configuration to validate

    Returns:
        True if configuration is valid

    Raises:
        ValueError: If configuration is invalid
    """
    if provider not in get_available_providers():
        raise ValueError(f"Unknown Vision Language Model provider: {provider}")

    if provider == "openai":
        if not config.openai_api_key:
            raise ValueError("OpenAI API key required for Vision Language Model provider")
        if not config.vision_model:
            raise ValueError("Vision Language Model is required")
        return True

    elif provider == "openrouter":
        if not config.openrouter_api_key:
            raise ValueError("OpenRouter API key required for Vision Language Model provider")
        if not config.vision_model:
            raise ValueError("Vision Language Model is required")
        return True
    
    return False