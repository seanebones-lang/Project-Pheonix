"""
Pastoral Care Agent for ELCA Mothership AI.
Handles member care tracking, prayer requests, pastoral visits, and spiritual guidance.
"""

import asyncio
import os
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from enum import Enum

from backend.services.agents.base.agent_base import AgentBase
from backend.shared.models import Directive
from backend.shared.ai_providers import get_ai_provider

class CarePriority(str, Enum):
    URGENT = "urgent"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class CareType(str, Enum):
    SPIRITUAL = "spiritual"
    EMOTIONAL = "emotional"
    PHYSICAL = "physical"
    FINANCIAL = "financial"
    FAMILY = "family"
    GRIEF = "grief"
    CELEBRATION = "celebration"

class PastoralCareAgent(AgentBase):
    """Agent specialized in pastoral care and member support."""
    
    def __init__(self, mothership_url: str):
        super().__init__("pastoral_care", mothership_url)
        self.care_requests: Dict[str, Dict[str, Any]] = {}
        self.prayer_requests: List[Dict[str, Any]] = []
        self.pastoral_visits: List[Dict[str, Any]] = {}
        self.ai_provider = get_ai_provider()
    
    async def process_directive(self, directive: Directive):
        """Process pastoral care directives."""
        print(f"Pastoral Care Agent {self.agent_id} processing directive: {directive.content}")
        
        task_type = directive.content.get("task_type", "")
        
        try:
            if task_type == "member_care_request":
                result = await self.handle_member_care_request(directive.content)
            elif task_type == "prayer_request":
                result = await self.handle_prayer_request(directive.content)
            elif task_type == "pastoral_visit":
                result = await self.schedule_pastoral_visit(directive.content)
            elif task_type == "spiritual_guidance":
                result = await self.provide_spiritual_guidance(directive.content)
            elif task_type == "care_summary":
                result = await self.generate_care_summary(directive.content)
            else:
                result = await self.handle_general_care_task(directive.content)
            
            await self.send_result(
                task_id=directive.task_id,
                status="completed",
                output=result
            )
            
        except Exception as e:
            print(f"Pastoral Care Agent error: {e}")
            await self.send_result(
                task_id=directive.task_id,
                status="failed",
                output={"error": str(e)}
            )
    
    async def handle_member_care_request(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a member care request."""
        member_id = content.get("member_id")
        care_type = content.get("care_type", CareType.SPIRITUAL)
        description = content.get("description", "")
        priority = content.get("priority", CarePriority.MEDIUM)
        
        # Generate AI-powered care suggestions based on ELCA values
        care_suggestions = await self.generate_care_suggestions(
            care_type, description, priority
        )
        
        care_request = {
            "id": str(uuid.uuid4()),
            "member_id": member_id,
            "care_type": care_type,
            "description": description,
            "priority": priority,
            "suggestions": care_suggestions,
            "created_at": datetime.utcnow().isoformat(),
            "status": "pending"
        }
        
        self.care_requests[care_request["id"]] = care_request
        
        return {
            "care_request_id": care_request["id"],
            "suggestions": care_suggestions,
            "next_steps": self.get_next_steps_for_care(care_type, priority),
            "scripture_references": self.get_relevant_scriptures(care_type)
        }
    
    async def handle_prayer_request(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Handle prayer requests."""
        requester_name = content.get("requester_name", "Anonymous")
        prayer_text = content.get("prayer_text", "")
        is_confidential = content.get("is_confidential", False)
        
        prayer_request = {
            "id": str(uuid.uuid4()),
            "requester_name": requester_name,
            "prayer_text": prayer_text,
            "is_confidential": is_confidential,
            "created_at": datetime.utcnow().isoformat(),
            "status": "active"
        }
        
        self.prayer_requests.append(prayer_request)
        
        # Generate prayer suggestions based on ELCA beliefs
        prayer_suggestions = await self.generate_prayer_suggestions(prayer_text)
        
        return {
            "prayer_request_id": prayer_request["id"],
            "confirmation_message": "Your prayer request has been received and will be lifted up in prayer.",
            "suggestions": prayer_suggestions,
            "scripture_references": self.get_prayer_scriptures()
        }
    
    async def schedule_pastoral_visit(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Schedule a pastoral visit."""
        member_id = content.get("member_id")
        visit_type = content.get("visit_type", "general")
        preferred_date = content.get("preferred_date")
        reason = content.get("reason", "")
        
        visit = {
            "id": str(uuid.uuid4()),
            "member_id": member_id,
            "visit_type": visit_type,
            "reason": reason,
            "preferred_date": preferred_date,
            "created_at": datetime.utcnow().isoformat(),
            "status": "scheduled"
        }
        
        self.pastoral_visits[visit["id"]] = visit
        
        # Generate visit preparation suggestions
        preparation_notes = await self.generate_visit_preparation(visit_type, reason)
        
        return {
            "visit_id": visit["id"],
            "preparation_notes": preparation_notes,
            "suggested_duration": self.get_visit_duration(visit_type),
            "follow_up_reminder": self.schedule_follow_up(visit["id"])
        }
    
    async def provide_spiritual_guidance(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Provide spiritual guidance based on ELCA theology."""
        situation = content.get("situation", "")
        guidance_type = content.get("guidance_type", "general")
        
        # Use AI to generate guidance based on ELCA values and beliefs
        guidance_prompt = f"""
        As a Lutheran pastor providing spiritual guidance, respond to this situation: {situation}
        
        Base your guidance on ELCA core values:
        - Grace: God's unconditional love and forgiveness
        - Faith: Trust in God's promises through Jesus Christ
        - Service: Serving neighbors with love and compassion
        - Justice: Working for equity and human dignity
        - Inclusion: Welcoming all people
        
        Provide compassionate, theologically sound guidance that reflects Lutheran understanding of grace, faith, and service.
        """
        
        guidance = self.ai_provider.generate_text(guidance_prompt)
        
        return {
            "guidance": guidance,
            "scripture_references": self.get_guidance_scriptures(guidance_type),
            "follow_up_suggestions": self.get_follow_up_suggestions(guidance_type),
            "resources": self.get_spiritual_resources(guidance_type)
        }
    
    async def generate_care_summary(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a summary of pastoral care activities."""
        time_period = content.get("time_period", "week")  # week, month, quarter
        
        # Calculate care statistics
        active_care_requests = len([r for r in self.care_requests.values() if r["status"] == "pending"])
        active_prayer_requests = len([r for r in self.prayer_requests if r["status"] == "active"])
        scheduled_visits = len([v for v in self.pastoral_visits.values() if v["status"] == "scheduled"])
        
        summary = {
            "time_period": time_period,
            "active_care_requests": active_care_requests,
            "active_prayer_requests": active_prayer_requests,
            "scheduled_visits": scheduled_visits,
            "care_types_breakdown": self.get_care_types_breakdown(),
            "priority_distribution": self.get_priority_distribution(),
            "recommendations": await self.generate_care_recommendations()
        }
        
        return summary
    
    async def generate_care_suggestions(self, care_type: str, description: str, priority: str) -> List[str]:
        """Generate AI-powered care suggestions."""
        prompt = f"""
        As a Lutheran pastor, suggest appropriate pastoral care responses for:
        Care Type: {care_type}
        Description: {description}
        Priority: {priority}
        
        Consider ELCA values of grace, accompaniment, and radical hospitality.
        Provide 3-5 specific, actionable suggestions.
        """
        
        suggestions_text = self.ai_provider.generate_text(prompt)
        return suggestions_text.split('\n')[:5]  # Limit to 5 suggestions
    
    async def generate_prayer_suggestions(self, prayer_text: str) -> List[str]:
        """Generate prayer suggestions based on the request."""
        prompt = f"""
        Based on this prayer request: "{prayer_text}"
        
        Suggest 3-5 specific prayers or prayer approaches that align with Lutheran theology and ELCA values.
        Focus on grace, hope, and God's presence in difficult times.
        """
        
        suggestions_text = self.ai_provider.generate_text(prompt)
        return suggestions_text.split('\n')[:5]
    
    async def generate_visit_preparation(self, visit_type: str, reason: str) -> Dict[str, Any]:
        """Generate preparation notes for pastoral visits."""
        prompt = f"""
        As a Lutheran pastor preparing for a {visit_type} visit, create preparation notes for this reason: {reason}
        
        Include:
        - Relevant scripture passages
        - Prayer suggestions
        - Conversation topics
        - Follow-up considerations
        
        Base suggestions on ELCA values of accompaniment and grace.
        """
        
        preparation_text = self.ai_provider.generate_text(prompt)
        
        return {
            "preparation_notes": preparation_text,
            "scripture_passages": self.get_visit_scriptures(visit_type),
            "prayer_suggestions": self.get_visit_prayers(visit_type),
            "conversation_starters": self.get_conversation_starters(visit_type)
        }
    
    def get_next_steps_for_care(self, care_type: str, priority: str) -> List[str]:
        """Get next steps based on care type and priority."""
        steps = {
            CareType.SPIRITUAL: [
                "Schedule pastoral conversation",
                "Provide relevant scripture passages",
                "Connect with appropriate ministry",
                "Follow up within 48 hours"
            ],
            CareType.EMOTIONAL: [
                "Offer immediate pastoral support",
                "Connect with counseling resources",
                "Schedule follow-up visit",
                "Notify appropriate staff if needed"
            ],
            CareType.PHYSICAL: [
                "Offer prayers for healing",
                "Connect with health ministry team",
                "Coordinate meal support if needed",
                "Schedule hospital visit if appropriate"
            ]
        }
        
        return steps.get(care_type, ["Schedule pastoral conversation", "Follow up within 24 hours"])
    
    def get_relevant_scriptures(self, care_type: str) -> List[str]:
        """Get relevant scripture references for care type."""
        scriptures = {
            CareType.SPIRITUAL: ["Psalm 23", "Matthew 11:28-30", "Romans 8:28"],
            CareType.EMOTIONAL: ["Psalm 34:18", "Isaiah 41:10", "2 Corinthians 1:3-4"],
            CareType.PHYSICAL: ["James 5:14-15", "Psalm 103:3", "Isaiah 53:5"],
            CareType.GRIEF: ["Psalm 30:5", "Revelation 21:4", "1 Thessalonians 4:13-14"],
            CareType.CELEBRATION: ["Psalm 100", "Philippians 4:4", "1 Thessalonians 5:16-18"]
        }
        
        return scriptures.get(care_type, ["Psalm 23", "Matthew 11:28-30"])
    
    def get_prayer_scriptures(self) -> List[str]:
        """Get scripture references for prayer."""
        return ["Matthew 6:9-13", "Philippians 4:6-7", "1 John 5:14-15", "James 5:16"]
    
    def get_guidance_scriptures(self, guidance_type: str) -> List[str]:
        """Get scripture references for spiritual guidance."""
        return ["Proverbs 3:5-6", "Psalm 119:105", "2 Timothy 3:16-17", "Hebrews 4:12"]
    
    def get_visit_duration(self, visit_type: str) -> str:
        """Get suggested visit duration."""
        durations = {
            "general": "30-45 minutes",
            "hospital": "15-30 minutes",
            "home": "45-60 minutes",
            "crisis": "60+ minutes"
        }
        
        return durations.get(visit_type, "30-45 minutes")
    
    def get_care_types_breakdown(self) -> Dict[str, int]:
        """Get breakdown of care types."""
        breakdown = {}
        for request in self.care_requests.values():
            care_type = request["care_type"]
            breakdown[care_type] = breakdown.get(care_type, 0) + 1
        return breakdown
    
    def get_priority_distribution(self) -> Dict[str, int]:
        """Get distribution of care priorities."""
        distribution = {}
        for request in self.care_requests.values():
            priority = request["priority"]
            distribution[priority] = distribution.get(priority, 0) + 1
        return distribution
    
    async def generate_care_recommendations(self) -> List[str]:
        """Generate recommendations for improving pastoral care."""
        return [
            "Consider implementing a care team rotation for better coverage",
            "Develop specialized resources for common care situations",
            "Create follow-up protocols for different care types",
            "Establish partnerships with local counseling services"
        ]
    
    def get_visit_scriptures(self, visit_type: str) -> List[str]:
        """Get scripture passages for specific visit types."""
        return ["Psalm 23", "Matthew 11:28-30", "Romans 8:28"]
    
    def get_visit_prayers(self, visit_type: str) -> List[str]:
        """Get prayer suggestions for visits."""
        return ["Opening prayer", "Prayer for healing", "Prayer for comfort", "Closing blessing"]
    
    def get_conversation_starters(self, visit_type: str) -> List[str]:
        """Get conversation starter suggestions."""
        return [
            "How are you feeling today?",
            "What's been on your heart lately?",
            "How can I support you in prayer?",
            "What brings you joy these days?"
        ]
    
    def get_follow_up_suggestions(self, guidance_type: str) -> List[str]:
        """Get follow-up suggestions."""
        return [
            "Schedule follow-up conversation",
            "Connect with appropriate ministry",
            "Provide additional resources",
            "Check in within one week"
        ]
    
    def get_spiritual_resources(self, guidance_type: str) -> List[str]:
        """Get spiritual resources."""
        return [
            "ELCA devotional materials",
            "Local Bible study groups",
            "Pastoral counseling services",
            "Community support groups"
        ]
    
    def schedule_follow_up(self, visit_id: str) -> Dict[str, str]:
        """Schedule follow-up reminder."""
        return {
            "reminder_date": (datetime.utcnow() + timedelta(days=3)).isoformat(),
            "message": "Follow up on pastoral visit"
        }
    
    async def handle_general_care_task(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Handle general pastoral care tasks."""
        return {
            "message": "Pastoral care task received",
            "status": "processed",
            "suggestions": ["Schedule pastoral conversation", "Provide prayer support", "Follow up appropriately"]
        }

if __name__ == "__main__":
    # This allows running the agent independently for testing
    MOTHERSHIP_URL = os.getenv("MOTHERSHIP_WEBSOCKET_URL", "ws://localhost:8000")
    agent = PastoralCareAgent(MOTHERSHIP_URL)
    asyncio.run(agent.run())
