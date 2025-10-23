"""
Worship Planning Agent for ELCA Mothership AI.
Handles liturgy planning, hymn selection, volunteer coordination, and worship service management.
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

class ServiceType(str, Enum):
    REGULAR = "regular"
    SPECIAL = "special"
    HOLIDAY = "holiday"
    FUNERAL = "funeral"
    WEDDING = "wedding"
    BAPTISM = "baptism"

class LiturgicalSeason(str, Enum):
    ADVENT = "advent"
    CHRISTMAS = "christmas"
    EPIPHANY = "epiphany"
    LENT = "lent"
    EASTER = "easter"
    PENTECOST = "pentecost"
    ORDINARY_TIME = "ordinary_time"

class WorshipPlanningAgent(AgentBase):
    """Agent specialized in worship planning and coordination."""
    
    def __init__(self, mothership_url: str):
        super().__init__("worship_planning", mothership_url)
        self.worship_services: Dict[str, Dict[str, Any]] = {}
        self.volunteer_schedules: Dict[str, List[Dict[str, Any]]] = {}
        self.hymn_database: List[Dict[str, Any]] = []
        self.ai_provider = get_ai_provider()
        self._initialize_hymn_database()
    
    async def process_directive(self, directive: Directive):
        """Process worship planning directives."""
        print(f"Worship Planning Agent {self.agent_id} processing directive: {directive.content}")
        
        task_type = directive.content.get("task_type", "")
        
        try:
            if task_type == "plan_service":
                result = await self.plan_worship_service(directive.content)
            elif task_type == "coordinate_volunteers":
                result = await self.coordinate_volunteers(directive.content)
            elif task_type == "select_hymns":
                result = await self.select_hymns(directive.content)
            elif task_type == "create_bulletin":
                result = await self.create_bulletin_template(directive.content)
            elif task_type == "schedule_services":
                result = await self.schedule_services(directive.content)
            else:
                result = await self.handle_general_worship_task(directive.content)
            
            await self.send_result(
                task_id=directive.task_id,
                status="completed",
                output=result
            )
            
        except Exception as e:
            print(f"Worship Planning Agent error: {e}")
            await self.send_result(
                task_id=directive.task_id,
                status="failed",
                output={"error": str(e)}
            )
    
    async def plan_worship_service(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Plan a worship service."""
        service_date = content.get("service_date")
        service_type = content.get("service_type", ServiceType.REGULAR)
        liturgical_season = content.get("liturgical_season", LiturgicalSeason.ORDINARY_TIME)
        theme = content.get("theme", "")
        scripture_readings = content.get("scripture_readings", [])
        
        # Generate AI-powered worship plan
        worship_plan = await self.generate_worship_plan(
            service_type, liturgical_season, theme, scripture_readings
        )
        
        service = {
            "id": str(uuid.uuid4()),
            "date": service_date,
            "type": service_type,
            "liturgical_season": liturgical_season,
            "theme": theme,
            "scripture_readings": scripture_readings,
            "plan": worship_plan,
            "created_at": datetime.utcnow().isoformat(),
            "status": "planned"
        }
        
        self.worship_services[service["id"]] = service
        
        return {
            "service_id": service["id"],
            "worship_plan": worship_plan,
            "volunteer_needs": self.get_volunteer_needs(service_type),
            "preparation_checklist": self.get_preparation_checklist(service_type)
        }
    
    async def coordinate_volunteers(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Coordinate worship volunteers."""
        service_id = content.get("service_id")
        volunteer_roles = content.get("volunteer_roles", [])
        available_volunteers = content.get("available_volunteers", [])
        
        # Generate volunteer assignments
        assignments = await self.generate_volunteer_assignments(
            volunteer_roles, available_volunteers
        )
        
        volunteer_schedule = {
            "service_id": service_id,
            "assignments": assignments,
            "created_at": datetime.utcnow().isoformat(),
            "status": "scheduled"
        }
        
        self.volunteer_schedules[service_id] = volunteer_schedule
        
        return {
            "assignments": assignments,
            "confirmation_messages": self.generate_confirmation_messages(assignments),
            "reminder_schedule": self.schedule_reminders(service_id, assignments)
        }
    
    async def select_hymns(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Select hymns for worship service."""
        service_type = content.get("service_type", ServiceType.REGULAR)
        liturgical_season = content.get("liturgical_season", LiturgicalSeason.ORDINARY_TIME)
        theme = content.get("theme", "")
        scripture_readings = content.get("scripture_readings", [])
        
        # Generate hymn suggestions
        hymn_suggestions = await self.generate_hymn_suggestions(
            service_type, liturgical_season, theme, scripture_readings
        )
        
        return {
            "hymn_suggestions": hymn_suggestions,
            "liturgical_notes": self.get_liturgical_notes(liturgical_season),
            "musical_considerations": self.get_musical_considerations(hymn_suggestions)
        }
    
    async def create_bulletin_template(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Create bulletin template for worship service."""
        service_id = content.get("service_id")
        custom_elements = content.get("custom_elements", [])
        
        if service_id not in self.worship_services:
            return {"error": "Service not found"}
        
        service = self.worship_services[service_id]
        
        # Generate bulletin content
        bulletin_content = await self.generate_bulletin_content(service, custom_elements)
        
        return {
            "bulletin_template": bulletin_content,
            "printing_notes": self.get_printing_notes(),
            "distribution_list": self.get_distribution_list()
        }
    
    async def schedule_services(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Schedule multiple worship services."""
        start_date = content.get("start_date")
        end_date = content.get("end_date")
        service_frequency = content.get("frequency", "weekly")
        
        # Generate service schedule
        schedule = await self.generate_service_schedule(start_date, end_date, service_frequency)
        
        return {
            "schedule": schedule,
            "planning_timeline": self.get_planning_timeline(),
            "resource_requirements": self.get_resource_requirements(schedule)
        }
    
    async def generate_worship_plan(self, service_type: str, liturgical_season: str, theme: str, scripture_readings: List[str]) -> Dict[str, Any]:
        """Generate AI-powered worship plan."""
        prompt = f"""
        Create a comprehensive worship plan for:
        Service Type: {service_type}
        Liturgical Season: {liturgical_season}
        Theme: {theme}
        Scripture Readings: {', '.join(scripture_readings)}
        
        Include:
        - Opening elements (call to worship, invocation)
        - Music selections (hymns, special music)
        - Liturgical elements (confession, creed, prayers)
        - Sermon focus and key points
        - Closing elements (benediction, sending)
        
        Base suggestions on ELCA worship traditions and Lutheran theology.
        """
        
        plan_text = self.ai_provider.generate_text(prompt)
        
        return {
            "plan_text": plan_text,
            "liturgical_elements": self.get_liturgical_elements(liturgical_season),
            "special_considerations": self.get_special_considerations(service_type)
        }
    
    async def generate_volunteer_assignments(self, volunteer_roles: List[str], available_volunteers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate volunteer assignments."""
        assignments = []
        
        for role in volunteer_roles:
            # Find best match for role
            suitable_volunteers = [
                v for v in available_volunteers 
                if role.lower() in v.get("skills", []).lower() or role.lower() in v.get("preferences", []).lower()
            ]
            
            if suitable_volunteers:
                volunteer = suitable_volunteers[0]  # Select first suitable volunteer
                assignment = {
                    "role": role,
                    "volunteer_id": volunteer["id"],
                    "volunteer_name": volunteer["name"],
                    "contact_info": volunteer.get("contact", ""),
                    "notes": f"Assigned based on skills/preferences"
                }
                assignments.append(assignment)
        
        return assignments
    
    async def generate_hymn_suggestions(self, service_type: str, liturgical_season: str, theme: str, scripture_readings: List[str]) -> List[Dict[str, Any]]:
        """Generate hymn suggestions."""
        prompt = f"""
        Suggest 5-7 hymns appropriate for:
        Service Type: {service_type}
        Liturgical Season: {liturgical_season}
        Theme: {theme}
        Scripture Readings: {', '.join(scripture_readings)}
        
        Include hymns from ELW (Evangelical Lutheran Worship) and other Lutheran hymnals.
        Provide hymn numbers and brief explanations for each selection.
        """
        
        suggestions_text = self.ai_provider.generate_text(prompt)
        
        # Parse suggestions into structured format
        hymn_suggestions = []
        lines = suggestions_text.split('\n')
        
        for line in lines:
            if line.strip() and ('ELW' in line or 'hymn' in line.lower()):
                hymn_suggestions.append({
                    "title": line.strip(),
                    "source": "ELW",
                    "reason": "Liturgical appropriateness"
                })
        
        return hymn_suggestions[:7]  # Limit to 7 hymns
    
    async def generate_bulletin_content(self, service: Dict[str, Any], custom_elements: List[str]) -> Dict[str, Any]:
        """Generate bulletin content."""
        prompt = f"""
        Create bulletin content for worship service:
        Date: {service['date']}
        Type: {service['type']}
        Theme: {service['theme']}
        Liturgical Season: {service['liturgical_season']}
        
        Include standard ELCA bulletin elements and any custom elements: {', '.join(custom_elements)}
        """
        
        bulletin_text = self.ai_provider.generate_text(prompt)
        
        return {
            "bulletin_text": bulletin_text,
            "announcements": self.get_standard_announcements(),
            "prayer_concerns": self.get_prayer_concerns_template()
        }
    
    async def generate_service_schedule(self, start_date: str, end_date: str, frequency: str) -> List[Dict[str, Any]]:
        """Generate service schedule."""
        schedule = []
        
        # This would typically integrate with a calendar system
        # For now, generate a basic schedule
        
        return [
            {
                "date": start_date,
                "type": ServiceType.REGULAR,
                "theme": "Weekly worship",
                "status": "scheduled"
            }
        ]
    
    def get_volunteer_needs(self, service_type: str) -> List[str]:
        """Get volunteer needs for service type."""
        needs = {
            ServiceType.REGULAR: ["Ushers", "Greeters", "Readers", "Communion assistants"],
            ServiceType.SPECIAL: ["Ushers", "Greeters", "Readers", "Communion assistants", "Special music"],
            ServiceType.HOLIDAY: ["Ushers", "Greeters", "Readers", "Communion assistants", "Special decorations"],
            ServiceType.FUNERAL: ["Ushers", "Readers", "Communion assistants"],
            ServiceType.WEDDING: ["Ushers", "Readers", "Special music"],
            ServiceType.BAPTISM: ["Readers", "Communion assistants"]
        }
        
        return needs.get(service_type, ["Ushers", "Greeters", "Readers"])
    
    def get_preparation_checklist(self, service_type: str) -> List[str]:
        """Get preparation checklist for service type."""
        return [
            "Confirm scripture readings",
            "Prepare sermon",
            "Select hymns",
            "Coordinate volunteers",
            "Prepare communion elements",
            "Print bulletins",
            "Set up sanctuary",
            "Test audio/visual equipment"
        ]
    
    def generate_confirmation_messages(self, assignments: List[Dict[str, Any]]) -> List[str]:
        """Generate confirmation messages for volunteers."""
        messages = []
        for assignment in assignments:
            message = f"Thank you {assignment['volunteer_name']} for serving as {assignment['role']} this Sunday."
            messages.append(message)
        return messages
    
    def schedule_reminders(self, service_id: str, assignments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Schedule reminders for volunteers."""
        reminders = []
        for assignment in assignments:
            reminder = {
                "volunteer_id": assignment["volunteer_id"],
                "reminder_date": (datetime.utcnow() + timedelta(days=2)).isoformat(),
                "message": f"Reminder: You are scheduled to serve as {assignment['role']} this Sunday."
            }
            reminders.append(reminder)
        return reminders
    
    def get_liturgical_notes(self, liturgical_season: str) -> List[str]:
        """Get liturgical notes for season."""
        notes = {
            LiturgicalSeason.ADVENT: ["Focus on anticipation and preparation", "Use purple/blue colors", "Emphasize hope and expectation"],
            LiturgicalSeason.CHRISTMAS: ["Celebrate incarnation", "Use white/gold colors", "Focus on joy and celebration"],
            LiturgicalSeason.LENT: ["Focus on repentance and reflection", "Use purple colors", "Emphasize sacrifice and preparation"],
            LiturgicalSeason.EASTER: ["Celebrate resurrection", "Use white/gold colors", "Focus on new life and victory"]
        }
        
        return notes.get(liturgical_season, ["Follow standard liturgical practices"])
    
    def get_musical_considerations(self, hymn_suggestions: List[Dict[str, Any]]) -> List[str]:
        """Get musical considerations for hymns."""
        return [
            "Consider congregational familiarity",
            "Balance traditional and contemporary selections",
            "Ensure appropriate tempo and key",
            "Coordinate with instrumental accompaniment"
        ]
    
    def get_printing_notes(self) -> List[str]:
        """Get printing notes for bulletins."""
        return [
            "Print on recycled paper if possible",
            "Include recycling instructions",
            "Check spelling and grammar",
            "Ensure adequate quantity for attendance"
        ]
    
    def get_distribution_list(self) -> List[str]:
        """Get distribution list for bulletins."""
        return [
            "Worship attendees",
            "Homebound members",
            "Visitors",
            "Staff and volunteers"
        ]
    
    def get_planning_timeline(self) -> Dict[str, str]:
        """Get planning timeline for services."""
        return {
            "4_weeks_prior": "Select theme and scripture readings",
            "3_weeks_prior": "Plan liturgy and select hymns",
            "2_weeks_prior": "Coordinate volunteers",
            "1_week_prior": "Finalize bulletin and prepare elements",
            "day_of": "Final setup and coordination"
        }
    
    def get_resource_requirements(self, schedule: List[Dict[str, Any]]) -> List[str]:
        """Get resource requirements for schedule."""
        return [
            "Communion elements",
            "Bulletin supplies",
            "Audio/visual equipment",
            "Volunteer coordination",
            "Facility preparation"
        ]
    
    def get_liturgical_elements(self, liturgical_season: str) -> List[str]:
        """Get liturgical elements for season."""
        elements = {
            LiturgicalSeason.ADVENT: ["Advent wreath", "Advent candles", "Advent hymns"],
            LiturgicalSeason.CHRISTMAS: ["Christmas hymns", "Nativity elements", "Joyful music"],
            LiturgicalSeason.LENT: ["Lenten hymns", "Purple paraments", "Reflective music"],
            LiturgicalSeason.EASTER: ["Easter hymns", "White paraments", "Celebratory music"]
        }
        
        return elements.get(liturgical_season, ["Standard liturgical elements"])
    
    def get_special_considerations(self, service_type: str) -> List[str]:
        """Get special considerations for service type."""
        considerations = {
            ServiceType.SPECIAL: ["Extended preparation time", "Additional volunteers", "Special decorations"],
            ServiceType.HOLIDAY: ["Holiday-specific elements", "Increased attendance", "Special music"],
            ServiceType.FUNERAL: ["Sensitive pastoral care", "Memorial elements", "Comforting music"],
            ServiceType.WEDDING: ["Celebratory elements", "Special decorations", "Joyful music"],
            ServiceType.BAPTISM: ["Baptismal elements", "Family involvement", "Celebratory atmosphere"]
        }
        
        return considerations.get(service_type, ["Standard considerations"])
    
    def get_standard_announcements(self) -> List[str]:
        """Get standard announcement template."""
        return [
            "Welcome and announcements",
            "Upcoming events",
            "Ministry opportunities",
            "Prayer concerns",
            "Offering and stewardship"
        ]
    
    def get_prayer_concerns_template(self) -> List[str]:
        """Get prayer concerns template."""
        return [
            "Prayers for healing",
            "Prayers for comfort",
            "Prayers for guidance",
            "Prayers of thanksgiving",
            "Prayers for the world"
        ]
    
    def _initialize_hymn_database(self):
        """Initialize basic hymn database."""
        self.hymn_database = [
            {"title": "A Mighty Fortress", "number": "ELW 504", "season": "general"},
            {"title": "Amazing Grace", "number": "ELW 779", "season": "general"},
            {"title": "Joy to the World", "number": "ELW 267", "season": "christmas"},
            {"title": "Christ the Lord is Risen Today", "number": "ELW 365", "season": "easter"}
        ]
    
    async def handle_general_worship_task(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Handle general worship planning tasks."""
        return {
            "message": "Worship planning task received",
            "status": "processed",
            "suggestions": ["Plan service elements", "Coordinate volunteers", "Select appropriate music"]
        }

if __name__ == "__main__":
    # This allows running the agent independently for testing
    MOTHERSHIP_URL = os.getenv("MOTHERSHIP_WEBSOCKET_URL", "ws://localhost:8000")
    agent = WorshipPlanningAgent(MOTHERSHIP_URL)
    asyncio.run(agent.run())
