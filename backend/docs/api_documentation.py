"""Enhanced API documentation for Catalyst backend."""

from fastapi import FastAPI
from typing import Dict, Any


def enhance_api_docs(app: FastAPI) -> None:
    """Enhance FastAPI documentation with detailed descriptions and examples."""
    
    # Update app metadata
    app.title = "Catalyst Backend API"
    app.description = """
    ## Catalyst Project Management & Analysis Platform
    
    A comprehensive backend API for project management with real-time communication analysis,
    sentiment tracking, and team collaboration insights.
    
    ### Key Features
    
    * **Project Management**: Create, update, and manage projects with detailed metadata
    * **Real-time Analysis**: WebSocket-based communication analysis with sentiment tracking
    * **Text Analysis**: Advanced NLP processing for meeting transcripts and messages
    * **Team Insights**: Participant tracking and collaboration metrics
    * **Performance Monitoring**: Built-in request tracking and performance metrics
    
    ### Authentication
    
    Currently, the API operates without authentication for development purposes.
    Production deployment should implement proper authentication mechanisms.
    
    ### Rate Limiting
    
    API endpoints are designed to handle reasonable request volumes.
    For production use, implement rate limiting based on your requirements.
    
    ### WebSocket Communication
    
    Real-time features are available through WebSocket connections at `/ws/{project_id}`.
    Supported message types include:
    
    * `whisper_message`: Real-time message analysis
    * `analysis_request`: Request text analysis
    * `status_update`: System status updates
    * `ping/pong`: Connection health checks
    
    ### Error Handling
    
    The API uses standard HTTP status codes and returns detailed error messages
    in JSON format for debugging and client-side error handling.
    """
    app.version = "1.0.0"
    app.contact = {
        "name": "Catalyst Development Team",
        "url": "https://github.com/Ajirohack/Catalyst",
        "email": "support@catalyst-platform.com"
    }
    app.license_info = {
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT"
    }


# API Response Examples
API_EXAMPLES = {
    "project_create_example": {
        "name": "Q1 Marketing Campaign",
        "description": "Comprehensive marketing campaign for Q1 product launch",
        "goals": [
            "Increase brand awareness by 25%",
            "Generate 1000 qualified leads",
            "Achieve 15% conversion rate"
        ],
        "metadata": {
            "department": "Marketing",
            "budget": 50000,
            "priority": "high",
            "stakeholders": ["john.doe@company.com", "jane.smith@company.com"]
        }
    },
    
    "project_response_example": {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "name": "Q1 Marketing Campaign",
        "description": "Comprehensive marketing campaign for Q1 product launch",
        "goals": [
            "Increase brand awareness by 25%",
            "Generate 1000 qualified leads",
            "Achieve 15% conversion rate"
        ],
        "status": "active",
        "created_at": "2024-01-15T10:30:00Z",
        "updated_at": "2024-01-15T10:30:00Z",
        "metadata": {
            "department": "Marketing",
            "budget": 50000,
            "priority": "high",
            "stakeholders": ["john.doe@company.com", "jane.smith@company.com"]
        }
    },
    
    "text_analysis_request_example": {
        "content": "Today's team meeting was very productive. We discussed the new feature requirements and everyone seemed excited about the upcoming release. However, there were some concerns about the timeline.",
        "project_id": "123e4567-e89b-12d3-a456-426614174000",
        "analysis_type": "comprehensive",
        "metadata": {
            "meeting_type": "standup",
            "duration_minutes": 30,
            "participants_count": 5
        }
    },
    
    "text_analysis_response_example": {
        "analysis_id": "987fcdeb-51a2-43d1-b456-426614174999",
        "sentiment": {
            "overall_sentiment": "positive",
            "confidence": 0.78,
            "positive_score": 0.65,
            "negative_score": 0.15,
            "neutral_score": 0.20
        },
        "keywords": [
            {"word": "productive", "frequency": 1, "relevance": 0.9},
            {"word": "feature", "frequency": 1, "relevance": 0.8},
            {"word": "timeline", "frequency": 1, "relevance": 0.7}
        ],
        "summary": "Team meeting focused on new feature requirements with positive reception but timeline concerns.",
        "participants": ["team", "everyone"],
        "project_id": "123e4567-e89b-12d3-a456-426614174000",
        "analyzed_at": "2024-01-15T14:30:00Z",
        "metadata": {
            "word_count": 34,
            "sentence_count": 3,
            "reading_time_seconds": 8
        }
    },
    
    "whisper_message_example": {
        "content": "I think we should prioritize the user authentication feature for the next sprint",
        "sender": "john.doe@company.com",
        "platform": "slack",
        "project_id": "123e4567-e89b-12d3-a456-426614174000",
        "timestamp": "2024-01-15T15:45:00Z",
        "metadata": {
            "channel": "#development",
            "thread_id": "1234567890",
            "message_type": "suggestion"
        }
    },
    
    "websocket_message_example": {
        "type": "whisper_message",
        "data": {
            "content": "Great progress on the API development!",
            "sender": "jane.smith@company.com",
            "platform": "teams",
            "project_id": "123e4567-e89b-12d3-a456-426614174000"
        }
    },
    
    "health_check_response_example": {
        "status": "healthy",
        "service": "catalyst-backend",
        "version": "1.0.0",
        "timestamp": "2024-01-15T16:00:00Z",
        "uptime": "operational",
        "services": {
            "database": "connected",
            "analysis_engine": "operational",
            "websocket_server": "running"
        },
        "performance": {
            "avg_response_time_ms": 45,
            "total_requests": 1250,
            "error_rate": 0.02
        }
    },
    
    "error_response_example": {
        "detail": "Project not found",
        "error_code": "PROJECT_NOT_FOUND",
        "timestamp": "2024-01-15T16:15:00Z",
        "request_id": "req_123456789"
    }
}


# API Tags for organization
API_TAGS = [
    {
        "name": "Projects",
        "description": "Project management operations including creation, updates, and retrieval"
    },
    {
        "name": "Analysis", 
        "description": "Text analysis and sentiment processing endpoints"
    },
    {
        "name": "WebSocket",
        "description": "Real-time communication and message processing"
    },
    {
        "name": "Health",
        "description": "System health checks and monitoring endpoints"
    },
    {
        "name": "Monitoring",
        "description": "Performance metrics and system statistics"
    }
]


def get_openapi_schema(app: FastAPI) -> Dict[str, Any]:
    """Generate enhanced OpenAPI schema with examples."""
    schema = app.openapi()
    
    # Add examples to schema components
    if "components" not in schema:
        schema["components"] = {}
    
    if "examples" not in schema["components"]:
        schema["components"]["examples"] = {}
    
    # Add our examples
    for example_name, example_data in API_EXAMPLES.items():
        schema["components"]["examples"][example_name] = {
            "summary": f"Example for {example_name.replace('_', ' ').title()}",
            "value": example_data
        }
    
    return schema