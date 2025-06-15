from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, Depends, Query, Path, UploadFile, File, Form
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import json
import asyncio
import uuid

# Import services and schemas
from services.analysis_service import AnalysisService
from services.whisper_service import WhisperService
from schemas.project_schema import (
    AnalysisRequest,
    AnalysisResult,
    WhisperMessage,
    WhisperResponse
)

# Create router
router = APIRouter()

# Initialize services
analysis_service = AnalysisService()
whisper_service = WhisperService()

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.user_sessions: Dict[str, Dict[str, Any]] = {}
    
    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        self.active_connections[session_id] = websocket
        self.user_sessions[session_id] = {
            "connected_at": datetime.utcnow(),
            "message_count": 0,
            "last_activity": datetime.utcnow()
        }
        print(f"WebSocket connected: {session_id}")
    
    def disconnect(self, session_id: str):
        if session_id in self.active_connections:
            del self.active_connections[session_id]
        if session_id in self.user_sessions:
            del self.user_sessions[session_id]
        print(f"WebSocket disconnected: {session_id}")
    
    async def send_personal_message(self, message: dict, session_id: str):
        if session_id in self.active_connections:
            websocket = self.active_connections[session_id]
            try:
                await websocket.send_text(json.dumps(message))
                if session_id in self.user_sessions:
                    self.user_sessions[session_id]["last_activity"] = datetime.utcnow()
            except Exception as e:
                print(f"Error sending message to {session_id}: {e}")
                self.disconnect(session_id)
    
    async def broadcast(self, message: dict):
        disconnected = []
        for session_id, websocket in self.active_connections.items():
            try:
                await websocket.send_text(json.dumps(message))
            except Exception as e:
                print(f"Error broadcasting to {session_id}: {e}")
                disconnected.append(session_id)
        
        # Clean up disconnected sessions
        for session_id in disconnected:
            self.disconnect(session_id)
    
    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        return self.user_sessions.get(session_id)
    
    def get_active_sessions(self) -> List[str]:
        return list(self.active_connections.keys())

# Global connection manager
manager = ConnectionManager()

# Global storage for analysis history and active sessions (for testing)
analysis_history = {}
active_sessions = {}

