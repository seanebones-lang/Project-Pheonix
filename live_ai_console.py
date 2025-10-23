#!/usr/bin/env python3
"""
ELCA Mothership AIs - LIVE AI CONSOLE
Interactive console with all agents visible and functional for live demo.
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
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

app = FastAPI(title="ELCA Mothership AIs - Live Console", version="1.0.0")

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

# ELCA Agents Configuration with Full ELCA Compliance
ELCA_AGENTS = {
    "pastoral_care": {
        "name": "Pastoral Care Agent",
        "description": "Provides comprehensive pastoral support grounded in Lutheran theology and ELCA policies",
        "icon": "🙏",
        "capabilities": [
            "Grief counseling and bereavement support following ELCA Guidelines for Ministry",
            "Spiritual direction and discernment using Lutheran theological framework",
            "Crisis intervention aligned with ELCA Social Statement on Mental Health",
            "Prayer and meditation guidance rooted in Lutheran spirituality",
            "Sacramental preparation following ELCA Worship Guidelines",
            "Pastoral care for LGBTQ+ individuals per ELCA Social Statement",
            "Mental health support following ELCA Mental Health Resources",
            "End-of-life care guided by ELCA Social Statement on End of Life"
        ],
        "elca_values": ["Grace", "Accompaniment", "Compassion", "Healing", "Inclusion", "Dignity"],
        "theological_foundation": [
            "Lutheran understanding of grace and forgiveness",
            "Theology of the cross and suffering",
            "Priesthood of all believers",
            "Sacramental theology of Baptism and Holy Communion",
            "ELCA Social Statements and policies"
        ],
        "compliance_standards": [
            "ELCA Guidelines for Ministry",
            "ELCA Social Statements",
            "ELCA Constitution and Bylaws",
            "Professional Standards for Ministry",
            "ELCA Mental Health Resources"
        ],
        "model": "claude-3-5-sonnet-20241022" if CLAUDE_AVAILABLE else "gpt-4o-mini"
    },
    "worship_planning": {
        "name": "Worship Planning Agent",
        "description": "Comprehensive liturgical planning following ELCA Worship Guidelines and Lutheran tradition",
        "icon": "⛪",
        "capabilities": [
            "Liturgical calendar integration following ELCA Calendar",
            "Hymn selection from Evangelical Lutheran Worship (ELW)",
            "Sermon preparation using ELCA Preaching Guidelines",
            "Seasonal worship themes aligned with ELCA Liturgical Year",
            "Accessibility considerations per ELCA Accessibility Guidelines",
            "Multicultural worship planning following ELCA Multicultural Guidelines",
            "Children's worship integration per ELCA Children's Ministry Guidelines",
            "Sacramental planning following ELCA Sacramental Guidelines"
        ],
        "elca_values": ["Worship", "Community", "Inclusion", "Tradition", "Excellence", "Accessibility"],
        "theological_foundation": [
            "Lutheran understanding of worship and liturgy",
            "Theology of Word and Sacrament",
            "Liturgical theology and seasons",
            "ELCA Worship Guidelines and resources",
            "Lutheran hymnody and music theology"
        ],
        "compliance_standards": [
            "ELCA Worship Guidelines",
            "Evangelical Lutheran Worship (ELW)",
            "ELCA Accessibility Guidelines",
            "ELCA Multicultural Guidelines",
            "ELCA Children's Ministry Guidelines"
        ],
        "model": "claude-3-5-sonnet-20241022" if CLAUDE_AVAILABLE else "gpt-4o-mini"
    },
    "member_engagement": {
        "name": "Member Engagement Agent",
        "description": "Comprehensive community building following ELCA Community Guidelines and Lutheran hospitality",
        "icon": "🤝",
        "capabilities": [
            "New member integration following ELCA New Member Guidelines",
            "Volunteer coordination per ELCA Volunteer Management Standards",
            "Event planning aligned with ELCA Event Planning Guidelines",
            "Communication strategies following ELCA Communication Guidelines",
            "Community building rooted in Lutheran understanding of fellowship",
            "Hospitality ministry per ELCA Hospitality Guidelines",
            "Small group ministry following ELCA Small Group Guidelines",
            "Intergenerational ministry per ELCA Intergenerational Guidelines"
        ],
        "elca_values": ["Hospitality", "Inclusion", "Community", "Service", "Fellowship", "Generosity"],
        "theological_foundation": [
            "Lutheran understanding of Christian community",
            "Theology of hospitality and welcome",
            "Priesthood of all believers in practice",
            "ELCA Community Guidelines and resources",
            "Lutheran social ministry tradition"
        ],
        "compliance_standards": [
            "ELCA Community Guidelines",
            "ELCA Volunteer Management Standards",
            "ELCA Communication Guidelines",
            "ELCA Hospitality Guidelines",
            "ELCA Small Group Guidelines"
        ],
        "model": "claude-3-5-sonnet-20241022" if CLAUDE_AVAILABLE else "gpt-4o-mini"
    },
    "education": {
        "name": "Education Agent",
        "description": "Comprehensive faith formation following ELCA Educational Guidelines and Lutheran pedagogy",
        "icon": "📚",
        "capabilities": [
            "Confirmation and catechism following ELCA Confirmation Guidelines",
            "Adult education programs per ELCA Adult Education Standards",
            "Children's ministry following ELCA Children's Ministry Guidelines",
            "Bible study facilitation using ELCA Bible Study Resources",
            "Theological education aligned with ELCA Theological Education Guidelines",
            "Youth ministry following ELCA Youth Ministry Guidelines",
            "Family ministry per ELCA Family Ministry Guidelines",
            "Interfaith education following ELCA Interfaith Guidelines"
        ],
        "elca_values": ["Faith Formation", "Learning", "Wisdom", "Growth", "Discipleship", "Excellence"],
        "theological_foundation": [
            "Lutheran understanding of faith formation",
            "Theology of education and discipleship",
            "Lutheran pedagogy and teaching methods",
            "ELCA Educational Guidelines and resources",
            "Lutheran tradition of theological education"
        ],
        "compliance_standards": [
            "ELCA Educational Guidelines",
            "ELCA Confirmation Guidelines",
            "ELCA Children's Ministry Guidelines",
            "ELCA Youth Ministry Guidelines",
            "ELCA Adult Education Standards"
        ],
        "model": "claude-3-5-sonnet-20241022" if CLAUDE_AVAILABLE else "gpt-4o-mini"
    },
    "administration": {
        "name": "Administration Agent",
        "description": "Comprehensive church operations following ELCA Administrative Guidelines and Lutheran stewardship",
        "icon": "📋",
        "capabilities": [
            "Volunteer scheduling following ELCA Volunteer Management Standards",
            "Facility management per ELCA Facility Management Guidelines",
            "Budget planning aligned with ELCA Financial Management Guidelines",
            "Record keeping following ELCA Record Keeping Standards",
            "Communication systems per ELCA Communication Guidelines",
            "Technology management following ELCA Technology Guidelines",
            "Risk management per ELCA Risk Management Guidelines",
            "Compliance monitoring following ELCA Compliance Standards"
        ],
        "elca_values": ["Stewardship", "Service", "Organization", "Efficiency", "Transparency", "Accountability"],
        "theological_foundation": [
            "Lutheran understanding of stewardship",
            "Theology of service and administration",
            "ELCA Administrative Guidelines and resources",
            "Lutheran tradition of good governance",
            "Theology of transparency and accountability"
        ],
        "compliance_standards": [
            "ELCA Administrative Guidelines",
            "ELCA Financial Management Guidelines",
            "ELCA Volunteer Management Standards",
            "ELCA Technology Guidelines",
            "ELCA Risk Management Guidelines"
        ],
        "model": "claude-3-5-sonnet-20241022" if CLAUDE_AVAILABLE else "gpt-4o-mini"
    },
    "mission": {
        "name": "Mission Agent",
        "description": "Comprehensive outreach following ELCA Mission Guidelines and Lutheran social ministry tradition",
        "icon": "🌍",
        "capabilities": [
            "Local outreach programs following ELCA Local Mission Guidelines",
            "Global mission support per ELCA Global Mission Guidelines",
            "Social justice initiatives aligned with ELCA Social Statements",
            "Community partnerships following ELCA Partnership Guidelines",
            "Service projects per ELCA Service Project Guidelines",
            "Disaster response following ELCA Disaster Response Guidelines",
            "Environmental ministry per ELCA Environmental Guidelines",
            "Advocacy work following ELCA Advocacy Guidelines"
        ],
        "elca_values": ["Justice", "Service", "Compassion", "Global Community", "Solidarity", "Advocacy"],
        "theological_foundation": [
            "Lutheran understanding of mission and service",
            "Theology of justice and advocacy",
            "ELCA Social Statements and mission theology",
            "Lutheran tradition of social ministry",
            "Theology of global community and solidarity"
        ],
        "compliance_standards": [
            "ELCA Mission Guidelines",
            "ELCA Social Statements",
            "ELCA Global Mission Guidelines",
            "ELCA Advocacy Guidelines",
            "ELCA Environmental Guidelines"
        ],
        "model": "claude-3-5-sonnet-20241022" if CLAUDE_AVAILABLE else "gpt-4o-mini"
    },
    "civic_engagement": {
        "name": "Civic Engagement Agent",
        "description": "Comprehensive civic participation following ELCA Civic Engagement Guidelines and Lutheran social teaching",
        "icon": "🗳️",
        "capabilities": [
            "Voter education and registration following ELCA Voter Education Guidelines",
            "Civic responsibility education per ELCA Civic Education Guidelines",
            "Community advocacy aligned with ELCA Advocacy Guidelines",
            "Public policy engagement following ELCA Public Policy Guidelines",
            "Democratic participation per ELCA Democratic Participation Guidelines",
            "Election integrity following ELCA Election Integrity Guidelines",
            "Civic dialogue per ELCA Civic Dialogue Guidelines",
            "Community organizing following ELCA Community Organizing Guidelines"
        ],
        "elca_values": ["Civic Life", "Justice", "Responsibility", "Community", "Democracy", "Participation"],
        "theological_foundation": [
            "Lutheran understanding of civic responsibility",
            "Theology of justice and public life",
            "ELCA Civic Engagement Guidelines and resources",
            "Lutheran tradition of civic engagement",
            "Theology of democracy and participation"
        ],
        "compliance_standards": [
            "ELCA Civic Engagement Guidelines",
            "ELCA Advocacy Guidelines",
            "ELCA Public Policy Guidelines",
            "ELCA Voter Education Guidelines",
            "ELCA Democratic Participation Guidelines"
        ],
        "model": "claude-3-5-sonnet-20241022" if CLAUDE_AVAILABLE else "gpt-4o-mini"
    },
    "stewardship": {
        "name": "Stewardship Agent",
        "description": "Comprehensive resource management following ELCA Stewardship Guidelines and Lutheran stewardship theology",
        "icon": "💰",
        "capabilities": [
            "Financial planning and budgeting following ELCA Financial Management Guidelines",
            "Resource management per ELCA Resource Management Guidelines",
            "Fundraising strategies aligned with ELCA Fundraising Guidelines",
            "Donor relations following ELCA Donor Relations Guidelines",
            "Sustainability initiatives per ELCA Environmental Guidelines",
            "Endowment management following ELCA Endowment Guidelines",
            "Capital campaigns per ELCA Capital Campaign Guidelines",
            "Financial transparency following ELCA Transparency Guidelines"
        ],
        "elca_values": ["Stewardship", "Responsibility", "Sustainability", "Generosity", "Transparency", "Accountability"],
        "theological_foundation": [
            "Lutheran understanding of stewardship",
            "Theology of generosity and giving",
            "ELCA Stewardship Guidelines and resources",
            "Lutheran tradition of financial stewardship",
            "Theology of sustainability and care for creation"
        ],
        "compliance_standards": [
            "ELCA Stewardship Guidelines",
            "ELCA Financial Management Guidelines",
            "ELCA Fundraising Guidelines",
            "ELCA Environmental Guidelines",
            "ELCA Transparency Guidelines"
        ],
        "model": "claude-3-5-sonnet-20241022" if CLAUDE_AVAILABLE else "gpt-4o-mini"
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
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                # Remove broken connections
                self.active_connections.remove(connection)

manager = ConnectionManager()

# Pydantic models
class AgentRequest(BaseModel):
    agent_id: str
    query: str
    context: Optional[Dict[str, Any]] = None

class AgentResponse(BaseModel):
    agent_id: str
    agent_name: str
    response: str
    elca_values_applied: List[str]
    timestamp: datetime
    model_used: str
    human_review_needed: bool = False

# AI Execution Functions
async def execute_openai_agent(agent_config: Dict, query: str, context: Dict = None) -> str:
    """Execute agent using OpenAI with comprehensive ELCA compliance"""
    if not openai_client:
        return "OpenAI client not available. Please check API key."
    
    # Build comprehensive ELCA-compliant system prompt
    theological_foundation = '\n'.join([f"- {foundation}" for foundation in agent_config.get('theological_foundation', [])])
    compliance_standards = '\n'.join([f"- {standard}" for standard in agent_config.get('compliance_standards', [])])
    capabilities = '\n'.join([f"- {capability}" for capability in agent_config.get('capabilities', [])])
    elca_values = ', '.join(agent_config.get('elca_values', []))
    
    system_prompt = f"""You are the {agent_config['name']} for ELCA (Evangelical Lutheran Church in America).

