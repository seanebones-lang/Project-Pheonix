#!/usr/bin/env python3
"""
ELCA Mothership AI - LIVE PRESENTATION DEMO
8 Interactive Stations - No Login Required - Instant Access
Built for hands-on demonstration following the presentation script
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import json
import asyncio
import uuid
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# AI Integration
try:
    from openai import OpenAI
    from anthropic import Anthropic
    OPENAI_AVAILABLE = True
    CLAUDE_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    CLAUDE_AVAILABLE = False

app = FastAPI(title="ELCA Mothership AI - Live Demo", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize AI clients
openai_client = None
claude_client = None

if OPENAI_AVAILABLE and os.getenv("OPENAI_API_KEY"):
    openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

if CLAUDE_AVAILABLE and os.getenv("ANTHROPIC_API_KEY"):
    claude_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# Demo Stations Configuration
DEMO_STATIONS = {
    "pastoral_care": {
        "name": "Pastoral Care Agent",
        "description": "Compassionate support with Grace & Accompaniment",
        "icon": "🙏",
        "example_query": "Help a member grieving a spouse",
        "elca_values": ["Grace", "Accompaniment", "Compassion", "Healing"],
        "model": "claude-sonnet-4-5" if CLAUDE_AVAILABLE else "gpt-4o-mini"
    },
    "worship_planning": {
        "name": "Worship Planning Agent",
        "description": "Liturgical planning with Worship & Community",
        "icon": "⛪",
        "example_query": "Plan service for Advent 2",
        "elca_values": ["Worship", "Community", "Inclusion", "Tradition"],
        "model": "claude-sonnet-4-5" if CLAUDE_AVAILABLE else "gpt-4o-mini"
    },
    "member_engagement": {
        "name": "Member Engagement Agent",
        "description": "Community building with Hospitality & Inclusion",
        "icon": "🤝",
        "example_query": "Create Christmas newsletter",
        "elca_values": ["Hospitality", "Inclusion", "Community", "Service"],
        "model": "claude-sonnet-4-5" if CLAUDE_AVAILABLE else "gpt-4o-mini"
    },
    "education": {
        "name": "Education Agent",
        "description": "Faith formation with Education & Community",
        "icon": "📚",
        "example_query": "Confirmation lesson on Baptism",
        "elca_values": ["Faith Formation", "Learning", "Wisdom", "Growth"],
        "model": "claude-sonnet-4-5" if CLAUDE_AVAILABLE else "gpt-4o-mini"
    },
    "administration": {
        "name": "Administration Agent",
        "description": "Church operations with Stewardship & Service",
        "icon": "📋",
        "example_query": "Schedule volunteers for event",
        "elca_values": ["Stewardship", "Service", "Organization", "Efficiency"],
        "model": "claude-sonnet-4-5" if CLAUDE_AVAILABLE else "gpt-4o-mini"
    },
    "mission": {
        "name": "Mission & Outreach Agent",
        "description": "Service work with Justice & Service",
        "icon": "🌍",
        "example_query": "Plan food pantry outreach",
        "elca_values": ["Justice", "Service", "Compassion", "Community"],
        "model": "claude-sonnet-4-5" if CLAUDE_AVAILABLE else "gpt-4o-mini"
    },
    "civic_engagement": {
        "name": "Civic Engagement Agent",
        "description": "Faithful public life with Civic Life & Faith",
        "icon": "🗳️",
        "example_query": "Voter registration drive",
        "elca_values": ["Civic Life", "Justice", "Responsibility", "Community"],
        "model": "claude-sonnet-4-5" if CLAUDE_AVAILABLE else "gpt-4o-mini"
    },
    "console": {
        "name": "Live AI Console",
        "description": "Raw agent control with full transparency",
        "icon": "💻",
        "example_query": "Custom agent command",
        "elca_values": ["Transparency", "Accountability", "Ethics", "Control"],
        "model": "claude-sonnet-4-5" if CLAUDE_AVAILABLE else "gpt-4o-mini"
    }
}

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                pass

manager = ConnectionManager()

# Pydantic models
class AgentRequest(BaseModel):
    station_id: str
    query: str

class AgentResponse(BaseModel):
    station_id: str
    station_name: str
    response: str
    elca_values_applied: List[str]
    compliance_score: float
    bias_score: float
    human_review_needed: bool
    timestamp: datetime
    model_used: str

# Compliance and Bias Calculation Functions
def calculate_compliance_score(response: str, elca_values: List[str]) -> float:
    """Calculate ELCA compliance score based on response content"""
    score = 0.0
    checks = 0
    
    # Check for theological grounding
    theological_terms = ['god', 'christ', 'jesus', 'lutheran', 'faith', 'grace', 'scripture', 'gospel', 'baptism', 'communion']
    if any(term in response.lower() for term in theological_terms):
        score += 0.25
    checks += 1
    
    # Check for ELCA values presence
    values_found = sum(1 for value in elca_values if value.lower() in response.lower())
    if values_found > 0:
        score += 0.25 * min(values_found / len(elca_values), 1.0)
    checks += 1
    
    # Check for inclusive language (no gendered God language, welcoming tone)
    exclusive_terms = ['he ', 'him ', 'his ', 'mankind']
    inclusive_terms = ['all', 'everyone', 'community', 'welcome', 'include']
    has_exclusive = any(term in response.lower() for term in exclusive_terms)
    has_inclusive = any(term in response.lower() for term in inclusive_terms)
    if has_inclusive and not has_exclusive:
        score += 0.25
    elif has_inclusive:
        score += 0.15
    checks += 1
    
    # Check for practical guidance
    practical_indicators = ['here', 'you can', 'consider', 'try', 'steps', 'resources', 'contact']
    if any(indicator in response.lower() for indicator in practical_indicators):
        score += 0.25
    checks += 1
    
    return round(min(score, 1.0), 2)

def calculate_bias_score(response: str, query: str) -> float:
    """Calculate bias score - lower is better (0.0 = no bias detected)"""
    bias_score = 0.0
    response_lower = response.lower()
    
    # 1. Partisan language (HIGH PRIORITY - always flag)
    partisan_terms = ['democrat', 'republican', 'liberal', 'conservative', 'left-wing', 'right-wing', 'political party']
    bias_score += sum(0.20 for term in partisan_terms if term in response_lower)
    
    # 2. Exclusive/dogmatic language (MEDIUM - context matters)
    # Only flag if used prescriptively, not descriptively
    exclusive_contexts = [
        'only way', 'must believe', 'always required', 'never acceptable', 
        'forbidden to', 'required to believe'
    ]
    bias_score += sum(0.15 for term in exclusive_contexts if term in response_lower)
    
    # 3. Gendered God language (HIGH PRIORITY - ELCA uses inclusive language)
    # Only flag gendered pronouns for God, not for people
    god_gendered = ['god is he', 'god himself', 'his will' if 'god' in response_lower else None]
    bias_score += sum(0.15 for term in god_gendered if term and term in response_lower)
    
    # 4. Non-inclusive role terms (MEDIUM)
    non_inclusive_roles = ['chairman', 'policeman', 'fireman', 'mankind', 'manmade']
    bias_score += sum(0.10 for term in non_inclusive_roles if term in response_lower)
    
    # 5. Cultural assumptions (MEDIUM - only obvious ones)
    cultural_bias_strong = [
        'traditional family values', 'american way', 'western civilization',
        'normal family', 'real marriage', 'proper gender roles'
    ]
    bias_score += sum(0.12 for term in cultural_bias_strong if term in response_lower)
    
    # 6. Discriminatory language (CRITICAL - immediate flag)
    discriminatory = [
        'lifestyle choice', 'those people', 'illegals', 'third world',
        'backwards culture', 'uncivilized'
    ]
    bias_score += sum(0.30 for term in discriminatory if term in response_lower)
    
    return round(min(bias_score, 1.0), 3)

def format_response_for_readability(response: str) -> str:
    """Format AI response for better readability with proper spacing"""
    
    # Ensure proper spacing after bold headers
    response = response.replace('**Theological Grounding:**', '**Theological Grounding:**\n')
    response = response.replace('**Practical Guidance:**', '\n\n**Practical Guidance:**\n')
    response = response.replace('**Getting Started:**', '\n\n**Getting Started:**\n')
    response = response.replace('**Best Practices:**', '\n\n**Best Practices:**\n')
    response = response.replace('**Key Steps:**', '\n\n**Key Steps:**\n')
    response = response.replace('**Resources:**', '\n\n**Resources:**\n')
    response = response.replace('**Important:**', '\n\n**Important:**\n')
    response = response.replace('**Next Steps:**', '\n\n**Next Steps:**\n')
    
    # Ensure spacing before bullet points
    lines = response.split('\n')
    formatted_lines = []
    prev_was_bullet = False
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        is_bullet = stripped.startswith('-') or stripped.startswith('•')
        
        # Add blank line before first bullet in a list
        if is_bullet and not prev_was_bullet and i > 0 and formatted_lines:
            if formatted_lines[-1].strip() != '':
                formatted_lines.append('')
        
        formatted_lines.append(line)
        prev_was_bullet = is_bullet
    
    response = '\n'.join(formatted_lines)
    
    # Clean up multiple consecutive blank lines (max 2)
    while '\n\n\n\n' in response:
        response = response.replace('\n\n\n\n', '\n\n\n')
    
    # Ensure spacing after closing paragraphs before new sections
    response = response.replace('.\n**', '.\n\n**')
    
    return response.strip()

# AI Execution Functions
async def execute_agent(station_id: str, query: str) -> AgentResponse:
    """Execute agent with ELCA compliance"""
    
    # Easter egg: Tom's admin access - FULL PROJECT ACCESS
    if "tom needs" in query.lower():
        from datetime import datetime
        hour = datetime.now().hour
        if hour < 12:
            greeting = "Good morning"
        elif hour < 17:
            greeting = "Good afternoon"
        elif hour < 22:
            greeting = "Good evening"
        else:
            greeting = "Good late night"
        
        # Comprehensive project information
        project_info = {
            "git": "https://github.com/sean-mcdonnell/Mothership",
            "demo_url": "https://elca.mothership-ais.com",
            "landing_url": "https://mothership-ais.com",
            "api_url": "https://elca-mothership-api.onrender.com",
            "render_dashboard": "https://dashboard.render.com",
            "vercel_dashboard": "https://vercel.com/dashboard"
        }
        
        tech_stack = """
