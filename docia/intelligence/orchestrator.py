"""
Docia Vision Intelligence Orchestrator

Core engine for adaptive document intelligence with Vision AI processing.
"""

import time
import logging
from typing import List, Optional, Dict, Any

from ..models.agent import (
    ConversationMessage, TaskPlan, TaskResult, AgentQueryResult, TaskStatus
)
from ..models.document import Document, Page
from ..integrations.base import BaseProvider
from ..storage.base import BaseStorage
from ..core.config import DociaConfig
from ..exceptions import (
    ContextProcessingError, QueryReformulationError, QueryClassificationError,
    TaskPlanningError, PageSelectionError, TaskAnalysisError, ResponseSynthesisError
)
from .query_processing.context_processor import ContextProcessor
from .query_processing.query_reformulator import QueryReformulator
from .query_processing.query_classifier import QueryClassifier
from .task_management.planner import Planner
from .task_management.page_selector import PageSelector
from .task_management.synthesizer import ResponseSynthesizer
from .prompts import (
    TASK_PROCESSING_PROMPT, SYSTEM_DOCIA,
    BASIC_GUIDELINES, TABLE_GUIDELINES, CHART_GUIDELINES, IMAGE_GUIDELINES
)

logger = logging.getLogger(__name__)


class Orchestrator:
    """
    Docia Vision Intelligence Orchestrator

    Adaptive intelligence engine with Vision AI capabilities:
    - Vision-first document understanding
    - Adaptive intelligence planning
    - Conversation-aware processing
    - Cost-optimized analysis
    """

    def __init__(
        self,
        provider: BaseProvider,
        storage: BaseStorage,
        config: DociaConfig
    ):
        if provider is None:
            raise ValueError("Vision AI provider cannot be None")
        if storage is None:
            raise ValueError("Storage backend cannot be None")

        self.provider = provider
        self.storage = storage
        self.config = config

        # Initialize intelligence components
        self.context_processor = ContextProcessor(provider, config)
        self.query_reformulator = QueryReformulator(provider)
        self.query_classifier = QueryClassifier(provider)
        self.planner = Planner(provider)
        self.page_selector = PageSelector(provider, config)
        self.synthesizer = ResponseSynthesizer(provider)

        logger.info("Docia Vision Intelligence Engine initialized")

    def _accumulate_cost(self, total_cost: float) -> float:
        """Accumulate Vision AI processing cost"""
        if hasattr(self.provider, 'get_last_cost'):
            last_cost = self.provider.get_last_cost()
            if last_cost is not None:
                return total_cost + last_cost
        return total_cost

    async def process_query(
        self,
        query: str,
        conversation_history: Optional[List[ConversationMessage]] = None,
        task_update_callback: Optional[Any] = None
    ) -> AgentQueryResult:
        """
        Execute Vision AI query processing with adaptive intelligence

        Args:
            query: User's question
            conversation_history: Conversation context memory

        Returns:
            Comprehensive AgentQueryResult with intelligence insights
        """
        start_time = time.time()
        total_cost = 0.0  # Track total cost for this query

        try:
            logger.info(f"Processing query: {query[:100]}...")

            # Step 1: Context Processing (conversation summarization if needed)
            processed_context = ""
            display_messages = conversation_history or []

            if conversation_history:
                processed_context, display_messages = await self.context_processor.process_conversation_context(
                    conversation_history, query
                )
                total_cost = self._accumulate_cost(total_cost)
                logger.info("Processed conversation context")

            # Step 2: Query Reformulation (if conversation context exists)
            reformulated_query = query
            if conversation_history:
                reformulated_query = await self.query_reformulator.reformulate_with_context(
                    query, processed_context
                )
                logger.info(f"Reformulated query: '{query}' → '{reformulated_query}'")

            # Step 3: Query Classification
            classification = await self.query_classifier.classify_query(reformulated_query)
            total_cost = self._accumulate_cost(total_cost)
            logger.info(f"Query classification: {classification['reasoning']}")

            # If query doesn't need documents, return direct answer
            if not classification["needs_documents"]:
                return self._create_direct_answer_result(query, classification["reasoning"], total_cost)

            # Step 4: Get all available documents and pages
            documents = await self.storage.get_all_documents()

            if not documents:
                logger.warning("No documents available for analysis")
                return self._create_no_documents_result(query)

            logger.info(f"Found {len(documents)} documents")

            # Step 5: Task Planning + Document Selection (merged)
            task_plan = await self.planner.create_initial_plan(reformulated_query, documents)

            # Report initial task plan
            if task_update_callback:
                await task_update_callback('plan_created', task_plan)

            # Step 6: Execute tasks adaptively
            task_results = await self._execute_adaptive_plan(
                task_plan, reformulated_query, documents, conversation_history, task_update_callback
            )
            
            # Accumulate any costs from task execution
            total_cost = self._accumulate_cost(total_cost)

            # Step 7: Synthesize final response
            final_answer = await self.synthesizer.synthesize_response(reformulated_query, task_results)

            # Step 8: Build final result
            processing_time = time.time() - start_time
            all_selected_pages = []
            for result in task_results:
                all_selected_pages.extend(result.selected_pages)

            result = AgentQueryResult(
                query=query,
                answer=final_answer,
                selected_pages=all_selected_pages,
                task_results=task_results,
                total_iterations=task_plan.current_iteration,
                processing_time_seconds=processing_time,
                total_cost=total_cost  # Always include cost, even if 0
            )

            logger.info(f"Query processed successfully in {processing_time:.2f}s")
            return result

        except Exception as e:
            logger.error(f"Vision intelligence processing failed: {e}")
            processing_time = time.time() - start_time
            return self._create_error_result(query, str(e), processing_time)

    async def _execute_adaptive_plan(
        self,
        task_plan: TaskPlan,
        original_query: str,
        documents: List[Document],
        conversation_history: Optional[List[ConversationMessage]] = None,
        task_update_callback: Optional[Any] = None
    ) -> List[TaskResult]:
        """Execute adaptive intelligence plan with dynamic replanning"""
        task_results = []
        iteration = 0

        while (task_plan.has_pending_tasks() and
               iteration < self.config.max_agent_iterations):

            iteration += 1
            logger.info(f"Vision intelligence iteration {iteration}")

            # Get next task to execute
            current_task = task_plan.get_next_pending_task()
            if not current_task:
                break

            logger.info(f"Executing task: {current_task.name}")
            current_task.status = TaskStatus.IN_PROGRESS

            # Report task starting
            if task_update_callback:
                await task_update_callback('task_started', {'task': current_task, 'plan': task_plan})

            # Execute the task
            task_result = await self._execute_single_task(
                current_task, documents, original_query, conversation_history, task_update_callback
            )

            # Mark task completed
            current_task.status = TaskStatus.COMPLETED
            task_results.append(task_result)

            logger.info(f"Intelligence task completed: {current_task.name} "
                       f"(analyzed {task_result.pages_analyzed} pages)")

            # Report task completion
            if task_update_callback:
                await task_update_callback('task_completed', {'task': current_task, 'result': task_result, 'plan': task_plan})

            # Update intelligence plan adaptively
            if task_plan.has_pending_tasks():
                logger.info("Evaluating intelligence plan for updates...")
                old_task_count = len(task_plan.tasks)
                task_plan = await self.planner.update_plan(
                    task_plan, task_result, original_query, documents
                )

                # Report intelligence plan update
                if task_update_callback and len(task_plan.tasks) != old_task_count:
                    await task_update_callback('plan_updated', task_plan)

        task_plan.current_iteration = iteration
        logger.info(f"Adaptive intelligence execution completed in {iteration} iterations")
        return task_results

    async def _execute_single_task(
        self,
        task: Any,  # AgentTask
        documents: List[Document],
        original_query: str,
        conversation_history: Optional[List[ConversationMessage]] = None,
        task_update_callback: Optional[Any] = None
    ) -> TaskResult:
        """Execute single intelligence task: document filtering + page selection + Vision AI analysis"""
        try:
            # Phase 1: Document Intelligence Assignment
            task_pages = []
            if task.document:
                # Find document assigned to this intelligence task
                task_doc = next((doc for doc in documents if doc.id == task.document), None)
                if task_doc:
                    task_pages = task_doc.pages
                    logger.info(f"Intelligence task {task.name} assigned to document: {task_doc.name} ({len(task_pages)} pages)")
                else:
                    logger.warning(f"Intelligence task {task.name} assigned to document {task.document} but document not found")
            else:
                # Fallback: use all pages for intelligence analysis
                task_pages = []
                for doc in documents:
                    task_pages.extend(doc.pages)
                logger.warning(f"Intelligence task {task.name} has no document assignment, using all pages")

            # Phase 2: Intelligent Page Selection
            selected_pages = await self.page_selector.select_pages_for_task(
                query=task.name,
                query_description=task.description,
                task_pages=task_pages
            )

            # Ensure selected_pages is not None
            if selected_pages is None:
                logger.warning(f"Page selection returned None for task {task.name}, using empty list")
                selected_pages = []

            logger.info(f"Intelligence selected {len(selected_pages)} pages for task: {task.name}")

            # Report page selection
            if task_update_callback:
                page_numbers = [p.page_number for p in selected_pages]
                await task_update_callback('pages_selected', {'task': task, 'page_numbers': page_numbers})

            # Phase 3: Vision AI Analysis
            analysis = await self._analyze_pages_for_task(
                task, selected_pages, original_query, conversation_history
            )

            # Ensure analysis is not None
            if analysis is None:
                logger.warning(f"Analysis returned None for task {task.name}, using empty string")
                analysis = ""

            # Phase 4: Intelligence Result Construction
            return TaskResult(
                task=task,
                selected_pages=selected_pages,
                analysis=analysis
            )

        except Exception as e:
            logger.error(f"Intelligence task execution failed: {task.name}: {e}")
            # Return intelligence result with error
            return TaskResult(
                task=task,
                selected_pages=[],
                analysis=f"Intelligence task execution failed: {e}"
            )

    async def _analyze_pages_for_task(
        self,
        task: Any,  # AgentTask
        pages: List[Page],
        original_query: str,
        conversation_history: Optional[List[ConversationMessage]] = None
    ) -> str:
        """Analyze pages with Vision AI to complete intelligence task"""
        if not pages:
            return f"No relevant pages found for intelligence task: {task.name}"

        try:
            # Build intelligence memory from conversation
            memory_summary = self._build_memory_summary(conversation_history)

            # Select specialized analysis guidelines based on information type
            information_type = getattr(task, 'information_type', 'basic')
            guidelines_map = {
                'basic': BASIC_GUIDELINES,
                'table': TABLE_GUIDELINES,
                'chart': CHART_GUIDELINES,
                'image': IMAGE_GUIDELINES
            }
            analysis_guidelines = guidelines_map.get(information_type, BASIC_GUIDELINES)

            # Create intelligence processing prompt with specialized guidelines
            prompt = TASK_PROCESSING_PROMPT.format(
                task_description=task.description,
                information_type=information_type,
                search_queries=task.description,  # Use task description for intelligence focus
                memory_summary=memory_summary,
                analysis_guidelines=analysis_guidelines
            )

            # Build multimodal message with selected page images
            messages = [
                {"role": "system", "content": SYSTEM_DOCIA},
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            ]

            # Add page images to message
            for i, page in enumerate(pages, 1):
                messages[1]["content"].extend([
                    {
                        "type": "image_path",
                        "image_path": page.image_path,
                        "detail": "high"  # Use high detail for task analysis
                    },
                    {
                        "type": "text",
                        "text": f"[Page {i} from document]"
                    }
                ])

            # Process with vision model
            result = await self.provider.process_multimodal_messages(
                messages=messages,
                max_tokens=600,
                temperature=0.3
            )

            # Ensure result is not None
            if result is None:
                logger.warning(f"Vision AI analysis returned None for task {task.name}")
                return "Vision AI analysis returned no result"

            return result.strip()

        except Exception as e:
            logger.error(f"Vision AI analysis failed for task {task.name}: {e}")
            return f"Vision AI analysis failed for intelligence task {task.name}: {e}"

    def _build_memory_summary(
        self,
        conversation_history: Optional[List[ConversationMessage]]
    ) -> str:
        """Build intelligence memory summary from conversation context"""
        if not conversation_history or len(conversation_history) == 0:
            return "INTELLIGENCE CONTEXT: First query in conversation session."

        # Extract recent intelligence context
        recent_messages = conversation_history[-4:] if len(conversation_history) > 4 else conversation_history

        context_parts = ["INTELLIGENCE CONTEXT:"]
        for msg in recent_messages:
            role = "User" if msg.role == "user" else "Assistant"
            content = msg.content[:100] + "..." if len(msg.content) > 100 else msg.content
            context_parts.append(f"- {role}: {content}")

        return "\n".join(context_parts)

    def _create_no_documents_result(self, query: str) -> AgentQueryResult:
        """Create intelligence result when no knowledge base available"""
        return AgentQueryResult(
            query=query,
            answer="Docia Intelligence requires documents for analysis. Please upload documents to the knowledge base first.",
            selected_pages=[],
            task_results=[],
            total_iterations=0,
            processing_time_seconds=0.0,
            total_cost=0.0
        )

    def _create_error_result(
        self,
        query: str,
        error_message: str,
        processing_time: float
    ) -> AgentQueryResult:
        """Create intelligence result when processing fails"""
        return AgentQueryResult(
            query=query,
            answer=f"Docia Intelligence encountered an error: {error_message}",
            selected_pages=[],
            task_results=[],
            total_iterations=0,
            processing_time_seconds=processing_time,
            total_cost=0.0
        )

    def _create_direct_answer_result(self, query: str, reasoning: str, total_cost: float = 0.0) -> AgentQueryResult:
        """Create direct intelligence result when no document analysis needed"""
        return AgentQueryResult(
            query=query,
            answer=f"This query can be answered directly without document analysis. {reasoning}",
            selected_pages=[],
            task_results=[],
            total_iterations=0,
            processing_time_seconds=0.0,
            total_cost=total_cost
        )

    async def process_conversation_query(
        self,
        query: str,
        conversation_history: List[ConversationMessage]
    ) -> AgentQueryResult:
        """
        Process query with conversation intelligence context
        Convenience method for conversation-aware intelligence processing
        """
        return await self.process_query(query, conversation_history)

    def get_agent_stats(self) -> Dict[str, Any]:
        """Get intelligence engine configuration and statistics"""
        return {
            "intelligence_provider": self.provider.__class__.__name__,
            "knowledge_storage": self.storage.__class__.__name__,
            "max_intelligence_iterations": self.config.max_agent_iterations,
            "max_pages_per_intelligence_task": self.config.max_pages_per_task,
            "max_tasks_per_intelligence_plan": self.config.max_tasks_per_plan,
        }
