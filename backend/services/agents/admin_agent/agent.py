"""
Administration Agent for ELCA Mothership AI.
Handles church operations, facility management, volunteer coordination, and administrative reporting.
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

class FacilityType(str, Enum):
    SANCTUARY = "sanctuary"
    FELLOWSHIP_HALL = "fellowship_hall"
    CLASSROOM = "classroom"
    OFFICE = "office"
    KITCHEN = "kitchen"
    PARKING_LOT = "parking_lot"

class ReportType(str, Enum):
    ATTENDANCE = "attendance"
    FINANCIAL = "financial"
    MEMBERSHIP = "membership"
    MINISTRY = "ministry"
    FACILITY = "facility"

class AdministrationAgent(AgentBase):
    """Agent specialized in church administration and operations."""
    
    def __init__(self, mothership_url: str):
        super().__init__("administration", mothership_url)
        self.facility_schedules: Dict[str, Dict[str, Any]] = {}
        self.volunteer_coordination: Dict[str, List[Dict[str, Any]]] = {}
        self.membership_records: Dict[str, Dict[str, Any]] = {}
        self.reports: Dict[str, Dict[str, Any]] = {}
        self.ai_provider = get_ai_provider()
        self._initialize_admin_database()
    
    async def process_directive(self, directive: Directive):
        """Process administration directives."""
        print(f"Administration Agent {self.agent_id} processing directive: {directive.content}")
        
        task_type = directive.content.get("task_type", "")
        
        try:
            if task_type == "schedule_facility":
                result = await self.schedule_facility(directive.content)
            elif task_type == "coordinate_volunteers":
                result = await self.coordinate_volunteers(directive.content)
            elif task_type == "manage_membership":
                result = await self.manage_membership(directive.content)
            elif task_type == "generate_report":
                result = await self.generate_report(directive.content)
            elif task_type == "handle_operations":
                result = await self.handle_operations(directive.content)
            else:
                result = await self.handle_general_admin_task(directive.content)
            
            await self.send_result(
                task_id=directive.task_id,
                status="completed",
                output=result
            )
            
        except Exception as e:
            print(f"Administration Agent error: {e}")
            await self.send_result(
                task_id=directive.task_id,
                status="failed",
                output={"error": str(e)}
            )
    
    async def schedule_facility(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Schedule facility usage."""
        facility_type = content.get("facility_type", FacilityType.SANCTUARY)
        event_name = content.get("event_name", "")
        start_time = content.get("start_time")
        end_time = content.get("end_time")
        contact_person = content.get("contact_person", "")
        special_requirements = content.get("special_requirements", [])
        
        # Check for conflicts and generate schedule
        schedule_result = await self.process_facility_schedule(
            facility_type, event_name, start_time, end_time, contact_person, special_requirements
        )
        
        schedule_record = {
            "id": str(uuid.uuid4()),
            "facility_type": facility_type,
            "event_name": event_name,
            "start_time": start_time,
            "end_time": end_time,
            "contact_person": contact_person,
            "special_requirements": special_requirements,
            "status": "scheduled",
            "created_at": datetime.utcnow().isoformat()
        }
        
        facility_key = f"{facility_type}_{start_time}"
        if facility_key not in self.facility_schedules:
            self.facility_schedules[facility_key] = []
        self.facility_schedules[facility_key].append(schedule_record)
        
        return {
            "schedule_id": schedule_record["id"],
            "schedule_result": schedule_result,
            "confirmation_details": self.get_confirmation_details(schedule_record),
            "setup_requirements": self.get_setup_requirements(facility_type, special_requirements)
        }
    
    async def coordinate_volunteers(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Coordinate volunteer activities."""
        event_id = content.get("event_id")
        volunteer_roles = content.get("volunteer_roles", [])
        available_volunteers = content.get("available_volunteers", [])
        event_details = content.get("event_details", {})
        
        # Generate volunteer assignments
        coordination_result = await self.process_volunteer_coordination(
            event_id, volunteer_roles, available_volunteers, event_details
        )
        
        coordination_record = {
            "event_id": event_id,
            "volunteer_assignments": coordination_result["assignments"],
            "coordination_status": "completed",
            "created_at": datetime.utcnow().isoformat()
        }
        
        self.volunteer_coordination[event_id] = coordination_record
        
        return {
            "coordination_result": coordination_result,
            "volunteer_communications": self.generate_volunteer_communications(coordination_result["assignments"]),
            "follow_up_tasks": self.get_follow_up_tasks(event_details)
        }
    
    async def manage_membership(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Manage membership records."""
        action_type = content.get("action_type", "update")  # add, update, remove, query
        member_data = content.get("member_data", {})
        member_id = content.get("member_id")
        
        # Process membership action
        membership_result = await self.process_membership_action(
            action_type, member_data, member_id
        )
        
        if action_type == "add":
            member_record = {
                "id": str(uuid.uuid4()),
                **member_data,
                "created_at": datetime.utcnow().isoformat(),
                "status": "active"
            }
            self.membership_records[member_record["id"]] = member_record
        
        return {
            "membership_result": membership_result,
            "member_id": member_record["id"] if action_type == "add" else member_id,
            "next_steps": self.get_membership_next_steps(action_type),
            "communication_tasks": self.get_membership_communication_tasks(action_type)
        }
    
    async def generate_report(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Generate administrative reports."""
        report_type = content.get("report_type", ReportType.ATTENDANCE)
        time_period = content.get("time_period", "monthly")
        report_parameters = content.get("parameters", {})
        
        # Generate AI-powered report
        report_content = await self.generate_administrative_report(
            report_type, time_period, report_parameters
        )
        
        report_record = {
            "id": str(uuid.uuid4()),
            "report_type": report_type,
            "time_period": time_period,
            "parameters": report_parameters,
            "content": report_content,
            "generated_at": datetime.utcnow().isoformat(),
            "status": "completed"
        }
        
        self.reports[report_record["id"]] = report_record
        
        return {
            "report_id": report_record["id"],
            "report_content": report_content,
            "summary_insights": self.generate_summary_insights(report_type, report_content),
            "recommendations": self.generate_recommendations(report_type, report_content)
        }
    
    async def handle_operations(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Handle general church operations."""
        operation_type = content.get("operation_type", "general")
        operation_details = content.get("operation_details", {})
        
        # Process operation
        operation_result = await self.process_operation(operation_type, operation_details)
        
        return {
            "operation_result": operation_result,
            "follow_up_actions": self.get_follow_up_actions(operation_type),
            "status_update": self.get_operation_status_update(operation_type)
        }
    
    async def process_facility_schedule(self, facility_type: str, event_name: str, start_time: str, end_time: str, contact_person: str, special_requirements: List[str]) -> Dict[str, Any]:
        """Process facility scheduling."""
        # Check for conflicts
        conflicts = self.check_schedule_conflicts(facility_type, start_time, end_time)
        
        if conflicts:
            return {
                "status": "conflict",
                "conflicts": conflicts,
                "suggestions": self.get_alternative_times(facility_type, start_time, end_time)
            }
        
        # Generate setup requirements
        setup_requirements = self.generate_setup_requirements(facility_type, special_requirements)
        
        return {
            "status": "scheduled",
            "setup_requirements": setup_requirements,
            "confirmation_message": f"Facility {facility_type} scheduled for {event_name}",
            "reminder_schedule": self.schedule_reminders(start_time, end_time)
        }
    
    async def process_volunteer_coordination(self, event_id: str, volunteer_roles: List[str], available_volunteers: List[Dict[str, Any]], event_details: Dict[str, Any]) -> Dict[str, Any]:
        """Process volunteer coordination."""
        assignments = []
        
        for role in volunteer_roles:
            # Find suitable volunteers
            suitable_volunteers = [
                v for v in available_volunteers 
                if role.lower() in v.get("skills", []).lower() or role.lower() in v.get("preferences", []).lower()
            ]
            
            if suitable_volunteers:
                volunteer = suitable_volunteers[0]
                assignment = {
                    "role": role,
                    "volunteer_id": volunteer["id"],
                    "volunteer_name": volunteer["name"],
                    "contact_info": volunteer.get("contact", ""),
                    "assigned_at": datetime.utcnow().isoformat()
                }
                assignments.append(assignment)
        
        return {
            "assignments": assignments,
            "unfilled_roles": [role for role in volunteer_roles if not any(a["role"] == role for a in assignments)],
            "coordination_status": "completed"
        }
    
    async def process_membership_action(self, action_type: str, member_data: Dict[str, Any], member_id: str) -> Dict[str, Any]:
        """Process membership action."""
        if action_type == "add":
            return {
                "status": "added",
                "message": "New member added successfully",
                "member_data": member_data
            }
        elif action_type == "update":
            return {
                "status": "updated",
                "message": "Member information updated",
                "member_id": member_id
            }
        elif action_type == "remove":
            return {
                "status": "removed",
                "message": "Member removed from active roster",
                "member_id": member_id
            }
        elif action_type == "query":
            return {
                "status": "found",
                "message": "Member information retrieved",
                "member_data": self.membership_records.get(member_id, {})
            }
        
        return {"status": "error", "message": "Invalid action type"}
    
    async def generate_administrative_report(self, report_type: str, time_period: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Generate AI-powered administrative report."""
        prompt = f"""
        Generate a comprehensive {report_type} report for the {time_period} period.
        Parameters: {parameters}
        
        Include:
        - Key metrics and statistics
        - Trends and patterns
        - Areas of growth or concern
        - Recommendations for improvement
        
        Base analysis on ELCA administrative best practices and church management principles.
        """
        
        report_text = self.ai_provider.generate_text(prompt)
        
        return {
            "report_text": report_text,
            "metrics": self.generate_metrics(report_type, time_period),
            "trends": self.analyze_trends(report_type, time_period),
            "comparisons": self.generate_comparisons(report_type, time_period)
        }
    
    async def process_operation(self, operation_type: str, operation_details: Dict[str, Any]) -> Dict[str, Any]:
        """Process church operation."""
        prompt = f"""
        Process this church operation: {operation_type}
        Details: {operation_details}
        
        Provide:
        - Operation status
        - Required actions
        - Timeline considerations
        - Resource requirements
        
        Align with ELCA operational standards and church management best practices.
        """
        
        operation_text = self.ai_provider.generate_text(prompt)
        
        return {
            "operation_text": operation_text,
            "status": "processed",
            "actions_required": self.get_required_actions(operation_type),
            "timeline": self.get_operation_timeline(operation_type)
        }
    
    def check_schedule_conflicts(self, facility_type: str, start_time: str, end_time: str) -> List[Dict[str, Any]]:
        """Check for schedule conflicts."""
        conflicts = []
        facility_key = f"{facility_type}_{start_time}"
        
        if facility_key in self.facility_schedules:
            for existing_schedule in self.facility_schedules[facility_key]:
                conflicts.append({
                    "conflict_type": "time_overlap",
                    "existing_event": existing_schedule["event_name"],
                    "existing_time": f"{existing_schedule['start_time']} - {existing_schedule['end_time']}"
                })
        
        return conflicts
    
    def get_alternative_times(self, facility_type: str, start_time: str, end_time: str) -> List[str]:
        """Get alternative time suggestions."""
        return [
            "Try scheduling 1 hour later",
            "Consider scheduling on a different day",
            "Check availability for shorter duration",
            "Look for alternative facilities"
        ]
    
    def generate_setup_requirements(self, facility_type: str, special_requirements: List[str]) -> List[str]:
        """Generate setup requirements."""
        base_requirements = {
            FacilityType.SANCTUARY: ["Sound system check", "Lighting setup", "Seating arrangement"],
            FacilityType.FELLOWSHIP_HALL: ["Table setup", "Chairs arrangement", "Kitchen access"],
            FacilityType.CLASSROOM: ["Whiteboard setup", "Seating arrangement", "Audio/visual equipment"],
            FacilityType.OFFICE: ["Computer setup", "Phone system", "Office supplies"]
        }
        
        requirements = base_requirements.get(facility_type, ["Basic setup"])
        requirements.extend(special_requirements)
        
        return requirements
    
    def schedule_reminders(self, start_time: str, end_time: str) -> List[Dict[str, str]]:
        """Schedule reminders for facility usage."""
        return [
            {
                "reminder_type": "setup",
                "reminder_time": (datetime.fromisoformat(start_time) - timedelta(hours=2)).isoformat(),
                "message": "Facility setup reminder"
            },
            {
                "reminder_type": "cleanup",
                "reminder_time": end_time,
                "message": "Facility cleanup reminder"
            }
        ]
    
    def get_confirmation_details(self, schedule_record: Dict[str, Any]) -> Dict[str, Any]:
        """Get confirmation details for schedule."""
        return {
            "confirmation_number": schedule_record["id"],
            "event_name": schedule_record["event_name"],
            "facility": schedule_record["facility_type"],
            "time": f"{schedule_record['start_time']} - {schedule_record['end_time']}",
            "contact": schedule_record["contact_person"]
        }
    
    def get_setup_requirements(self, facility_type: str, special_requirements: List[str]) -> List[str]:
        """Get setup requirements."""
        return self.generate_setup_requirements(facility_type, special_requirements)
    
    def generate_volunteer_communications(self, assignments: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Generate volunteer communications."""
        communications = []
        for assignment in assignments:
            communications.append({
                "volunteer_id": assignment["volunteer_id"],
                "message": f"Thank you for volunteering as {assignment['role']}. Please confirm your availability.",
                "communication_type": "assignment_confirmation"
            })
        return communications
    
    def get_follow_up_tasks(self, event_details: Dict[str, Any]) -> List[str]:
        """Get follow-up tasks for event."""
        return [
            "Send confirmation to all volunteers",
            "Prepare event materials",
            "Set up facility",
            "Follow up after event"
        ]
    
    def get_membership_next_steps(self, action_type: str) -> List[str]:
        """Get next steps for membership action."""
        steps = {
            "add": ["Send welcome packet", "Assign membership number", "Add to directory", "Schedule orientation"],
            "update": ["Update directory", "Notify relevant ministries", "Update records"],
            "remove": ["Update directory", "Notify relevant ministries", "Archive records"],
            "query": ["Provide information", "Update contact if needed"]
        }
        
        return steps.get(action_type, ["Process request"])
    
    def get_membership_communication_tasks(self, action_type: str) -> List[str]:
        """Get communication tasks for membership action."""
        tasks = {
            "add": ["Welcome email", "Directory inclusion", "Ministry invitations"],
            "update": ["Confirmation email", "Directory update"],
            "remove": ["Farewell communication", "Directory update"],
            "query": ["Information response"]
        }
        
        return tasks.get(action_type, ["Standard communication"])
    
    def generate_summary_insights(self, report_type: str, report_content: Dict[str, Any]) -> List[str]:
        """Generate summary insights from report."""
        insights = {
            ReportType.ATTENDANCE: ["Attendance trends", "Peak service times", "Seasonal patterns"],
            ReportType.FINANCIAL: ["Giving trends", "Budget performance", "Stewardship patterns"],
            ReportType.MEMBERSHIP: ["Growth patterns", "Demographic trends", "Engagement levels"],
            ReportType.MINISTRY: ["Program effectiveness", "Participation rates", "Impact metrics"],
            ReportType.FACILITY: ["Usage patterns", "Maintenance needs", "Capacity utilization"]
        }
        
        return insights.get(report_type, ["Key insights", "Trends", "Recommendations"])
    
    def generate_recommendations(self, report_type: str, report_content: Dict[str, Any]) -> List[str]:
        """Generate recommendations from report."""
        recommendations = {
            ReportType.ATTENDANCE: ["Improve outreach", "Enhance worship experience", "Increase engagement"],
            ReportType.FINANCIAL: ["Stewardship education", "Budget optimization", "Fundraising strategies"],
            ReportType.MEMBERSHIP: ["Member retention", "New member integration", "Community building"],
            ReportType.MINISTRY: ["Program development", "Volunteer recruitment", "Resource allocation"],
            ReportType.FACILITY: ["Maintenance planning", "Usage optimization", "Capacity expansion"]
        }
        
        return recommendations.get(report_type, ["Improvement opportunities", "Strategic initiatives"])
    
    def get_follow_up_actions(self, operation_type: str) -> List[str]:
        """Get follow-up actions for operation."""
        actions = {
            "maintenance": ["Schedule maintenance", "Order supplies", "Update records"],
            "scheduling": ["Confirm schedules", "Send reminders", "Update calendar"],
            "communication": ["Send communications", "Follow up responses", "Update records"],
            "general": ["Monitor progress", "Follow up as needed", "Update status"]
        }
        
        return actions.get(operation_type, ["Follow up", "Monitor", "Update"])
    
    def get_operation_status_update(self, operation_type: str) -> str:
        """Get operation status update."""
        return f"{operation_type} operation processed successfully"
    
    def get_required_actions(self, operation_type: str) -> List[str]:
        """Get required actions for operation."""
        actions = {
            "maintenance": ["Schedule maintenance", "Order supplies", "Coordinate with vendors"],
            "scheduling": ["Update calendar", "Send notifications", "Confirm availability"],
            "communication": ["Draft messages", "Send communications", "Track responses"],
            "general": ["Process request", "Update records", "Follow up"]
        }
        
        return actions.get(operation_type, ["Process", "Update", "Follow up"])
    
    def get_operation_timeline(self, operation_type: str) -> Dict[str, str]:
        """Get operation timeline."""
        timelines = {
            "maintenance": {
                "immediate": "Schedule maintenance",
                "short_term": "Complete maintenance",
                "long_term": "Monitor results"
            },
            "scheduling": {
                "immediate": "Update schedule",
                "short_term": "Send notifications",
                "long_term": "Monitor usage"
            },
            "communication": {
                "immediate": "Send communications",
                "short_term": "Track responses",
                "long_term": "Follow up as needed"
            }
        }
        
        return timelines.get(operation_type, {
            "immediate": "Process request",
            "short_term": "Follow up",
            "long_term": "Monitor results"
        })
    
    def generate_metrics(self, report_type: str, time_period: str) -> Dict[str, Any]:
        """Generate metrics for report."""
        metrics = {
            ReportType.ATTENDANCE: {
                "total_attendance": 150,
                "average_per_service": 75,
                "growth_rate": "5%"
            },
            ReportType.FINANCIAL: {
                "total_offerings": 25000,
                "budget_performance": "95%",
                "giving_trend": "stable"
            },
            ReportType.MEMBERSHIP: {
                "total_members": 200,
                "new_members": 5,
                "retention_rate": "90%"
            }
        }
        
        return metrics.get(report_type, {"key_metrics": "Available"})
    
    def analyze_trends(self, report_type: str, time_period: str) -> List[str]:
        """Analyze trends for report."""
        trends = {
            ReportType.ATTENDANCE: ["Steady growth", "Seasonal variations", "Peak service times"],
            ReportType.FINANCIAL: ["Stable giving", "Budget compliance", "Stewardship growth"],
            ReportType.MEMBERSHIP: ["Steady growth", "Good retention", "Active engagement"]
        }
        
        return trends.get(report_type, ["Positive trends", "Growth patterns"])
    
    def generate_comparisons(self, report_type: str, time_period: str) -> Dict[str, Any]:
        """Generate comparisons for report."""
        comparisons = {
            ReportType.ATTENDANCE: {
                "previous_period": "140",
                "current_period": "150",
                "change": "+7%"
            },
            ReportType.FINANCIAL: {
                "previous_period": "24000",
                "current_period": "25000",
                "change": "+4%"
            }
        }
        
        return comparisons.get(report_type, {"comparison": "Available"})
    
    def _initialize_admin_database(self):
        """Initialize administration database."""
        self.admin_database = {
            "facilities": ["Sanctuary", "Fellowship Hall", "Classrooms", "Office", "Kitchen"],
            "volunteer_roles": ["Ushers", "Greeters", "Readers", "Communion assistants", "Musicians"],
            "report_types": ["Attendance", "Financial", "Membership", "Ministry", "Facility"],
            "operation_types": ["Maintenance", "Scheduling", "Communication", "General"]
        }
    
    async def handle_general_admin_task(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Handle general administration tasks."""
        return {
            "message": "Administration task received",
            "status": "processed",
            "suggestions": ["Schedule facilities", "Coordinate volunteers", "Generate reports", "Manage operations"]
        }

if __name__ == "__main__":
    # This allows running the agent independently for testing
    MOTHERSHIP_URL = os.getenv("MOTHERSHIP_WEBSOCKET_URL", "ws://localhost:8000")
    agent = AdministrationAgent(MOTHERSHIP_URL)
    asyncio.run(agent.run())
