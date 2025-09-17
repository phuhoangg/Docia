"""
Docia - VisionLM-powered Documents Intelligence Solution

A multimodal RAG system that understands documents through vision intelligence.
No vector databases required.
"""

import asyncio
from typing import Optional, List, Dict, Any, Union, Callable
from pathlib import Path
import logging

from .models.document import (
    Document, Page, QueryResult, QueryMode,
    DocumentProcessRequest, QueryRequest, DocumentStatus
)
from .models.agent import ConversationMessage
from .core.config import DociaConfig
from .processors.factory import ProcessorFactory
from .storage.local import LocalStorage
from .storage.memory import InMemoryStorage
from .storage.base import BaseStorage
from .intelligence.summarizer import PageSummarizer
from .intelligence.orchestrator import Orchestrator
from .integrations import create_provider
from .utils.async_helpers import sync_wrapper, make_sync_version

logger = logging.getLogger(__name__)


class Docia:
    """
    Docia - VisionLM-powered Document Intelligence API

    Transform documents into intelligent knowledge bases using Vision AI.
    """
    
    def __init__(
        self,
        config: Optional[DociaConfig] = None,
        storage: Optional[BaseStorage] = None,
        api_key: Optional[str] = None
    ):
        """
        Initialize Docia Intelligence Engine

        Args:
            config: Intelligence configuration (uses smart defaults if None)
            storage: Knowledge storage backend (local filesystem if None)
            api_key: AI provider API key (can use environment variables)
        """
        # Initialize configuration
        if config is None:
            config = DociaConfig()
        
        # Override API key if provided
        if api_key:
            if config.provider == "openai":
                config.openai_api_key = api_key
        
        self.config = config
        
        # Initialize intelligence components
        self.processor_factory = ProcessorFactory(config)

        # Initialize knowledge storage
        if storage is None:
            if config.storage_type == "memory":
                self.storage = InMemoryStorage(config)
            else:
                self.storage = LocalStorage(config)
        else:
            self.storage = storage

        # Initialize Vision AI components
        try:
            self.provider = create_provider(config)
            if self.provider is None:
                raise ValueError("Failed to create Vision AI provider - check configuration")
        except Exception as e:
            logger.error(f"Failed to initialize Vision AI provider: {e}")
            raise ValueError(f"Vision AI provider initialization failed: {e}")

        self.summarizer = PageSummarizer(config)
        self.orchestrator = Orchestrator(self.provider, self.storage, config)
        
        logger.info(f"Docia Intelligence Engine initialized with {config.provider} Vision AI and {type(self.storage).__name__} knowledge storage")
    
    # Document Intelligence Operations

    async def add_document(
        self,
        file_path: Union[str, Path],
        document_id: Optional[str] = None,
        document_name: Optional[str] = None
    ) -> Document:
        """
        Add document to Docia's intelligence system

        Args:
            file_path: Path to document (PDF, images supported)
            document_id: Optional custom document identifier
            document_name: Optional custom document name

        Returns:
            Enhanced Document with intelligence metadata
        """
        file_path = str(file_path)
        logger.info(f"Adding document: {file_path}")
        
        # Process document with Vision AI
        processor = self.processor_factory.get_processor(file_path)
        document = await processor.process(file_path, document_id)

        # Override name if provided
        if document_name:
            document.name = document_name

        # Generate intelligence summary
        logger.info(f"Generating intelligence summary for {document.name}")
        document = await self.summarizer.summarize_document(document)

        # Store in knowledge base
        document.status = DocumentStatus.COMPLETED
        await self.storage.save_document(document)

        logger.info(f"Document {document.id} intelligence-ready: {document.name}")
        return document
    
    async def get_document(self, document_id: str) -> Optional[Document]:
        """Get a document by ID"""
        return await self.storage.get_document(document_id)
    
    async def list_documents(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """List all documents with metadata"""
        return await self.storage.list_documents(limit)
    
    async def delete_document(self, document_id: str) -> bool:
        """Delete a document and its associated files"""
        return await self.storage.delete_document(document_id)
    
    async def search_documents(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search documents by name and summary"""
        return await self.storage.search_documents(query, limit)
    
    # Intelligence Query Operations (Vision-based RAG)

    async def query(
        self,
        question: str,
        mode: QueryMode = QueryMode.AUTO,
        document_ids: Optional[List[str]] = None,
        max_pages: Optional[int] = None,
        stream: bool = False,
        conversation_history: Optional[List[ConversationMessage]] = None,
        task_update_callback: Optional[Any] = None
    ) -> QueryResult:
        """
        Query documents with Vision AI intelligence

        Args:
            question: User's question
            mode: Intelligence mode (Auto adapts automatically)
            document_ids: Target documents (None = all documents)
            max_pages: Maximum pages to analyze
            stream: Response streaming (future enhancement)
            conversation_history: Conversation context memory

        Returns:
            Intelligent QueryResult with answer and insights
        """
        logger.info(f"Vision AI processing query: {question}")

        try:
            # Execute adaptive Vision AI analysis
            agent_result = await self.orchestrator.process_query(question, conversation_history, task_update_callback)

            # Transform to API response format
            return QueryResult(
                query=agent_result.query,
                answer=agent_result.answer,
                selected_pages=agent_result.get_unique_pages(),
                mode=mode,
                confidence=self._calculate_confidence(agent_result),
                processing_time=agent_result.processing_time_seconds,
                total_cost=agent_result.total_cost,
                metadata={
                    'agent_iterations': agent_result.total_iterations,
                    'tasks_completed': len(agent_result.task_results),
                    'total_pages_analyzed': agent_result.get_total_pages_analyzed(),
                    'intelligence_mode': 'adaptive_vision_ai',
                    'engine': 'Docia VisionLM 1.0'
                }
            )
            
        except Exception as e:
            logger.error(f"Vision AI query failed: {e}")
            return QueryResult(
                query=question,
                answer=f"Docia Intelligence encountered an issue: {str(e)}",
                selected_pages=[],
                mode=mode,
                confidence=0.0,
                processing_time=0.0,
                total_cost=0.0,
                metadata={'error': str(e)}
            )
    
    def _calculate_confidence(self, agent_result) -> float:
        """Calculate intelligence confidence score"""
        # Base confidence on task success rate
        task_success_rate = len([r for r in agent_result.task_results
                               if r.analysis and not r.analysis.startswith("Task execution failed")]) / len(agent_result.task_results)

        # Boost confidence for page analysis depth
        page_boost = min(0.2, agent_result.get_total_pages_analyzed() * 0.02)

        return min(1.0, 0.6 + (task_success_rate * 0.3) + page_boost)
    
    async def query_with_conversation(
        self,
        question: str,
        conversation_history: List[ConversationMessage],
        mode: QueryMode = QueryMode.AUTO
    ) -> QueryResult:
        """
        Context-aware query with conversation memory

        Args:
            question: Current user question
            conversation_history: Conversation context memory
            mode: Intelligence mode

        Returns:
            Context-enhanced QueryResult
        """
        return await self.query(
            question=question, 
            mode=mode, 
            conversation_history=conversation_history
        )
    
    # Intelligence Capabilities

    def supports_file(self, file_path: str) -> bool:
        """Check if file format is supported by Docia"""
        return self.processor_factory.supports_file(file_path)
    
    def get_supported_extensions(self) -> Dict[str, str]:
        """Get all supported file formats"""
        return self.processor_factory.get_supported_extensions()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get Docia intelligence system statistics"""
        storage_stats = self.storage.get_storage_stats()
        summarizer_stats = self.summarizer.get_summary_stats()
        agent_stats = self.orchestrator.get_agent_stats()
        
        return {
            'docia_version': '1.0.0',
            'intelligence_engine': 'VisionLM-powered',
            'config': {
                'provider': self.config.provider,
                'storage_type': self.config.storage_type,
                'max_agent_iterations': self.config.max_agent_iterations,
                'max_pages_per_task': self.config.max_pages_per_task
            },
            'knowledge_storage': storage_stats,
            'intelligence': {
                'summarizer': summarizer_stats,
                'agent': agent_stats
            },
            'supported_formats': list(self.get_supported_extensions().keys()),
            'capabilities': ['vision_intelligence', 'adaptive_learning', 'conversational_ai', 'document_understanding']
        }
    
    # Synchronous Intelligence API

    def add_document_sync(
        self,
        file_path: Union[str, Path],
        document_id: Optional[str] = None,
        document_name: Optional[str] = None
    ) -> Document:
        """Synchronous document intelligence processing"""
        return sync_wrapper(self.add_document(file_path, document_id, document_name))
    
    def get_document_sync(self, document_id: str) -> Optional[Document]:
        """Synchronous version of get_document"""
        return sync_wrapper(self.get_document(document_id))
    
    def list_documents_sync(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Synchronous version of list_documents"""
        return sync_wrapper(self.list_documents(limit))
    
    def delete_document_sync(self, document_id: str) -> bool:
        """Synchronous version of delete_document"""
        return sync_wrapper(self.delete_document(document_id))
    
    def query_sync(
        self,
        question: str,
        mode: QueryMode = QueryMode.AUTO,
        document_ids: Optional[List[str]] = None,
        max_pages: Optional[int] = None,
        conversation_history: Optional[List[ConversationMessage]] = None,
        task_update_callback: Optional[Any] = None
    ) -> QueryResult:
        """Synchronous version of query"""
        return sync_wrapper(self.query(question, mode, document_ids, max_pages, stream=False, conversation_history=conversation_history, task_update_callback=task_update_callback))
    
    def search_documents_sync(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Synchronous version of search_documents"""
        return sync_wrapper(self.search_documents(query, limit))
    
    def query_with_conversation_sync(
        self,
        question: str,
        conversation_history: List[ConversationMessage],
        mode: QueryMode = QueryMode.AUTO
    ) -> QueryResult:
        """Synchronous version of query_with_conversation"""
        return sync_wrapper(self.query_with_conversation(question, conversation_history, mode))
    
    # Context manager support
    
    async def __aenter__(self):
        """Async context manager entry"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        # Cleanup if needed
        pass
    
    def __enter__(self):
        """Sync context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Sync context manager exit"""
        # Cleanup if needed
        pass


# Convenience factory functions

def create_docia(
    provider: str = "openai",
    api_key: Optional[str] = None,
    storage_path: Optional[str] = None
) -> Docia:
    """
    Create Docia Intelligence Engine with simple configuration

    Args:
        provider: Vision AI provider ("openai", "openrouter")
        api_key: AI provider API key
        storage_path: Knowledge storage location

    Returns:
        Configured Docia Intelligence Engine
    """
    config = DociaConfig(
        provider=provider,
        local_storage_path=storage_path or "./docia_data"
    )

    return Docia(config=config, api_key=api_key)


def create_memory_docia(
    provider: str = "openai",
    api_key: Optional[str] = None
) -> Docia:
    """
    Create Docia with in-memory intelligence (for testing)

    Args:
        provider: Vision AI provider
        api_key: AI provider API key

    Returns:
        Docia with memory intelligence storage
    """
    config = DociaConfig(
        provider=provider,
        storage_type="memory"
    )

    return Docia(config=config, api_key=api_key)