"""
WebSocket Manager for real-time agent communication.
"""

import asyncio
import json
import uuid
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime

import socketio
from sqlalchemy.ext.asyncio import AsyncSession

from shared.models import Agent, Task, TaskStatus, AgentStatus

class WebSocketManager:
    """Manages WebSocket connections for real-time agent communication."""
    
    def __init__(self, db_session: AsyncSession):
        self.db = db_session
        self.sio = socketio.AsyncServer(
            cors_allowed_origins="*",
            logger=True,
            engineio_logger=True
        )
        self.agent_connections: Dict[str, str] = {}  # agent_id -> session_id
        self.user_connections: Dict[str, str] = {}   # user_id -> session_id
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup WebSocket event handlers."""
        
        @self.sio.event
        async def connect(sid, environ):
            """Handle client connection."""
            print(f"Client {sid} connected")
            await self.sio.emit('connected', {'message': 'Connected to Mothership'}, room=sid)
        
        @self.sio.event
        async def disconnect(sid):
            """Handle client disconnection."""
            print(f"Client {sid} disconnected")
            
            # Remove agent connection if exists
            agent_id = None
            for aid, session_id in self.agent_connections.items():
                if session_id == sid:
                    agent_id = aid
                    break
            
            if agent_id:
                await self._handle_agent_disconnect(agent_id)
            
            # Remove user connection if exists
            user_id = None
            for uid, session_id in self.user_connections.items():
                if session_id == sid:
                    user_id = uid
                    break
            
            if user_id:
                del self.user_connections[user_id]
        
        @self.sio.event
        async def agent_register(sid, data):
            """Handle agent registration."""
            try:
                agent_id = data.get('agent_id')
                agent_name = data.get('agent_name')
                agent_type = data.get('agent_type')
                capabilities = data.get('capabilities', {})
                
                if not all([agent_id, agent_name, agent_type]):
                    await self.sio.emit('error', {'message': 'Missing required fields'}, room=sid)
                    return
                
                # Register agent in database
                agent = await self._register_agent(agent_id, agent_name, agent_type, capabilities)
                
                # Store connection mapping
                self.agent_connections[agent_id] = sid
                
                # Join agent namespace
                await self.sio.enter_room(sid, f"agent_{agent_type}")
                
                await self.sio.emit('agent_registered', {
                    'agent_id': agent_id,
                    'status': 'registered'
                }, room=sid)
                
                # Notify users about new agent
                await self.sio.emit('agent_available', {
                    'agent_id': agent_id,
                    'agent_name': agent_name,
                    'agent_type': agent_type,
                    'capabilities': capabilities
                }, room='users')
                
            except Exception as e:
                await self.sio.emit('error', {'message': str(e)}, room=sid)
        
        @self.sio.event
        async def agent_heartbeat(sid, data):
            """Handle agent heartbeat."""
            try:
                agent_id = data.get('agent_id')
                status = data.get('status', 'active')
                
                if agent_id:
                    await self._update_agent_heartbeat(agent_id, status)
                    
                    await self.sio.emit('heartbeat_ack', {
                        'agent_id': agent_id,
                        'timestamp': datetime.utcnow().isoformat()
                    }, room=sid)
                
            except Exception as e:
                await self.sio.emit('error', {'message': str(e)}, room=sid)
        
        @self.sio.event
        async def task_request(sid, data):
            """Handle task request from user."""
            try:
                user_id = data.get('user_id')
                task_type = data.get('task_type')
                input_data = data.get('input_data')
                
                if not all([user_id, task_type, input_data]):
                    await self.sio.emit('error', {'message': 'Missing required fields'}, room=sid)
                    return
                
                # Store user connection
                self.user_connections[user_id] = sid
                
                # Find available agent for task type
                agent = await self._find_available_agent(task_type)
                
                if not agent:
                    await self.sio.emit('task_rejected', {
                        'reason': 'No available agent for this task type'
                    }, room=sid)
                    return
                
                # Create task
                task = await self._create_task(user_id, agent.id, input_data)
                
                # Send task to agent
                await self.sio.emit('task_assigned', {
                    'task_id': str(task.id),
                    'task_type': task_type,
                    'input_data': input_data,
                    'user_id': user_id
                }, room=f"agent_{agent.agent_type}")
                
                await self.sio.emit('task_accepted', {
                    'task_id': str(task.id),
                    'agent_name': agent.name,
                    'estimated_time': 'Processing...'
                }, room=sid)
                
            except Exception as e:
                await self.sio.emit('error', {'message': str(e)}, room=sid)
        
        @self.sio.event
        async def task_result(sid, data):
            """Handle task result from agent."""
            try:
                task_id = data.get('task_id')
                output_data = data.get('output_data')
                status = data.get('status', 'completed')
                error_message = data.get('error_message')
                
                if not task_id:
                    await self.sio.emit('error', {'message': 'Missing task_id'}, room=sid)
                    return
                
                # Update task in database
                task = await self._update_task_result(task_id, output_data, status, error_message)
                
                if not task:
                    await self.sio.emit('error', {'message': 'Task not found'}, room=sid)
                    return
                
                # Send result to user
                await self.sio.emit('task_completed', {
                    'task_id': str(task.id),
                    'output_data': output_data,
                    'status': status,
                    'error_message': error_message,
                    'completed_at': task.completed_at.isoformat() if task.completed_at else None
                }, room=self.user_connections.get(str(task.user_id)))
                
            except Exception as e:
                await self.sio.emit('error', {'message': str(e)}, room=sid)
    
    async def _register_agent(self, agent_id: str, agent_name: str, agent_type: str, capabilities: Dict[str, Any]) -> Agent:
        """Register agent in database."""
        agent = Agent(
            id=uuid.UUID(agent_id),
            name=agent_name,
            agent_type=agent_type,
            capabilities=capabilities,
            status=AgentStatus.ACTIVE,
            last_heartbeat=datetime.utcnow()
        )
        
        self.db.add(agent)
        await self.db.commit()
        await self.db.refresh(agent)
        
        return agent
    
    async def _update_agent_heartbeat(self, agent_id: str, status: str):
        """Update agent heartbeat."""
        agent = await self.db.get(Agent, uuid.UUID(agent_id))
        if agent:
            agent.last_heartbeat = datetime.utcnow()
            agent.status = AgentStatus(status) if status in [e.value for e in AgentStatus] else AgentStatus.ACTIVE
            await self.db.commit()
    
    async def _find_available_agent(self, task_type: str) -> Optional[Agent]:
        """Find available agent for task type."""
        from sqlalchemy import select, and_
        
        result = await self.db.execute(
            select(Agent)
            .where(
                and_(
                    Agent.agent_type == task_type,
                    Agent.status == AgentStatus.ACTIVE
                )
            )
            .limit(1)
        )
        
        return result.scalar_one_or_none()
    
    async def _create_task(self, user_id: str, agent_id: uuid.UUID, input_data: Dict[str, Any]) -> Task:
        """Create new task."""
        task = Task(
            user_id=uuid.UUID(user_id) if user_id else None,
            agent_id=agent_id,
            input_data=input_data,
            status=TaskStatus.PENDING
        )
        
        self.db.add(task)
        await self.db.commit()
        await self.db.refresh(task)
        
        return task
    
    async def _update_task_result(self, task_id: str, output_data: Dict[str, Any], 
                                 status: str, error_message: str = None) -> Optional[Task]:
        """Update task with result."""
        task = await self.db.get(Task, uuid.UUID(task_id))
        if task:
            task.output_data = output_data
            task.status = TaskStatus(status) if status in [e.value for e in TaskStatus] else TaskStatus.COMPLETED
            task.error_message = error_message
            task.completed_at = datetime.utcnow()
            
            await self.db.commit()
            await self.db.refresh(task)
        
        return task
    
    async def _handle_agent_disconnect(self, agent_id: str):
        """Handle agent disconnection."""
        agent = await self.db.get(Agent, uuid.UUID(agent_id))
        if agent:
            agent.status = AgentStatus.INACTIVE
            await self.db.commit()
        
        del self.agent_connections[agent_id]
        
        # Notify users about agent unavailability
        await self.sio.emit('agent_unavailable', {
            'agent_id': agent_id
        }, room='users')
    
    async def broadcast_to_agents(self, event: str, data: Dict[str, Any], agent_type: str = None):
        """Broadcast message to all agents or specific agent type."""
        room = f"agent_{agent_type}" if agent_type else "agents"
        await self.sio.emit(event, data, room=room)
    
    async def send_to_user(self, user_id: str, event: str, data: Dict[str, Any]):
        """Send message to specific user."""
        session_id = self.user_connections.get(user_id)
        if session_id:
            await self.sio.emit(event, data, room=session_id)
    
    async def send_to_agent(self, agent_id: str, event: str, data: Dict[str, Any]):
        """Send message to specific agent."""
        session_id = self.agent_connections.get(agent_id)
        if session_id:
            await self.sio.emit(event, data, room=session_id)
    
    def get_app(self):
        """Get SocketIO app instance."""
        return self.sio
