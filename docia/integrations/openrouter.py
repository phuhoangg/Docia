"""
Docia OpenRouter Provider for Multi-Vision Language Model Access

OpenRouter provider implementation supporting multiple Vision Language Models.
Uses OpenAI-compatible API with OpenRouter's unified endpoint.
"""

import logging
from typing import List, Dict, Any

from .base import BaseProvider, ProviderError
from ..core.config import DociaConfig

logger = logging.getLogger(__name__)


class OpenRouterProvider(BaseProvider):
    """OpenRouter Multi-Vision Language Model provider

    Provides access to multiple Vision Language Models through OpenRouter's unified API.
    """

    def __init__(self, config: DociaConfig):
        super().__init__(config)

        if not config.openrouter_api_key:
            raise ValueError("OpenRouter API key required for Vision Language Model provider")

        # Import OpenAI client for Vision Language Model operations
        try:
            from openai import AsyncOpenAI
            self.client = AsyncOpenAI(
                api_key=config.openrouter_api_key,
                base_url="https://openrouter.ai/api/v1"
            )
        except ImportError:
            raise ImportError("OpenAI library required for Vision Language Model operations. Install with: pip install openai")

        self.model = config.vision_model  # Selected Vision Language Model

    async def process_text_messages(
        self,
        messages: List[Dict[str, Any]],
        max_tokens: int = 300,
        temperature: float = 0.3
    ) -> str:
        """Process text-only messages through OpenRouter's Language Model access"""
        try:
            response = await self.client.chat.completions.create(
                model=self.config.model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                extra_body= {
                      "usage": {
                        "include": True,
                      },
                },
            )

            result = response.choices[0].message.content.strip()
            logger.debug(f"OpenRouter text response: {result[:50]}...")

            # Track Vision Language Model cost if available
            if hasattr(response, 'usage') and hasattr(response.usage, 'cost'):
                self.last_api_cost = response.usage.cost
                self.total_cost += response.usage.cost
                logger.debug(f"OpenRouter Vision Language Model cost: ${response.usage.cost}")
            else:
                self.last_api_cost = None

            return result

        except Exception as e:
            logger.error(f"OpenRouter text processing failed: {e}")
            raise ProviderError(f"Text processing failed: {e}", "openrouter")

    async def process_multimodal_messages(
        self,
        messages: List[Dict[str, Any]],
        max_tokens: int = 300,
        temperature: float = 0.3
    ) -> str:
        """Process multimodal messages through OpenRouter's Vision Language Model access"""
        try:
            # Process messages for Vision Language Model input
            processed_messages = self._prepare_openai_messages(messages)

            response = await self.client.chat.completions.create(
                model=self.model,  # Selected Vision Language Model
                messages=processed_messages,
                max_tokens=max_tokens,
                temperature=temperature,
                extra_body={
                    "usage": {
                        "include": True,
                    },
                },
            )

            result = response.choices[0].message.content.strip()
            logger.debug(f"OpenRouter multimodal response: {result[:50]}...")

            # Track Vision Language Model cost if available
            if hasattr(response, 'usage') and hasattr(response.usage, 'cost'):
                self.last_api_cost = response.usage.cost
                self.total_cost += response.usage.cost
                logger.debug(f"OpenRouter Vision Language Model cost: ${response.usage.cost}")
            else:
                self.last_api_cost = None

            return result

        except Exception as e:
            logger.error(f"OpenRouter multimodal processing failed: {e}")
            raise ProviderError(f"Multimodal processing failed: {e}", "openrouter")

    def _prepare_openai_messages(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Prepare messages for OpenRouter Vision Language Model by converting image paths to data URLs"""
        processed_messages = []

        for message in messages:
            if message["role"] == "system":
                # System messages remain text-only
                processed_messages.append(message)
            elif message["role"] == "user" and isinstance(message["content"], list):
                # User message with multimodal content for Vision Language Model
                processed_content = []

                for content_item in message["content"]:
                    if content_item["type"] == "text":
                        processed_content.append(content_item)
                    elif content_item["type"] == "image_path":
                        # Convert image path to OpenRouter Vision Language Model format
                        image_path = content_item["image_path"]
                        if self._validate_image_path(image_path):
                            image_data_url = self._create_image_data_url(image_path)
                            processed_content.append({
                                "type": "image_url",
                                "image_url": {
                                    "url": image_data_url,
                                    "detail": content_item.get("detail", "high")
                                }
                            })
                        else:
                            logger.warning(f"Skipping invalid image path for Vision Language Model: {image_path}")
                    else:
                        # Pass through other content types to Vision Language Model
                        processed_content.append(content_item)

                processed_messages.append({
                    "role": message["role"],
                    "content": processed_content
                })
            else:
                # Regular text message
                processed_messages.append(message)

        return processed_messages
