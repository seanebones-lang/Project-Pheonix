"""
Multi-tenancy support for ELCA congregations and synods.
Implements tenant isolation with Row-Level Security (RLS) in PostgreSQL.
"""

import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from enum import Enum
from sqlalchemy import Column, String, Text, DateTime, JSON, Boolean, ForeignKey, Index, select
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from pydantic import BaseModel, Field, ConfigDict
from pgvector.sqlalchemy import Vector

Base = declarative_base()

class TenantType(str, Enum):
    CONGREGATION = "congregation"
    SYNOD = "synod"
    CHURCHWIDE = "churchwide"

class TenantStatus(str, Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    PENDING = "pending"
    INACTIVE = "inactive"

class Tenant(Base):
    """Tenant model for ELCA congregations and synods."""
    __tablename__ = "tenants"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True, nullable=False)
    tenant_type = Column(String(50), nullable=False, default=TenantType.CONGREGATION)
    status = Column(String(50), nullable=False, default=TenantStatus.ACTIVE)
    
    # ELCA-specific fields
    synod_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=True)
    congregation_number = Column(String(20), nullable=True)
    elca_id = Column(String(50), nullable=True, unique=True)
    
    # Configuration
    settings = Column(JSONB, nullable=False, default=dict)
    features = Column(JSONB, nullable=False, default=dict)
    
    # Contact information
    contact_email = Column(String(255), nullable=True)
    contact_phone = Column(String(50), nullable=True)
    address = Column(JSONB, nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(UUID(as_uuid=True), nullable=True)
    
    # Relationships
    parent_synod = relationship("Tenant", remote_side=[id], backref="congregations")
    
    # Indexes
    __table_args__ = (
        Index('idx_tenant_slug', 'slug'),
        Index('idx_tenant_type', 'tenant_type'),
        Index('idx_tenant_synod', 'synod_id'),
        Index('idx_tenant_status', 'status'),
    )

class TenantUser(Base):
    """User-tenant relationship for multi-tenancy."""
    __tablename__ = "tenant_users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    role = Column(String(50), nullable=False, default="member")
    permissions = Column(JSONB, nullable=False, default=dict)
    
    # Status
    is_active = Column(Boolean, nullable=False, default=True)
    joined_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    tenant = relationship("Tenant")
    
    # Indexes
    __table_args__ = (
        Index('idx_tenant_user_user', 'user_id'),
        Index('idx_tenant_user_tenant', 'tenant_id'),
        Index('idx_tenant_user_active', 'is_active'),
    )

# Pydantic schemas
class TenantCreate(BaseModel):
    """Schema for creating a tenant."""
    name: str = Field(..., min_length=1, max_length=255)
    slug: str = Field(..., min_length=1, max_length=100, regex=r'^[a-z0-9-]+$')
    tenant_type: TenantType = TenantType.CONGREGATION
    synod_id: Optional[uuid.UUID] = None
    congregation_number: Optional[str] = None
    elca_id: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    address: Optional[Dict[str, Any]] = None
    settings: Dict[str, Any] = Field(default_factory=dict)
    features: Dict[str, Any] = Field(default_factory=dict)

class TenantResponse(BaseModel):
    """Schema for tenant response."""
    model_config = ConfigDict(from_attributes=True)
    
    id: uuid.UUID
    name: str
    slug: str
    tenant_type: str
    status: str
    synod_id: Optional[uuid.UUID]
    congregation_number: Optional[str]
    elca_id: Optional[str]
    contact_email: Optional[str]
    contact_phone: Optional[str]
    address: Optional[Dict[str, Any]]
    settings: Dict[str, Any]
    features: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

class TenantUserCreate(BaseModel):
    """Schema for adding user to tenant."""
    user_id: uuid.UUID
    role: str = "member"
    permissions: Dict[str, Any] = Field(default_factory=dict)

class TenantUserResponse(BaseModel):
    """Schema for tenant user response."""
    model_config = ConfigDict(from_attributes=True)
    
    id: uuid.UUID
    user_id: uuid.UUID
    tenant_id: uuid.UUID
    role: str
    permissions: Dict[str, Any]
    is_active: bool
    joined_at: datetime

class TenantContext(BaseModel):
    """Context for current tenant operations."""
    tenant_id: uuid.UUID
    tenant_slug: str
    tenant_type: str
    user_role: str
    user_permissions: Dict[str, Any]

class TenantManager:
    """Manages tenant operations and context."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_tenant(self, tenant_data: TenantCreate) -> Tenant:
        """Create a new tenant."""
        tenant = Tenant(
            name=tenant_data.name,
            slug=tenant_data.slug,
            tenant_type=tenant_data.tenant_type,
            synod_id=tenant_data.synod_id,
            congregation_number=tenant_data.congregation_number,
            elca_id=tenant_data.elca_id,
            contact_email=tenant_data.contact_email,
            contact_phone=tenant_data.contact_phone,
            address=tenant_data.address,
            settings=tenant_data.settings,
            features=tenant_data.features
        )
        
        self.db.add(tenant)
        await self.db.commit()
        await self.db.refresh(tenant)
        
        # Create tenant-specific schema for data isolation
        await self._create_tenant_schema(tenant.slug)
        
        return tenant
    
    async def get_tenant(self, tenant_id: uuid.UUID) -> Optional[Tenant]:
        """Get tenant by ID."""
        result = await self.db.execute(
            select(Tenant).where(Tenant.id == tenant_id)
        )
        return result.scalar_one_or_none()
    
    async def get_tenant_by_slug(self, slug: str) -> Optional[Tenant]:
        """Get tenant by slug."""
        result = await self.db.execute(
            select(Tenant).where(Tenant.slug == slug)
        )
        return result.scalar_one_or_none()
    
    async def add_user_to_tenant(
        self, 
        tenant_id: uuid.UUID, 
        user_data: TenantUserCreate
    ) -> TenantUser:
        """Add user to tenant."""
        tenant_user = TenantUser(
            user_id=user_data.user_id,
            tenant_id=tenant_id,
            role=user_data.role,
            permissions=user_data.permissions
        )
        
        self.db.add(tenant_user)
        await self.db.commit()
        await self.db.refresh(tenant_user)
        
        return tenant_user
    
    async def get_tenant_users(self, tenant_id: uuid.UUID) -> List[TenantUser]:
        """Get all users for a tenant."""
        result = await self.db.execute(
            select(TenantUser)
            .where(TenantUser.tenant_id == tenant_id)
            .where(TenantUser.is_active == True)
        )
        return result.scalars().all()
    
    async def get_user_tenants(self, user_id: uuid.UUID) -> List[Tenant]:
        """Get all tenants for a user."""
        result = await self.db.execute(
            select(Tenant)
            .join(TenantUser)
            .where(TenantUser.user_id == user_id)
            .where(TenantUser.is_active == True)
        )
        return result.scalars().all()
    
    async def _create_tenant_schema(self, tenant_slug: str):
        """Create tenant-specific schema for data isolation."""
        schema_name = f"tenant_{tenant_slug}"
        
        # Create schema
        await self.db.execute(f"CREATE SCHEMA IF NOT EXISTS {schema_name}")
        
        # Enable RLS on tenant-specific tables
        tables = ['values', 'beliefs', 'directives', 'agents', 'tasks']
        for table in tables:
            await self.db.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
            
            # Create RLS policy for tenant isolation
            await self.db.execute(f"""
                CREATE POLICY tenant_isolation_{table} ON {table}
                FOR ALL TO PUBLIC
                USING (tenant_id = current_setting('app.current_tenant_id')::uuid)
            """)
    
    async def set_tenant_context(self, tenant_id: uuid.UUID):
        """Set current tenant context for RLS."""
        await self.db.execute(f"SET app.current_tenant_id = '{tenant_id}'")
    
    async def get_tenant_context(self, user_id: uuid.UUID, tenant_slug: str) -> Optional[TenantContext]:
        """Get tenant context for user."""
        tenant = await self.get_tenant_by_slug(tenant_slug)
        if not tenant:
            return None
        
        # Get user's role in tenant
        result = await self.db.execute(
            select(TenantUser)
            .where(TenantUser.user_id == user_id)
            .where(TenantUser.tenant_id == tenant.id)
            .where(TenantUser.is_active == True)
        )
        tenant_user = result.scalar_one_or_none()
        
        if not tenant_user:
            return None
        
        return TenantContext(
            tenant_id=tenant.id,
            tenant_slug=tenant.slug,
            tenant_type=tenant.tenant_type,
            user_role=tenant_user.role,
            user_permissions=tenant_user.permissions
        )