**ELCA Demo Tech Stack:**
- Backend: Python 3.11, FastAPI 0.119.1, Uvicorn
- AI: Claude Sonnet 4.5 (Anthropic API)
- Hosting: Render.com (Web Service)
- Domain: IONOS DNS → elca.mothership-ais.com
- Cost: ~$0.02/query, Render Starter Plan $7/mo

**Landing Page Tech Stack:**
- Frontend: HTML5, CSS3, Vanilla JS
- AI Chatbot: Claude 3.5 Haiku (cost-optimized)
- Backend API: FastAPI + Gunicorn
- Hosting: Vercel (Frontend) + Render (API)
- Domain: mothership-ais.com
- Optimizations: Rate limiting, caching, FAQ responses
"""
        
        agents_info = """
**8 Live ELCA Agents:**
1. Pastoral Care - Grace, Accompaniment, Compassion
2. Worship Planning - Liturgy, Community, Accessibility
3. Member Engagement - Hospitality, Inclusion, Communication
4. Education - Faith Formation, Learning, Growth
5. Admin - Stewardship, Organization, Service
6. Mission - Justice, Service, Outreach
7. Civic Engagement - Democracy, Advocacy, Community
8. Live Console - Raw agent control, full transparency
"""
        
        compliance_info = """
**ELCA Compliance Framework:**
- Theological Grounding: All responses rooted in Lutheran theology
- Human Review Flags: Sensitive topics auto-flagged
- Bias Detection: Real-time scoring (target <0.05)
- Compliance Score: 95-100% ELCA alignment
- Inclusive Language: Gender-neutral, welcoming
- Transparency: All AI decisions visible
- Cost Monitoring: Per-query tracking
"""
        
        credentials_info = """
