"""
Docia Intelligence Engine Exceptions

Exception classes for VisionLM-powered document intelligence system.
"""


class DociaError(Exception):
    """Base exception for Docia Intelligence Engine"""
    pass


class ContextProcessingError(DociaError):
    """Conversation intelligence context processing failure"""
    pass


class QueryReformulationError(DociaError):
    """Intelligence query reformulation failure"""
    pass


class QueryClassificationError(DociaError):
    """Intelligence query classification failure"""
    pass


class TaskPlanningError(DociaError):
    """Intelligence task planning or document selection failure"""
    pass


class PageSelectionError(DociaError):
    """Intelligence page selection failure"""
    pass


class TaskAnalysisError(DociaError):
    """Intelligence task analysis failure"""
    pass


class ResponseSynthesisError(DociaError):
    """Intelligence response synthesis failure"""
    pass


class DocumentSelectionError(DociaError):
    """Intelligence document selection failure"""
    pass


class PlanUpdateError(DociaError):
    """Intelligence adaptive plan update failure"""
    pass