"""
ELCA-Specific Ontology Manager with 2025 AI Guidelines Integration.
Implements ELCA values, beliefs, and AI ethics guidelines.
"""

import uuid
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
import structlog

from shared.models import Value, Belief, ValueCreate, BeliefCreate
from shared.ai_providers import AIProviderManager
from shared.tenant_manager import TenantManager, TenantContext

logger = structlog.get_logger()

class ELCAOntologyManager:
    """ELCA-specific ontology manager with AI ethics integration."""
    
    def __init__(self, db: AsyncSession, tenant_context: Optional[TenantContext] = None):
        self.db = db
        self.ai_provider = AIProviderManager()
        self.tenant_manager = TenantManager(db)
        self.tenant_context = tenant_context
    
    async def initialize_elca_ontology(self, tenant_id: uuid.UUID):
        """Initialize ELCA-specific values and beliefs for a tenant."""
        
        # ELCA Core Values (2025 AI Guidelines)
        elca_values = [
            {
                "name": "Radical Hospitality",
                "description": "Welcome all people with open hearts, recognizing the inherent dignity of every person as created in God's image. AI should enhance, not replace, human connection and pastoral care."
            },
            {
                "name": "Grace-Centered Faith",
                "description": "Ground all actions in God's unconditional love and forgiveness. AI decisions should reflect grace, mercy, and understanding rather than judgment or exclusion."
            },
            {
                "name": "Justice and Advocacy",
                "description": "Work for justice, peace, and reconciliation in all relationships. AI should be used to amplify voices of the marginalized and promote equity."
            },
            {
                "name": "Stewardship of Creation",
                "description": "Care for God's creation and use resources responsibly. AI should be environmentally conscious and sustainable."
            },
            {
                "name": "Transparency and Accountability",
                "description": "Be open about AI use and maintain accountability for AI decisions. All AI-assisted content should be clearly marked."
            },
            {
                "name": "Inclusion and Diversity",
                "description": "Embrace diversity and work against bias. AI systems must be trained on diverse data and regularly audited for bias."
            },
            {
                "name": "Human Dignity",
                "description": "Respect the inherent worth of every person. AI should never dehumanize or replace human discernment in pastoral care."
            },
            {
                "name": "Community and Connection",
                "description": "Build authentic relationships and community. AI should facilitate, not replace, human connection and fellowship."
            }
        ]
        
        # ELCA Operational Beliefs (2025 AI Guidelines)
        elca_beliefs = [
            {
                "name": "AI-Assisted, Not AI-Replaced",
                "description": "AI should assist human ministry, not replace human discernment, especially in pastoral care, worship leadership, and spiritual guidance.",
                "related_values": ["Human Dignity", "Grace-Centered Faith"]
            },
            {
                "name": "Bias Detection and Mitigation",
                "description": "Regularly audit AI systems for bias, especially regarding race, gender, age, ability, and socioeconomic status. Implement corrective measures.",
                "related_values": ["Inclusion and Diversity", "Justice and Advocacy"]
            },
            {
                "name": "Transparent AI Decisions",
                "description": "Make AI decision-making processes transparent and explainable. Users should understand how AI recommendations are generated.",
                "related_values": ["Transparency and Accountability"]
            },
            {
                "name": "Privacy and Data Protection",
                "description": "Protect member data with the highest standards, especially sensitive information shared in pastoral care contexts.",
                "related_values": ["Human Dignity", "Stewardship of Creation"]
            },
            {
                "name": "Accessibility First",
                "description": "Ensure AI tools are accessible to people with disabilities and available in multiple languages for diverse congregations.",
                "related_values": ["Inclusion and Diversity", "Radical Hospitality"]
            },
            {
                "name": "Environmental Responsibility",
                "description": "Choose AI providers and models that minimize environmental impact. Consider carbon footprint in AI decisions.",
                "related_values": ["Stewardship of Creation"]
            },
            {
                "name": "Community-Centered Design",
                "description": "Design AI tools that strengthen community bonds and support congregational life rather than individual consumption.",
                "related_values": ["Community and Connection", "Radical Hospitality"]
            },
            {
                "name": "Ethical AI Procurement",
                "description": "Evaluate AI vendors based on their ethical practices, labor conditions, and alignment with ELCA values.",
                "related_values": ["Justice and Advocacy", "Stewardship of Creation"]
            }
        ]
        
        # Create values
        created_values = []
        for value_data in elca_values:
            value = Value(
                name=value_data["name"],
                description=value_data["description"],
                tenant_id=tenant_id
            )
            self.db.add(value)
            created_values.append(value)
        
        await self.db.commit()
        
        # Refresh values to get IDs
        for value in created_values:
            await self.db.refresh(value)
        
        # Create beliefs with value relationships
        for belief_data in elca_beliefs:
            # Find related value IDs
            related_value_ids = []
            for value_name in belief_data["related_values"]:
                for value in created_values:
                    if value.name == value_name:
                        related_value_ids.append(value.id)
                        break
            
            belief = Belief(
                name=belief_data["name"],
                description=belief_data["description"],
                related_values=related_value_ids,
                tenant_id=tenant_id
            )
            self.db.add(belief)
        
        await self.db.commit()
        
        logger.info("ELCA ontology initialized", tenant_id=str(tenant_id), values_count=len(elca_values), beliefs_count=len(elca_beliefs))
    
    async def create_value(self, value_data: ValueCreate, tenant_id: uuid.UUID) -> Value:
        """Create a new ontological value with ELCA compliance checks."""
        try:
            # Generate embedding for the value
            embedding = await self.ai_provider.get_embedding(
                f"{value_data.name}: {value_data.description}"
            )
            
            # Create value record
            value = Value(
                name=value_data.name,
                description=value_data.description,
                embedding=embedding,
                tenant_id=tenant_id
            )
            
            self.db.add(value)
            await self.db.commit()
            await self.db.refresh(value)
            
            logger.info("Created ELCA value with embedding", value_id=str(value.id), value_name=value.name, tenant_id=str(tenant_id))
            return value
            
        except Exception as e:
            await self.db.rollback()
            logger.error("Failed to create ELCA value", error=str(e), tenant_id=str(tenant_id))
            raise
    
    async def create_belief(self, belief_data: BeliefCreate, tenant_id: uuid.UUID) -> Belief:
        """Create a new ontological belief with ELCA compliance checks."""
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
                related_values=belief_data.related_values,
                tenant_id=tenant_id
            )
            
            self.db.add(belief)
            await self.db.commit()
            await self.db.refresh(belief)
            
            logger.info("Created ELCA belief with embedding", belief_id=str(belief.id), belief_name=belief.name, tenant_id=str(tenant_id))
            return belief
            
        except Exception as e:
            await self.db.rollback()
            logger.error("Failed to create ELCA belief", error=str(e), tenant_id=str(tenant_id))
            raise
    
    async def get_values(self, tenant_id: uuid.UUID, limit: int = 100, offset: int = 0) -> List[Value]:
        """Get all ontological values for a tenant."""
        try:
            result = await self.db.execute(
                select(Value)
                .where(Value.tenant_id == tenant_id)
                .order_by(Value.created_at.desc())
                .limit(limit)
                .offset(offset)
            )
            return result.scalars().all()
        except Exception as e:
            logger.error("Failed to get ELCA values", error=str(e), tenant_id=str(tenant_id))
            raise
    
    async def get_beliefs(self, tenant_id: uuid.UUID, limit: int = 100, offset: int = 0) -> List[Belief]:
        """Get all ontological beliefs for a tenant."""
        try:
            result = await self.db.execute(
                select(Belief)
                .where(Belief.tenant_id == tenant_id)
                .order_by(Belief.created_at.desc())
                .limit(limit)
                .offset(offset)
            )
            return result.scalars().all()
        except Exception as e:
            logger.error("Failed to get ELCA beliefs", error=str(e), tenant_id=str(tenant_id))
            raise
    
    async def search_values(self, query: str, tenant_id: uuid.UUID, limit: int = 10) -> List[Value]:
        """Search values using semantic similarity with ELCA context."""
        try:
            # Generate embedding for search query
            query_embedding = await self.ai_provider.get_embedding(query)
            
            # Perform vector similarity search within tenant
            result = await self.db.execute(
                select(Value)
                .where(Value.tenant_id == tenant_id)
                .order_by(Value.embedding.cosine_distance(query_embedding))
                .limit(limit)
            )
            return result.scalars().all()
        except Exception as e:
            logger.error("Failed to search ELCA values", error=str(e), tenant_id=str(tenant_id))
            raise
    
    async def search_beliefs(self, query: str, tenant_id: uuid.UUID, limit: int = 10) -> List[Belief]:
        """Search beliefs using semantic similarity with ELCA context."""
        try:
            # Generate embedding for search query
            query_embedding = await self.ai_provider.get_embedding(query)
            
            # Perform vector similarity search within tenant
            result = await self.db.execute(
                select(Belief)
                .where(Belief.tenant_id == tenant_id)
                .order_by(Belief.embedding.cosine_distance(query_embedding))
                .limit(limit)
            )
            return result.scalars().all()
        except Exception as e:
            logger.error("Failed to search ELCA beliefs", error=str(e), tenant_id=str(tenant_id))
            raise
    
    async def get_relevant_values_and_beliefs(
        self, 
        task_description: str, 
        task_type: str,
        tenant_id: uuid.UUID,
        limit: int = 5
    ) -> tuple[List[Value], List[Belief]]:
        """Get relevant values and beliefs for a task with ELCA context."""
        try:
            # Create search query with ELCA context
            search_query = f"ELCA {task_type}: {task_description}"
            
            # Search for relevant values and beliefs within tenant
            relevant_values = await self.search_values(search_query, tenant_id, limit)
            relevant_beliefs = await self.search_beliefs(search_query, tenant_id, limit)
            
            logger.info(
                "Found relevant ELCA ontology items",
                task_type=task_type,
                tenant_id=str(tenant_id),
                values_count=len(relevant_values),
                beliefs_count=len(relevant_beliefs)
            )
            
            return relevant_values, relevant_beliefs
            
        except Exception as e:
            logger.error("Failed to get relevant ELCA ontology items", error=str(e), tenant_id=str(tenant_id))
            raise
    
    async def audit_ai_bias(self, tenant_id: uuid.UUID) -> Dict[str, Any]:
        """Audit AI systems for bias according to ELCA guidelines."""
        try:
            # Get all beliefs related to bias detection
            bias_beliefs = await self.search_beliefs("bias detection mitigation", tenant_id, 10)
            
            # Generate bias audit report using AI
            audit_prompt = f"""
            Conduct a bias audit for an ELCA congregation's AI system according to 2025 AI guidelines.
            
            ELCA Values to Consider:
            - Radical Hospitality
            - Inclusion and Diversity
            - Justice and Advocacy
            - Human Dignity
            
            Generate a comprehensive bias audit report covering:
            1. Demographic representation in training data
            2. Potential bias in AI outputs
            3. Accessibility considerations
            4. Recommendations for bias mitigation
            5. Compliance with ELCA 2025 AI guidelines
            
            Focus on pastoral care, worship planning, and member engagement use cases.
            """
            
            audit_schema = {
                "type": "object",
                "properties": {
                    "demographic_analysis": {
                        "type": "object",
                        "properties": {
                            "age_representation": {"type": "string"},
                            "gender_representation": {"type": "string"},
                            "racial_ethnic_diversity": {"type": "string"},
                            "ability_accessibility": {"type": "string"},
                            "socioeconomic_diversity": {"type": "string"}
                        }
                    },
                    "bias_risks": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "risk_type": {"type": "string"},
                                "severity": {"type": "string"},
                                "description": {"type": "string"},
                                "mitigation_strategy": {"type": "string"}
                            }
                        }
                    },
                    "accessibility_score": {"type": "integer", "minimum": 0, "maximum": 100},
                    "elca_compliance_score": {"type": "integer", "minimum": 0, "maximum": 100},
                    "recommendations": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                },
                "required": ["demographic_analysis", "bias_risks", "accessibility_score", "elca_compliance_score", "recommendations"]
            }
            
            audit_result = await self.ai_provider.generate_structured_output(audit_prompt, audit_schema)
            
            logger.info("AI bias audit completed", tenant_id=str(tenant_id), compliance_score=audit_result.get("elca_compliance_score"))
            
            return audit_result
            
        except Exception as e:
            logger.error("Failed to conduct AI bias audit", error=str(e), tenant_id=str(tenant_id))
            raise
    
    async def validate_ai_content(self, content: str, tenant_id: uuid.UUID) -> Dict[str, Any]:
        """Validate AI-generated content against ELCA guidelines."""
        try:
            # Get ELCA values for validation
            elca_values = await self.get_values(tenant_id, limit=50)
            elca_beliefs = await self.get_beliefs(tenant_id, limit=50)
            
            # Create validation prompt
            values_text = "\n".join([f"- {v.name}: {v.description}" for v in elca_values])
            beliefs_text = "\n".join([f"- {b.name}: {b.description}" for b in elca_beliefs])
            
            validation_prompt = f"""
            Validate the following AI-generated content against ELCA 2025 AI guidelines:
            
            Content to validate: {content}
            
            ELCA Values:
            {values_text}
            
            ELCA Beliefs:
            {beliefs_text}
            
            Check for:
            1. Alignment with ELCA values and beliefs
            2. Appropriate tone for church context
            3. Inclusivity and accessibility
            4. Transparency about AI assistance
            5. Respect for human dignity
            6. Avoidance of bias or exclusion
            
            Provide a validation report with recommendations.
            """
            
            validation_schema = {
                "type": "object",
                "properties": {
                    "is_approved": {"type": "boolean"},
                    "compliance_score": {"type": "integer", "minimum": 0, "maximum": 100},
                    "value_alignment": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "concerns": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "type": {"type": "string"},
                                "severity": {"type": "string"},
                                "description": {"type": "string"},
                                "suggestion": {"type": "string"}
                            }
                        }
                    },
                    "recommendations": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "requires_human_review": {"type": "boolean"}
                },
                "required": ["is_approved", "compliance_score", "value_alignment", "concerns", "recommendations", "requires_human_review"]
            }
            
            validation_result = await self.ai_provider.generate_structured_output(validation_prompt, validation_schema)
            
            logger.info("AI content validation completed", tenant_id=str(tenant_id), approved=validation_result.get("is_approved"))
            
            return validation_result
            
        except Exception as e:
            logger.error("Failed to validate AI content", error=str(e), tenant_id=str(tenant_id))
            raise

