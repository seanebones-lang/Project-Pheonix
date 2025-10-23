"""
WebSocket Manager for real-time agent communication.
"""

import json
import uuid
from typing import Dict, List, Optional, Any, Set
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
import structlog
import asyncio
from fastapi import WebSocket, WebSocketDisconnect
from fastapi.websockets import WebSocketState

from ...shared.models import Agent, Task, AgentStatus, TaskStatus

logger = structlog.get_logger()

class ConnectionManager:
    """Manages WebSocket connections."""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.agent_connections: Dict[uuid.UUID, str] = {}  # agent_id -> connection_id
        self.connection_agents: Dict[str, uuid.UUID] = {}  # connection_id -> agent_id
    
    async def connect(self, websocket: WebSocket, connection_id: str, agent_id: Optional[uuid.UUID] = None):
        """Accept a WebSocket connection."""
        await websocket.accept()
        self.active_connections[connection_id] = websocket
        
        if agent_id:
            self.agent_connections[agent_id] = connection_id
            self.connection_agents[connection_id] = agent_id
        
        logger.info("WebSocket connection established", connection_id=connection_id, agent_id=str(agent_id) if agent_id else None)
    
    def disconnect(self, connection_id: str):
        """Remove a WebSocket connection."""
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]
        
        if connection_id in self.connection_agents:
            agent_id = self.connection_agents[connection_id]
            if agent_id in self.agent_connections:
                del self.agent_connections[agent_id]
            del self.connection_agents[connection_id]
        
        logger.info("WebSocket connection closed", connection_id=connection_id)
    
    async def send_personal_message(self, message: dict, connection_id: str):
        """Send a message to a specific connection."""
        if connection_id in self.active_connections:
            websocket = self.active_connections[connection_id]
            try:
                if websocket.client_state == WebSocketState.CONNECTED:
                    await websocket.send_text(json.dumps(message))
            except Exception as e:
                logger.error("Failed to send personal message", error=str(e), connection_id=connection_id)
                self.disconnect(connection_id)
    
    async def send_to_agent(self, message: dict, agent_id: uuid.UUID):
        """Send a message to a specific agent."""
        if agent_id in self.agent_connections:
            connection_id = self.agent_connections[agent_id]
            await self.send_personal_message(message, connection_id)
        else:
            logger.warning("Agent not connected", agent_id=str(agent_id))
    
    async def broadcast_to_agents(self, message: dict, agent_types: Optional[List[str]] = None):
        """Broadcast a message to all connected agents or specific agent types."""
        for connection_id, websocket in self.active_connections.items():
            try:
                if websocket.client_state == WebSocketState.CONNECTED:
                    await websocket.send_text(json.dumps(message))
            except Exception as e:
                logger.error("Failed to broadcast message", error=str(e), connection_id=connection_id)
                self.disconnect(connection_id)
    
    def get_connected_agents(self) -> List[uuid.UUID]:
        """Get list of connected agent IDs."""
        return list(self.agent_connections.keys())
    
    def is_agent_connected(self, agent_id: uuid.UUID) -> bool:
        """Check if an agent is connected."""
        return agent_id in self.agent_connections

