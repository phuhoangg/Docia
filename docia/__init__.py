"""
Docia - VisionLM-powered Documents Intelligence Solution

Transform documents into intelligent knowledge bases using Vision AI.
No vector databases required - just pure document understanding.
"""

__version__ = "0.1.0"

from .models.document import Document, Page, QueryResult, QueryMode
from .models.agent import ConversationMessage
from .core.config import DociaConfig
from .integrations import BaseProvider, create_provider
from .docia import Docia, create_docia, create_memory_docia

__all__ = [
    "Docia",
    "create_docia",
    "create_memory_docia",
    "Document",
    "Page",
    "QueryResult",
    "QueryMode",
    "ConversationMessage",
    "DociaConfig",
    "BaseProvider",
    "create_provider"
]