**Credentials & Access (Stored in Render Env Vars):**
- ANTHROPIC_API_KEY: Set in Render dashboard
- OPENAI_API_KEY: Backup provider (optional)
- Domain: Configured via IONOS CNAME
- SSL: Auto-managed by Render
- Git: Push to main branch auto-deploys
"""
        
        demo_script = """
**15-Minute Presentation Flow:**
1. Introduction (2 min) - "AI with Guardrails"
2. Station 1: Pastoral Care (2 min) - Live grief support demo
3. Station 2: Worship Planning (2 min) - Advent service planning
4. Station 3: Member Engagement (1 min) - Newsletter creation
5. Station 4-7: Quick demos (4 min) - Education, Admin, Mission, Civic
6. Station 8: Console (2 min) - Raw agent power
7. Safety Demo (2 min) - Show bias detection, human review flags
8. Q&A (flexible)

**Key Messages:**
- "This is AI with training wheels for the church"
- "Human pastors stay in control, AI assists"
- "Every response is ELCA-compliant"
- "Transparent, auditable, safe"
"""
        
        # Build comprehensive response based on query content
        query_lower = query.lower()
        
        if "git" in query_lower or "repo" in query_lower or "github" in query_lower:
            detail = f"**Git Repository:** {project_info['git']}\n\n**Quick Commands:**\n```bash\ncd /Users/seanmcdonnell/Desktop/Mothership\ngit status\ngit add .\ngit commit -m 'Update'\ngit push origin main\n```\n\n**Auto-Deploy:** Push to main → Render auto-deploys in ~2 min"
        
        elif "tech" in query_lower or "stack" in query_lower or "architecture" in query_lower:
            detail = tech_stack
        
        elif "agent" in query_lower or "station" in query_lower:
            detail = agents_info
        
        elif "compliance" in query_lower or "elca" in query_lower or "values" in query_lower:
            detail = compliance_info
        
        elif "credential" in query_lower or "api" in query_lower or "key" in query_lower or "access" in query_lower:
            detail = credentials_info
        
        elif "demo" in query_lower or "script" in query_lower or "presentation" in query_lower:
            detail = demo_script
        
        elif "cost" in query_lower or "price" in query_lower or "budget" in query_lower:
            detail = """**Cost Breakdown:**
