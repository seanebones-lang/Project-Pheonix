"""
Database models and Pydantic schemas for Mothership AIs.
"""

import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from enum import Enum

from sqlalchemy import Column, String, Text, DateTime, JSON, ForeignKey, ARRAY
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from pydantic import BaseModel, Field, ConfigDict
from pgvector.sqlalchemy import Vector

# Database configuration
DATABASE_URL = "postgresql+asyncpg://mothership:mothership@localhost:5432/mothership_ais"

engine = create_async_engine(DATABASE_URL, echo=True)
async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()

# Enums
class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class AgentStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    BUSY = "busy"
    ERROR = "error"

# Database Models
class Value(Base):
    """Ontological values table."""
    __tablename__ = "values"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), unique=True, nullable=False)
    description = Column(Text, nullable=False)
    embedding = Column(Vector(1536))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class Belief(Base):
    """Ontological beliefs table."""
    __tablename__ = "beliefs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), unique=True, nullable=False)
    description = Column(Text, nullable=False)
    embedding = Column(Vector(1536))
    related_values = Column(ARRAY(UUID(as_uuid=True)), default=list)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class Directive(Base):
    """Generated directives table."""
    __tablename__ = "directives"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_type = Column(String(255), nullable=False)
    constraints = Column(JSONB, nullable=False, default=dict)
    source_values = Column(ARRAY(UUID(as_uuid=True)), default=list)
    source_beliefs = Column(ARRAY(UUID(as_uuid=True)), default=list)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True))

class Agent(Base):
    """Agent registry table."""
    __tablename__ = "agents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), unique=True, nullable=False)
    agent_type = Column(String(255), nullable=False)
    capabilities = Column(JSONB, nullable=False, default=dict)
    status = Column(String(50), default=AgentStatus.INACTIVE)
    last_heartbeat = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    tasks = relationship("Task", back_populates="agent")

class Task(Base):
    """Task tracking table."""
    __tablename__ = "tasks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True))
    agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id"))
    directive_id = Column(UUID(as_uuid=True), ForeignKey("directives.id"))
    input_data = Column(JSONB, nullable=False)
    output_data = Column(JSONB)
    status = Column(String(50), default=TaskStatus.PENDING)
    error_message = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    
    # Relationships
    agent = relationship("Agent", back_populates="tasks")
    directive = relationship("Directive")

# Pydantic Schemas
class ValueCreate(BaseModel):
    """Schema for creating a value."""
    name: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1)

class ValueResponse(BaseModel):
    """Schema for value response."""
    model_config = ConfigDict(from_attributes=True)
    
    id: uuid.UUID
    name: str
    description: str
    created_at: datetime
    updated_at: datetime

class BeliefCreate(BaseModel):
    """Schema for creating a belief."""
    name: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1)
    related_values: List[uuid.UUID] = Field(default_factory=list)

class BeliefResponse(BaseModel):
    """Schema for belief response."""
    model_config = ConfigDict(from_attributes=True)
    
    id: uuid.UUID
    name: str
    description: str
    related_values: List[uuid.UUID]
    created_at: datetime
    updated_at: datetime

class DirectiveCreate(BaseModel):
    """Schema for creating a directive."""
    task_type: str = Field(..., min_length=1, max_length=255)
    constraints: Dict[str, Any] = Field(default_factory=dict)
    source_values: List[uuid.UUID] = Field(default_factory=list)
    source_beliefs: List[uuid.UUID] = Field(default_factory=list)
    expires_at: Optional[datetime] = None

class DirectiveResponse(BaseModel):
    """Schema for directive response."""
    model_config = ConfigDict(from_attributes=True)
    
    id: uuid.UUID
    task_type: str
    constraints: Dict[str, Any]
    source_values: List[uuid.UUID]
    source_beliefs: List[uuid.UUID]
    created_at: datetime
    expires_at: Optional[datetime]

class AgentResponse(BaseModel):
    """Schema for agent response."""
    model_config = ConfigDict(from_attributes=True)
    
    id: uuid.UUID
    name: str
    agent_type: str
    capabilities: Dict[str, Any]
    status: str
    last_heartbeat: Optional[datetime]
    created_at: datetime
    updated_at: datetime

class TaskCreate(BaseModel):
    """Schema for creating a task."""
    user_id: Optional[uuid.UUID] = None
    agent_id: uuid.UUID
    directive_id: uuid.UUID
    input_data: Dict[str, Any]

class TaskResponse(BaseModel):
    """Schema for task response."""
    model_config = ConfigDict(from_attributes=True)
    
    id: uuid.UUID
    user_id: Optional[uuid.UUID]
    agent_id: uuid.UUID
    directive_id: uuid.UUID
    input_data: Dict[str, Any]
    output_data: Optional[Dict[str, Any]]
    status: str
    error_message: Optional[str]
    created_at: datetime
    completed_at: Optional[datetime]

# Database dependency
async def get_db() -> AsyncSession:
    """Get database session."""
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()