class WebSocketManager:
    """Manages WebSocket communication for the Mothership AI system."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.connection_manager = ConnectionManager()
        self.heartbeat_interval = 30  # seconds
        self.heartbeat_task: Optional[asyncio.Task] = None
    
    async def start_heartbeat(self):
        """Start heartbeat monitoring for connected agents."""
        if not self.heartbeat_task:
            self.heartbeat_task = asyncio.create_task(self._heartbeat_loop())
    
    async def stop_heartbeat(self):
        """Stop heartbeat monitoring."""
        if self.heartbeat_task:
            self.heartbeat_task.cancel()
            try:
                await self.heartbeat_task
            except asyncio.CancelledError:
                pass
            self.heartbeat_task = None
    
    async def _heartbeat_loop(self):
        """Heartbeat monitoring loop."""
        while True:
            try:
                await asyncio.sleep(self.heartbeat_interval)
                await self._send_heartbeat()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Heartbeat loop error", error=str(e))
    
    async def _send_heartbeat(self):
        """Send heartbeat to all connected agents."""
        heartbeat_message = {
            "type": "heartbeat",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await self.connection_manager.broadcast_to_agents(heartbeat_message)
    
    async def handle_connection(self, websocket: WebSocket, connection_id: str):
        """Handle a new WebSocket connection."""
        try:
            await self.connection_manager.connect(websocket, connection_id)
            
            # Send welcome message
            welcome_message = {
                "type": "welcome",
                "connection_id": connection_id,
                "timestamp": datetime.utcnow().isoformat(),
                "message": "Connected to Mothership AI"
            }
            await self.connection_manager.send_personal_message(welcome_message, connection_id)
            
            # Handle messages
            while True:
                try:
                    data = await websocket.receive_text()
                    message = json.loads(data)
                    await self._handle_message(websocket, connection_id, message)
                except WebSocketDisconnect:
                    break
                except json.JSONDecodeError as e:
                    logger.error("Invalid JSON message", error=str(e), connection_id=connection_id)
                    error_message = {
                        "type": "error",
                        "message": "Invalid JSON format"
                    }
                    await self.connection_manager.send_personal_message(error_message, connection_id)
                except Exception as e:
                    logger.error("Message handling error", error=str(e), connection_id=connection_id)
                    break
        
        except WebSocketDisconnect:
            pass
        finally:
            await self._cleanup_connection(connection_id)
    
    async def _handle_message(self, websocket: WebSocket, connection_id: str, message: dict):
        """Handle incoming WebSocket messages."""
        message_type = message.get("type")
        
        if message_type == "agent_register":
            await self._handle_agent_registration(websocket, connection_id, message)
        elif message_type == "task_response":
            await self._handle_task_response(websocket, connection_id, message)
        elif message_type == "heartbeat_response":
            await self._handle_heartbeat_response(websocket, connection_id, message)
        elif message_type == "status_update":
            await self._handle_status_update(websocket, connection_id, message)
        else:
            logger.warning("Unknown message type", message_type=message_type, connection_id=connection_id)
            error_message = {
                "type": "error",
                "message": f"Unknown message type: {message_type}"
            }
            await self.connection_manager.send_personal_message(error_message, connection_id)
    
    async def _handle_agent_registration(self, websocket: WebSocket, connection_id: str, message: dict):
        """Handle agent registration."""
        try:
            agent_data = message.get("agent_data", {})
            agent_id = uuid.UUID(agent_data.get("id"))
            
            # Update agent status in database
            await self.db.execute(
                update(Agent)
                .where(Agent.id == agent_id)
                .values(
                    status=AgentStatus.ACTIVE,
                    last_heartbeat=datetime.utcnow()
                )
            )
            await self.db.commit()
            
            # Update connection mapping
            self.connection_manager.agent_connections[agent_id] = connection_id
            self.connection_manager.connection_agents[connection_id] = agent_id
            
            # Send confirmation
            confirmation_message = {
                "type": "registration_confirmed",
                "agent_id": str(agent_id),
                "timestamp": datetime.utcnow().isoformat()
            }
            await self.connection_manager.send_personal_message(confirmation_message, connection_id)
            
            logger.info("Agent registered", agent_id=str(agent_id), connection_id=connection_id)
            
        except Exception as e:
            logger.error("Agent registration failed", error=str(e), connection_id=connection_id)
            error_message = {
                "type": "registration_failed",
                "message": "Agent registration failed"
            }
            await self.connection_manager.send_personal_message(error_message, connection_id)
    
    async def _handle_task_response(self, websocket: WebSocket, connection_id: str, message: dict):
        """Handle task response from agent."""
        try:
            task_id = uuid.UUID(message.get("task_id"))
            output_data = message.get("output_data", {})
            status = message.get("status", TaskStatus.COMPLETED)
            error_message = message.get("error_message")
            
            # Update task in database
            await self.db.execute(
                update(Task)
                .where(Task.id == task_id)
                .values(
                    output_data=output_data,
                    status=status,
                    error_message=error_message,
                    completed_at=datetime.utcnow() if status == TaskStatus.COMPLETED else None
                )
            )
            await self.db.commit()
            
            logger.info("Task response received", task_id=str(task_id), status=status)
            
        except Exception as e:
            logger.error("Task response handling failed", error=str(e), connection_id=connection_id)
    
    async def _handle_heartbeat_response(self, websocket: WebSocket, connection_id: str, message: dict):
        """Handle heartbeat response from agent."""
        try:
            if connection_id in self.connection_manager.connection_agents:
                agent_id = self.connection_manager.connection_agents[connection_id]
                
                # Update last heartbeat in database
                await self.db.execute(
                    update(Agent)
                    .where(Agent.id == agent_id)
                    .values(last_heartbeat=datetime.utcnow())
                )
                await self.db.commit()
                
                logger.debug("Heartbeat response received", agent_id=str(agent_id))
            
        except Exception as e:
            logger.error("Heartbeat response handling failed", error=str(e), connection_id=connection_id)
    
    async def _handle_status_update(self, websocket: WebSocket, connection_id: str, message: dict):
        """Handle status update from agent."""
        try:
            if connection_id in self.connection_manager.connection_agents:
                agent_id = self.connection_manager.connection_agents[connection_id]
                status = message.get("status")
                
                # Update agent status in database
                await self.db.execute(
                    update(Agent)
                    .where(Agent.id == agent_id)
                    .values(status=status, last_heartbeat=datetime.utcnow())
                )
                await self.db.commit()
                
                logger.info("Agent status updated", agent_id=str(agent_id), status=status)
            
        except Exception as e:
            logger.error("Status update handling failed", error=str(e), connection_id=connection_id)
    
    async def _cleanup_connection(self, connection_id: str):
        """Clean up connection when agent disconnects."""
        try:
            if connection_id in self.connection_manager.connection_agents:
                agent_id = self.connection_manager.connection_agents[connection_id]
                
                # Update agent status to inactive
                await self.db.execute(
                    update(Agent)
                    .where(Agent.id == agent_id)
                    .values(status=AgentStatus.INACTIVE)
                )
                await self.db.commit()
                
                logger.info("Agent disconnected", agent_id=str(agent_id))
            
            self.connection_manager.disconnect(connection_id)
            
        except Exception as e:
            logger.error("Connection cleanup failed", error=str(e), connection_id=connection_id)
    
    async def send_task_to_agent(self, agent_id: uuid.UUID, task_data: dict):
        """Send a task to a specific agent."""
        if self.connection_manager.is_agent_connected(agent_id):
            task_message = {
                "type": "task_assignment",
                "task_data": task_data,
                "timestamp": datetime.utcnow().isoformat()
            }
            await self.connection_manager.send_to_agent(task_message, agent_id)
            return True
        else:
            logger.warning("Cannot send task to disconnected agent", agent_id=str(agent_id))
            return False
    
    async def broadcast_directive(self, directive_data: dict, agent_types: Optional[List[str]] = None):
        """Broadcast a directive to relevant agents."""
        directive_message = {
            "type": "directive_update",
            "directive_data": directive_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await self.connection_manager.broadcast_to_agents(directive_message, agent_types)
    
    def get_connected_agents(self) -> List[uuid.UUID]:
        """Get list of connected agent IDs."""
        return self.connection_manager.get_connected_agents()
    
    def is_agent_connected(self, agent_id: uuid.UUID) -> bool:
        """Check if an agent is connected."""
        return self.connection_manager.is_agent_connected(agent_id)