## ELCA VALUES TO APPLY: {elca_values}

## CAPABILITIES (All ELCA-Compliant):
{capabilities}

## THEOLOGICAL FOUNDATION:
{theological_foundation}

## ELCA COMPLIANCE STANDARDS:
{compliance_standards}

## RESPONSE GUIDELINES:
1. **ELCA Compliance**: Every response must align with ELCA policies, guidelines, and social statements
2. **Lutheran Theology**: Ground all responses in Lutheran theological understanding
3. **Comprehensive Content**: Provide detailed, actionable guidance that fully addresses the query
4. **Inclusive Language**: Use language that welcomes all people as created in God's image
5. **Practical Application**: Offer specific, implementable recommendations
6. **Resource References**: Include relevant ELCA resources and guidelines
7. **Human Review**: Flag sensitive topics requiring pastoral or professional review
8. **Theological Depth**: Connect practical advice to Lutheran theological principles

## FORMAT REQUIREMENTS:
- Begin with a brief theological grounding
- Provide comprehensive, detailed guidance
- Include specific ELCA policy references where applicable
- End with practical next steps and resources
- Flag any content requiring human review

Query: {query}"""

    try:
        response = openai_client.chat.completions.create(
            model=agent_config['model'],
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ],
            temperature=0.2,  # Lower temperature for more consistent ELCA compliance
            max_tokens=2000   # Increased for comprehensive responses
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error executing OpenAI agent: {str(e)}"

async def execute_claude_agent(agent_config: Dict, query: str, context: Dict = None) -> str:
    """Execute agent using Claude with comprehensive ELCA compliance"""
    if not claude_client:
        return "Claude client not available. Please check API key."
    
    # Build comprehensive ELCA-compliant system prompt
    theological_foundation = '\n'.join([f"- {foundation}" for foundation in agent_config.get('theological_foundation', [])])
    compliance_standards = '\n'.join([f"- {standard}" for standard in agent_config.get('compliance_standards', [])])
    capabilities = '\n'.join([f"- {capability}" for capability in agent_config.get('capabilities', [])])
    elca_values = ', '.join(agent_config.get('elca_values', []))
    
    system_prompt = f"""You are the {agent_config['name']} for ELCA (Evangelical Lutheran Church in America).