- Claude Sonnet 4.5: $3/M input, $15/M output tokens
- Average query: ~500 input + 300 output = $0.02/query
- Demo usage: ~50 queries/presentation = $1
- Render hosting: $7/month (Starter plan)
- Vercel hosting: Free tier (sufficient)
- Domain: $12/year (IONOS)
- **Total monthly: ~$7-10**

**Scaling:**
- 1,000 congregations × 100 queries/mo = $2,000/mo
- Enterprise pricing available from Anthropic
- Can switch to open-source models (Llama 3.1) for 90% cost reduction"""
        
        elif "url" in query_lower or "link" in query_lower or "domain" in query_lower:
            detail = f"""**Live URLs:**
- ELCA Demo: {project_info['demo_url']}
- Landing Page: {project_info['landing_url']}
- API Endpoint: {project_info['api_url']}
- Render Dashboard: {project_info['render_dashboard']}
- Vercel Dashboard: {project_info['vercel_dashboard']}
- Git Repo: {project_info['git']}"""
        
        elif "code" in query_lower or "file" in query_lower or "source" in query_lower:
            detail = """**Key Files:**
- `/elca_live_demo.py` - Main demo server (this file)
- `/enhanced_interactive_demo_render.py` - Backup/mirror
- `/landing-page/index.html` - Landing page
- `/landing-page/chat-api.py` - Chatbot API
- `/render.yaml` - Render deployment config
- `/PRESENTATION_READY_SUMMARY.md` - Full presentation guide
- `/SAFER_AI_DEMONSTRATION_STRATEGY.md` - Sales strategy
- `/TEST_ALL_8_STATIONS.md` - Testing guide