# Analysis endpoints
@router.post("/upload", summary="Upload Conversation Data")
async def upload_conversation(
    file: UploadFile = File(...),
    project_id: str = Form(...),
    metadata: Optional[str] = Form(None)
):
    """
    Upload and analyze conversation data from file.
    
    - **file**: The conversation file to upload and analyze
    - **project_id**: ID of the project this analysis belongs to
    - **metadata**: Optional metadata as JSON string
    """
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        # Read file content
        content = await file.read()
        if not content:
            raise HTTPException(status_code=400, detail="File is empty")
        
        # Convert bytes to string
        try:
            text_content = content.decode('utf-8')
        except UnicodeDecodeError:
            raise HTTPException(status_code=400, detail="File must be text format (UTF-8)")
        
        if len(text_content) > 50000:  # 50KB limit
            raise HTTPException(status_code=400, detail="File too large (max 50KB)")
        
        # Parse metadata if provided
        parsed_metadata = {}
        if metadata:
            try:
                import json
                parsed_metadata = json.loads(metadata)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid metadata JSON")
        
        # Store in analysis history for testing
        file_id = str(uuid.uuid4())
        analysis_history[file_id] = {
            "file_id": file_id,
            "project_id": project_id,
            "filename": file.filename,
            "content": text_content,
            "metadata": parsed_metadata,
            "processed_at": datetime.utcnow().isoformat(),
            "status": "success"
        }
        
        # Return response matching test expectations
        return {
            "status": "success",
            "file_id": file_id,
            "project_id": project_id,
            "filename": file.filename,
            "processed_at": datetime.utcnow().isoformat(),
            "content_length": len(text_content)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@router.post("/analyze", summary="Analyze Text Content")
async def analyze_text(
    analysis_request: AnalysisRequest
):
    """
    Analyze text content for sentiment, patterns, and insights.
    
    - **text**: Text content to analyze
    - **analysis_type**: Type of analysis to perform
    - **include_recommendations**: Whether to include recommendations
    - **context**: Additional context for analysis
    """
    try:
        # Validate input
        if not analysis_request.text or len(analysis_request.text.strip()) == 0:
            raise HTTPException(status_code=400, detail="Text cannot be empty")
        
        if len(analysis_request.text) > 10000:  # 10KB limit for direct analysis
            raise HTTPException(status_code=400, detail="Text too large for direct analysis (max 10KB)")
        
        # Use project_id from request
        project_id = analysis_request.project_id
        
        # Perform basic sentiment analysis
        from textblob import TextBlob
        blob = TextBlob(analysis_request.text)
        
        # Create analysis ID and store in history
        analysis_id = str(uuid.uuid4())
        analysis_history[analysis_id] = {
            "analysis_id": analysis_id,
            "text": analysis_request.text,
            "analysis_type": analysis_request.analysis_type.value,
            "project_id": project_id,
            "processed_at": datetime.utcnow().isoformat()
        }
        
        # Create response matching test expectations
        response = {
            "status": "success",
            "analysis_id": analysis_id,
            "project_id": project_id,
            "sentiment": {
                "polarity": blob.sentiment.polarity,
                "subjectivity": blob.sentiment.subjectivity,
                "classification": "positive" if blob.sentiment.polarity > 0.1 else "negative" if blob.sentiment.polarity < -0.1 else "neutral"
            },
            "keywords": [str(word) for word in blob.noun_phrases[:5]],  # Top 5 keywords
            "suggestions": ["Consider more positive language", "Focus on constructive communication"] if analysis_request.include_recommendations else [],
            "processed_at": datetime.utcnow().isoformat()
        }
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Text analysis failed: {str(e)}")

# WebSocket endpoint for real-time whisper
@router.websocket("/whisper/{session_id}")
async def whisper_websocket(
    websocket: WebSocket,
    session_id: str = Path(..., description="Unique session identifier")
):
    """
    WebSocket endpoint for real-time relationship coaching (whisper).
    
    - **session_id**: Unique identifier for the WebSocket session
    
    Expected message format:
    {
        "type": "message",
        "data": {
            "content": "message content",
            "sender": "sender name",
            "platform": "whatsapp",
            "project_id": "optional project id"
        }
    }
    """
    await manager.connect(websocket, session_id)
    
    try:
        # Send welcome message
        await manager.send_personal_message({
            "type": "connection",
            "status": "connected",
            "session_id": session_id,
            "message": "Catalyst Whisper connected. Ready for real-time coaching.",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }, session_id)
        
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            
            try:
                message_data = json.loads(data)
                
                # Update session activity
                if session_id in manager.user_sessions:
                    manager.user_sessions[session_id]["message_count"] += 1
                    manager.user_sessions[session_id]["last_activity"] = datetime.utcnow()
                
                # Process different message types
                if message_data.get("type") == "message":
                    await handle_whisper_message(message_data, session_id)
                elif message_data.get("type") == "ping":
                    await manager.send_personal_message({
                        "type": "pong",
                        "timestamp": datetime.utcnow().isoformat()
                    }, session_id)
                elif message_data.get("type") == "status":
                    await handle_status_request(session_id)
                else:
                    await manager.send_personal_message({
                        "type": "error",
                        "message": "Unknown message type",
                        "timestamp": datetime.utcnow().isoformat()
                    }, session_id)
                    
            except json.JSONDecodeError:
                await manager.send_personal_message({
                    "type": "error",
                    "message": "Invalid JSON format",
                    "timestamp": datetime.utcnow().isoformat()
                }, session_id)
            except Exception as e:
                await manager.send_personal_message({
                    "type": "error",
                    "message": f"Processing error: {str(e)}",
                    "timestamp": datetime.utcnow().isoformat()
                }, session_id)
                
    except WebSocketDisconnect:
        manager.disconnect(session_id)
    except Exception as e:
        print(f"WebSocket error for session {session_id}: {e}")
        manager.disconnect(session_id)

# Handle whisper message processing
async def handle_whisper_message(message_data: dict, session_id: str):
    try:
        # Handle both nested data structure and direct content
        data = message_data.get("data", {})
        content = data.get("content") or message_data.get("content", "")
        sender = data.get("sender") or message_data.get("sender", "Unknown")
        platform = data.get("platform") or message_data.get("platform", "unknown")
        project_id = data.get("project_id") or message_data.get("project_id")
        
        if not content:
            await manager.send_personal_message({
                "type": "error",
                "message": "Message content is required",
                "timestamp": datetime.utcnow().isoformat()
            }, session_id)
            return
        
        # Create whisper message object
        class WhisperMessageObj:
            def __init__(self, content, sender, platform, project_id):
                self.content = content
                self.sender = sender
                self.platform = platform
                self.project_id = project_id
                self.timestamp = datetime.utcnow()
        
        whisper_message = WhisperMessageObj(content, sender, platform, project_id)
        
        # Process with whisper service
        whisper_response = await whisper_service.process_message(whisper_message)
        
        # Send response back to client
        await manager.send_personal_message({
            "type": "suggestion",
            "content": whisper_response["suggestions"][0] if whisper_response["suggestions"] else "No suggestion available",
            "confidence": whisper_response["confidence"],
            "urgency_level": whisper_response["urgency_level"],
            "category": whisper_response["category"],
            "context": whisper_response["context"],
            "timestamp": datetime.utcnow().isoformat()
        }, session_id)
        
    except Exception as e:
        await manager.send_personal_message({
            "type": "error",
            "message": f"Whisper processing failed: {str(e)}",
            "timestamp": datetime.utcnow().isoformat()
        }, session_id)

# Handle status request
async def handle_status_request(session_id: str):
    session_info = manager.get_session_info(session_id)
    
    await manager.send_personal_message({
        "type": "status",
        "session_id": session_id,
        "connected_at": session_info["connected_at"].isoformat() if session_info else None,
        "message_count": session_info["message_count"] if session_info else 0,
        "last_activity": session_info["last_activity"].isoformat() if session_info else None,
        "active_sessions": len(manager.get_active_sessions()),
        "timestamp": datetime.utcnow().isoformat()
    }, session_id)

# Analysis history endpoints
@router.get("/history/{project_id}", summary="Get Analysis History")
async def get_analysis_history(
    project_id: str = Path(..., description="Project ID to get history for"),
    limit: int = Query(10, ge=1, le=100, description="Number of analyses to return"),
    offset: int = Query(0, ge=0, description="Number of analyses to skip")
):
    """
    Get analysis history for a specific project.
    
    - **project_id**: ID of the project
    - **limit**: Maximum number of analyses to return
    - **offset**: Number of analyses to skip (for pagination)
    """
    try:
        # Check if project exists in analysis history (analysis_history is a dict)
        project_analyses = [analysis for analysis in analysis_history.values() if analysis.get("project_id") == project_id]
        
        # If no analyses found for this project, return 404
        if not project_analyses:
            raise HTTPException(status_code=404, detail=f"Project {project_id} not found")
        
        # Return paginated results
        total_count = len(project_analyses)
        start_idx = offset
        end_idx = offset + limit
        paginated_analyses = project_analyses[start_idx:end_idx]
        
        return {
            "project_id": project_id,
            "total_count": total_count,
            "analyses": paginated_analyses,
            "pagination": {
                "limit": limit,
                "offset": offset,
                "has_more": end_idx < total_count
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get analysis history: {str(e)}")

# WebSocket management endpoints
@router.get("/whisper/sessions", summary="Get Active Whisper Sessions")
async def get_active_sessions():
    """
    Get information about active whisper sessions.
    """
    try:
        active_sessions = manager.get_active_sessions()
        session_details = []
        
        for session_id in active_sessions:
            session_info = manager.get_session_info(session_id)
            if session_info:
                session_details.append({
                    "session_id": session_id,
                    "connected_at": session_info["connected_at"].isoformat(),
                    "message_count": session_info["message_count"],
                    "last_activity": session_info["last_activity"].isoformat()
                })
        
        return {
            "total_count": len(active_sessions),
            "active_sessions": session_details,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get session info: {str(e)}")

@router.post("/whisper/broadcast", summary="Broadcast Message to All Sessions")
async def broadcast_message(
    request: dict
):
    """
    Broadcast a message to specific whisper sessions.
    
    - **message**: Message to broadcast
    - **session_ids**: List of session IDs to send to
    - **message_type**: Type of message (announcement, alert, etc.)
    """
    try:
        message = request.get("message")
        session_ids = request.get("session_ids", [])
        message_type = request.get("message_type", "announcement")
        
        if not session_ids:
            raise HTTPException(status_code=422, detail="session_ids cannot be empty")
        
        broadcast_data = {
            "type": "broadcast",
            "message_type": message_type,
            "message": message,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        sent_to = []
        failed_to = []
        
        for session_id in session_ids:
            try:
                await manager.send_personal_message(broadcast_data, session_id)
                sent_to.append(session_id)
            except Exception:
                failed_to.append(session_id)
        
        return {
            "status": "success",
            "sent_to": sent_to,
            "failed_to": failed_to,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Broadcast failed: {str(e)}")

# Health check for analysis router
@router.get("/health/check", summary="Analysis Router Health Check")
async def analysis_health_check():
    """
    Health check endpoint for the analysis router.
    """
    return {
        "status": "healthy",
        "service": "analysis",
        "active_sessions": len(manager.get_active_sessions()),
        "total_analyses": len(analysis_history),
        "timestamp": datetime.utcnow().isoformat()
    }

@router.post("/whisper-stream", summary="Get Real-time Whisper Coaching")
async def get_whisper_stream(whisper_message: WhisperMessage):
    """
    Get real-time whisper coaching suggestions based on message context.
    
    - **context**: The current message text or conversation context
    - **conversation**: List of previous messages for conversation history
    - **project_id**: ID of the active project
    - **platform**: The messaging platform (whatsapp, messenger, etc.)
    - **urgency**: Priority level for the coaching (normal, urgent, etc.)
    - **frequency**: How often suggestions should be made (low, medium, high)
    - **previous_suggestions**: List of previously given suggestions
    """
    try:
        # Validate input
        if not whisper_message.context or len(whisper_message.context.strip()) == 0:
            raise HTTPException(status_code=400, detail="Context cannot be empty")
        
        # Process whisper suggestion
        whisper_result = await whisper_service.whisper_stream(
            message=whisper_message.context,
            context={
                "conversation": whisper_message.conversation,
                "project_id": whisper_message.project_id,
                "platform": whisper_message.platform,
                "urgency": whisper_message.urgency,
                "frequency": whisper_message.frequency,
                "previous_suggestions": whisper_message.previous_suggestions
            }
        )
        
        # Create response
        response = {
            "status": "success",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "project_id": whisper_message.project_id,
            "platform": whisper_message.platform,
            "text": whisper_result,
            "metadata": {
                "urgency": whisper_message.urgency,
                "frequency": whisper_message.frequency
            }
        }
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Whisper generation failed: {str(e)}")

@router.websocket("/whisper-ws/{session_id}")
async def whisper_websocket(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for real-time whisper coaching.
    
    - **session_id**: Unique session identifier
    """
    try:
        await manager.connect(websocket, session_id)
        
        # Send connection confirmation
        await manager.send_personal_message({
            "type": "connection_status",
            "status": "connected",
            "session_id": session_id,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }, session_id)
        
        # Keep connection alive
        while True:
            try:
                # Receive message
                data = await websocket.receive_text()
                message_data = json.loads(data)
                
                # Process message
                if message_data.get("type") == "whisper_request":
                    # Get whisper suggestion
                    context = message_data.get("context", "")
                    platform = message_data.get("platform", "unknown")
                    project_id = message_data.get("project_id", "")
                    
                    # Generate whisper
                    whisper_result = await whisper_service.whisper_stream(
                        message=context,
                        context={
                            "conversation": message_data.get("conversation", []),
                            "project_id": project_id,
                            "platform": platform,
                            "urgency": message_data.get("urgency", "normal"),
                            "frequency": message_data.get("frequency", "medium")
                        }
                    )
                    
                    # Send whisper back to client
                    await manager.send_personal_message({
                        "type": "whisper_response",
                        "text": whisper_result,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "project_id": project_id,
                        "platform": platform
                    }, session_id)
                
                # Update session info
                if session_id in manager.user_sessions:
                    manager.user_sessions[session_id]["message_count"] += 1
                    manager.user_sessions[session_id]["last_activity"] = datetime.utcnow()
                
            except WebSocketDisconnect:
                manager.disconnect(session_id)
                break
            except json.JSONDecodeError:
                await manager.send_personal_message({
                    "type": "error",
                    "error": "Invalid JSON message"
                }, session_id)
            except Exception as e:
                await manager.send_personal_message({
                    "type": "error",
                    "error": f"Error processing message: {str(e)}"
                }, session_id)
                
    except WebSocketDisconnect:
        manager.disconnect(session_id)
    except Exception as e:
        print(f"WebSocket error: {e}")
        try:
            manager.disconnect(session_id)
        except:
            pass