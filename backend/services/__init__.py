"""Services module for Catalyst backend."""

# Import services to make them available at the module level
try:
    from .project_service import ProjectService
except ImportError:
    pass

try:
    from .analysis_service import AnalysisService
except ImportError:
    pass

try:
    from .ai_service import EnhancedAIService, AIProvider, AnalysisType, TherapyApproach, InterventionType
except ImportError:
    pass

try:
    from .ai_service_kb import AIService
except ImportError:
    pass

try:
    from .multi_format_processor import MultiFormatProcessor, InputFormat, ProcessingMode
except ImportError:
    pass

# Expose specific classes and functions
__all__ = [
    "ProjectService",
    "AnalysisService",
    "EnhancedAIService",
    "AIService", 
    "AIProvider",
    "AnalysisType",
    "TherapyApproach",
    "InterventionType",
    "MultiFormatProcessor",
    "InputFormat", 
    "ProcessingMode"
]
