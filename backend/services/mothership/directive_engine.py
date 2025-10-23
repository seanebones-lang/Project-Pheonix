"""
Directive Engine for generating task-specific directives based on ontological values and beliefs.
"""

import uuid
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from shared.models import Directive, DirectiveCreate, Value, Belief
from shared.ai_providers import ai_manager, AIProvider
from ontology_manager import OntologyManager

class DirectiveEngine:
    """Generates directives for agents based on ontological values and beliefs."""
    
    def __init__(self, db_session: AsyncSession):
        self.db = db_session
        self.ontology_manager = OntologyManager(db_session)
    
    async def generate_directive(self, task_description: str, task_type: str, user_context: Dict[str, Any] = None) -> Directive:
        """Generate a directive for a specific task."""
        
        # Analyze the task to identify relevant values and beliefs
        relevant_values, relevant_beliefs = await self._analyze_task(task_description, task_type)
        
        # Generate constraints based on the ontological analysis
        constraints = await self._generate_constraints(
            task_description, 
            task_type, 
            relevant_values, 
            relevant_beliefs,
            user_context
        )
        
        # Create the directive
        directive_data = DirectiveCreate(
            task_type=task_type,
            constraints=constraints,
            source_values=[v.id for v in relevant_values],
            source_beliefs=[b.id for b in relevant_beliefs]
        )
        
        directive = Directive(
            task_type=directive_data.task_type,
            constraints=directive_data.constraints,
            source_values=directive_data.source_values,
            source_beliefs=directive_data.source_beliefs
        )
        
        self.db.add(directive)
        await self.db.commit()
        await self.db.refresh(directive)
        
        return directive
    
    async def _analyze_task(self, task_description: str, task_type: str) -> Tuple[List[Value], List[Belief]]:
        """Analyze the task to identify relevant values and beliefs."""
        
        # Create a comprehensive task analysis prompt
        analysis_prompt = f"""
        Analyze this task and identify which ontological values and beliefs are most relevant:
        
        Task Type: {task_type}
        Task Description: {task_description}
        
        Consider the following aspects:
        1. What values should guide the execution of this task?
        2. What beliefs should inform how this task is performed?
        3. What ethical considerations are important?
        4. What quality standards should be maintained?
        
        Respond with a JSON object containing:
        - relevant_values: List of value names that apply
        - relevant_beliefs: List of belief names that apply
        - reasoning: Brief explanation of why these are relevant
        """
        
        # Get AI analysis
        analysis_schema = {
            "type": "object",
            "properties": {
                "relevant_values": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "relevant_beliefs": {
                    "type": "array", 
                    "items": {"type": "string"}
                },
                "reasoning": {"type": "string"}
            },
            "required": ["relevant_values", "relevant_beliefs", "reasoning"]
        }
        
        analysis = await ai_manager.generate_structured(analysis_prompt, analysis_schema)
        
        # Find matching values and beliefs in the database
        relevant_values = []
        relevant_beliefs = []
        
        # Search for values
        for value_name in analysis["relevant_values"]:
            similar_values = await self.ontology_manager.search_similar_values(value_name, limit=1)
            if similar_values and similar_values[0][1] < 0.3:  # Similarity threshold
                relevant_values.append(similar_values[0][0])
        
        # Search for beliefs
        for belief_name in analysis["relevant_beliefs"]:
            similar_beliefs = await self.ontology_manager.search_similar_beliefs(belief_name, limit=1)
            if similar_beliefs and similar_beliefs[0][1] < 0.3:  # Similarity threshold
                relevant_beliefs.append(similar_beliefs[0][0])
        
        # If no matches found, get the most general values and beliefs
        if not relevant_values:
            all_values = await self.ontology_manager.get_values(limit=3)
            relevant_values.extend(all_values)
        
        if not relevant_beliefs:
            all_beliefs = await self.ontology_manager.get_beliefs(limit=3)
            relevant_beliefs.extend(all_beliefs)
        
        return relevant_values, relevant_beliefs
    
    async def _generate_constraints(self, task_description: str, task_type: str, 
                                  values: List[Value], beliefs: List[Belief], 
                                  user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate specific constraints based on values and beliefs."""
        
        # Create constraint generation prompt
        values_text = "\n".join([f"- {v.name}: {v.description}" for v in values])
        beliefs_text = "\n".join([f"- {b.name}: {b.description}" for b in beliefs])
        
        constraint_prompt = f"""
        Generate specific constraints for executing this task based on the following ontological values and beliefs:
        
        Task: {task_description}
        Task Type: {task_type}
        
        Relevant Values:
        {values_text}
        
        Relevant Beliefs:
        {beliefs_text}
        
        User Context: {user_context or "No specific context provided"}
        
        Generate a JSON object with specific, actionable constraints that an AI agent should follow when executing this task. Include:
        - quality_standards: Specific quality requirements
        - ethical_guidelines: Ethical considerations to follow
        - output_format: How the output should be formatted
        - safety_measures: Safety precautions to take
        - performance_criteria: How success should be measured
        
        Make constraints specific and actionable, not generic.
        """
        
        constraint_schema = {
            "type": "object",
            "properties": {
                "quality_standards": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "ethical_guidelines": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "output_format": {
                    "type": "object",
                    "properties": {
                        "format": {"type": "string"},
                        "include_explanations": {"type": "boolean"},
                        "step_by_step": {"type": "boolean"}
                    }
                },
                "safety_measures": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "performance_criteria": {
                    "type": "array",
                    "items": {"type": "string"}
                }
            },
            "required": ["quality_standards", "ethical_guidelines", "output_format", "safety_measures", "performance_criteria"]
        }
        
        constraints = await ai_manager.generate_structured(constraint_prompt, constraint_schema)
        
        # Add metadata
        constraints["generated_at"] = "2025-01-27T00:00:00Z"
        constraints["source_values"] = [v.name for v in values]
        constraints["source_beliefs"] = [b.name for b in beliefs]
        
        return constraints
    
    async def get_directive(self, directive_id: uuid.UUID) -> Optional[Directive]:
        """Get a directive by ID."""
        return await self.db.get(Directive, directive_id)
    
    async def get_directives_by_task_type(self, task_type: str, limit: int = 10) -> List[Directive]:
        """Get directives by task type."""
        result = await self.db.execute(
            select(Directive)
            .where(Directive.task_type == task_type)
            .order_by(Directive.created_at.desc())
            .limit(limit)
        )
        return result.scalars().all()
    
    async def update_directive_constraints(self, directive_id: uuid.UUID, new_constraints: Dict[str, Any]) -> Directive:
        """Update constraints for an existing directive."""
        directive = await self.db.get(Directive, directive_id)
        if not directive:
            raise ValueError(f"Directive with id {directive_id} not found")
        
        directive.constraints = new_constraints
        await self.db.commit()
        await self.db.refresh(directive)
        
        return directive
    
    async def validate_directive_compliance(self, directive_id: uuid.UUID, agent_output: Dict[str, Any]) -> Dict[str, Any]:
        """Validate if agent output complies with directive constraints."""
        directive = await self.db.get(Directive, directive_id)
        if not directive:
            raise ValueError(f"Directive with id {directive_id} not found")
        
        validation_prompt = f"""
        Validate if the following agent output complies with the directive constraints:
        
        Directive Constraints:
        {directive.constraints}
        
        Agent Output:
        {agent_output}
        
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
        
        validation_result = await ai_manager.generate_structured(validation_prompt, validation_schema)
        
        return validation_result
