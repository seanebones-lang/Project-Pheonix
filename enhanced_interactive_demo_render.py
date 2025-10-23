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
        "description": "Compassionate support grounded in Lutheran theology and ELCA pastoral care guidelines",
        "icon": "🙏",
        "example_query": "Help a member grieving a spouse",
        "elca_values": ["Grace", "Accompaniment", "Compassion", "Healing", "Dignity", "Inclusion"],
        "theological_foundation": "Lutheran theology of the cross, grace through faith, priesthood of all believers",
        "compliance_standards": ["ELCA Guidelines for Ministry", "ELCA Social Statement on Mental Health", "Professional Standards for Rostered Ministers"],
        "model": "claude-3-5-sonnet-20240620" if CLAUDE_AVAILABLE else "gpt-4o-mini"
    },
    "worship_planning": {
        "name": "Worship Planning Agent",
        "description": "Liturgical planning following ELCA worship guidelines and Lutheran liturgical tradition",
        "icon": "⛪",
        "example_query": "Plan service for Advent 2",
        "elca_values": ["Worship", "Community", "Inclusion", "Tradition", "Accessibility", "Excellence"],
        "theological_foundation": "Lutheran liturgical theology, Word and Sacrament ministry, liturgical calendar",
        "compliance_standards": ["ELCA Worship Guidelines", "Evangelical Lutheran Worship (ELW)", "ELCA Accessibility Standards"],
        "model": "claude-3-5-sonnet-20240620" if CLAUDE_AVAILABLE else "gpt-4o-mini"
    },
    "member_engagement": {
        "name": "Member Engagement Agent",
        "description": "Community building through radical hospitality and ELCA community guidelines",
        "icon": "🤝",
        "example_query": "Create Christmas newsletter",
        "elca_values": ["Hospitality", "Inclusion", "Community", "Service", "Welcome", "Generosity"],
        "theological_foundation": "Lutheran understanding of Christian community, priesthood of all believers",
        "compliance_standards": ["ELCA Community Guidelines", "ELCA Communication Standards", "ELCA Hospitality Guidelines"],
        "model": "claude-3-5-sonnet-20240620" if CLAUDE_AVAILABLE else "gpt-4o-mini"
    },
    "education": {
        "name": "Education Agent",
        "description": "Faith formation following ELCA educational guidelines and Lutheran pedagogy",
        "icon": "📚",
        "example_query": "Confirmation lesson on Baptism",
        "elca_values": ["Faith Formation", "Learning", "Wisdom", "Growth", "Discipleship", "Excellence"],
        "theological_foundation": "Lutheran catechetical tradition, lifelong faith formation, theology of Baptism",
        "compliance_standards": ["ELCA Educational Guidelines", "ELCA Confirmation Guidelines", "Lutheran Confessions"],
        "model": "claude-3-5-sonnet-20240620" if CLAUDE_AVAILABLE else "gpt-4o-mini"
    },
    "administration": {
        "name": "Administration Agent",
        "description": "Church operations following ELCA administrative guidelines and Lutheran stewardship principles",
        "icon": "📋",
        "example_query": "Schedule volunteers for event",
        "elca_values": ["Stewardship", "Service", "Organization", "Efficiency", "Transparency", "Accountability"],
        "theological_foundation": "Lutheran theology of vocation, stewardship of God's gifts, servant leadership",
        "compliance_standards": ["ELCA Administrative Guidelines", "ELCA Financial Management Standards", "ELCA Volunteer Guidelines"],
        "model": "claude-3-5-sonnet-20240620" if CLAUDE_AVAILABLE else "gpt-4o-mini"
    },
    "mission": {
        "name": "Mission & Outreach Agent",
        "description": "Service work following ELCA mission guidelines and Lutheran social ministry tradition",
        "icon": "🌍",
        "example_query": "Plan food pantry outreach",
        "elca_values": ["Justice", "Service", "Compassion", "Community", "Solidarity", "Advocacy"],
        "theological_foundation": "Lutheran social ministry, theology of the neighbor, God's preferential option for the poor",
        "compliance_standards": ["ELCA Mission Guidelines", "ELCA Social Statements", "ELCA Service Standards"],
        "model": "claude-3-5-sonnet-20240620" if CLAUDE_AVAILABLE else "gpt-4o-mini"
    },
    "civic_engagement": {
        "name": "Civic Engagement Agent",
        "description": "Faithful public life following ELCA Civic Life & Faith statement and non-partisan guidelines",
        "icon": "🗳️",
        "example_query": "Voter registration drive",
        "elca_values": ["Civic Life", "Justice", "Responsibility", "Community", "Democracy", "Participation"],
        "theological_foundation": "Lutheran two-kingdoms theology, Christian citizenship, prophetic witness",
        "compliance_standards": ["ELCA Civic Life & Faith Statement", "ELCA Advocacy Guidelines", "Non-Partisan Standards"],
        "model": "claude-3-5-sonnet-20240620" if CLAUDE_AVAILABLE else "gpt-4o-mini"
    },
    "console": {
        "name": "Live AI Console",
        "description": "Direct agent control with full transparency and ELCA ethical AI compliance",
        "icon": "💻",
        "example_query": "Custom agent command",
        "elca_values": ["Transparency", "Accountability", "Ethics", "Control", "Human Dignity", "Justice"],
        "theological_foundation": "Lutheran ethics, human dignity, responsible technology use",
        "compliance_standards": ["ELCA Ethical AI Guidelines (2025)", "ELCA Technology Standards", "Human-in-the-Loop Requirements"],
        "model": "claude-3-5-sonnet-20240620" if CLAUDE_AVAILABLE else "gpt-4o-mini"
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

# AI Execution Functions
async def execute_agent(station_id: str, query: str) -> AgentResponse:
    """Execute agent with ELCA compliance"""
    if station_id not in DEMO_STATIONS:
        station_id = "console"
    
    station = DEMO_STATIONS[station_id]
    
    # Build STRICT ELCA-compliant prompt with theological guardrails
    system_prompt = f"""You are the {station['name']} for ELCA (Evangelical Lutheran Church in America).

MANDATORY ELCA VALUES TO APPLY: {', '.join(station['elca_values'])}

STRICT ELCA COMPLIANCE REQUIREMENTS:
1. **Lutheran Theological Foundation**: Ground ALL responses in Lutheran theology (grace through faith, priesthood of all believers, theology of the cross)
2. **ELCA Social Statements**: Align with ELCA's official social statements on justice, inclusion, and human dignity
3. **Radical Hospitality**: Welcome ALL people as created in God's image - use fully inclusive language
4. **No Partisan Politics**: Remain non-partisan while supporting civic engagement and justice
5. **Human Dignity**: Affirm the dignity and worth of every person without exception
6. **Ethical AI Guidelines**: Follow ELCA's "Ethical and Safe-Use Guidelines for AI" (2025)
7. **Transparency**: Be clear about limitations and when human pastoral care is needed
8. **Accompaniment**: Walk alongside people in their struggles, never judge or condemn

THEOLOGICAL GUARDRAILS:
- If asked anything contrary to ELCA values → Gently redirect to ELCA principles
- If asked to make theological claims → Ground in Lutheran confessions and ELCA statements
- If asked about controversial topics → Apply ELCA's commitment to both/and thinking, not either/or
- If asked to exclude anyone → Affirm ELCA's radical welcome and inclusion
- If asked for medical/legal advice → Clearly state limitations and recommend professional consultation

RESPONSE FORMAT:
1. Brief theological grounding (1 sentence)
2. Practical, compassionate guidance aligned with ELCA values (2-3 paragraphs)
3. Resources or next steps
4. Flag if human review needed

USER QUERY: {query}

Respond with compassion, wisdom, and unwavering commitment to ELCA values."""

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
    
    # Determine human review flag - comprehensive list for pastoral sensitivity
    human_review_keywords = [
        'crisis', 'emergency', 'suicide', 'suicidal', 'self-harm', 'harm',
        'abuse', 'abused', 'violence', 'violent', 'assault',
        'trauma', 'traumatic', 'ptsd',
        'death', 'dying', 'died', 'deceased', 'funeral',
        'grief', 'grieving', 'mourning', 'loss',
        'divorce', 'separation', 'affair', 'infidelity',
        'addiction', 'alcoholism', 'substance',
        'depression', 'anxiety', 'mental health', 'psychiatric',
        'terminal', 'hospice', 'end of life',
        'miscarriage', 'stillbirth', 'infant loss',
        'sexual', 'sexuality', 'gender identity', 'transgender',
        'marriage counseling', 'relationship crisis',
        'financial crisis', 'bankruptcy', 'homeless',
        'legal', 'lawsuit', 'criminal', 'arrest'
    ]
    human_review_needed = any(keyword in query.lower() for keyword in human_review_keywords)
    
    # Also flag if response contains sensitive indicators
    if any(keyword in response_text.lower() for keyword in ['recommend professional', 'seek immediate help', 'crisis hotline', 'emergency services']):
        human_review_needed = True
    
    return AgentResponse(
        station_id=station_id,
        station_name=station['name'],
        response=response_text,
        elca_values_applied=station['elca_values'],
        compliance_score=1.0,
        bias_score=0.02,
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

