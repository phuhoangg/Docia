"""
Docia OpenAI Provider for GPT-4 Vision Language Model

OpenAI GPT-4V provider implementation for Vision Language Model operations.
"""

import logging
from typing import List, Dict, Any

from .base import BaseProvider, ProviderError
from ..core.config import DociaConfig

logger = logging.getLogger(__name__)


class OpenAIProvider(BaseProvider):
    """OpenAI GPT-4 Vision Language Model provider

    Implements Vision Language Model capabilities using OpenAI's GPT-4V.
    """
    
    def __init__(self, config: DociaConfig):
        super().__init__(config)

        if not config.openai_api_key:
            raise ValueError("OpenAI API key required for Vision Language Model provider")

        # Import OpenAI client for Vision Language Model operations
        try:
            from openai import AsyncOpenAI
            self.client = AsyncOpenAI(api_key=config.openai_api_key)
        except ImportError:
            raise ImportError("OpenAI library required for Vision Language Model operations. Install with: pip install openai")

        self.model = config.vision_model  # GPT-4 Vision Language Model
    
    async def process_text_messages(
        self,
        messages: List[Dict[str, Any]],
        max_tokens: int = 300,
        temperature: float = 0.3
    ) -> str:
        """Process text-only messages through OpenAI's Language Model"""
        try:
            response = await self.client.chat.completions.create(
                model=self.config.model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            content = response.choices[0].message.content
            if content is None:
                logger.error("OpenAI returned None content for text processing")
                raise ProviderError("OpenAI returned None content", "openai")

            result = content.strip()
            logger.debug(f"OpenAI text response: {result[:50]}...")

            return result
            
        except Exception as e:
            logger.error(f"OpenAI text processing failed: {e}")
            raise ProviderError(f"Text processing failed: {e}", "openai")
    
    async def process_multimodal_messages(
        self,
        messages: List[Dict[str, Any]],
        max_tokens: int = 300,
        temperature: float = 0.3
    ) -> str:
        """Process multimodal messages through OpenAI GPT-4 Vision Language Model"""
        try:
            # Process messages for Vision Language Model input
            processed_messages = self._prepare_openai_messages(messages)

            response = await self.client.chat.completions.create(
                model=self.model,  # GPT-4 Vision Language Model
                messages=processed_messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            content = response.choices[0].message.content
            if content is None:
                logger.error("OpenAI returned None content for multimodal processing")
                raise ProviderError("OpenAI returned None content", "openai")

            result = content.strip()
            logger.debug(f"OpenAI multimodal response: {result[:50]}...")

            return result
            
        except Exception as e:
            logger.error(f"OpenAI multimodal processing failed: {e}")
            raise ProviderError(f"Multimodal processing failed: {e}", "openai")
    
    def _prepare_openai_messages(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Prepare messages for OpenAI Vision Language Model by converting image paths to data URLs"""
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
                        # Convert image path to Vision Language Model format
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