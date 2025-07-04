from fastapi import WebSocket, WebSocketDisconnect
from fastapi import APIRouter
from typing import Dict
import logging
import json

router = APIRouter()
logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections and message broadcasting."""

    def __init__(self):
        """Initialize active connections dictionary."""
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        """Accept a new WebSocket connection."""
        await websocket.accept()
        self.active_connections[client_id] = websocket
        logger.info("Client %s connected", client_id)
        # Send welcome message
        await self.send_personal_message(
            json.dumps({"type": "connection_established", "client_id": client_id}),
            client_id,
        )

    def disconnect(self, client_id: str):
        """Remove a WebSocket connection."""
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            logger.info("Client %s disconnected", client_id)

    async def send_personal_message(self, message: str, client_id: str):
        """Send a message to a specific client."""
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id].send_text(message)
            except Exception as e:
                logger.error(
                    "Error sending message to client %s: %s", client_id, str(e)
                )
                self.disconnect(client_id)

    async def broadcast(self, message: str, exclude: str = None):
        """Send a message to all connected clients, optionally excluding one."""
        for client_id, connection in list(self.active_connections.items()):
            if client_id != exclude:
                try:
                    await connection.send_text(message)
                except Exception as e:
                    logger.error(
                        "Error broadcasting to client %s: %s", client_id, str(e)
                    )
                    self.disconnect(client_id)


# Create a single instance of the connection manager
manager = ConnectionManager()


@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """Handle WebSocket connections and messages."""
    await manager.connect(websocket, client_id)
    try:
        while True:
            # Wait for any message from the client
            data = await websocket.receive_text()
            logger.info("Message from %s: %s", client_id, data)

            # Echo the message back to the client
            await manager.send_personal_message(
                json.dumps({"type": "echo", "message": data}), client_id
            )

    except WebSocketDisconnect:
        manager.disconnect(client_id)
        logger.info("Client %s disconnected", client_id)
    except Exception as e:
        logger.error("WebSocket error for client %s: %s", client_id, str(e))
        manager.disconnect(client_id)