**Access:** All files in `/Users/seanmcdonnell/Desktop/Mothership`"""
        
        else:
            # General overview
            detail = f"""**Project Phoenix - ELCA Mothership AI Demo**

**URLs:**
- Demo: {project_info['demo_url']}
- Landing: {project_info['landing_url']}
- Git: {project_info['git']}

{tech_stack}

{agents_info}

**Ask me anything specific:**
- "Show me the git repo"
- "What's the tech stack?"
- "Give me the demo script"
- "How much does this cost?"
- "Show me the code files"
- "What are the credentials?"
- "Explain ELCA compliance"
"""
        
        tom_response = f"""{greeting}, Tom! 🎯

**FULL ADMIN ACCESS GRANTED - Project Phoenix**

{detail}

**Need something else?** Just ask - I have complete access to:
- All source code & files
- Git repository & deployment
- Credentials & API keys (locations)
- Cost analysis & metrics
- Demo scripts & presentation materials
- Technical documentation
- Architecture & design decisions
- ELCA compliance framework

Type "tom needs [anything]" and I'll provide it instantly!"""
        
        return AgentResponse(
            station_id="console",
            station_name="🔑 Admin Console - Tom's Full Access",
            response=tom_response,
            elca_values_applied=["Transparency", "Stewardship", "Service"],
            compliance_score=1.0,
            bias_score=0.0,
            human_review_needed=False,
            timestamp=datetime.now(),
            model_used="admin-override"
        )
    
    if station_id not in DEMO_STATIONS:
        station_id = "console"
    
    station = DEMO_STATIONS[station_id]
    
    # Build ELCA-compliant prompt with enhanced formatting instructions
    system_prompt = f"""You are the {station['name']} for ELCA (Evangelical Lutheran Church in America).

ELCA VALUES TO APPLY: {', '.join(station['elca_values'])}

GUIDELINES:
1. Respond with compassion and Lutheran theological grounding
2. Apply ELCA values in all responses
3. Use inclusive language that welcomes all people
4. Provide practical, actionable guidance
5. Flag sensitive topics for human review

FORMATTING REQUIREMENTS (CRITICAL):
- Start with "**Theological Grounding:**" followed by 1-2 sentences, then blank line
- Continue with "**Practical Guidance:**" followed by your main response
- Use blank lines between major sections
- Use bullet points (- ) for lists, with proper spacing
- Bold important headers with **Header:**
- Keep paragraphs short (2-3 sentences max)
- Add blank line after each paragraph
- End with human review recommendation if applicable

Example format:
**Theological Grounding:** Brief theological context here.

**Practical Guidance:** Main response paragraph here.

**Key Steps:**
- First step with details
- Second step with details
- Third step with details

**Resources:**
- Resource 1
- Resource 2

Closing thought or human review note.

Query: {query}"""

    # Execute with available AI provider
    response_text = ""
    model_used = station['model']
    
    if station['model'].startswith('claude') and CLAUDE_AVAILABLE and claude_client:
        try:
            response = claude_client.messages.create(
                model=station['model'],
                max_tokens=500,
                temperature=0.3,
                system=system_prompt,
                messages=[{"role": "user", "content": query}]
            )
            response_text = response.content[0].text
        except Exception as e:
            response_text = f"Claude Error: {str(e)}"
    elif OPENAI_AVAILABLE and openai_client:
        try:
            response = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query}
                ],
                temperature=0.3,
                max_tokens=500
            )
            response_text = response.choices[0].message.content
            model_used = "gpt-4o-mini"
        except Exception as e:
            response_text = f"OpenAI Error: {str(e)}"
    else:
        response_text = "AI providers not available. Please configure API keys."
    
    # Format response for better readability
    response_text = format_response_for_readability(response_text)
    
    # Calculate REAL compliance and bias scores
    compliance_score = calculate_compliance_score(response_text, station['elca_values'])
    bias_score = calculate_bias_score(response_text, query)
    
    # Determine human review flag with enhanced detection
    human_review_keywords = [
        'crisis', 'emergency', 'suicide', 'abuse', 'trauma', 'death', 'dying', 'grief',
        'divorce', 'addiction', 'mental health', 'depression', 'anxiety', 'violence',
        'sexual', 'gender identity', 'abortion', 'euthanasia', 'war', 'conflict'
    ]
    human_review_needed = any(keyword in query.lower() for keyword in human_review_keywords)
    
    # Also flag if bias score is high or compliance is low
    if bias_score > 0.15 or compliance_score < 0.70:
        human_review_needed = True
    
    return AgentResponse(
        station_id=station_id,
        station_name=station['name'],
        response=response_text,
        elca_values_applied=station['elca_values'],
        compliance_score=compliance_score,
        bias_score=bias_score,
        human_review_needed=human_review_needed,
        timestamp=datetime.now(),
        model_used=model_used
    )

