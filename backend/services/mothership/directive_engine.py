"""
Directive Engine for generating AI task constraints based on ontological values and beliefs.
"""

import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import structlog

from ...shared.models import Directive, Value, Belief, DirectiveCreate
from ...shared.ai_providers import AIProviderManager
from .ontology_manager import OntologyManager

logger = structlog.get_logger()

class DirectiveEngine:
    """Generates AI directives based on ontological values and beliefs."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.ai_provider = AIProviderManager()
        self.ontology_manager = OntologyManager(db)
    
    async def generate_directive(
        self, 
        task_description: str, 
        task_type: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Directive:
        """Generate a directive for a specific task."""
        try:
            # Get relevant values and beliefs
            relevant_values, relevant_beliefs = await self.ontology_manager.get_relevant_values_and_beliefs(
                task_description, task_type, limit=5
            )
            
            # Generate constraints using AI
            constraints = await self._generate_constraints(
                task_description, 
                task_type, 
                relevant_values, 
                relevant_beliefs,
                user_context
            )
            
            # Create directive
            directive = Directive(
                task_type=task_type,
                constraints=constraints,
                source_values=[v.id for v in relevant_values],
                source_beliefs=[b.id for b in relevant_beliefs],
                expires_at=datetime.utcnow() + timedelta(hours=24)  # 24-hour expiry
            )
            
            self.db.add(directive)
            await self.db.commit()
            await self.db.refresh(directive)
            
            logger.info(
                "Generated directive",
                directive_id=str(directive.id),
                task_type=task_type,
                constraints_count=len(constraints)
            )
            
            return directive
            
        except Exception as e:
            await self.db.rollback()
            logger.error("Failed to generate directive", error=str(e))
            raise
    
    async def _generate_constraints(
        self,
        task_description: str,
        task_type: str,
        relevant_values: List[Value],
        relevant_beliefs: List[Belief],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate task constraints using AI based on relevant ontology."""
        
        # Build context from relevant values and beliefs
        values_context = "\n".join([f"- {v.name}: {v.description}" for v in relevant_values])
        beliefs_context = "\n".join([f"- {b.name}: {b.description}" for b in relevant_beliefs])
        
        # Create the prompt
        prompt = f"""
        You are the Mothership AI directive engine. Generate task constraints for an AI agent based on ontological values and beliefs.
        
        Task Type: {task_type}
        Task Description: {task_description}
        
        Relevant Values:
        {values_context}
        
        Relevant Beliefs:
        {beliefs_context}
        
        User Context: {user_context or "None"}
        
        Generate a JSON object with the following structure:
        {{
            "ethical_constraints": [
                "List of ethical guidelines the agent must follow"
            ],
            "quality_standards": [
                "List of quality requirements for the task"
            ],
            "safety_measures": [
                "List of safety precautions to implement"
            ],
            "output_format": {{
                "description": "Expected output format",
                "validation_rules": ["List of validation rules"]
            }},
            "resource_limits": {{
                "max_computation_time": "Maximum time allowed",
                "max_memory_usage": "Maximum memory allowed",
                "max_api_calls": "Maximum API calls allowed"
            }},
            "monitoring_requirements": [
                "List of monitoring and logging requirements"
            ],
            "fallback_behavior": {{
                "on_error": "What to do when errors occur",
                "on_timeout": "What to do when timeout occurs",
                "on_invalid_input": "What to do with invalid input"
            }}
        }}
        
        Ensure the constraints are specific, actionable, and aligned with the provided values and beliefs.
        """
        
        schema = {
            "type": "object",
            "properties": {
                "ethical_constraints": {"type": "array", "items": {"type": "string"}},
                "quality_standards": {"type": "array", "items": {"type": "string"}},
                "safety_measures": {"type": "array", "items": {"type": "string"}},
                "output_format": {
                    "type": "object",
                    "properties": {
                        "description": {"type": "string"},
                        "validation_rules": {"type": "array", "items": {"type": "string"}}
                    }
                },
                "resource_limits": {
                    "type": "object",
                    "properties": {
                        "max_computation_time": {"type": "string"},
                        "max_memory_usage": {"type": "string"},
                        "max_api_calls": {"type": "string"}
                    }
                },
                "monitoring_requirements": {"type": "array", "items": {"type": "string"}},
                "fallback_behavior": {
                    "type": "object",
                    "properties": {
                        "on_error": {"type": "string"},
                        "on_timeout": {"type": "string"},
                        "on_invalid_input": {"type": "string"}
                    }
                }
            },
            "required": ["ethical_constraints", "quality_standards", "safety_measures", "output_format", "resource_limits", "monitoring_requirements", "fallback_behavior"]
        }
        
        try:
            constraints = await self.ai_provider.generate_structured_output(prompt, schema)
            return constraints
        except Exception as e:
            logger.warning("AI constraint generation failed, using defaults", error=str(e))
            return self._get_default_constraints(task_type)
    
    def _get_default_constraints(self, task_type: str) -> Dict[str, Any]:
        """Get default constraints when AI generation fails."""
        return {
            "ethical_constraints": [
                "Maintain user privacy and data protection",
                "Provide accurate and truthful information",
                "Respect user autonomy and choices"
            ],
            "quality_standards": [
                "Ensure output accuracy and completeness",
                "Provide clear explanations when requested",
                "Validate all inputs before processing"
            ],
            "safety_measures": [
                "Implement input validation and sanitization",
                "Log all operations for audit purposes",
                "Handle errors gracefully without exposing sensitive information"
            ],
            "output_format": {
                "description": "Structured JSON response with clear status and data fields",
                "validation_rules": [
                    "Response must be valid JSON",
                    "Include status field indicating success/failure",
                    "Include error messages when applicable"
                ]
            },
            "resource_limits": {
                "max_computation_time": "30 seconds",
                "max_memory_usage": "512MB",
                "max_api_calls": "10"
            },
            "monitoring_requirements": [
                "Log task start and completion times",
                "Monitor resource usage",
                "Track success/failure rates"
            ],
            "fallback_behavior": {
                "on_error": "Return error message and log details",
                "on_timeout": "Return timeout message and partial results if available",
                "on_invalid_input": "Return validation error with specific field issues"
            }
        }
    
    async def get_directive(self, directive_id: uuid.UUID) -> Optional[Directive]:
        """Get a directive by ID."""
        try:
            result = await self.db.execute(select(Directive).where(Directive.id == directive_id))
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error("Failed to get directive", error=str(e))
            raise
    
    async def validate_directive_compliance(
        self, 
        directive_id: uuid.UUID, 
        agent_output: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate agent output against directive constraints."""
        try:
            directive = await self.get_directive(directive_id)
            if not directive:
                return {"valid": False, "error": "Directive not found"}
            
            # Check if directive has expired
            if directive.expires_at and datetime.utcnow() > directive.expires_at:
                return {"valid": False, "error": "Directive has expired"}
            
            # Validate against constraints
            validation_result = {
                "valid": True,
                "violations": [],
                "warnings": []
            }
            
            constraints = directive.constraints
            
            # Check output format
            if "output_format" in constraints:
                format_constraints = constraints["output_format"]
                if "validation_rules" in format_constraints:
                    for rule in format_constraints["validation_rules"]:
                        if not self._validate_output_rule(agent_output, rule):
                            validation_result["violations"].append(f"Output format violation: {rule}")
                            validation_result["valid"] = False
            
            # Check ethical constraints
            if "ethical_constraints" in constraints:
                for constraint in constraints["ethical_constraints"]:
                    if not self._check_ethical_compliance(agent_output, constraint):
                        validation_result["warnings"].append(f"Ethical concern: {constraint}")
            
            logger.info(
                "Directive compliance validation completed",
                directive_id=str(directive_id),
                valid=validation_result["valid"],
                violations_count=len(validation_result["violations"])
            )
            
            return validation_result
            
        except Exception as e:
            logger.error("Failed to validate directive compliance", error=str(e))
            raise
    
    def _validate_output_rule(self, output: Dict[str, Any], rule: str) -> bool:
        """Validate output against a specific rule."""
        # This is a simplified implementation
        # In production, you'd want more sophisticated rule validation
        if "valid JSON" in rule.lower():
            try:
                import json
                json.dumps(output)
                return True
            except:
                return False
        elif "status field" in rule.lower():
            return "status" in output
        return True  # Default to valid for unknown rules
    
    def _check_ethical_compliance(self, output: Dict[str, Any], constraint: str) -> bool:
        """Check if output complies with ethical constraint."""
        # This is a simplified implementation
        # In production, you'd want more sophisticated ethical checking
        output_str = str(output).lower()
        
        if "privacy" in constraint.lower():
            return "password" not in output_str and "secret" not in output_str
        elif "accurate" in constraint.lower():
            return "error" not in output_str or output.get("status") != "error"
        
        return True  # Default to compliant for unknown constraints