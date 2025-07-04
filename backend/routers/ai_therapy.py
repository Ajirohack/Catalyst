"""AI Therapy Router
Provides endpoints for AI-powered therapy and coaching features
"""

# Import standard libraries with proper error handling
import logging
logger = logging.getLogger(__name__)

try:
    from typing import List, Dict, Any, Optional
    from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, WebSocket, WebSocketDisconnect
    from fastapi.responses import JSONResponse
    from pydantic import BaseModel, Field
    from datetime import datetime
    import json
    import asyncio

    # Import our enhanced services
    from services.ai_service import EnhancedAIService, AIProvider
    from services.enhanced_analysis_service import EnhancedAnalysisService
    
    from schemas.ai_therapy_schema import (
        ConflictDetectionRequest,
        ConflictDetectionResponse,
        RealTimeCoachingRequest,
        RealTimeCoachingResponse,
        WebSocketMessage,
        AnalysisType,
        TherapyApproach,
        InterventionType
    )
    
    from schemas.project_schema import Platform as MessagePlatform
    from database.unified_models import (
        Project, Analysis, TherapeuticIntervention, RealTimeCoaching,
        AnalysisRequest, WhisperMessage
    )
except ImportError as e:
    # Log the import error but continue
    logger.error(f"Error importing required modules in ai_therapy.py: {e}")

# Create router
router = APIRouter()

# Initialize services (in try block to handle initialization errors)
try:
    ai_service = EnhancedAIService()
    analysis_service = EnhancedAnalysisService()
except NameError:
    # Define placeholders if imports failed
    ai_service = None
    analysis_service = None
except Exception as e:
    logger.error(f"Error initializing services: {e}")
    ai_service = None
    analysis_service = None

# WebSocket connection manager for real-time coaching
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.user_projects: Dict[str, str] = {}  # user_id -> project_id
    
    async def connect(self, websocket: WebSocket, user_id: str, project_id: str):
        await websocket.accept()
        self.active_connections[user_id] = websocket
        self.user_projects[user_id] = project_id
        logger.info(f"User {user_id} connected for project {project_id}")
    
    def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]
        if user_id in self.user_projects:
            del self.user_projects[user_id]
        logger.info(f"User {user_id} disconnected")
    
    async def send_coaching(self, user_id: str, coaching_data: dict):
        if user_id in self.active_connections:
            try:
                await self.active_connections[user_id].send_json(coaching_data)
                logger.debug(f"Sent coaching to user {user_id}")
                return True
            except Exception as e:
                logger.error(f"Error sending coaching to user {user_id}: {e}")
                return False
        return False

# Create connection manager instance
manager = ConnectionManager()

# Endpoints for therapy and coaching features
@router.post("/api/therapy/conflict-detection", response_model=ConflictDetectionResponse)
async def detect_conflict(
    request: ConflictDetectionRequest,
    background_tasks: BackgroundTasks
):
    """
    Analyze conversation for conflict patterns and provide therapeutic insights
    """
    try:
        if ai_service is None:
            raise HTTPException(status_code=503, detail="AI service is not available")
        
        # Log the request
        logger.info(f"Conflict detection request for project {request.project_id}")
        
        # Analyze the conversation with AI
        results = await ai_service.analyze_conversation(
            conversation=request.conversation,
            analysis_type=AnalysisType.CONFLICT_DETECTION,
            project_id=request.project_id
        )
        
        # Save the analysis in background
        background_tasks.add_task(
            analysis_service.save_analysis,
            project_id=request.project_id,
            analysis_type=AnalysisType.CONFLICT_DETECTION,
            content=results,
            conversation=request.conversation
        )
        
        return ConflictDetectionResponse(
            conflict_detected=results.get("conflict_detected", False),
            conflict_type=results.get("conflict_type", ""),
            conflict_severity=results.get("conflict_severity", 0),
            patterns=results.get("patterns", []),
            therapeutic_advice=results.get("therapeutic_advice", ""),
            suggested_interventions=results.get("suggested_interventions", [])
        )
    except Exception as e:
        logger.error(f"Error in conflict detection: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/therapy/coaching", response_model=RealTimeCoachingResponse)
async def get_coaching(
    request: RealTimeCoachingRequest,
    background_tasks: BackgroundTasks
):
    """
    Get real-time coaching advice for an ongoing conversation
    """
    try:
        if ai_service is None:
            raise HTTPException(status_code=503, detail="AI service is not available")
        
        # Log the request
        logger.info(f"Coaching request for project {request.project_id}")
        
        # Generate coaching with AI
        coaching = await ai_service.generate_coaching(
            conversation=request.conversation,
            approach=request.approach,
            project_id=request.project_id
        )
        
        # Save the coaching in background
        background_tasks.add_task(
            analysis_service.save_coaching,
            project_id=request.project_id,
            approach=request.approach,
            content=coaching,
            conversation=request.conversation
        )
        
        return RealTimeCoachingResponse(
            advice=coaching.get("advice", ""),
            suggested_responses=coaching.get("suggested_responses", []),
            key_observations=coaching.get("key_observations", []),
            approach=request.approach
        )
    except Exception as e:
        logger.error(f"Error in generating coaching: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.websocket("/ws/therapy/realtime/{project_id}/{user_id}")
async def websocket_coaching(
    websocket: WebSocket,
    project_id: str,
    user_id: str
):
    """
    WebSocket endpoint for real-time coaching
    """
    try:
        await manager.connect(websocket, user_id, project_id)
        logger.info(f"WebSocket connection established for user {user_id}, project {project_id}")
        
        try:
            while True:
                data = await websocket.receive_json()
                message = WebSocketMessage(**data)
                
                if message.type == "message":
                    # Process new message in conversation
                    if ai_service is not None:
                        conversation = message.data.get("conversation", [])
                        approach = message.data.get("approach", TherapyApproach.COGNITIVE_BEHAVIORAL)
                        
                        # Generate coaching asynchronously
                        coaching = await ai_service.generate_coaching(
                            conversation=conversation,
                            approach=approach,
                            project_id=project_id
                        )
                        
                        # Send coaching response
                        response = {
                            "type": "coaching",
                            "data": {
                                "advice": coaching.get("advice", ""),
                                "suggested_responses": coaching.get("suggested_responses", []),
                                "key_observations": coaching.get("key_observations", []),
                                "approach": approach
                            }
                        }
                        await websocket.send_json(response)
                        
                        # Save in database asynchronously
                        asyncio.create_task(
                            analysis_service.save_coaching(
                                project_id=project_id,
                                approach=approach,
                                content=coaching,
                                conversation=conversation
                            )
                        )
                elif message.type == "close":
                    # Client is closing connection
                    break
        except WebSocketDisconnect:
            logger.info(f"WebSocket disconnected for user {user_id}")
        except Exception as e:
            logger.error(f"Error in websocket communication: {e}")
            await websocket.send_json({"type": "error", "data": {"message": str(e)}})
        finally:
            manager.disconnect(user_id)
    except Exception as e:
        logger.error(f"Failed to establish WebSocket connection: {e}")
        return
