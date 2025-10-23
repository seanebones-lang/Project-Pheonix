"""
Ontology Manager for handling values and beliefs with vector embeddings.
"""

import uuid
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.dialects.postgresql import insert
import structlog

from ...shared.models import Value, Belief, ValueCreate, BeliefCreate
from ...shared.ai_providers import AIProviderManager

logger = structlog.get_logger()

class OntologyManager:
    """Manages ontological values and beliefs with vector embeddings."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.ai_provider = AIProviderManager()
    
    async def create_value(self, value_data: ValueCreate) -> Value:
        """Create a new ontological value with embedding."""
        try:
            # Generate embedding for the value
            embedding = await self.ai_provider.get_embedding(
                f"{value_data.name}: {value_data.description}"
            )
            
            # Create value record
            value = Value(
                name=value_data.name,
                description=value_data.description,
                embedding=embedding
            )
            
            self.db.add(value)
            await self.db.commit()
            await self.db.refresh(value)
            
            logger.info("Created value with embedding", value_id=str(value.id), value_name=value.name)
            return value
            
        except Exception as e:
            await self.db.rollback()
            logger.error("Failed to create value", error=str(e))
            raise
    
    async def get_values(self, limit: int = 100, offset: int = 0) -> List[Value]:
        """Get all ontological values."""
        try:
            result = await self.db.execute(
                select(Value)
                .order_by(Value.created_at.desc())
                .limit(limit)
                .offset(offset)
            )
            return result.scalars().all()
        except Exception as e:
            logger.error("Failed to get values", error=str(e))
            raise
    
    async def search_values(self, query: str, limit: int = 10) -> List[Value]:
        """Search values using semantic similarity."""
        try:
            # Generate embedding for search query
            query_embedding = await self.ai_provider.get_embedding(query)
            
            # Perform vector similarity search
            result = await self.db.execute(
                select(Value)
                .order_by(Value.embedding.cosine_distance(query_embedding))
                .limit(limit)
            )
            return result.scalars().all()
        except Exception as e:
            logger.error("Failed to search values", error=str(e))
            raise
    
    async def create_belief(self, belief_data: BeliefCreate) -> Belief:
        """Create a new ontological belief with embedding."""
        try:
            # Generate embedding for the belief
            embedding = await self.ai_provider.get_embedding(
                f"{belief_data.name}: {belief_data.description}"
            )
            
            # Create belief record
            belief = Belief(
                name=belief_data.name,
                description=belief_data.description,
                embedding=embedding,
                related_values=belief_data.related_values
            )
            
            self.db.add(belief)
            await self.db.commit()
            await self.db.refresh(belief)
            
            logger.info("Created belief with embedding", belief_id=str(belief.id), belief_name=belief.name)
            return belief
            
        except Exception as e:
            await self.db.rollback()
            logger.error("Failed to create belief", error=str(e))
            raise
    
    async def get_beliefs(self, limit: int = 100, offset: int = 0) -> List[Belief]:
        """Get all ontological beliefs."""
        try:
            result = await self.db.execute(
                select(Belief)
                .order_by(Belief.created_at.desc())
                .limit(limit)
                .offset(offset)
            )
            return result.scalars().all()
        except Exception as e:
            logger.error("Failed to get beliefs", error=str(e))
            raise
    
    async def search_beliefs(self, query: str, limit: int = 10) -> List[Belief]:
        """Search beliefs using semantic similarity."""
        try:
            # Generate embedding for search query
            query_embedding = await self.ai_provider.get_embedding(query)
            
            # Perform vector similarity search
            result = await self.db.execute(
                select(Belief)
                .order_by(Belief.embedding.cosine_distance(query_embedding))
                .limit(limit)
            )
            return result.scalars().all()
        except Exception as e:
            logger.error("Failed to search beliefs", error=str(e))
            raise
    
    async def get_relevant_values_and_beliefs(
        self, 
        task_description: str, 
        task_type: str,
        limit: int = 5
    ) -> tuple[List[Value], List[Belief]]:
        """Get relevant values and beliefs for a task."""
        try:
            # Create search query combining task description and type
            search_query = f"{task_type}: {task_description}"
            
            # Search for relevant values and beliefs
            relevant_values = await self.search_values(search_query, limit)
            relevant_beliefs = await self.search_beliefs(search_query, limit)
            
            logger.info(
                "Found relevant ontology items",
                task_type=task_type,
                values_count=len(relevant_values),
                beliefs_count=len(relevant_beliefs)
            )
            
            return relevant_values, relevant_beliefs
            
        except Exception as e:
            logger.error("Failed to get relevant ontology items", error=str(e))
            raise
    
    async def update_value_embedding(self, value_id: uuid.UUID) -> bool:
        """Update embedding for an existing value."""
        try:
            # Get the value
            result = await self.db.execute(select(Value).where(Value.id == value_id))
            value = result.scalar_one_or_none()
            
            if not value:
                return False
            
            # Generate new embedding
            embedding = await self.ai_provider.get_embedding(
                f"{value.name}: {value.description}"
            )
            
            # Update the embedding
            value.embedding = embedding
            await self.db.commit()
            
            logger.info("Updated value embedding", value_id=str(value_id))
            return True
            
        except Exception as e:
            await self.db.rollback()
            logger.error("Failed to update value embedding", error=str(e))
            raise
    
    async def update_belief_embedding(self, belief_id: uuid.UUID) -> bool:
        """Update embedding for an existing belief."""
        try:
            # Get the belief
            result = await self.db.execute(select(Belief).where(Belief.id == belief_id))
            belief = result.scalar_one_or_none()
            
            if not belief:
                return False
            
            # Generate new embedding
            embedding = await self.ai_provider.get_embedding(
                f"{belief.name}: {belief.description}"
            )
            
            # Update the embedding
            belief.embedding = embedding
            await self.db.commit()
            
            logger.info("Updated belief embedding", belief_id=str(belief_id))
            return True
            
        except Exception as e:
            await self.db.rollback()
            logger.error("Failed to update belief embedding", error=str(e))
            raise