"""
Main FastAPI application for Mothership AIs.
"""

import os
import uuid
from contextlib import asynccontextmanager
from typing import List, Dict, Any, Optional

from fastapi import FastAPI, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
import structlog
import asyncio

from shared.models import (
    get_db, Value, Belief, Directive, Agent, Task,
    ValueCreate, ValueResponse, BeliefCreate, BeliefResponse,
    DirectiveCreate, DirectiveResponse, AgentResponse, TaskCreate, TaskResponse
)
from services.mothership.ontology_manager import OntologyManager
from services.mothership.directive_engine import DirectiveEngine
from services.mothership.websocket_manager import WebSocketManager

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Global variables for services
websocket_manager: Optional[WebSocketManager] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    global websocket_manager
    
    # Startup
    logger.info("Starting Mothership AIs application")
    
    # Initialize WebSocket manager
    async for db in get_db():
        websocket_manager = WebSocketManager(db)
        break
    
    yield
    
    # Shutdown
    logger.info("Shutting down Mothership AIs application")

# Create FastAPI app
app = FastAPI(
    title="Mothership AIs",
    description="Central AI with ontological library for specialized agents",
    version="1.0.0",
    lifespan=lifespan
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # Configure appropriately for production
)

# Health check endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "mothership-ais"}

@app.get("/ready")
async def readiness_check():
    """Readiness check endpoint."""
    try:
        # Check database connection
        async for db in get_db():
            await db.execute(select(1))
            break
        
        return {"status": "ready", "service": "mothership-ais"}
    except Exception as e:
        logger.error("Readiness check failed", error=str(e))
        raise HTTPException(status_code=503, detail="Service not ready")

