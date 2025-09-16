"""
Docia Document Intelligence Models

Core data structures for VisionLM-powered document understanding.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum
from pathlib import Path
import uuid
from datetime import datetime


class QueryMode(str, Enum):
    """Docia Intelligence Processing Modes"""
    AUTO = "auto"    # Adaptive Vision AI processing


class DocumentStatus(str, Enum):
    """Document Intelligence Processing Status"""
    PENDING = "pending"        # Ready for intelligence processing
    PROCESSING = "processing"   # Undergoing Vision AI analysis
    COMPLETED = "completed"     # Intelligence-ready
    FAILED = "failed"          # Intelligence processing failed


@dataclass
class Page:
    """Document Page Intelligence Unit"""
    page_number: int                    # Page position in document
    image_path: str                     # Path to Vision-ready image
    metadata: Dict[str, Any] = field(default_factory=dict)  # Intelligence metadata
    document_name: Optional[str] = None  # Source document name
    document_id: Optional[str] = None    # Source document ID

    def __post_init__(self):
        """Validate page intelligence data"""
        if self.page_number <= 0:
            raise ValueError("Page number must be positive")
        if not self.image_path:
            raise ValueError("Image path is required")


@dataclass
class Document:
    """Document Intelligence Container"""
    id: str                             # Unique document identifier
    name: str                           # Document name
    pages: List[Page]                   # Page intelligence units
    summary: Optional[str] = None       # AI-generated document summary
    status: DocumentStatus = DocumentStatus.PENDING  # Intelligence status
    metadata: Dict[str, Any] = field(default_factory=dict)  # Intelligence metadata
    created_at: datetime = field(default_factory=datetime.now)  # Intelligence timestamp

    def __post_init__(self):
        """Initialize intelligence container"""
        if not self.id:
            self.id = str(uuid.uuid4())
        if not self.name:
            raise ValueError("Document name is required")
        if not isinstance(self.pages, list):
            raise ValueError("Pages must be a list")
    
    @property
    def page_count(self) -> int:
        """Total pages in document"""
        return len(self.pages)

    def get_page(self, page_number: int) -> Optional[Page]:
        """Retrieve page intelligence by number"""
        for page in self.pages:
            if page.page_number == page_number:
                return page
        return None
    
    def get_pages_range(self, start: int, end: int) -> List[Page]:
        """Retrieve page intelligence in specified range"""
        return [p for p in self.pages if start <= p.page_number <= end]


@dataclass
class QueryResult:
    """Docia Intelligence Query Response"""
    query: str                              # User question
    answer: str                             # AI-generated answer
    selected_pages: List[Page]              # Pages used for intelligence
    mode: QueryMode                         # Intelligence processing mode
    confidence: float = 0.0                # Answer confidence score
    processing_time: float = 0.0            # Intelligence processing time
    metadata: Dict[str, Any] = field(default_factory=dict)  # Intelligence metadata
    total_cost: float = 0.0                 # Vision AI processing cost

    def __post_init__(self):
        """Validate intelligence response"""
        if not self.query:
            raise ValueError("Query is required")
        if not self.answer:
            raise ValueError("Answer is required")
        if self.confidence < 0 or self.confidence > 1:
            raise ValueError("Confidence must be between 0 and 1")
    
    @property
    def page_count(self) -> int:
        """Pages used for intelligence analysis"""
        return len(self.selected_pages)

    @property
    def page_numbers(self) -> List[int]:
        """Page numbers used for intelligence analysis"""
        return [p.page_number for p in self.selected_pages]

    def get_pages_by_document(self) -> Dict[str, List[int]]:
        """Group intelligence sources by document"""
        pages_by_doc = {}
        for page in self.selected_pages:
            doc_name = page.document_name or "Unknown Document"
            if doc_name not in pages_by_doc:
                pages_by_doc[doc_name] = []
            pages_by_doc[doc_name].append(page.page_number)
        
        # Sort intelligence sources numerically
        for doc_name in pages_by_doc:
            pages_by_doc[doc_name].sort()

        return pages_by_doc


@dataclass
class DocumentProcessRequest:
    """Document Intelligence Processing Request"""
    file_path: str                         # Path to document file
    document_id: Optional[str] = None      # Custom document identifier
    document_name: Optional[str] = None    # Custom document name

    def __post_init__(self):
        """Validate intelligence request"""
        if not self.file_path or not Path(self.file_path).exists():
            raise FileNotFoundError(f"Document file not found: {self.file_path}")

        # Generate intelligence-friendly name
        if not self.document_name:
            self.document_name = Path(self.file_path).stem

        # Generate unique intelligence identifier
        if not self.document_id:
            self.document_id = str(uuid.uuid4())


@dataclass
class QueryRequest:
    """Docia Intelligence Query Request"""
    query: str                             # User question
    mode: QueryMode = QueryMode.AUTO       # Intelligence mode
    document_ids: Optional[List[str]] = None  # Target documents
    max_pages: Optional[int] = None        # Page analysis limit
    stream: bool = False                   # Stream response

    def __post_init__(self):
        """Validate intelligence query request"""
        if not self.query.strip():
            raise ValueError("Intelligence query cannot be empty")

        # Set intelligent page limit
        if self.max_pages is None:
            self.max_pages = 15  # Optimal intelligence depth