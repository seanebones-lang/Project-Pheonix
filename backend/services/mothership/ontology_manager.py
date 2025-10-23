"""
Ontology Manager for managing values, beliefs, and their relationships.
"""

import uuid
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload

from shared.models import Value, Belief, Directive, ValueCreate, BeliefCreate, DirectiveCreate
from shared.ai_providers import ai_manager, AIProvider

class OntologyManager:
    """Manages the ontological library of values and beliefs."""
    
    def __init__(self, db_session: AsyncSession):
        self.db = db_session
    
    async def create_value(self, value_data: ValueCreate) -> Value:
        """Create a new ontological value."""
        # Generate embedding for the value
        embedding = await ai_manager.generate_embeddings(f"{value_data.name}: {value_data.description}")
        
        value = Value(
            name=value_data.name,
            description=value_data.description,
            embedding=embedding
        )
        
        self.db.add(value)
        await self.db.commit()
        await self.db.refresh(value)
        return value
    
    async def create_belief(self, belief_data: BeliefCreate) -> Belief:
        """Create a new ontological belief."""
        # Generate embedding for the belief
        embedding = await ai_manager.generate_embeddings(f"{belief_data.name}: {belief_data.description}")
        
        belief = Belief(
            name=belief_data.name,
            description=belief_data.description,
            embedding=embedding,
            related_values=belief_data.related_values
        )
        
        self.db.add(belief)
        await self.db.commit()
        await self.db.refresh(belief)
        return belief
    
    async def get_values(self, limit: int = 100, offset: int = 0) -> List[Value]:
        """Get all ontological values."""
        result = await self.db.execute(
            select(Value).offset(offset).limit(limit)
        )
        return result.scalars().all()
    
    async def get_beliefs(self, limit: int = 100, offset: int = 0) -> List[Belief]:
        """Get all ontological beliefs."""
        result = await self.db.execute(
            select(Belief).offset(offset).limit(limit)
        )
        return result.scalars().all()
    
    async def search_similar_values(self, query: str, limit: int = 5) -> List[Tuple[Value, float]]:
        """Search for values similar to the query using vector similarity."""
        query_embedding = await ai_manager.generate_embeddings(query)
        
        result = await self.db.execute(
            select(Value, Value.embedding.cosine_distance(query_embedding).label('distance'))
            .order_by('distance')
            .limit(limit)
        )
        
        return [(row.Value, row.distance) for row in result]
    
    async def search_similar_beliefs(self, query: str, limit: int = 5) -> List[Tuple[Belief, float]]:
        """Search for beliefs similar to the query using vector similarity."""
        query_embedding = await ai_manager.generate_embeddings(query)
        
        result = await self.db.execute(
            select(Belief, Belief.embedding.cosine_distance(query_embedding).label('distance'))
            .order_by('distance')
            .limit(limit)
        )
        
        return [(row.Belief, row.distance) for row in result]
    
    async def get_related_beliefs(self, value_id: uuid.UUID) -> List[Belief]:
        """Get beliefs related to a specific value."""
        result = await self.db.execute(
            select(Belief).where(Belief.related_values.contains([value_id]))
        )
        return result.scalars().all()
    
    async def get_related_values(self, belief_id: uuid.UUID) -> List[Value]:
        """Get values related to a specific belief."""
        belief = await self.db.get(Belief, belief_id)
        if not belief or not belief.related_values:
            return []
        
        result = await self.db.execute(
            select(Value).where(Value.id.in_(belief.related_values))
        )
        return result.scalars().all()
    
    async def update_value_embedding(self, value_id: uuid.UUID) -> Value:
        """Update the embedding for a value."""
        value = await self.db.get(Value, value_id)
        if not value:
            raise ValueError(f"Value with id {value_id} not found")
        
        embedding = await ai_manager.generate_embeddings(f"{value.name}: {value.description}")
        value.embedding = embedding
        
        await self.db.commit()
        await self.db.refresh(value)
        return value
    
    async def update_belief_embedding(self, belief_id: uuid.UUID) -> Belief:
        """Update the embedding for a belief."""
        belief = await self.db.get(Belief, belief_id)
        if not belief:
            raise ValueError(f"Belief with id {belief_id} not found")
        
        embedding = await ai_manager.generate_embeddings(f"{belief.name}: {belief.description}")
        belief.embedding = embedding
        
        await self.db.commit()
        await self.db.refresh(belief)
        return belief
    
    async def get_ontology_summary(self) -> Dict[str, Any]:
        """Get a summary of the ontology."""
        values_count = await self.db.scalar(select(func.count(Value.id)))
        beliefs_count = await self.db.scalar(select(func.count(Belief.id)))
        
        return {
            "total_values": values_count,
            "total_beliefs": beliefs_count,
            "ontology_size": values_count + beliefs_count
        }