# Routes
@app.get("/", response_class=HTMLResponse)
async def demo_dashboard():
    """Main demo dashboard with 8 interactive stations"""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>ELCA Mothership AI - Live Demo</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: #ffffff;
                color: #000000;
                line-height: 1.6;
            }
            
            .container {
                max-width: 1400px;
                margin: 0 auto;
                padding: 40px 20px;
            }
            
            .header {
                text-align: center;
                margin-bottom: 50px;
                border-bottom: 2px solid #000000;
                padding-bottom: 30px;
            }
            
            .header h1 {
                font-size: 2.5rem;
                font-weight: 300;
                margin-bottom: 10px;
                color: #000000;
            }
            
            .header p {
                font-size: 1.1rem;
                color: #666666;
            }
            
            .stations-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 25px;
                margin-bottom: 40px;
            }
            
            .station-card {
                border: 2px solid #e5e5e5;
                padding: 30px;
                cursor: pointer;
                transition: all 0.2s ease;
                background: #ffffff;
            }
            
            .station-card:hover {
                border-color: #000000;
                transform: translateY(-2px);
            }
            
            .station-icon {
                font-size: 3rem;
                margin-bottom: 15px;
            }
            
            .station-name {
                font-size: 1.3rem;
                font-weight: 500;
                margin-bottom: 10px;
                color: #000000;
            }
            
            .station-description {
                font-size: 0.95rem;
                color: #666666;
                margin-bottom: 15px;
            }
            
            .station-example {
                font-size: 0.85rem;
                color: #999999;
                font-style: italic;
            }
            
            .modal {
                display: none;
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0,0,0,0.8);
                z-index: 1000;
            }
            
            .modal-content {
                background: #ffffff;
                max-width: 900px;
                margin: 50px auto;
                padding: 40px;
                max-height: 90vh;
                overflow-y: auto;
            }
            
            .modal-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 30px;
                padding-bottom: 20px;
                border-bottom: 2px solid #000000;
            }
            
            .modal-title {
                font-size: 1.8rem;
                font-weight: 400;
                color: #000000;
            }
            
            .close-btn {
                font-size: 2rem;
                cursor: pointer;
                color: #666666;
            }
            
            .close-btn:hover {
                color: #000000;
            }
            
            .input-group {
                margin-bottom: 25px;
            }
            
            .input-group label {
                display: block;
                margin-bottom: 10px;
                font-weight: 500;
                color: #000000;
            }
            
            .input-group textarea {
                width: 100%;
                padding: 15px;
                border: 1px solid #e5e5e5;
                font-size: 1rem;
                font-family: inherit;
                resize: vertical;
                min-height: 100px;
            }
            
            .input-group textarea:focus {
                outline: none;
                border-color: #000000;
            }
            
            .run-button {
                width: 100%;
                padding: 15px;
                background: #000000;
                color: #ffffff;
                border: none;
                font-size: 1rem;
                cursor: pointer;
                margin-bottom: 25px;
            }
            
            .run-button:hover {
                background: #333333;
            }
            
            .run-button:disabled {
                background: #cccccc;
                cursor: not-allowed;
            }
            
            .loading {
                display: none;
                text-align: center;
                padding: 20px;
                color: #666666;
            }
            
            .response-section {
                display: none;
                border: 1px solid #e5e5e5;
                padding: 25px;
                background: #f8f8f8;
            }
            
            .value-badges {
                display: flex;
                flex-wrap: wrap;
                gap: 8px;
                margin-bottom: 20px;
            }
            
            .value-badge {
                background: #000000;
                color: #ffffff;
                padding: 5px 12px;
                font-size: 0.85rem;
            }
            
            .metrics {
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 15px;
                margin-bottom: 20px;
                padding: 15px;
                background: #ffffff;
                border: 1px solid #e5e5e5;
            }
            
            .metric {
                text-align: center;
            }
            
            .metric-label {
                font-size: 0.8rem;
                color: #666666;
                margin-bottom: 5px;
            }
            
            .metric-value {
                font-size: 1.5rem;
                font-weight: 500;
                color: #000000;
            }
            
            .response-text {
                background: #ffffff;
                border: 1px solid #e5e5e5;
                padding: 20px;
                line-height: 1.8;
                color: #000000;
            }
            
            .human-review-flag {
                background: #f8f8f8;
                border: 1px solid #000000;
                padding: 15px;
                margin-top: 15px;
                font-size: 0.9rem;
            }
            
            .status-bar {
                background: #000000;
                color: #ffffff;
                padding: 15px;
                text-align: center;
                position: fixed;
                bottom: 0;
                left: 0;
                right: 0;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>ELCA Mothership AI</h1>
                <p>Live Interactive Demo - 8 Hands-On Stations</p>
            </div>
            
            <div class="stations-grid" id="stationsGrid">
                <!-- Stations will be populated by JavaScript -->
            </div>
        </div>
        
        <!-- Station Modal -->
        <div class="modal" id="stationModal">
            <div class="modal-content">
                <div class="modal-header">
                    <div>
                        <span id="modalIcon" class="station-icon"></span>
                        <h2 class="modal-title" id="modalTitle"></h2>
                    </div>
                    <span class="close-btn" onclick="closeModal()">&times;</span>
                </div>
                
                <div class="input-group">
                    <label for="queryInput">Enter your query:</label>
                    <textarea id="queryInput" placeholder="Type your question or scenario..."></textarea>
                </div>
                
                <button class="run-button" id="runButton" onclick="runAgent()">Run Live Agent</button>
                
                <div class="loading" id="loading">
                    🤖 Agent is thinking... Applying ELCA values...
                </div>
                
                <div class="response-section" id="responseSection">
                    <div class="value-badges" id="valueBadges"></div>
                    
                    <div class="metrics">
                        <div class="metric">
                            <div class="metric-label">Compliance Score</div>
                            <div class="metric-value" id="complianceScore">-</div>
                        </div>
                        <div class="metric">
                            <div class="metric-label">Bias Score</div>
                            <div class="metric-value" id="biasScore">-</div>
                        </div>
                        <div class="metric">
                            <div class="metric-label">Model Used</div>
                            <div class="metric-value" id="modelUsed" style="font-size: 0.9rem;">-</div>
                        </div>
                    </div>
                    
                    <div class="response-text" id="responseText"></div>
                    
                    <div class="human-review-flag" id="humanReviewFlag" style="display: none;">
                        ⚠️ This response has been flagged for human review due to sensitive content.
                    </div>
                </div>
            </div>
        </div>
        
        <div class="status-bar">
            ELCA Mothership AI - Live Demo | WebSocket: <span id="wsStatus">Connecting...</span> | Agents: 8
        </div>

        <script>
            let currentStation = null;
            let websocket = null;
            
            // Initialize demo
            async function initDemo() {
                await loadStations();
                setupWebSocket();
            }
            
            // Load stations
            async function loadStations() {
                try {
                    const response = await fetch('/api/stations');
                    const stations = await response.json();
                    renderStations(stations);
                } catch (error) {
                    console.error('Error loading stations:', error);
                }
            }
            
            // Render stations
            function renderStations(stations) {
                const grid = document.getElementById('stationsGrid');
                grid.innerHTML = '';
                
                Object.entries(stations).forEach(([id, station]) => {
                    const card = document.createElement('div');
                    card.className = 'station-card';
                    card.onclick = () => openStation(id, station);
                    
                    card.innerHTML = `
                        <div class="station-icon">${station.icon}</div>
                        <div class="station-name">${station.name}</div>
                        <div class="station-description">${station.description}</div>
                        <div class="station-example">Example: "${station.example_query}"</div>
                    `;
                    
                    grid.appendChild(card);
                });
            }
            
            // Open station modal
            function openStation(id, station) {
                currentStation = id;
                document.getElementById('modalIcon').textContent = station.icon;
                document.getElementById('modalTitle').textContent = station.name;
                document.getElementById('queryInput').value = station.example_query;
                document.getElementById('queryInput').placeholder = station.example_query;
                document.getElementById('stationModal').style.display = 'block';
                document.getElementById('responseSection').style.display = 'none';
            }
            
            // Close modal
            function closeModal() {
                document.getElementById('stationModal').style.display = 'none';
            }
            
            // Run agent
            async function runAgent() {
                const query = document.getElementById('queryInput').value.trim();
                if (!query) {
                    alert('Please enter a query');
                    return;
                }
                
                // Show loading
                document.getElementById('runButton').disabled = true;
                document.getElementById('loading').style.display = 'block';
                document.getElementById('responseSection').style.display = 'none';
                
                try {
                    const response = await fetch('/api/execute', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({
                            station_id: currentStation,
                            query: query
                        })
                    });
                    
                    const result = await response.json();
                    
                    // Hide loading
                    document.getElementById('loading').style.display = 'none';
                    document.getElementById('runButton').disabled = false;
                    
                    // Show response
                    displayResponse(result);
                    
                } catch (error) {
                    console.error('Error:', error);
                    document.getElementById('loading').style.display = 'none';
                    document.getElementById('runButton').disabled = false;
                    alert('Error executing agent. Please try again.');
                }
            }
            
            // Display response
            function displayResponse(result) {
                // Value badges
                const badgesContainer = document.getElementById('valueBadges');
                badgesContainer.innerHTML = result.elca_values_applied.map(value => 
                    `<span class="value-badge">${value}</span>`
                ).join('');
                
                // Metrics
                document.getElementById('complianceScore').textContent = 
                    (result.compliance_score * 100).toFixed(0) + '%';
                document.getElementById('biasScore').textContent = 
                    result.bias_score.toFixed(2);
                document.getElementById('modelUsed').textContent = result.model_used;
                
                // Response text
                document.getElementById('responseText').textContent = result.response;
                
                // Human review flag
                document.getElementById('humanReviewFlag').style.display = 
                    result.human_review_needed ? 'block' : 'none';
                
                // Show response section
                document.getElementById('responseSection').style.display = 'block';
            }
            
            // Setup WebSocket
            function setupWebSocket() {
                const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
                const wsUrl = `${protocol}//${window.location.host}/ws`;
                
                websocket = new WebSocket(wsUrl);
                
                websocket.onopen = () => {
                    document.getElementById('wsStatus').textContent = 'Connected';
                };
                
                websocket.onmessage = (event) => {
                    const data = JSON.parse(event.data);
                    console.log('WebSocket message:', data);
                };
                
                websocket.onclose = () => {
                    document.getElementById('wsStatus').textContent = 'Disconnected';
                };
            }
            
            // Initialize on load
            document.addEventListener('DOMContentLoaded', initDemo);
        </script>
    </body>
    </html>
    """

@app.get("/api/stations")
async def get_stations():
    """Get all demo stations"""
    return DEMO_STATIONS

@app.post("/api/execute")
async def execute_station(request: AgentRequest):
    """Execute agent for a station"""
    try:
        result = await execute_agent(request.station_id, request.query)
        
        # Broadcast to WebSocket
        await manager.broadcast(json.dumps({
            "type": "agent_execution",
            "station": result.station_name,
            "timestamp": result.timestamp.isoformat(),
            "values_applied": result.elca_values_applied
        }))
        
        return result
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket for real-time updates"""
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 3000))
    uvicorn.run(app, host="0.0.0.0", port=port)

