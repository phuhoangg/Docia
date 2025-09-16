"""
Docia Provider Interface for Vision Language Model Operations

Base interface for AI providers with Vision Language Model capabilities.
"""

import base64
from abc import ABC, abstractmethod
from typing import List, Optional
from pathlib import Path
from dataclasses import dataclass
import logging

from ..core.config import DociaConfig

logger = logging.getLogger(__name__)


@dataclass
class APIResult:
    """Vision AI API response container with cost tracking"""
    text: str
    cost: Optional[float] = None


class BaseProvider(ABC):
    """Base class for Vision Language Model providers"""

    def __init__(self, config: DociaConfig):
        self.config = config
        self.last_api_cost: Optional[float] = None
        self.total_cost: float = 0.0

    @abstractmethod
    async def process_text_messages(
        self,
        messages: List[dict],
        max_tokens: int = 512,
        temperature: float = 0.3
    ) -> str:
        """Process text-only messages through the provider API"""
        pass

    @abstractmethod
    async def process_multimodal_messages(
        self,
        messages: List[dict],
        max_tokens: int = 300,
        temperature: float = 0.3
    ) -> str:
        """Process messages with text and images through the Vision Language Model API"""
        pass

    def get_last_cost(self) -> Optional[float]:
        """Get cost of the last Vision Language Model API call"""
        return self.last_api_cost

    def get_total_cost(self) -> float:
        """Get total accumulated Vision AI processing cost"""
        return self.total_cost

    def reset_cost_tracking(self):
        """Reset Vision AI cost tracking"""
        self.last_api_cost = None
        self.total_cost = 0.0

    # Helper methods for image handling (shared by all providers)

    def _encode_image(self, image_path: str) -> str:
        """Encode image to base64 for Vision Language Model API calls"""
        try:
            with open(image_path, 'rb') as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                return encoded_string
        except Exception as e:
            logger.error(f"Failed to encode image {image_path}: {e}")
            raise

    def _create_image_data_url(self, image_path: str) -> str:
        """Create data URL for Vision Language Model image input"""
        encoded_image = self._encode_image(image_path)
        return f"data:image/jpeg;base64,{encoded_image}"

    def _validate_image_path(self, image_path: str) -> bool:
        """Validate image path for Vision Language Model processing"""
        path = Path(image_path)
        return path.exists() and path.is_file()


class ProviderError(Exception):
    """Exception raised by Vision Language Model provider operations"""

    def __init__(self, message: str, provider: str, image_path: str = None):
        self.provider = provider
        self.image_path = image_path
        super().__init__(message)
