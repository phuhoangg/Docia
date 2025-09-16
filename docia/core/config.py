"""
Docia Intelligence Engine Configuration

VisionLM-powered document intelligence configuration.
Optimized for maximum understanding and minimum complexity.
"""

import os
from dataclasses import dataclass, field
from typing import Tuple, Optional, Dict, Any
from pathlib import Path


@dataclass
class DociaConfig:
    """Docia Intelligence Engine Configuration

    Smart defaults for VisionLM-powered document intelligence.
    """

    # Vision Intelligence Processing
    pdf_render_scale: float = 2.0  # Vision quality multiplier (higher = better intelligence)
    pdf_max_image_size: Tuple[int, int] = (1200, 1200)  # Maximum vision resolution
    jpeg_quality: int = 90         # Vision quality preservation
    thumbnail_size: Tuple[int, int] = (256, 256)      # Quick preview intelligence

    # Intelligence Settings
    vision_detail: str = "high"    # Maximum vision detail for optimal understanding

    # Knowledge Storage
    storage_type: str = "local"          # Knowledge storage type: local, memory, s3
    local_storage_path: str = "./docia_data"  # Intelligence storage location

    # Vision AI Provider Configuration
    provider: str = "openrouter"         # Vision AI provider: openai, openrouter
    model: str = "gpt-4o"                # Primary intelligence model
    vision_model: str = "gpt-4o"         # Vision intelligence model

    # Vision AI Security
    openai_api_key: Optional[str] = None
    openrouter_api_key: Optional[str] = None

    # Adaptive Intelligence Settings
    max_agent_iterations: int = 5    # Maximum adaptive reasoning cycles
    max_pages_per_task: int = 6      # Pages per intelligence cycle
    max_tasks_per_plan: int = 4      # Initial intelligence tasks

    # Conversation Intelligence Settings
    max_conversation_turns: int = 8  # Conversation memory depth
    turns_to_summarize: int = 5      # Conversation summary window
    turns_to_keep_full: int = 3      # Recent conversation retention

    # Intelligence Logging
    log_level: str = "INFO"          # Intelligence engine logging
    log_requests: bool = False       # Request visibility for debugging

    def __post_init__(self):
        """Initialize and validate intelligence engine configuration"""
        # Create knowledge storage directory
        if self.storage_type == "local":
            Path(self.local_storage_path).mkdir(parents=True, exist_ok=True)

        # Load Vision AI keys from environment
        if not self.openai_api_key:
            self.openai_api_key = os.getenv("OPENAI_API_KEY")

        if not self.openrouter_api_key:
            self.openrouter_api_key = os.getenv("OPENROUTER_API_KEY")

        # Set provider-specific intelligence defaults
        self._set_provider_defaults()

        # Skip validation for test environments
        if self.openai_api_key != "test-key" and self.openrouter_api_key != "test-key":
            # Validate Vision AI provider requirements
            if self.provider == "openai" and not self.openai_api_key:
                raise ValueError("OpenAI API key required for Vision AI")

            if self.provider == "openrouter" and not self.openrouter_api_key:
                raise ValueError("OpenRouter API key required for Vision AI")

        # Validate intelligence quality settings
        if self.pdf_render_scale <= 0:
            raise ValueError("Vision quality scale must be positive")

        if self.jpeg_quality < 1 or self.jpeg_quality > 100:
            raise ValueError("Vision quality must be between 1 and 100")

    def _set_provider_defaults(self):
        """Set optimal Vision AI defaults by provider"""
        provider_defaults = {
            "openai": {
                "model": "gpt-4o",
                "vision_model": "gpt-4o"
            },
            "openrouter": {
                "model": "openai/gpt-4o",
                "vision_model": "google/gemini-2.5-flash"
            }
        }

        if self.provider in provider_defaults:
            defaults = provider_defaults[self.provider]
            # Apply provider-specific model defaults
            if self.model == "gpt-4o":
                self.model = defaults["model"]
            if self.vision_model == "gpt-4o":
                self.vision_model = defaults["vision_model"]

    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'DociaConfig':
        """Create intelligence configuration from dictionary"""
        return cls(**config_dict)

    @classmethod
    def from_env(cls) -> 'DociaConfig':
        """Create intelligence configuration from environment"""
        config_dict = {}

        # Map environment variables to intelligence settings
        env_mapping = {
            'DOCIA_PROVIDER': 'provider',
            'DOCIA_MODEL': 'model',
            'DOCIA_VISION_MODEL': 'vision_model',
            'DOCIA_STORAGE_PATH': 'local_storage_path',
            'DOCIA_STORAGE_TYPE': 'storage_type',
            'DOCIA_JPEG_QUALITY': 'jpeg_quality',
            'DOCIA_VISION_DETAIL': 'vision_detail',
            'DOCIA_MAX_AGENT_ITERATIONS': 'max_agent_iterations',
            'DOCIA_MAX_PAGES_PER_TASK': 'max_pages_per_task',
            'DOCIA_MAX_TASKS_PER_PLAN': 'max_tasks_per_plan',
            'DOCIA_MAX_CONVERSATION_TURNS': 'max_conversation_turns',
            'DOCIA_LOG_LEVEL': 'log_level',
            'DOCIA_LOG_REQUESTS': 'log_requests',
        }

        for env_var, config_field in env_mapping.items():
            value = os.getenv(env_var)
            if value is not None:
                # Convert environment values to appropriate types
                if config_field in ['jpeg_quality', 'max_agent_iterations', 'max_pages_per_task', 'max_tasks_per_plan', 'max_conversation_turns']:
                    config_dict[config_field] = int(value)
                elif config_field in ['log_requests']:
                    config_dict[config_field] = value.lower() in ('true', '1', 'yes')
                else:
                    config_dict[config_field] = value

        return cls(**config_dict)

    def get_query_config(self) -> Dict[str, Any]:
        """Get intelligence query configuration"""
        return {
            'vision_detail': self.vision_detail,
            'model': self.model
        }

    def validate_provider_config(self) -> None:
        """Validate Vision AI provider configuration"""
        if self.provider == "openai":
            if not self.openai_api_key:
                raise ValueError("OpenAI API key required for Vision AI")
        elif self.provider == "openrouter":
            if not self.openrouter_api_key:
                raise ValueError("OpenRouter API key required for Vision AI")
        else:
            raise ValueError(f"Unsupported Vision AI provider: {self.provider}")
