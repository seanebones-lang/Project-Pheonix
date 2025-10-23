"""
Base agent class for all specialized agents.
"""

import asyncio
import json
import uuid
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime

import socketio
from sqlalchemy.ext.asyncio import AsyncSession

from ...shared.models import Agent, Task, TaskStatus, AgentStatus
from ...shared.ai_providers import AIProviderManager

class BaseAgent(ABC):
    """Base class for all specialized agents."""
    
    def __init__(self, agent_id: str, agent_name: str, agent_type: str, capabilities: Dict[str, Any]):
        self.agent_id = agent_id
        self.agent_name = agent_name
        self.agent_type = agent_type
        self.capabilities = capabilities
        self.status = AgentStatus.ACTIVE
        
        # AI provider for validation
        self.ai_provider = AIProviderManager()
        
        # WebSocket client for communication with Mothership
        self.sio = socketio.AsyncClient()
        self._setup_websocket_handlers()
        
        # Task tracking
        self.current_tasks: Dict[str, Task] = {}
        self.task_history: List[Task] = []
    
    def _setup_websocket_handlers(self):
        """Setup WebSocket event handlers."""
        
        @self.sio.event
        async def connect():
            """Handle connection to Mothership."""
            print(f"Agent {self.agent_name} connected to Mothership")
            
            # Register with Mothership
            await self.sio.emit('agent_register', {
                'agent_id': self.agent_id,
                'agent_name': self.agent_name,
                'agent_type': self.agent_type,
                'capabilities': self.capabilities
            })
        
        @self.sio.event
        async def disconnect():
            """Handle disconnection from Mothership."""
            print(f"Agent {self.agent_name} disconnected from Mothership")
        
        @self.sio.event
        async def task_assigned(data):
            """Handle task assignment from Mothership."""
            try:
                task_id = data.get('task_id')
                task_type = data.get('task_type')
                input_data = data.get('input_data')
                user_id = data.get('user_id')
                
                print(f"Agent {self.agent_name} received task {task_id}")
                
                # Create task object
                task = Task(
                    id=uuid.UUID(task_id),
                    user_id=uuid.UUID(user_id) if user_id else None,
                    agent_id=uuid.UUID(self.agent_id),
                    input_data=input_data,
                    status=TaskStatus.IN_PROGRESS
                )
                
                self.current_tasks[task_id] = task
                
                # Process the task
                await self._process_task(task)
                
            except Exception as e:
                print(f"Error processing task: {e}")
                await self.sio.emit('task_result', {
                    'task_id': data.get('task_id'),
                    'status': 'failed',
                    'error_message': str(e)
                })
        
        @self.sio.event
        async def task_cancelled(data):
            """Handle task cancellation."""
            task_id = data.get('task_id')
            if task_id in self.current_tasks:
                task = self.current_tasks[task_id]
                task.status = TaskStatus.CANCELLED
                del self.current_tasks[task_id]
                print(f"Task {task_id} cancelled")
    
    async def _process_task(self, task: Task):
        """Process a task and send results back to Mothership."""
        try:
            # Validate task can be handled by this agent
            if not self._can_handle_task(task):
                await self.sio.emit('task_result', {
                    'task_id': str(task.id),
                    'status': 'failed',
                    'error_message': f'Agent {self.agent_name} cannot handle this task type'
                })
                return
            
            # Execute the task
            result = await self.execute_task(task)
            
            # Update task status
            task.status = TaskStatus.COMPLETED
            task.output_data = result
            task.completed_at = datetime.utcnow()
            
            # Move to history
            self.task_history.append(task)
            if str(task.id) in self.current_tasks:
                del self.current_tasks[str(task.id)]
            
            # Send result to Mothership
            await self.sio.emit('task_result', {
                'task_id': str(task.id),
                'output_data': result,
                'status': 'completed'
            })
            
            print(f"Task {task.id} completed successfully")
            
        except Exception as e:
            # Handle task failure
            task.status = TaskStatus.FAILED
            task.error_message = str(e)
            task.completed_at = datetime.utcnow()
            
            # Move to history
            self.task_history.append(task)
            if str(task.id) in self.current_tasks:
                del self.current_tasks[str(task.id)]
            
            # Send error to Mothership
            await self.sio.emit('task_result', {
                'task_id': str(task.id),
                'status': 'failed',
                'error_message': str(e)
            })
            
            print(f"Task {task.id} failed: {e}")
    
    def _can_handle_task(self, task: Task) -> bool:
        """Check if this agent can handle the given task."""
        # Override in subclasses for specific validation
        return True
    
    @abstractmethod
    async def execute_task(self, task: Task) -> Dict[str, Any]:
        """Execute the task and return results."""
        pass
    
    async def start(self, mothership_url: str = "http://localhost:8000"):
        """Start the agent and connect to Mothership."""
        try:
            await self.sio.connect(mothership_url)
            
            # Start heartbeat loop
            asyncio.create_task(self._heartbeat_loop())
            
            # Wait for connection
            await self.sio.wait()
            
        except Exception as e:
            print(f"Failed to start agent {self.agent_name}: {e}")
            raise
    
    async def stop(self):
        """Stop the agent and disconnect from Mothership."""
        try:
            await self.sio.disconnect()
            print(f"Agent {self.agent_name} stopped")
        except Exception as e:
            print(f"Error stopping agent {self.agent_name}: {e}")
    
    async def _heartbeat_loop(self):
        """Send periodic heartbeats to Mothership."""
        while self.sio.connected:
            try:
                await self.sio.emit('agent_heartbeat', {
                    'agent_id': self.agent_id,
                    'status': self.status.value,
                    'current_tasks': len(self.current_tasks),
                    'completed_tasks': len(self.task_history)
                })
                
                await asyncio.sleep(30)  # Send heartbeat every 30 seconds
                
            except Exception as e:
                print(f"Heartbeat error: {e}")
                await asyncio.sleep(5)
    
    def get_status(self) -> Dict[str, Any]:
        """Get current agent status."""
        return {
            'agent_id': self.agent_id,
            'agent_name': self.agent_name,
            'agent_type': self.agent_type,
            'status': self.status.value,
            'capabilities': self.capabilities,
            'current_tasks': len(self.current_tasks),
            'completed_tasks': len(self.task_history),
            'connected': self.sio.connected
        }
    
    async def validate_directive_compliance(self, directive: Dict[str, Any], output: Dict[str, Any]) -> Dict[str, Any]:
        """Validate if output complies with directive constraints."""
        try:
            validation_prompt = f"""
            Validate if the following agent output complies with the directive constraints:
            
            Directive Constraints:
            {json.dumps(directive.get('constraints', {}), indent=2)}
            
            Agent Output:
            {json.dumps(output, indent=2)}
            
            Provide a validation report with:
            - compliance_score: Score from 0-100
            - violations: List of any constraint violations
            - recommendations: Suggestions for improvement
            - overall_assessment: Brief summary
            """
            
            validation_schema = {
                "type": "object",
                "properties": {
                    "compliance_score": {"type": "integer", "minimum": 0, "maximum": 100},
                    "violations": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "recommendations": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "overall_assessment": {"type": "string"}
                },
                "required": ["compliance_score", "violations", "recommendations", "overall_assessment"]
            }
            
            validation_result = await self.ai_provider.generate_structured_output(validation_prompt, validation_schema)
            return validation_result
            
        except Exception as e:
            return {
                "compliance_score": 0,
                "violations": [f"Validation error: {str(e)}"],
                "recommendations": ["Fix validation error"],
                "overall_assessment": "Validation failed"
            }
