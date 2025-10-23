"""
Education Agent for ELCA Mothership AI.
Handles curriculum development, Bible study creation, faith formation, and educational program management.
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

class ProgramType(str, Enum):
    CONFIRMATION = "confirmation"
    BIBLE_STUDY = "bible_study"
    ADULT_EDUCATION = "adult_education"
    CHILDREN_MINISTRY = "children_ministry"
    YOUTH_MINISTRY = "youth_ministry"
    SENIOR_MINISTRY = "senior_ministry"

class AgeGroup(str, Enum):
    CHILDREN = "children"  # Ages 3-12
    YOUTH = "youth"        # Ages 13-18
    ADULTS = "adults"      # Ages 19-64
    SENIORS = "seniors"    # Ages 65+

class EducationAgent(AgentBase):
    """Agent specialized in Christian education and faith formation."""
    
    def __init__(self, mothership_url: str):
        super().__init__("education", mothership_url)
        self.curricula: Dict[str, Dict[str, Any]] = {}
        self.bible_studies: Dict[str, Dict[str, Any]] = {}
        self.educational_programs: Dict[str, Dict[str, Any]] = {}
        self.ai_provider = get_ai_provider()
        self._initialize_resource_database()
    
    async def process_directive(self, directive: Directive):
        """Process education directives."""
        print(f"Education Agent {self.agent_id} processing directive: {directive.content}")
        
        task_type = directive.content.get("task_type", "")
        
        try:
            if task_type == "create_curriculum":
                result = await self.create_curriculum(directive.content)
            elif task_type == "develop_bible_study":
                result = await self.develop_bible_study(directive.content)
            elif task_type == "plan_educational_program":
                result = await self.plan_educational_program(directive.content)
            elif task_type == "create_faith_formation":
                result = await self.create_faith_formation_content(directive.content)
            elif task_type == "assess_learning":
                result = await self.assess_learning_progress(directive.content)
            else:
                result = await self.handle_general_education_task(directive.content)
            
            await self.send_result(
                task_id=directive.task_id,
                status="completed",
                output=result
            )
            
        except Exception as e:
            print(f"Education Agent error: {e}")
            await self.send_result(
                task_id=directive.task_id,
                status="failed",
                output={"error": str(e)}
            )
    
    async def create_curriculum(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Create educational curriculum."""
        program_type = content.get("program_type", ProgramType.BIBLE_STUDY)
        age_group = content.get("age_group", AgeGroup.ADULTS)
        duration_weeks = content.get("duration_weeks", 8)
        theme = content.get("theme", "")
        learning_objectives = content.get("learning_objectives", [])
        
        # Generate AI-powered curriculum
        curriculum = await self.generate_curriculum(
            program_type, age_group, duration_weeks, theme, learning_objectives
        )
        
        curriculum_record = {
            "id": str(uuid.uuid4()),
            "program_type": program_type,
            "age_group": age_group,
            "duration_weeks": duration_weeks,
            "theme": theme,
            "learning_objectives": learning_objectives,
            "curriculum": curriculum,
            "created_at": datetime.utcnow().isoformat(),
            "status": "draft"
        }
        
        self.curricula[curriculum_record["id"]] = curriculum_record
        
        return {
            "curriculum_id": curriculum_record["id"],
            "curriculum": curriculum,
            "resource_requirements": self.get_resource_requirements(program_type, age_group),
            "assessment_strategies": self.get_assessment_strategies(age_group)
        }
    
    async def develop_bible_study(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Develop Bible study materials."""
        study_title = content.get("study_title", "")
        scripture_focus = content.get("scripture_focus", [])
        age_group = content.get("age_group", AgeGroup.ADULTS)
        session_count = content.get("session_count", 6)
        study_goals = content.get("study_goals", [])
        
        # Generate AI-powered Bible study
        bible_study = await self.generate_bible_study(
            study_title, scripture_focus, age_group, session_count, study_goals
        )
        
        study_record = {
            "id": str(uuid.uuid4()),
            "title": study_title,
            "scripture_focus": scripture_focus,
            "age_group": age_group,
            "session_count": session_count,
            "study_goals": study_goals,
            "content": bible_study,
            "created_at": datetime.utcnow().isoformat(),
            "status": "draft"
        }
        
        self.bible_studies[study_record["id"]] = study_record
        
        return {
            "study_id": study_record["id"],
            "bible_study": bible_study,
            "facilitator_notes": self.get_facilitator_notes(age_group),
            "discussion_questions": self.generate_discussion_questions(scripture_focus)
        }
    
    async def plan_educational_program(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Plan educational program."""
        program_name = content.get("program_name", "")
        program_type = content.get("program_type", ProgramType.ADULT_EDUCATION)
        target_audience = content.get("target_audience", "")
        duration = content.get("duration", "ongoing")
        goals = content.get("goals", [])
        
        # Generate program plan
        program_plan = await self.generate_program_plan(
            program_name, program_type, target_audience, duration, goals
        )
        
        program_record = {
            "id": str(uuid.uuid4()),
            "name": program_name,
            "type": program_type,
            "target_audience": target_audience,
            "duration": duration,
            "goals": goals,
            "plan": program_plan,
            "created_at": datetime.utcnow().isoformat(),
            "status": "planned"
        }
        
        self.educational_programs[program_record["id"]] = program_record
        
        return {
            "program_id": program_record["id"],
            "program_plan": program_plan,
            "implementation_timeline": self.get_implementation_timeline(duration),
            "success_metrics": self.get_success_metrics(program_type)
        }
    
    async def create_faith_formation_content(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Create faith formation content."""
        content_type = content.get("content_type", "devotional")
        age_group = content.get("age_group", AgeGroup.ADULTS)
        topic = content.get("topic", "")
        format_type = content.get("format", "written")
        
        # Generate faith formation content
        formation_content = await self.generate_faith_formation_content(
            content_type, age_group, topic, format_type
        )
        
        return {
            "content": formation_content,
            "age_appropriate_activities": self.get_age_appropriate_activities(age_group),
            "follow_up_resources": self.get_follow_up_resources(content_type)
        }
    
    async def assess_learning_progress(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Assess learning progress."""
        program_id = content.get("program_id")
        participant_id = content.get("participant_id")
        assessment_type = content.get("assessment_type", "formative")
        
        # Generate assessment
        assessment = await self.generate_assessment(program_id, participant_id, assessment_type)
        
        return {
            "assessment": assessment,
            "recommendations": self.get_learning_recommendations(assessment_type),
            "next_steps": self.get_next_learning_steps(assessment_type)
        }
    
    async def generate_curriculum(self, program_type: str, age_group: str, duration_weeks: int, theme: str, learning_objectives: List[str]) -> Dict[str, Any]:
        """Generate AI-powered curriculum."""
        prompt = f"""
        Create a comprehensive curriculum for:
        Program Type: {program_type}
        Age Group: {age_group}
        Duration: {duration_weeks} weeks
        Theme: {theme}
        Learning Objectives: {', '.join(learning_objectives)}
        
        Include:
        - Weekly lesson plans
        - Learning activities
        - Assessment methods
        - Resource materials
        - Faith formation elements
        
        Base content on ELCA educational principles and Lutheran theology.
        """
        
        curriculum_text = self.ai_provider.generate_text(prompt)
        
        return {
            "curriculum_text": curriculum_text,
            "weekly_outline": self.generate_weekly_outline(duration_weeks, theme),
            "learning_activities": self.get_learning_activities(age_group),
            "faith_formation_elements": self.get_faith_formation_elements(program_type)
        }
    
    async def generate_bible_study(self, title: str, scripture_focus: List[str], age_group: str, session_count: int, study_goals: List[str]) -> Dict[str, Any]:
        """Generate AI-powered Bible study."""
        prompt = f"""
        Create a Bible study titled "{title}" with:
        Scripture Focus: {', '.join(scripture_focus)}
        Age Group: {age_group}
        Sessions: {session_count}
        Goals: {', '.join(study_goals)}
        
        Include for each session:
        - Scripture reading
        - Key themes
        - Discussion questions
        - Application activities
        - Prayer suggestions
        
        Use Lutheran hermeneutical principles and ELCA educational approaches.
        """
        
        study_text = self.ai_provider.generate_text(prompt)
        
        return {
            "study_text": study_text,
            "session_outlines": self.generate_session_outlines(session_count, scripture_focus),
            "study_guide": self.create_study_guide(age_group),
            "supplementary_materials": self.get_supplementary_materials(scripture_focus)
        }
    
    async def generate_program_plan(self, name: str, program_type: str, target_audience: str, duration: str, goals: List[str]) -> Dict[str, Any]:
        """Generate program plan."""
        prompt = f"""
        Create a program plan for "{name}":
        Program Type: {program_type}
        Target Audience: {target_audience}
        Duration: {duration}
        Goals: {', '.join(goals)}
        
        Include:
        - Program structure
        - Learning outcomes
        - Implementation steps
        - Resource needs
        - Evaluation methods
        
        Align with ELCA educational standards and Lutheran faith formation principles.
        """
        
        plan_text = self.ai_provider.generate_text(prompt)
        
        return {
            "plan_text": plan_text,
            "program_structure": self.get_program_structure(program_type),
            "learning_outcomes": self.get_learning_outcomes(program_type),
            "implementation_steps": self.get_implementation_steps(program_type)
        }
    
    async def generate_faith_formation_content(self, content_type: str, age_group: str, topic: str, format_type: str) -> Dict[str, Any]:
        """Generate faith formation content."""
        prompt = f"""
        Create {content_type} content for {age_group} on the topic: {topic}
        Format: {format_type}
        
        Include:
        - Age-appropriate language and concepts
        - Lutheran theological perspectives
        - Practical application
        - Faith formation elements
        
        Ensure content aligns with ELCA educational standards and Lutheran understanding of grace and faith.
        """
        
        content_text = self.ai_provider.generate_text(prompt)
        
        return {
            "content_text": content_text,
            "age_appropriate_elements": self.get_age_appropriate_elements(age_group),
            "theological_focus": self.get_theological_focus(topic),
            "practical_applications": self.get_practical_applications(topic)
        }
    
    async def generate_assessment(self, program_id: str, participant_id: str, assessment_type: str) -> Dict[str, Any]:
        """Generate learning assessment."""
        prompt = f"""
        Create a {assessment_type} assessment for educational program {program_id} and participant {participant_id}.
        
        Include:
        - Assessment methods appropriate for faith formation
        - Learning indicators
        - Reflection questions
        - Growth markers
        
        Focus on spiritual growth and faith development rather than just knowledge acquisition.
        """
        
        assessment_text = self.ai_provider.generate_text(prompt)
        
        return {
            "assessment_text": assessment_text,
            "assessment_methods": self.get_assessment_methods(assessment_type),
            "learning_indicators": self.get_learning_indicators(),
            "reflection_questions": self.get_reflection_questions()
        }
    
    def get_resource_requirements(self, program_type: str, age_group: str) -> List[str]:
        """Get resource requirements for program."""
        requirements = {
            ProgramType.CONFIRMATION: ["Confirmation materials", "Bible", "Catechism", "Mentor resources"],
            ProgramType.BIBLE_STUDY: ["Study Bibles", "Commentaries", "Discussion guides", "Audio/visual materials"],
            ProgramType.ADULT_EDUCATION: ["Educational materials", "Discussion resources", "Multimedia content"],
            ProgramType.CHILDREN_MINISTRY: ["Age-appropriate materials", "Visual aids", "Interactive resources"],
            ProgramType.YOUTH_MINISTRY: ["Contemporary resources", "Discussion materials", "Activity supplies"]
        }
        
        return requirements.get(program_type, ["Basic educational materials"])
    
    def get_assessment_strategies(self, age_group: str) -> List[str]:
        """Get assessment strategies for age group."""
        strategies = {
            AgeGroup.CHILDREN: ["Observation", "Creative expression", "Storytelling", "Interactive activities"],
            AgeGroup.YOUTH: ["Discussion participation", "Reflection journals", "Project-based assessment", "Peer feedback"],
            AgeGroup.ADULTS: ["Written reflections", "Discussion participation", "Practical application", "Self-assessment"],
            AgeGroup.SENIORS: ["Life experience sharing", "Reflection discussions", "Practical application", "Peer support"]
        }
        
        return strategies.get(age_group, ["Discussion participation", "Reflection"])
    
    def get_facilitator_notes(self, age_group: str) -> List[str]:
        """Get facilitator notes for age group."""
        notes = {
            AgeGroup.CHILDREN: ["Use simple language", "Include visual aids", "Encourage participation", "Keep sessions short"],
            AgeGroup.YOUTH: ["Encourage questions", "Use contemporary examples", "Foster discussion", "Respect different perspectives"],
            AgeGroup.ADULTS: ["Encourage life experience sharing", "Use discussion-based format", "Respect diverse viewpoints", "Connect to daily life"],
            AgeGroup.SENIORS: ["Honor life experience", "Use discussion format", "Encourage sharing", "Respect wisdom"]
        }
        
        return notes.get(age_group, ["Encourage participation", "Foster discussion"])
    
    def generate_discussion_questions(self, scripture_focus: List[str]) -> List[str]:
        """Generate discussion questions for scripture."""
        questions = []
        for scripture in scripture_focus:
            questions.extend([
                f"What does {scripture} teach us about God?",
                f"How does {scripture} apply to our lives today?",
                f"What questions does {scripture} raise for you?",
                f"How might {scripture} guide our actions?"
            ])
        return questions[:8]  # Limit to 8 questions
    
    def get_implementation_timeline(self, duration: str) -> Dict[str, str]:
        """Get implementation timeline."""
        timelines = {
            "ongoing": {
                "month_1": "Program launch and orientation",
                "month_2": "Content delivery and engagement",
                "month_3": "Assessment and adjustment",
                "ongoing": "Continuous improvement"
            },
            "semester": {
                "week_1": "Program introduction",
                "week_2-12": "Content delivery",
                "week_13": "Assessment and evaluation",
                "week_14": "Closure and next steps"
            }
        }
        
        return timelines.get(duration, {"ongoing": "Continuous implementation"})
    
    def get_success_metrics(self, program_type: str) -> List[str]:
        """Get success metrics for program type."""
        metrics = {
            ProgramType.CONFIRMATION: ["Faith commitment", "Knowledge retention", "Community engagement", "Service participation"],
            ProgramType.BIBLE_STUDY: ["Scripture understanding", "Discussion participation", "Life application", "Continued learning"],
            ProgramType.ADULT_EDUCATION: ["Knowledge acquisition", "Skill development", "Faith growth", "Community building"],
            ProgramType.CHILDREN_MINISTRY: ["Age-appropriate understanding", "Engagement level", "Faith formation", "Family involvement"]
        }
        
        return metrics.get(program_type, ["Learning outcomes", "Participation", "Growth"])
    
    def get_age_appropriate_activities(self, age_group: str) -> List[str]:
        """Get age-appropriate activities."""
        activities = {
            AgeGroup.CHILDREN: ["Storytelling", "Art projects", "Music and movement", "Interactive games"],
            AgeGroup.YOUTH: ["Discussion groups", "Service projects", "Creative expression", "Peer mentoring"],
            AgeGroup.ADULTS: ["Study groups", "Service opportunities", "Reflection journals", "Community building"],
            AgeGroup.SENIORS: ["Life sharing", "Wisdom circles", "Service opportunities", "Intergenerational activities"]
        }
        
        return activities.get(age_group, ["Discussion", "Reflection", "Service"])
    
    def get_follow_up_resources(self, content_type: str) -> List[str]:
        """Get follow-up resources."""
        resources = {
            "devotional": ["Daily devotionals", "Prayer resources", "Scripture study guides"],
            "curriculum": ["Additional lesson plans", "Assessment tools", "Resource materials"],
            "bible_study": ["Commentaries", "Study guides", "Discussion resources"],
            "program": ["Implementation guides", "Evaluation tools", "Resource libraries"]
        }
        
        return resources.get(content_type, ["Additional resources", "Support materials"])
    
    def get_learning_recommendations(self, assessment_type: str) -> List[str]:
        """Get learning recommendations."""
        return [
            "Continue current learning path",
            "Explore additional resources",
            "Engage in community discussion",
            "Apply learning in daily life"
        ]
    
    def get_next_learning_steps(self, assessment_type: str) -> List[str]:
        """Get next learning steps."""
        return [
            "Review key concepts",
            "Practice application",
            "Share with others",
            "Plan continued learning"
        ]
    
    def generate_weekly_outline(self, duration_weeks: int, theme: str) -> List[Dict[str, str]]:
        """Generate weekly outline."""
        outline = []
        for week in range(1, duration_weeks + 1):
            outline.append({
                "week": str(week),
                "focus": f"Week {week} of {theme}",
                "activities": f"Week {week} activities and learning"
            })
        return outline
    
    def get_learning_activities(self, age_group: str) -> List[str]:
        """Get learning activities for age group."""
        activities = {
            AgeGroup.CHILDREN: ["Story time", "Art activities", "Music and songs", "Interactive games"],
            AgeGroup.YOUTH: ["Discussion groups", "Service projects", "Creative projects", "Peer activities"],
            AgeGroup.ADULTS: ["Study groups", "Reflection", "Service", "Community building"],
            AgeGroup.SENIORS: ["Life sharing", "Reflection", "Service", "Community engagement"]
        }
        
        return activities.get(age_group, ["Discussion", "Reflection", "Application"])
    
    def get_faith_formation_elements(self, program_type: str) -> List[str]:
        """Get faith formation elements."""
        elements = {
            ProgramType.CONFIRMATION: ["Faith commitment", "Community belonging", "Service orientation", "Continued learning"],
            ProgramType.BIBLE_STUDY: ["Scripture engagement", "Faith reflection", "Life application", "Community building"],
            ProgramType.ADULT_EDUCATION: ["Faith development", "Community engagement", "Service learning", "Spiritual growth"],
            ProgramType.CHILDREN_MINISTRY: ["Faith foundations", "Community belonging", "Service learning", "Spiritual growth"]
        }
        
        return elements.get(program_type, ["Faith formation", "Community building", "Service learning"])
    
    def generate_session_outlines(self, session_count: int, scripture_focus: List[str]) -> List[Dict[str, str]]:
        """Generate session outlines."""
        outlines = []
        for session in range(1, session_count + 1):
            scripture = scripture_focus[session % len(scripture_focus)] if scripture_focus else "Scripture focus"
            outlines.append({
                "session": str(session),
                "scripture": scripture,
                "focus": f"Session {session} focus",
                "activities": f"Session {session} activities"
            })
        return outlines
    
    def create_study_guide(self, age_group: str) -> Dict[str, List[str]]:
        """Create study guide."""
        return {
            "preparation": ["Read scripture", "Review questions", "Prepare thoughts"],
            "during_study": ["Listen actively", "Participate in discussion", "Ask questions"],
            "after_study": ["Reflect on learning", "Apply to life", "Share with others"]
        }
    
    def get_supplementary_materials(self, scripture_focus: List[str]) -> List[str]:
        """Get supplementary materials."""
        return [
            "Commentaries",
            "Study guides",
            "Historical context",
            "Cultural background",
            "Theological perspectives"
        ]
    
    def get_program_structure(self, program_type: str) -> List[str]:
        """Get program structure."""
        structures = {
            ProgramType.CONFIRMATION: ["Orientation", "Core curriculum", "Mentorship", "Service project", "Confirmation"],
            ProgramType.BIBLE_STUDY: ["Introduction", "Scripture study", "Discussion", "Application", "Reflection"],
            ProgramType.ADULT_EDUCATION: ["Introduction", "Content delivery", "Discussion", "Application", "Evaluation"]
        }
        
        return structures.get(program_type, ["Introduction", "Content", "Discussion", "Application"])
    
    def get_learning_outcomes(self, program_type: str) -> List[str]:
        """Get learning outcomes."""
        outcomes = {
            ProgramType.CONFIRMATION: ["Faith commitment", "Community belonging", "Service orientation"],
            ProgramType.BIBLE_STUDY: ["Scripture understanding", "Faith reflection", "Life application"],
            ProgramType.ADULT_EDUCATION: ["Knowledge acquisition", "Skill development", "Faith growth"]
        }
        
        return outcomes.get(program_type, ["Learning", "Growth", "Application"])
    
    def get_implementation_steps(self, program_type: str) -> List[str]:
        """Get implementation steps."""
        return [
            "Program planning",
            "Resource preparation",
            "Participant recruitment",
            "Program delivery",
            "Assessment and evaluation"
        ]
    
    def get_age_appropriate_elements(self, age_group: str) -> List[str]:
        """Get age-appropriate elements."""
        elements = {
            AgeGroup.CHILDREN: ["Simple language", "Visual aids", "Interactive activities", "Short sessions"],
            AgeGroup.YOUTH: ["Contemporary examples", "Discussion format", "Peer interaction", "Relevant topics"],
            AgeGroup.ADULTS: ["Life experience integration", "Discussion-based", "Practical application", "Respectful dialogue"],
            AgeGroup.SENIORS: ["Life wisdom integration", "Discussion format", "Respectful sharing", "Community building"]
        }
        
        return elements.get(age_group, ["Appropriate content", "Engaging format"])
    
    def get_theological_focus(self, topic: str) -> List[str]:
        """Get theological focus for topic."""
        return [
            "Grace-centered approach",
            "Faith formation",
            "Community building",
            "Service orientation"
        ]
    
    def get_practical_applications(self, topic: str) -> List[str]:
        """Get practical applications."""
        return [
            "Daily life integration",
            "Community service",
            "Faith sharing",
            "Continued learning"
        ]
    
    def get_assessment_methods(self, assessment_type: str) -> List[str]:
        """Get assessment methods."""
        methods = {
            "formative": ["Observation", "Discussion participation", "Reflection", "Self-assessment"],
            "summative": ["Written reflection", "Project completion", "Peer evaluation", "Portfolio review"]
        }
        
        return methods.get(assessment_type, ["Participation", "Reflection", "Application"])
    
    def get_learning_indicators(self) -> List[str]:
        """Get learning indicators."""
        return [
            "Understanding of key concepts",
            "Ability to apply learning",
            "Engagement in discussion",
            "Growth in faith"
        ]
    
    def get_reflection_questions(self) -> List[str]:
        """Get reflection questions."""
        return [
            "What did I learn today?",
            "How does this apply to my life?",
            "What questions do I have?",
            "How has my faith grown?"
        ]
    
    def _initialize_resource_database(self):
        """Initialize resource database."""
        self.resource_database = {
            "curricula": ["ELCA confirmation materials", "Bible study curricula", "Adult education programs"],
            "materials": ["Study Bibles", "Commentaries", "Discussion guides", "Multimedia resources"],
            "programs": ["Faith formation programs", "Educational initiatives", "Community building activities"]
        }
    
    async def handle_general_education_task(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Handle general education tasks."""
        return {
            "message": "Education task received",
            "status": "processed",
            "suggestions": ["Develop curriculum", "Create learning materials", "Plan educational programs"]
        }

if __name__ == "__main__":
    # This allows running the agent independently for testing
    MOTHERSHIP_URL = os.getenv("MOTHERSHIP_WEBSOCKET_URL", "ws://localhost:8000")
    agent = EducationAgent(MOTHERSHIP_URL)
    asyncio.run(agent.run())