## ELCA VALUES TO APPLY: {elca_values}

## CAPABILITIES (All ELCA-Compliant):
{capabilities}

## THEOLOGICAL FOUNDATION:
{theological_foundation}

## ELCA COMPLIANCE STANDARDS:
{compliance_standards}

## RESPONSE GUIDELINES:
1. **ELCA Compliance**: Every response must align with ELCA policies, guidelines, and social statements
2. **Lutheran Theology**: Ground all responses in Lutheran theological understanding
3. **Comprehensive Content**: Provide detailed, actionable guidance that fully addresses the query
4. **Inclusive Language**: Use language that welcomes all people as created in God's image
5. **Practical Application**: Offer specific, implementable recommendations
6. **Resource References**: Include relevant ELCA resources and guidelines
7. **Human Review**: Flag sensitive topics requiring pastoral or professional review
8. **Theological Depth**: Connect practical advice to Lutheran theological principles

## FORMAT REQUIREMENTS:
- Begin with a brief theological grounding
- Provide comprehensive, detailed guidance
- Include specific ELCA policy references where applicable
- End with practical next steps and resources
- Flag any content requiring human review

Query: {query}"""

    try:
        response = claude_client.messages.create(
            model=agent_config['model'],
            max_tokens=2000,  # Increased for comprehensive responses
            temperature=0.2,  # Lower temperature for more consistent ELCA compliance
            system=system_prompt,
            messages=[
                {"role": "user", "content": query}
            ]
        )
        return response.content[0].text
    except Exception as e:
        return f"Error executing Claude agent: {str(e)}"

async def execute_agent(agent_id: str, query: str, context: Dict = None) -> AgentResponse:
    """Execute the specified agent"""
    if agent_id not in ELCA_AGENTS:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    agent_config = ELCA_AGENTS[agent_id]
    
    # Determine which AI provider to use
    if agent_config['model'].startswith('claude') and CLAUDE_AVAILABLE:
        response_text = await execute_claude_agent(agent_config, query, context)
        model_used = agent_config['model']
    elif OPENAI_AVAILABLE:
        response_text = await execute_openai_agent(agent_config, query, context)
        model_used = agent_config['model']
    else:
        response_text = "No AI providers available. Please check API keys."
        model_used = "none"
    
    # Determine if human review is needed
    human_review_needed = any(keyword in query.lower() for keyword in [
        'crisis', 'emergency', 'suicide', 'abuse', 'trauma', 'death', 'dying'
    ])
    
    return AgentResponse(
        agent_id=agent_id,
        agent_name=agent_config['name'],
        response=response_text,
        elca_values_applied=agent_config['elca_values'],
        timestamp=datetime.now(),
        model_used=model_used,
        human_review_needed=human_review_needed
    )

# Routes
@app.get("/", response_class=HTMLResponse)
async def live_console():
    """Live AI Console Interface"""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>ELCA Mothership AIs - Live Console</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                color: #333;
            }
            
            .container {
                max-width: 1400px;
                margin: 0 auto;
                padding: 20px;
            }
            
            .header {
                text-align: center;
                color: white;
                margin-bottom: 30px;
            }
            
            .header h1 {
                font-size: 2.5rem;
                margin-bottom: 10px;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            }
            
            .header p {
                font-size: 1.2rem;
                opacity: 0.9;
            }
            
            .console-grid {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 20px;
                margin-bottom: 20px;
            }
            
            .agents-panel {
                background: white;
                border-radius: 15px;
                padding: 20px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            }
            
            .agents-panel h2 {
                color: #4a5568;
                margin-bottom: 20px;
                font-size: 1.5rem;
            }
            
            .agent-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 15px;
            }
            
            .agent-card {
                border: 2px solid #e2e8f0;
                border-radius: 10px;
                padding: 15px;
                cursor: pointer;
                transition: all 0.3s ease;
                background: #f8fafc;
            }
            
            .agent-card:hover {
                border-color: #667eea;
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
            }
            
            .agent-card.selected {
                border-color: #667eea;
                background: #e6f3ff;
            }
            
            .agent-header {
                display: flex;
                align-items: center;
                margin-bottom: 10px;
            }
            
            .agent-icon {
                font-size: 1.5rem;
                margin-right: 10px;
            }
            
            .agent-name {
                font-weight: bold;
                color: #2d3748;
            }
            
            .agent-description {
                font-size: 0.9rem;
                color: #718096;
                margin-bottom: 10px;
            }
            
            .agent-values {
                display: flex;
                flex-wrap: wrap;
                gap: 5px;
            }
            
            .value-tag {
                background: #667eea;
                color: white;
                padding: 2px 8px;
                border-radius: 12px;
                font-size: 0.8rem;
            }
            
            .agent-compliance {
                margin-top: 10px;
                padding-top: 10px;
                border-top: 1px solid #e2e8f0;
            }
            
            .compliance-header {
                font-size: 0.8rem;
                font-weight: bold;
                color: #38a169;
                margin-bottom: 5px;
            }
            
            .compliance-items {
                display: flex;
                flex-wrap: wrap;
                gap: 3px;
            }
            
            .compliance-tag {
                background: #c6f6d5;
                color: #22543d;
                padding: 1px 6px;
                border-radius: 8px;
                font-size: 0.7rem;
            }
            
            .chat-panel {
                background: white;
                border-radius: 15px;
                padding: 20px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                display: flex;
                flex-direction: column;
                height: 600px;
            }
            
            .chat-header {
                display: flex;
                justify-content: between;
                align-items: center;
                margin-bottom: 20px;
                padding-bottom: 15px;
                border-bottom: 2px solid #e2e8f0;
            }
            
            .selected-agent {
                font-weight: bold;
                color: #667eea;
            }
            
            .chat-messages {
                flex: 1;
                overflow-y: auto;
                margin-bottom: 20px;
                padding: 10px;
                background: #f8fafc;
                border-radius: 10px;
                border: 1px solid #e2e8f0;
            }
            
            .message {
                margin-bottom: 15px;
                padding: 10px;
                border-radius: 10px;
                max-width: 80%;
            }
            
            .message.user {
                background: #667eea;
                color: white;
                margin-left: auto;
            }
            
            .message.agent {
                background: white;
                border: 1px solid #e2e8f0;
            }
            
            .message-header {
                font-weight: bold;
                margin-bottom: 5px;
                font-size: 0.9rem;
            }
            
            .message-content {
                line-height: 1.5;
            }
            
            .chat-input {
                display: flex;
                gap: 10px;
            }
            
            .chat-input input {
                flex: 1;
                padding: 12px;
                border: 2px solid #e2e8f0;
                border-radius: 10px;
                font-size: 1rem;
                outline: none;
            }
            
            .chat-input input:focus {
                border-color: #667eea;
            }
            
            .chat-input button {
                padding: 12px 24px;
                background: #667eea;
                color: white;
                border: none;
                border-radius: 10px;
                cursor: pointer;
                font-size: 1rem;
                transition: background 0.3s ease;
            }
            
            .chat-input button:hover {
                background: #5a67d8;
            }
            
            .chat-input button:disabled {
                background: #a0aec0;
                cursor: not-allowed;
            }
            
            .status-bar {
                background: white;
                border-radius: 15px;
                padding: 15px;
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
                margin-top: 20px;
            }
            
            .status-item {
                display: inline-block;
                margin-right: 20px;
                padding: 5px 10px;
                background: #f0f4f8;
                border-radius: 20px;
                font-size: 0.9rem;
            }
            
            .status-item.connected {
                background: #c6f6d5;
                color: #22543d;
            }
            
            .status-item.error {
                background: #fed7d7;
                color: #742a2a;
            }
            
            .loading {
                display: none;
                text-align: center;
                color: #667eea;
                font-style: italic;
            }
            
            .human-review {
                background: #fff3cd;
                border: 1px solid #ffeaa7;
                border-radius: 10px;
                padding: 10px;
                margin-top: 10px;
                font-size: 0.9rem;
                color: #856404;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🎯 ELCA Mothership AIs - Live Console</h1>
                <p>Interactive AI Agents for Lutheran Ministry</p>
            </div>
            
            <div class="console-grid">
                <div class="agents-panel">
                    <h2>🤖 Available Agents</h2>
                    <div class="agent-grid" id="agentGrid">
                        <!-- Agents will be populated by JavaScript -->
                    </div>
                </div>
                
                <div class="chat-panel">
                    <div class="chat-header">
                        <div>
                            <span>Selected Agent: </span>
                            <span class="selected-agent" id="selectedAgent">None</span>
                        </div>
                    </div>
                    
                    <div class="chat-messages" id="chatMessages">
                        <div class="message agent">
                            <div class="message-header">System</div>
                            <div class="message-content">Welcome to the ELCA Mothership AIs Live Console! Select an agent to begin interacting.</div>
                        </div>
                    </div>
                    
                    <div class="loading" id="loading">🤖 Agent is thinking...</div>
                    
                    <div class="chat-input">
                        <input type="text" id="messageInput" placeholder="Ask your selected agent..." disabled>
                        <button id="sendButton" disabled>Send</button>
                    </div>
                </div>
            </div>
            
            <div class="status-bar">
                <div class="status-item" id="connectionStatus">🔌 Connecting...</div>
                <div class="status-item" id="aiStatus">🤖 AI Status: Checking...</div>
                <div class="status-item" id="agentCount">Agents: 8</div>
            </div>
        </div>

        <script>
            let selectedAgent = null;
            let websocket = null;
            
            // Initialize the console
            async function initConsole() {
                await loadAgents();
                setupWebSocket();
                setupEventListeners();
                updateAIStatus();
            }
            
            // Load agents from API
            async function loadAgents() {
                try {
                    const response = await fetch('/api/agents');
                    const agents = await response.json();
                    renderAgents(agents);
                } catch (error) {
                    console.error('Error loading agents:', error);
                }
            }
            
            // Render agents in the grid
            function renderAgents(agents) {
                const agentGrid = document.getElementById('agentGrid');
                agentGrid.innerHTML = '';
                
                Object.entries(agents).forEach(([id, agent]) => {
                    const agentCard = document.createElement('div');
                    agentCard.className = 'agent-card';
                    agentCard.dataset.agentId = id;
                    
                    agentCard.innerHTML = `
                        <div class="agent-header">
                            <span class="agent-icon">${agent.icon}</span>
                            <span class="agent-name">${agent.name}</span>
                        </div>
                        <div class="agent-description">${agent.description}</div>
                        <div class="agent-values">
                            ${agent.elca_values.map(value => `<span class="value-tag">${value}</span>`).join('')}
                        </div>
                        <div class="agent-compliance">
                            <div class="compliance-header">ELCA Compliant</div>
                            <div class="compliance-items">
                                ${agent.compliance_standards ? agent.compliance_standards.slice(0, 3).map(standard => 
                                    `<span class="compliance-tag">${standard}</span>`
                                ).join('') : ''}
                            </div>
                        </div>
                    `;
                    
                    agentCard.addEventListener('click', () => selectAgent(id, agent));
                    agentGrid.appendChild(agentCard);
                });
            }
            
            // Select an agent
            function selectAgent(agentId, agent) {
                // Remove previous selection
                document.querySelectorAll('.agent-card').forEach(card => {
                    card.classList.remove('selected');
                });
                
                // Add selection to clicked card
                document.querySelector(`[data-agent-id="${agentId}"]`).classList.add('selected');
                
                selectedAgent = agentId;
                document.getElementById('selectedAgent').textContent = agent.name;
                
                // Enable input
                document.getElementById('messageInput').disabled = false;
                document.getElementById('sendButton').disabled = false;
                document.getElementById('messageInput').focus();
                
                // Add selection message
                addMessage('system', `Selected ${agent.name}. You can now ask questions!`);
            }
            
            // Setup WebSocket connection
            function setupWebSocket() {
                const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
                const wsUrl = `${protocol}//${window.location.host}/ws`;
                
                websocket = new WebSocket(wsUrl);
                
                websocket.onopen = () => {
                    document.getElementById('connectionStatus').textContent = '🔌 Connected';
                    document.getElementById('connectionStatus').className = 'status-item connected';
                };
                
                websocket.onmessage = (event) => {
                    const data = JSON.parse(event.data);
                    handleWebSocketMessage(data);
                };
                
                websocket.onclose = () => {
                    document.getElementById('connectionStatus').textContent = '🔌 Disconnected';
                    document.getElementById('connectionStatus').className = 'status-item error';
                };
                
                websocket.onerror = (error) => {
                    console.error('WebSocket error:', error);
                    document.getElementById('connectionStatus').textContent = '🔌 Error';
                    document.getElementById('connectionStatus').className = 'status-item error';
                };
            }
            
            // Setup event listeners
            function setupEventListeners() {
                document.getElementById('sendButton').addEventListener('click', sendMessage);
                document.getElementById('messageInput').addEventListener('keypress', (e) => {
                    if (e.key === 'Enter') {
                        sendMessage();
                    }
                });
            }
            
            // Send message
            async function sendMessage() {
                if (!selectedAgent) {
                    alert('Please select an agent first!');
                    return;
                }
                
                const input = document.getElementById('messageInput');
                const message = input.value.trim();
                
                if (!message) return;
                
                // Add user message
                addMessage('user', message);
                input.value = '';
                
                // Show loading
                document.getElementById('loading').style.display = 'block';
                document.getElementById('sendButton').disabled = true;
                
                try {
                    const response = await fetch('/api/execute-agent', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            agent_id: selectedAgent,
                            query: message
                        })
                    });
                    
                    const result = await response.json();
                    
                    // Hide loading
                    document.getElementById('loading').style.display = 'none';
                    document.getElementById('sendButton').disabled = false;
                    
                    // Add agent response
                    addMessage('agent', result.response, result);
                    
                } catch (error) {
                    console.error('Error sending message:', error);
                    document.getElementById('loading').style.display = 'none';
                    document.getElementById('sendButton').disabled = false;
                    addMessage('system', 'Error: Could not get response from agent.');
                }
            }
            
            // Add message to chat
            function addMessage(type, content, metadata = null) {
                const messagesContainer = document.getElementById('chatMessages');
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${type}`;
                
                let header = '';
                if (type === 'user') {
                    header = 'You';
                } else if (type === 'agent') {
                    header = metadata ? metadata.agent_name : 'Agent';
                } else {
                    header = 'System';
                }
                
                messageDiv.innerHTML = `
                    <div class="message-header">${header}</div>
                    <div class="message-content">${content}</div>
                `;
                
                messagesContainer.appendChild(messageDiv);
                messagesContainer.scrollTop = messagesContainer.scrollHeight;
                
                // Add human review notice if needed
                if (metadata && metadata.human_review_needed) {
                    const reviewDiv = document.createElement('div');
                    reviewDiv.className = 'human-review';
                    reviewDiv.textContent = '⚠️ This response has been flagged for human review due to sensitive content.';
                    messageDiv.appendChild(reviewDiv);
                }
            }
            
            // Handle WebSocket messages
            function handleWebSocketMessage(data) {
                if (data.type === 'agent_response') {
                    addMessage('agent', data.response, data);
                } else if (data.type === 'status_update') {
                    // Handle status updates
                }
            }
            
            // Update AI status
            async function updateAIStatus() {
                try {
                    const response = await fetch('/api/status');
                    const status = await response.json();
                    
                    let statusText = '🤖 AI Status: ';
                    if (status.openai_available && status.claude_available) {
                        statusText += 'OpenAI + Claude Ready';
                    } else if (status.openai_available) {
                        statusText += 'OpenAI Ready';
                    } else if (status.claude_available) {
                        statusText += 'Claude Ready';
                    } else {
                        statusText += 'No AI Available';
                    }
                    
                    document.getElementById('aiStatus').textContent = statusText;
                } catch (error) {
                    document.getElementById('aiStatus').textContent = '🤖 AI Status: Error';
                }
            }
            
            // Initialize when page loads
            document.addEventListener('DOMContentLoaded', initConsole);
        </script>
    </body>
    </html>
    """

@app.get("/api/agents")
async def get_agents():
    """Get all available agents"""
    return ELCA_AGENTS

@app.get("/api/status")
async def get_status():
    """Get system status"""
    return {
        "openai_available": OPENAI_AVAILABLE and openai_client is not None,
        "claude_available": CLAUDE_AVAILABLE and claude_client is not None,
        "agents_count": len(ELCA_AGENTS),
        "websocket_connections": len(manager.active_connections)
    }

@app.post("/api/execute-agent")
async def execute_agent_endpoint(request: AgentRequest):
    """Execute an agent with the given query"""
    try:
        result = await execute_agent(request.agent_id, request.query, request.context)
        
        # Broadcast to WebSocket connections
        await manager.broadcast(json.dumps({
            "type": "agent_response",
            "agent_id": result.agent_id,
            "agent_name": result.agent_name,
            "response": result.response,
            "elca_values_applied": result.elca_values_applied,
            "timestamp": result.timestamp.isoformat(),
            "model_used": result.model_used,
            "human_review_needed": result.human_review_needed
        }))
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time communication"""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Handle incoming WebSocket messages if needed
    except WebSocketDisconnect:
        manager.disconnect(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
