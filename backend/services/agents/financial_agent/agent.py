"""
Financial Stewardship Agent for ELCA Mothership AI.
Handles financial management, stewardship education, giving tracking, and budget planning.
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

class FinancialCategory(str, Enum):
    OFFERINGS = "offerings"
    PLEDGES = "pledges"
    SPECIAL_GIVING = "special_giving"
    MISSION_SUPPORT = "mission_support"
    CAPITAL_CAMPAIGN = "capital_campaign"
    ENDOWMENT = "endowment"

class BudgetCategory(str, Enum):
    MINISTRY = "ministry"
    ADMINISTRATION = "administration"
    FACILITIES = "facilities"
    MISSION = "mission"
    EDUCATION = "education"
    WORSHIP = "worship"

class FinancialStewardshipAgent(AgentBase):
    """Agent specialized in financial stewardship and church financial management."""
    
    def __init__(self, mothership_url: str):
        super().__init__("financial_stewardship", mothership_url)
        self.financial_records: Dict[str, Dict[str, Any]] = {}
        self.budget_plans: Dict[str, Dict[str, Any]] = {}
        self.giving_statements: Dict[str, Dict[str, Any]] = {}
        self.stewardship_programs: Dict[str, Dict[str, Any]] = {}
        self.ai_provider = get_ai_provider()
        self._initialize_financial_database()
    
    async def process_directive(self, directive: Directive):
        """Process financial stewardship directives."""
        print(f"Financial Stewardship Agent {self.agent_id} processing directive: {directive.content}")
        
        task_type = directive.content.get("task_type", "")
        
        try:
            if task_type == "track_giving":
                result = await self.track_giving(directive.content)
            elif task_type == "manage_budget":
                result = await self.manage_budget(directive.content)
            elif task_type == "generate_giving_statement":
                result = await self.generate_giving_statement(directive.content)
            elif task_type == "plan_stewardship_campaign":
                result = await self.plan_stewardship_campaign(directive.content)
            elif task_type == "analyze_financial_health":
                result = await self.analyze_financial_health(directive.content)
            else:
                result = await self.handle_general_financial_task(directive.content)
            
            await self.send_result(
                task_id=directive.task_id,
                status="completed",
                output=result
            )
            
        except Exception as e:
            print(f"Financial Stewardship Agent error: {e}")
            await self.send_result(
                task_id=directive.task_id,
                status="failed",
                output={"error": str(e)}
            )
    
    async def track_giving(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Track member giving and donations."""
        member_id = content.get("member_id")
        giving_amount = content.get("giving_amount", 0)
        giving_category = content.get("giving_category", FinancialCategory.OFFERINGS)
        giving_date = content.get("giving_date", datetime.utcnow().isoformat())
        giving_method = content.get("giving_method", "cash")
        special_notes = content.get("special_notes", "")
        
        # Create giving record
        giving_record = await self.create_giving_record(
            member_id, giving_amount, giving_category, giving_date, giving_method, special_notes
        )
        
        # Update member giving history
        if member_id not in self.financial_records:
            self.financial_records[member_id] = {
                "member_id": member_id,
                "giving_history": [],
                "total_given": 0,
                "giving_categories": {},
                "last_giving_date": giving_date
            }
        
        self.financial_records[member_id]["giving_history"].append(giving_record)
        self.financial_records[member_id]["total_given"] += giving_amount
        self.financial_records[member_id]["last_giving_date"] = giving_date
        
        if giving_category not in self.financial_records[member_id]["giving_categories"]:
            self.financial_records[member_id]["giving_categories"][giving_category] = 0
        self.financial_records[member_id]["giving_categories"][giving_category] += giving_amount
        
        return {
            "giving_record": giving_record,
            "member_giving_summary": self.financial_records[member_id],
            "stewardship_insights": self.generate_stewardship_insights(member_id),
            "follow_up_suggestions": self.get_follow_up_suggestions(giving_category)
        }
    
    async def manage_budget(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Manage church budget planning and tracking."""
        budget_year = content.get("budget_year", datetime.utcnow().year)
        action_type = content.get("action_type", "create")  # create, update, track, analyze
        budget_data = content.get("budget_data", {})
        
        if action_type == "create":
            result = await self.create_budget_plan(budget_year, budget_data)
        elif action_type == "update":
            result = await self.update_budget_plan(budget_data)
        elif action_type == "track":
            result = await self.track_budget_performance(budget_data)
        elif action_type == "analyze":
            result = await self.analyze_budget_performance(budget_data)
        else:
            result = await self.handle_general_budget_task(action_type, budget_data)
        
        return {
            "budget_management_result": result,
            "budget_recommendations": self.get_budget_recommendations(budget_year),
            "financial_insights": self.generate_financial_insights(budget_year)
        }
    
    async def generate_giving_statement(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Generate giving statement for member."""
        member_id = content.get("member_id")
        statement_year = content.get("statement_year", datetime.utcnow().year)
        statement_type = content.get("statement_type", "annual")  # annual, quarterly, monthly
        
        # Generate AI-powered giving statement
        giving_statement = await self.create_giving_statement(
            member_id, statement_year, statement_type
        )
        
        statement_record = {
            "id": str(uuid.uuid4()),
            "member_id": member_id,
            "statement_year": statement_year,
            "statement_type": statement_type,
            "statement_content": giving_statement,
            "generated_at": datetime.utcnow().isoformat(),
            "status": "generated"
        }
        
        self.giving_statements[statement_record["id"]] = statement_record
        
        return {
            "statement_id": statement_record["id"],
            "giving_statement": giving_statement,
            "tax_information": self.get_tax_information(member_id, statement_year),
            "stewardship_education": self.get_stewardship_education_resources()
        }
    
    async def plan_stewardship_campaign(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Plan stewardship campaign."""
        campaign_name = content.get("campaign_name", "")
        campaign_type = content.get("campaign_type", "annual")  # annual, capital, special
        campaign_goals = content.get("campaign_goals", {})
        timeline = content.get("timeline", {})
        target_audience = content.get("target_audience", "all_members")
        
        # Generate AI-powered campaign plan
        campaign_plan = await self.generate_stewardship_campaign(
            campaign_name, campaign_type, campaign_goals, timeline, target_audience
        )
        
        campaign_record = {
            "id": str(uuid.uuid4()),
            "name": campaign_name,
            "type": campaign_type,
            "goals": campaign_goals,
            "timeline": timeline,
            "target_audience": target_audience,
            "plan": campaign_plan,
            "status": "planning",
            "created_at": datetime.utcnow().isoformat()
        }
        
        self.stewardship_programs[campaign_record["id"]] = campaign_record
        
        return {
            "campaign_id": campaign_record["id"],
            "campaign_plan": campaign_plan,
            "communication_strategy": self.get_communication_strategy(campaign_type),
            "volunteer_needs": self.get_volunteer_needs(campaign_type),
            "success_metrics": self.get_success_metrics(campaign_type)
        }
    
    async def analyze_financial_health(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze church financial health."""
        analysis_period = content.get("analysis_period", "annual")
        analysis_scope = content.get("analysis_scope", "comprehensive")
        focus_areas = content.get("focus_areas", ["revenue", "expenses", "reserves", "giving"])
        
        # Generate AI-powered financial analysis
        financial_analysis = await self.generate_financial_analysis(
            analysis_period, analysis_scope, focus_areas
        )
        
        return {
            "financial_analysis": financial_analysis,
            "financial_metrics": self.calculate_financial_metrics(focus_areas),
            "trend_analysis": self.analyze_financial_trends(analysis_period),
            "recommendations": self.generate_financial_recommendations(financial_analysis)
        }
    
    async def create_giving_record(self, member_id: str, giving_amount: float, giving_category: str, giving_date: str, giving_method: str, special_notes: str) -> Dict[str, Any]:
        """Create giving record."""
        record = {
            "id": str(uuid.uuid4()),
            "member_id": member_id,
            "giving_amount": giving_amount,
            "giving_category": giving_category,
            "giving_date": giving_date,
            "giving_method": giving_method,
            "special_notes": special_notes,
            "created_at": datetime.utcnow().isoformat()
        }
        
        return record
    
    async def create_budget_plan(self, budget_year: int, budget_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create budget plan."""
        budget_plan = {
            "id": str(uuid.uuid4()),
            "budget_year": budget_year,
            "revenue_categories": budget_data.get("revenue_categories", {}),
            "expense_categories": budget_data.get("expense_categories", {}),
            "reserve_targets": budget_data.get("reserve_targets", {}),
            "ministry_allocations": budget_data.get("ministry_allocations", {}),
            "created_at": datetime.utcnow().isoformat(),
            "status": "draft"
        }
        
        self.budget_plans[budget_plan["id"]] = budget_plan
        
        return {
            "budget_plan_id": budget_plan["id"],
            "budget_plan": budget_plan,
            "budget_guidelines": self.get_budget_guidelines(budget_year),
            "allocation_recommendations": self.get_allocation_recommendations(budget_data)
        }
    
    async def update_budget_plan(self, budget_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update budget plan."""
        budget_id = budget_data.get("budget_id")
        
        if budget_id in self.budget_plans:
            self.budget_plans[budget_id].update(budget_data)
            return {
                "status": "updated",
                "budget_plan": self.budget_plans[budget_id],
                "update_summary": "Budget plan updated successfully"
            }
        else:
            return {
                "status": "error",
                "message": "Budget plan not found"
            }
    
    async def track_budget_performance(self, budget_data: Dict[str, Any]) -> Dict[str, Any]:
        """Track budget performance."""
        budget_id = budget_data.get("budget_id")
        
        if budget_id in self.budget_plans:
            budget_plan = self.budget_plans[budget_id]
            
            # Calculate performance metrics
            performance_metrics = self.calculate_budget_performance(budget_plan)
            
            return {
                "budget_performance": performance_metrics,
                "variance_analysis": self.analyze_budget_variance(budget_plan),
                "recommendations": self.get_budget_recommendations(budget_plan["budget_year"])
            }
        else:
            return {
                "status": "error",
                "message": "Budget plan not found"
            }
    
    async def analyze_budget_performance(self, budget_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze budget performance."""
        budget_id = budget_data.get("budget_id")
        
        if budget_id in self.budget_plans:
            budget_plan = self.budget_plans[budget_id]
            
            # Generate AI-powered analysis
            analysis = await self.generate_budget_analysis(budget_plan)
            
            return {
                "budget_analysis": analysis,
                "performance_insights": self.generate_performance_insights(budget_plan),
                "improvement_recommendations": self.get_improvement_recommendations(budget_plan)
            }
        else:
            return {
                "status": "error",
                "message": "Budget plan not found"
            }
    
    async def create_giving_statement(self, member_id: str, statement_year: int, statement_type: str) -> Dict[str, Any]:
        """Create giving statement."""
        if member_id not in self.financial_records:
            return {
                "status": "error",
                "message": "No giving records found for member"
            }
        
        member_records = self.financial_records[member_id]
        
        # Filter records by year
        year_records = [
            record for record in member_records["giving_history"]
            if datetime.fromisoformat(record["giving_date"]).year == statement_year
        ]
        
        # Generate AI-powered statement
        statement_content = await self.generate_giving_statement_content(
            member_id, year_records, statement_type
        )
        
        return {
            "member_id": member_id,
            "statement_year": statement_year,
            "statement_type": statement_type,
            "total_given": sum(record["giving_amount"] for record in year_records),
            "giving_breakdown": self.create_giving_breakdown(year_records),
            "statement_content": statement_content,
            "generated_at": datetime.utcnow().isoformat()
        }
    
    async def generate_stewardship_campaign(self, campaign_name: str, campaign_type: str, campaign_goals: Dict[str, Any], timeline: Dict[str, Any], target_audience: str) -> Dict[str, Any]:
        """Generate AI-powered stewardship campaign."""
        prompt = f"""
        Create a comprehensive stewardship campaign plan for:
        Campaign Name: {campaign_name}
        Campaign Type: {campaign_type}
        Goals: {campaign_goals}
        Timeline: {timeline}
        Target Audience: {target_audience}
        
        Include:
        - Campaign objectives and messaging
        - Communication strategy
        - Engagement activities
        - Volunteer coordination
        - Success metrics
        
        Base recommendations on ELCA stewardship principles and Lutheran understanding of generosity.
        """
        
        campaign_text = self.ai_provider.generate_text(prompt)
        
        return {
            "campaign_text": campaign_text,
            "messaging_framework": self.get_messaging_framework(campaign_type),
            "engagement_activities": self.get_engagement_activities(campaign_type),
            "timeline_milestones": self.create_timeline_milestones(timeline)
        }
    
    async def generate_financial_analysis(self, analysis_period: str, analysis_scope: str, focus_areas: List[str]) -> Dict[str, Any]:
        """Generate AI-powered financial analysis."""
        prompt = f"""
        Analyze church financial health for:
        Analysis Period: {analysis_period}
        Analysis Scope: {analysis_scope}
        Focus Areas: {', '.join(focus_areas)}
        
        Include:
        - Financial health assessment
        - Revenue and expense analysis
        - Giving patterns and trends
        - Budget performance
        - Recommendations for improvement
        
        Base analysis on church financial best practices and ELCA stewardship principles.
        """
        
        analysis_text = self.ai_provider.generate_text(prompt)
        
        return {
            "analysis_text": analysis_text,
            "financial_summary": self.create_financial_summary(focus_areas),
            "health_indicators": self.get_health_indicators(focus_areas),
            "risk_assessment": self.assess_financial_risks(focus_areas)
        }
    
    async def generate_budget_analysis(self, budget_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Generate budget analysis."""
        prompt = f"""
        Analyze budget performance for budget year {budget_plan['budget_year']}:
        Revenue Categories: {budget_plan['revenue_categories']}
        Expense Categories: {budget_plan['expense_categories']}
        Ministry Allocations: {budget_plan['ministry_allocations']}
        
        Include:
        - Budget performance analysis
        - Variance explanations
        - Ministry impact assessment
        - Recommendations for improvement
        
        Focus on ELCA ministry priorities and financial stewardship principles.
        """
        
        analysis_text = self.ai_provider.generate_text(prompt)
        
        return {
            "analysis_text": analysis_text,
            "performance_summary": self.create_performance_summary(budget_plan),
            "variance_analysis": self.analyze_budget_variance(budget_plan),
            "ministry_impact": self.assess_ministry_impact(budget_plan)
        }
    
    async def generate_giving_statement_content(self, member_id: str, year_records: List[Dict[str, Any]], statement_type: str) -> str:
        """Generate giving statement content."""
        prompt = f"""
        Create a giving statement for member {member_id} for {statement_type} giving:
        Giving Records: {year_records}
        
        Include:
        - Personal thank you message
        - Giving summary
        - Impact of giving
        - Stewardship encouragement
        
        Use warm, appreciative tone that reflects ELCA values and Lutheran understanding of generosity.
        """
        
        statement_text = self.ai_provider.generate_text(prompt)
        return statement_text
    
    def generate_stewardship_insights(self, member_id: str) -> List[str]:
        """Generate stewardship insights for member."""
        if member_id not in self.financial_records:
            return ["No giving history available"]
        
        member_data = self.financial_records[member_id]
        insights = []
        
        total_given = member_data["total_given"]
        if total_given > 5000:
            insights.append("Generous supporter - consider leadership giving opportunities")
        elif total_given > 2000:
            insights.append("Faithful supporter - encourage continued giving")
        elif total_given > 500:
            insights.append("Regular supporter - suggest increased giving opportunities")
        else:
            insights.append("New or occasional supporter - provide stewardship education")
        
        return insights
    
    def get_follow_up_suggestions(self, giving_category: str) -> List[str]:
        """Get follow-up suggestions for giving category."""
        suggestions = {
            FinancialCategory.OFFERINGS: ["Thank you note", "Annual giving statement", "Stewardship education"],
            FinancialCategory.PLEDGES: ["Pledge reminder", "Progress update", "Thank you note"],
            FinancialCategory.SPECIAL_GIVING: ["Impact report", "Thank you note", "Special recognition"],
            FinancialCategory.MISSION_SUPPORT: ["Mission update", "Thank you note", "Impact story"],
            FinancialCategory.CAPITAL_CAMPAIGN: ["Campaign update", "Thank you note", "Progress report"],
            FinancialCategory.ENDOWMENT: ["Endowment report", "Thank you note", "Legacy recognition"]
        }
        
        return suggestions.get(giving_category, ["Thank you note", "Giving statement"])
    
    def get_budget_recommendations(self, budget_year: int) -> List[str]:
        """Get budget recommendations."""
        return [
            "Maintain 3-6 months operating reserves",
            "Allocate 10-15% for mission and outreach",
            "Plan for facility maintenance and improvements",
            "Consider ministry growth opportunities",
            "Regular budget review and adjustment"
        ]
    
    def generate_financial_insights(self, budget_year: int) -> List[str]:
        """Generate financial insights."""
        return [
            "Strong giving trends",
            "Budget performance on track",
            "Reserve levels adequate",
            "Ministry allocations appropriate",
            "Growth opportunities identified"
        ]
    
    def get_tax_information(self, member_id: str, statement_year: int) -> Dict[str, Any]:
        """Get tax information for giving statement."""
        return {
            "tax_deductible_amount": "Total giving amount",
            "tax_id": "Church tax ID number",
            "statement_year": statement_year,
            "contact_information": "Church contact for tax questions"
        }
    
    def get_stewardship_education_resources(self) -> List[str]:
        """Get stewardship education resources."""
        return [
            "ELCA stewardship materials",
            "Biblical giving principles",
            "Financial planning resources",
            "Generosity education programs"
        ]
    
    def get_communication_strategy(self, campaign_type: str) -> List[str]:
        """Get communication strategy for campaign."""
        strategies = {
            "annual": ["Worship announcements", "Newsletter articles", "Personal invitations", "Stewardship education"],
            "capital": ["Campaign materials", "Vision casting", "Progress updates", "Celebration events"],
            "special": ["Specific need communication", "Impact stories", "Urgent appeals", "Thank you messages"]
        }
        
        return strategies.get(campaign_type, ["Worship announcements", "Newsletter articles", "Personal invitations"])
    
    def get_volunteer_needs(self, campaign_type: str) -> List[str]:
        """Get volunteer needs for campaign."""
        needs = {
            "annual": ["Campaign coordinators", "Communication volunteers", "Education facilitators"],
            "capital": ["Campaign leaders", "Communication team", "Event coordinators"],
            "special": ["Communication volunteers", "Event coordinators", "Follow-up team"]
        }
        
        return needs.get(campaign_type, ["Campaign coordinators", "Communication volunteers"])
    
    def get_success_metrics(self, campaign_type: str) -> List[str]:
        """Get success metrics for campaign."""
        metrics = {
            "annual": ["Participation rate", "Total giving", "New givers", "Increased giving"],
            "capital": ["Campaign goal achievement", "Participation rate", "Major gifts", "Timeline adherence"],
            "special": ["Goal achievement", "Participation rate", "Response rate", "Follow-up engagement"]
        }
        
        return metrics.get(campaign_type, ["Participation rate", "Goal achievement", "Total giving"])
    
    def calculate_financial_metrics(self, focus_areas: List[str]) -> Dict[str, Any]:
        """Calculate financial metrics."""
        metrics = {}
        for area in focus_areas:
            if area == "revenue":
                metrics[area] = {"total": 250000, "growth": "5%", "trend": "positive"}
            elif area == "expenses":
                metrics[area] = {"total": 200000, "growth": "3%", "trend": "stable"}
            elif area == "reserves":
                metrics[area] = {"total": 75000, "months": "4.5", "status": "adequate"}
            elif area == "giving":
                metrics[area] = {"total": 200000, "growth": "7%", "trend": "positive"}
        
        return metrics
    
    def analyze_financial_trends(self, analysis_period: str) -> List[str]:
        """Analyze financial trends."""
        return [
            "Steady growth in giving",
            "Stable expense management",
            "Adequate reserve levels",
            "Positive ministry impact",
            "Strong financial health"
        ]
    
    def generate_financial_recommendations(self, financial_analysis: Dict[str, Any]) -> List[str]:
        """Generate financial recommendations."""
        return [
            "Continue current giving trends",
            "Maintain reserve levels",
            "Plan for ministry growth",
            "Enhance stewardship education",
            "Regular financial review"
        ]
    
    def get_budget_guidelines(self, budget_year: int) -> List[str]:
        """Get budget guidelines."""
        return [
            "Maintain balanced budget",
            "Plan for contingencies",
            "Allocate for ministry priorities",
            "Regular budget review",
            "Transparent reporting"
        ]
    
    def get_allocation_recommendations(self, budget_data: Dict[str, Any]) -> List[str]:
        """Get allocation recommendations."""
        return [
            "Ministry programs: 60%",
            "Administration: 20%",
            "Facilities: 15%",
            "Mission support: 5%"
        ]
    
    def calculate_budget_performance(self, budget_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate budget performance."""
        return {
            "revenue_performance": "95%",
            "expense_performance": "98%",
            "ministry_allocation": "102%",
            "reserve_target": "110%"
        }
    
    def analyze_budget_variance(self, budget_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze budget variance."""
        return {
            "revenue_variance": "5% under budget",
            "expense_variance": "2% under budget",
            "ministry_variance": "2% over budget",
            "reserve_variance": "10% over target"
        }
    
    def get_messaging_framework(self, campaign_type: str) -> List[str]:
        """Get messaging framework for campaign."""
        frameworks = {
            "annual": ["Gratitude", "Ministry impact", "Community building", "Faithful stewardship"],
            "capital": ["Vision", "Future impact", "Legacy building", "Community investment"],
            "special": ["Urgent need", "Immediate impact", "Community response", "Faithful action"]
        }
        
        return frameworks.get(campaign_type, ["Gratitude", "Ministry impact", "Community building"])
    
    def get_engagement_activities(self, campaign_type: str) -> List[str]:
        """Get engagement activities for campaign."""
        activities = {
            "annual": ["Stewardship education", "Giving commitments", "Thank you events", "Impact sharing"],
            "capital": ["Vision events", "Campaign kickoff", "Progress celebrations", "Dedication events"],
            "special": ["Urgent appeals", "Response events", "Thank you gatherings", "Impact reports"]
        }
        
        return activities.get(campaign_type, ["Education", "Commitments", "Thank you events"])
    
    def create_timeline_milestones(self, timeline: Dict[str, Any]) -> List[Dict[str, str]]:
        """Create timeline milestones."""
        milestones = []
        for phase, duration in timeline.items():
            milestones.append({
                "phase": phase,
                "duration": duration,
                "deliverables": f"{phase} deliverables"
            })
        return milestones
    
    def create_financial_summary(self, focus_areas: List[str]) -> Dict[str, Any]:
        """Create financial summary."""
        return {
            "total_revenue": 250000,
            "total_expenses": 200000,
            "net_income": 50000,
            "reserve_balance": 75000,
            "focus_areas": focus_areas
        }
    
    def get_health_indicators(self, focus_areas: List[str]) -> List[str]:
        """Get financial health indicators."""
        return [
            "Strong revenue growth",
            "Controlled expenses",
            "Adequate reserves",
            "Healthy giving trends",
            "Ministry impact"
        ]
    
    def assess_financial_risks(self, focus_areas: List[str]) -> List[str]:
        """Assess financial risks."""
        return [
            "Economic uncertainty",
            "Giving volatility",
            "Expense inflation",
            "Facility maintenance",
            "Ministry growth needs"
        ]
    
    def create_performance_summary(self, budget_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Create performance summary."""
        return {
            "budget_year": budget_plan["budget_year"],
            "overall_performance": "Good",
            "revenue_performance": "95%",
            "expense_performance": "98%",
            "ministry_impact": "Positive"
        }
    
    def generate_performance_insights(self, budget_plan: Dict[str, Any]) -> List[str]:
        """Generate performance insights."""
        return [
            "Budget performance on track",
            "Ministry allocations appropriate",
            "Reserve targets met",
            "Growth opportunities identified"
        ]
    
    def get_improvement_recommendations(self, budget_plan: Dict[str, Any]) -> List[str]:
        """Get improvement recommendations."""
        return [
            "Enhance revenue forecasting",
            "Optimize expense management",
            "Strengthen ministry allocations",
            "Improve reserve planning"
        ]
    
    def assess_ministry_impact(self, budget_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Assess ministry impact."""
        return {
            "worship_impact": "Strong",
            "education_impact": "Positive",
            "mission_impact": "Significant",
            "community_impact": "Positive"
        }
    
    def create_giving_breakdown(self, year_records: List[Dict[str, Any]]) -> Dict[str, float]:
        """Create giving breakdown."""
        breakdown = {}
        for record in year_records:
            category = record["giving_category"]
            if category not in breakdown:
                breakdown[category] = 0
            breakdown[category] += record["giving_amount"]
        return breakdown
    
    def _initialize_financial_database(self):
        """Initialize financial database."""
        self.financial_database = {
            "giving_categories": ["Offerings", "Pledges", "Special Giving", "Mission Support", "Capital Campaign", "Endowment"],
            "budget_categories": ["Ministry", "Administration", "Facilities", "Mission", "Education", "Worship"],
            "campaign_types": ["Annual", "Capital", "Special"],
            "statement_types": ["Annual", "Quarterly", "Monthly"]
        }
    
    async def handle_general_financial_task(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Handle general financial stewardship tasks."""
        return {
            "message": "Financial stewardship task received",
            "status": "processed",
            "suggestions": ["Track giving", "Manage budget", "Generate statements", "Plan campaigns"]
        }

if __name__ == "__main__":
    # This allows running the agent independently for testing
    MOTHERSHIP_URL = os.getenv("MOTHERSHIP_WEBSOCKET_URL", "ws://localhost:8000")
    agent = FinancialStewardshipAgent(MOTHERSHIP_URL)
    asyncio.run(agent.run())
