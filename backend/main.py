"""
Main FastAPI application for Mothership AIs.
"""

import os
import uuid
from contextlib import asynccontextmanager
from typing import List, Dict, Any, Optional

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import structlog

from shared.models import (
    get_db, Value, Belief, Directive, Agent, Task,
    ValueCreate, ValueResponse, BeliefCreate, BeliefResponse,
    DirectiveCreate, DirectiveResponse, AgentResponse, TaskCreate, TaskResponse
)

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

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info("Starting Mothership AIs application")
    yield
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
        value = Value(
            name=value_data.name,
            description=value_data.description
        )
        
        db.add(value)
        await db.commit()
        await db.refresh(value)
        
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
        result = await db.execute(select(Value).offset(offset).limit(limit))
        values = result.scalars().all()
        
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