# Ontology endpoints
@app.post("/api/ontology/values", response_model=ValueResponse)
async def create_value(
    value_data: ValueCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new ontological value."""
    try:
        ontology_manager = OntologyManager(db)
        value = await ontology_manager.create_value(value_data)
        
        logger.info("Created new value", value_id=str(value.id), value_name=value.name)
        
        return ValueResponse(
            id=value.id,
            name=value.name,
            description=value.description,
            created_at=value.created_at,
            updated_at=value.updated_at
        )
    except Exception as e:
        logger.error("Failed to create value", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/ontology/values", response_model=List[ValueResponse])
async def get_values(
    limit: int = 100,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """Get all ontological values."""
    try:
        ontology_manager = OntologyManager(db)
        values = await ontology_manager.get_values(limit, offset)
        
        return [
            ValueResponse(
                id=v.id,
                name=v.name,
                description=v.description,
                created_at=v.created_at,
                updated_at=v.updated_at
            )
            for v in values
        ]
    except Exception as e:
        logger.error("Failed to get values", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ontology/beliefs", response_model=BeliefResponse)
async def create_belief(
    belief_data: BeliefCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new ontological belief."""
    try:
        ontology_manager = OntologyManager(db)
        belief = await ontology_manager.create_belief(belief_data)
        
        logger.info("Created new belief", belief_id=str(belief.id), belief_name=belief.name)
        
        return BeliefResponse(
            id=belief.id,
            name=belief.name,
            description=belief.description,
            related_values=belief.related_values,
            created_at=belief.created_at,
            updated_at=belief.updated_at
        )
    except Exception as e:
        logger.error("Failed to create belief", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/ontology/beliefs", response_model=List[BeliefResponse])
async def get_beliefs(
    limit: int = 100,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """Get all ontological beliefs."""
    try:
        ontology_manager = OntologyManager(db)
        beliefs = await ontology_manager.get_beliefs(limit, offset)
        
        return [
            BeliefResponse(
                id=b.id,
                name=b.name,
                description=b.description,
                related_values=b.related_values,
                created_at=b.created_at,
                updated_at=b.updated_at
            )
            for b in beliefs
        ]
    except Exception as e:
        logger.error("Failed to get beliefs", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

# Directive endpoints
@app.post("/api/directives", response_model=DirectiveResponse)
async def create_directive(
    task_description: str,
    task_type: str,
    user_context: Optional[Dict[str, Any]] = None,
    db: AsyncSession = Depends(get_db)
):
    """Generate a directive for a specific task."""
    try:
        directive_engine = DirectiveEngine(db)
        directive = await directive_engine.generate_directive(task_description, task_type, user_context)
        
        logger.info("Generated new directive", directive_id=str(directive.id), task_type=task_type)
        
        return DirectiveResponse(
            id=directive.id,
            task_type=directive.task_type,
            constraints=directive.constraints,
            source_values=directive.source_values,
            source_beliefs=directive.source_beliefs,
            created_at=directive.created_at,
            expires_at=directive.expires_at
        )
    except Exception as e:
        logger.error("Failed to generate directive", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/directives/{directive_id}", response_model=DirectiveResponse)
async def get_directive(
    directive_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get a directive by ID."""
    try:
        directive_engine = DirectiveEngine(db)
        directive = await directive_engine.get_directive(directive_id)
        
        if not directive:
            raise HTTPException(status_code=404, detail="Directive not found")
        
        return DirectiveResponse(
            id=directive.id,
            task_type=directive.task_type,
            constraints=directive.constraints,
            source_values=directive.source_values,
            source_beliefs=directive.source_beliefs,
            created_at=directive.created_at,
            expires_at=directive.expires_at
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get directive", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

# Agent endpoints
@app.get("/api/agents", response_model=List[AgentResponse])
async def get_agents(
    agent_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get all registered agents."""
    try:
        query = select(Agent)
        if agent_type:
            query = query.where(Agent.agent_type == agent_type)
        
        result = await db.execute(query)
        agents = result.scalars().all()
        
        return [
            AgentResponse(
                id=a.id,
                name=a.name,
                agent_type=a.agent_type,
                capabilities=a.capabilities,
                status=a.status,
                last_heartbeat=a.last_heartbeat,
                created_at=a.created_at,
                updated_at=a.updated_at
            )
            for a in agents
        ]
    except Exception as e:
        logger.error("Failed to get agents", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

# Task endpoints
@app.post("/api/tasks", response_model=TaskResponse)
async def create_task(
    task_data: TaskCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new task."""
    try:
        task = Task(
            user_id=task_data.user_id,
            agent_id=task_data.agent_id,
            directive_id=task_data.directive_id,
            input_data=task_data.input_data
        )
        
        db.add(task)
        await db.commit()
        await db.refresh(task)
        
        logger.info("Created new task", task_id=str(task.id), agent_id=str(task.agent_id))
        
        return TaskResponse(
            id=task.id,
            user_id=task.user_id,
            agent_id=task.agent_id,
            directive_id=task.directive_id,
            input_data=task.input_data,
            output_data=task.output_data,
            status=task.status,
            error_message=task.error_message,
            created_at=task.created_at,
            completed_at=task.completed_at
        )
    except Exception as e:
        logger.error("Failed to create task", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/tasks/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get a task by ID."""
    try:
        task = await db.get(Task, task_id)
        
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        return TaskResponse(
            id=task.id,
            user_id=task.user_id,
            agent_id=task.agent_id,
            directive_id=task.directive_id,
            input_data=task.input_data,
            output_data=task.output_data,
            status=task.status,
            error_message=task.error_message,
            created_at=task.created_at,
            completed_at=task.completed_at
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get task", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/tasks/recent", response_model=List[TaskResponse])
async def get_recent_tasks(
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    """Get recent tasks."""
    try:
        result = await db.execute(
            select(Task)
            .order_by(Task.created_at.desc())
            .limit(limit)
        )
        tasks = result.scalars().all()
        
        return [
            TaskResponse(
                id=t.id,
                user_id=t.user_id,
                agent_id=t.agent_id,
                directive_id=t.directive_id,
                input_data=t.input_data,
                output_data=t.output_data,
                status=t.status,
                error_message=t.error_message,
                created_at=t.created_at,
                completed_at=t.completed_at
            )
            for t in tasks
        ]
    except Exception as e:
        logger.error("Failed to get recent tasks", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/ontology/summary")
async def get_ontology_summary(db: AsyncSession = Depends(get_db)):
    """Get ontology summary statistics."""
    try:
        # Count values
        values_result = await db.execute(select(func.count(Value.id)))
        total_values = values_result.scalar()
        
        # Count beliefs
        beliefs_result = await db.execute(select(func.count(Belief.id)))
        total_beliefs = beliefs_result.scalar()
        
        return {
            "total_values": total_values,
            "total_beliefs": total_beliefs,
            "ontology_size": total_values + total_beliefs
        }
    except Exception as e:
        logger.error("Failed to get ontology summary", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time communication."""
    if not websocket_manager:
        await websocket.close(code=1011, reason="WebSocket manager not available")
        return
    
    connection_id = str(uuid.uuid4())
    await websocket_manager.handle_connection(websocket, connection_id)

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"detail": "Resource not found"}
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    logger.error("Internal server error", error=str(exc))
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
