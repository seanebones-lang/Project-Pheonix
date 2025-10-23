#!/usr/bin/env python3
"""
ELCA Mothership AIs - LIVE AI CONSOLE
Interactive console with all agents visible and functional for live demo.
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, HTTPException, Depends, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import json
import asyncio
import uuid
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import jwt
from passlib.context import CryptContext

# Load environment variables
load_dotenv()

# Authentication Setup
SECRET_KEY = os.getenv("SECRET_KEY", "elca-mothership-secret-key-2025")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Security
security = HTTPBearer()

# Simple user database (in production, use a real database)
USERS_DB = {
    "admin": {
        "username": "admin",
        "hashed_password": pwd_context.hash("elca2025"),
        "role": "admin",
        "congregation": "Global ELCA Community"
    },
    "pastor": {
        "username": "pastor", 
        "hashed_password": pwd_context.hash("pastor2025"),
        "role": "pastor",
        "congregation": "Sample Lutheran Church"
    },
    "member": {
        "username": "member",
        "hashed_password": pwd_context.hash("member2025"), 
        "role": "member",
        "congregation": "Sample Lutheran Church"
    }
}

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
class LoginRequest(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user_info: Dict[str, Any]

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

# Authentication functions
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_user(username: str):
    if username in USERS_DB:
        user_dict = USERS_DB[username]
        return user_dict
    return None

def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user:
        return False
    if not verify_password(password, user["hashed_password"]):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    user = get_user(username)
    if user is None:
        raise credentials_exception
    return user

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
@app.post("/api/login", response_model=Token)
async def login(login_request: LoginRequest):
    """Login endpoint for global access"""
    user = authenticate_user(login_request.username, login_request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_info": {
            "username": user["username"],
            "role": user["role"],
            "congregation": user["congregation"]
        }
    }

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
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: #ffffff;
                min-height: 100vh;
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
                margin-bottom: 40px;
                border-bottom: 2px solid #e5e5e5;
                padding-bottom: 30px;
            }
            
            .header h1 {
                font-size: 2.2rem;
                font-weight: 300;
                margin-bottom: 10px;
                color: #000000;
                letter-spacing: -0.5px;
            }
            
            .header p {
                font-size: 1rem;
                color: #666666;
                font-weight: 400;
            }
            
            .console-grid {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 30px;
                margin-bottom: 30px;
            }
            
            .agents-panel {
                background: #ffffff;
                border: 1px solid #e5e5e5;
                padding: 30px;
            }
            
            .agents-panel h2 {
                color: #000000;
                margin-bottom: 25px;
                font-size: 1.3rem;
                font-weight: 400;
                border-bottom: 1px solid #e5e5e5;
                padding-bottom: 10px;
            }
            
            .agent-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
                gap: 20px;
            }
            
            .agent-card {
                border: 1px solid #e5e5e5;
                padding: 20px;
                cursor: pointer;
                transition: all 0.2s ease;
                background: #ffffff;
            }
            
            .agent-card:hover {
                border-color: #000000;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }
            
            .agent-card.selected {
                border-color: #000000;
                background: #f8f8f8;
            }
            
            .agent-header {
                display: flex;
                align-items: center;
                margin-bottom: 12px;
            }
            
            .agent-icon {
                font-size: 1.2rem;
                margin-right: 12px;
                color: #666666;
            }
            
            .agent-name {
                font-weight: 500;
                color: #000000;
                font-size: 1rem;
            }
            
            .agent-description {
                font-size: 0.9rem;
                color: #666666;
                margin-bottom: 15px;
                line-height: 1.5;
            }
            
            .agent-values {
                display: flex;
                flex-wrap: wrap;
                gap: 6px;
                margin-bottom: 15px;
            }
            
            .value-tag {
                background: #f0f0f0;
                color: #000000;
                padding: 3px 8px;
                font-size: 0.75rem;
                border: 1px solid #e5e5e5;
            }
            
            .agent-compliance {
                margin-top: 15px;
                padding-top: 15px;
                border-top: 1px solid #e5e5e5;
            }
            
            .compliance-header {
                font-size: 0.75rem;
                font-weight: 500;
                color: #000000;
                margin-bottom: 8px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            
            .compliance-items {
                display: flex;
                flex-wrap: wrap;
                gap: 4px;
            }
            
            .compliance-tag {
                background: #f8f8f8;
                color: #666666;
                padding: 2px 6px;
                font-size: 0.7rem;
                border: 1px solid #e5e5e5;
            }
            
            .chat-panel {
                background: #ffffff;
                border: 1px solid #e5e5e5;
                padding: 30px;
                display: flex;
                flex-direction: column;
                height: 600px;
            }
            
            .chat-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 25px;
                padding-bottom: 15px;
                border-bottom: 1px solid #e5e5e5;
            }
            
            .selected-agent {
                font-weight: 500;
                color: #000000;
            }
            
            .chat-messages {
                flex: 1;
                overflow-y: auto;
                margin-bottom: 25px;
                padding: 15px;
                background: #f8f8f8;
                border: 1px solid #e5e5e5;
            }
            
            .message {
                margin-bottom: 20px;
                padding: 15px;
                max-width: 80%;
            }
            
            .message.user {
                background: #000000;
                color: #ffffff;
                margin-left: auto;
            }
            
            .message.agent {
                background: #ffffff;
                border: 1px solid #e5e5e5;
            }
            
            .message-header {
                font-weight: 500;
                margin-bottom: 8px;
                font-size: 0.85rem;
                color: #666666;
            }
            
            .message-content {
                line-height: 1.6;
                font-size: 0.9rem;
            }
            
            .chat-input {
                display: flex;
                gap: 12px;
            }
            
            .chat-input input {
                flex: 1;
                padding: 12px 15px;
                border: 1px solid #e5e5e5;
                font-size: 0.9rem;
                outline: none;
                background: #ffffff;
            }
            
            .chat-input input:focus {
                border-color: #000000;
            }
            
            .chat-input button {
                padding: 12px 20px;
                background: #000000;
                color: #ffffff;
                border: none;
                cursor: pointer;
                font-size: 0.9rem;
                transition: background 0.2s ease;
            }
            
            .chat-input button:hover {
                background: #333333;
            }
            
            .chat-input button:disabled {
                background: #cccccc;
                cursor: not-allowed;
            }
            
            .status-bar {
                background: #ffffff;
                border: 1px solid #e5e5e5;
                padding: 20px;
                margin-top: 30px;
            }
            
            .status-item {
                display: inline-block;
                margin-right: 25px;
                padding: 6px 12px;
                background: #f8f8f8;
                border: 1px solid #e5e5e5;
                font-size: 0.85rem;
                color: #666666;
            }
            
            .status-item.connected {
                background: #f0f0f0;
                color: #000000;
                border-color: #000000;
            }
            
            .status-item.error {
                background: #f8f8f8;
                color: #666666;
                border-color: #cccccc;
            }
            
            .loading {
                display: none;
                text-align: center;
                color: #666666;
                font-style: italic;
                font-size: 0.9rem;
            }
            
            .human-review {
                background: #f8f8f8;
                border: 1px solid #e5e5e5;
                padding: 12px;
                margin-top: 12px;
                font-size: 0.85rem;
                color: #666666;
            }
            
            .login-form {
                max-width: 400px;
                margin: 0 auto;
                background: #ffffff;
                border: 1px solid #e5e5e5;
                padding: 40px;
                text-align: center;
            }
            
            .login-form h2 {
                font-size: 1.5rem;
                font-weight: 400;
                margin-bottom: 10px;
                color: #000000;
            }
            
            .login-form p {
                color: #666666;
                margin-bottom: 30px;
            }
            
            .form-group {
                margin-bottom: 20px;
                text-align: left;
            }
            
            .form-group label {
                display: block;
                margin-bottom: 5px;
                font-weight: 500;
                color: #000000;
            }
            
            .form-group input {
                width: 100%;
                padding: 12px 15px;
                border: 1px solid #e5e5e5;
                font-size: 0.9rem;
                outline: none;
            }
            
            .form-group input:focus {
                border-color: #000000;
            }
            
            .login-form button {
                width: 100%;
                padding: 12px;
                background: #000000;
                color: #ffffff;
                border: none;
                cursor: pointer;
                font-size: 0.9rem;
                margin-bottom: 20px;
            }
            
            .login-form button:hover {
                background: #333333;
            }
            
            .demo-credentials {
                background: #f8f8f8;
                border: 1px solid #e5e5e5;
                padding: 20px;
                text-align: left;
            }
            
            .demo-credentials h3 {
                font-size: 1rem;
                margin-bottom: 10px;
                color: #000000;
            }
            
            .demo-credentials p {
                margin-bottom: 5px;
                font-size: 0.85rem;
                color: #666666;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>ELCA Mothership AIs - Live Console</h1>
                <p>Interactive AI Agents for Lutheran Ministry - Global Access</p>
            </div>
            
            <!-- Login Form -->
            <div id="loginForm" class="login-form">
                <h2>Global Access Login</h2>
                <p>Access the ELCA Mothership AIs from anywhere in the world</p>
                <form id="loginFormElement">
                    <div class="form-group">
                        <label for="username">Username</label>
                        <input type="text" id="username" name="username" required>
                    </div>
                    <div class="form-group">
                        <label for="password">Password</label>
                        <input type="password" id="password" name="password" required>
                    </div>
                    <button type="submit">Login</button>
                </form>
                <div class="demo-credentials">
                    <h3>Demo Credentials:</h3>
                    <p><strong>Admin:</strong> admin / elca2025</p>
                    <p><strong>Pastor:</strong> pastor / pastor2025</p>
                    <p><strong>Member:</strong> member / member2025</p>
                </div>
            </div>
            
            <!-- Main Console (hidden initially) -->
            <div id="mainConsole" style="display: none;">
            
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
                <div class="status-item" id="userInfo">User: Not logged in</div>
            </div>
            </div> <!-- End mainConsole -->
        </div>

        <script>
            let selectedAgent = null;
            let websocket = null;
            let authToken = null;
            let currentUser = null;
            
            // Initialize the console
            async function initConsole() {
                await loadAgents();
                setupWebSocket();
                setupEventListeners();
                updateAIStatus();
            }
            
            // Handle login
            async function handleLogin(event) {
                event.preventDefault();
                const username = document.getElementById('username').value;
                const password = document.getElementById('password').value;
                
                try {
                    const response = await fetch('/api/login', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ username, password })
                    });
                    
                    if (response.ok) {
                        const data = await response.json();
                        authToken = data.access_token;
                        currentUser = data.user_info;
                        
                        // Hide login form and show console
                        document.getElementById('loginForm').style.display = 'none';
                        document.getElementById('mainConsole').style.display = 'block';
                        
                        // Update user info in status bar
                        document.getElementById('userInfo').textContent = 
                            `User: ${currentUser.username} (${currentUser.role})`;
                        
                        // Initialize console
                        await initConsole();
                    } else {
                        alert('Login failed. Please check your credentials.');
                    }
                } catch (error) {
                    console.error('Login error:', error);
                    alert('Login failed. Please try again.');
                }
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
                            'Authorization': `Bearer ${authToken}`
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
            document.addEventListener('DOMContentLoaded', () => {
                // Setup login form
                document.getElementById('loginFormElement').addEventListener('submit', handleLogin);
            });
        </script>
    </body>
    </html>
    """

@app.get("/api/agents")
async def get_agents(current_user: dict = Depends(get_current_user)):
    """Get all available agents (requires authentication)"""
    return ELCA_AGENTS

@app.get("/api/status")
async def get_status(current_user: dict = Depends(get_current_user)):
    """Get system status (requires authentication)"""
    return {
        "openai_available": OPENAI_AVAILABLE and openai_client is not None,
        "claude_available": CLAUDE_AVAILABLE and claude_client is not None,
        "agents_count": len(ELCA_AGENTS),
        "websocket_connections": len(manager.active_connections),
        "user_info": {
            "username": current_user["username"],
            "role": current_user["role"],
            "congregation": current_user["congregation"]
        }
    }

@app.post("/api/execute-agent")
async def execute_agent_endpoint(request: AgentRequest, current_user: dict = Depends(get_current_user)):
    """Execute an agent with the given query (requires authentication)"""
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
            "human_review_needed": result.human_review_needed,
            "user": current_user["username"]
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
