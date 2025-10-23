"""
Shared models and database configuration for Mothership AIs.
"""

import os
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum

from sqlalchemy import create_engine, Column, String, Text, DateTime, JSON, ARRAY, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql import func
from pydantic import BaseModel, Field
from pgvector.sqlalchemy import Vector

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://mothership:mothership_password@localhost:5432/mothership")
ASYNC_DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

# Create async engine
async_engine = create_async_engine(ASYNC_DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()

# Enums
class AgentStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    MAINTENANCE = "maintenance"

class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

# Database Models
class Value(Base):
    __tablename__ = "values"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), unique=True, nullable=False)
    description = Column(Text, nullable=False)
    embedding = Column(Vector(1536))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class Belief(Base):
    __tablename__ = "beliefs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), unique=True, nullable=False)
    description = Column(Text, nullable=False)
    embedding = Column(Vector(1536))
    related_values = Column(ARRAY(UUID), default=list)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class Directive(Base):
    __tablename__ = "directives"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_type = Column(String(255), nullable=False)
    constraints = Column(JSON, nullable=False, default=dict)
    source_values = Column(ARRAY(UUID), default=list)
    source_beliefs = Column(ARRAY(UUID), default=list)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True))

class Agent(Base):
    __tablename__ = "agents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), unique=True, nullable=False)
    agent_type = Column(String(255), nullable=False)
    capabilities = Column(JSON, nullable=False, default=dict)
    status = Column(String(50), default=AgentStatus.INACTIVE)
    last_heartbeat = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    tasks = relationship("Task", back_populates="agent")

class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True))
    agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id"))
    directive_id = Column(UUID(as_uuid=True), ForeignKey("directives.id"))
    input_data = Column(JSON, nullable=False)
    output_data = Column(JSON)
    status = Column(String(50), default=TaskStatus.PENDING)
    error_message = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    
    # Relationships
    agent = relationship("Agent", back_populates="tasks")
    directive = relationship("Directive")

# Pydantic Models for API
class ValueCreate(BaseModel):
    name: str = Field(..., max_length=255)
    description: str

class ValueResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: str
    created_at: datetime
    updated_at: datetime

class BeliefCreate(BaseModel):
    name: str = Field(..., max_length=255)
    description: str
    related_values: List[uuid.UUID] = Field(default_factory=list)

class BeliefResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: str
    related_values: List[uuid.UUID]
    created_at: datetime
    updated_at: datetime

class DirectiveCreate(BaseModel):
    task_type: str = Field(..., max_length=255)
    constraints: Dict[str, Any] = Field(default_factory=dict)
    source_values: List[uuid.UUID] = Field(default_factory=list)
    source_beliefs: List[uuid.UUID] = Field(default_factory=list)
    expires_at: Optional[datetime] = None

class DirectiveResponse(BaseModel):
    id: uuid.UUID
    task_type: str
    constraints: Dict[str, Any]
    source_values: List[uuid.UUID]
    source_beliefs: List[uuid.UUID]
    created_at: datetime
    expires_at: Optional[datetime]

class AgentCreate(BaseModel):
    name: str = Field(..., max_length=255)
    agent_type: str = Field(..., max_length=255)
    capabilities: Dict[str, Any] = Field(default_factory=dict)

class AgentResponse(BaseModel):
    id: uuid.UUID
    name: str
    agent_type: str
    capabilities: Dict[str, Any]
    status: AgentStatus
    last_heartbeat: Optional[datetime]
    created_at: datetime
    updated_at: datetime

class TaskCreate(BaseModel):
    user_id: Optional[uuid.UUID] = None
    agent_id: uuid.UUID
    directive_id: uuid.UUID
    input_data: Dict[str, Any]

class TaskResponse(BaseModel):
    id: uuid.UUID
    user_id: Optional[uuid.UUID]
    agent_id: uuid.UUID
    directive_id: uuid.UUID
    input_data: Dict[str, Any]
    output_data: Optional[Dict[str, Any]]
    status: TaskStatus
    error_message: Optional[str]
    created_at: datetime
    completed_at: Optional[datetime]

# Database dependency
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
