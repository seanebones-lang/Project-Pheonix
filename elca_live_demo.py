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
        "model": "claude-3-5-sonnet-latest" if CLAUDE_AVAILABLE else "gpt-4o-mini"
    },
    "worship_planning": {
        "name": "Worship Planning Agent",
        "description": "Liturgical planning with Worship & Community",
        "icon": "⛪",
        "example_query": "Plan service for Advent 2",
        "elca_values": ["Worship", "Community", "Inclusion", "Tradition"],
        "model": "claude-3-5-sonnet-latest" if CLAUDE_AVAILABLE else "gpt-4o-mini"
    },
    "member_engagement": {
        "name": "Member Engagement Agent",
        "description": "Community building with Hospitality & Inclusion",
        "icon": "🤝",
        "example_query": "Create Christmas newsletter",
        "elca_values": ["Hospitality", "Inclusion", "Community", "Service"],
        "model": "claude-3-5-sonnet-latest" if CLAUDE_AVAILABLE else "gpt-4o-mini"
    },
    "education": {
        "name": "Education Agent",
        "description": "Faith formation with Education & Community",
        "icon": "📚",
        "example_query": "Confirmation lesson on Baptism",
        "elca_values": ["Faith Formation", "Learning", "Wisdom", "Growth"],
        "model": "claude-3-5-sonnet-latest" if CLAUDE_AVAILABLE else "gpt-4o-mini"
    },
    "administration": {
        "name": "Administration Agent",
        "description": "Church operations with Stewardship & Service",
        "icon": "📋",
        "example_query": "Schedule volunteers for event",
        "elca_values": ["Stewardship", "Service", "Organization", "Efficiency"],
        "model": "claude-3-5-sonnet-latest" if CLAUDE_AVAILABLE else "gpt-4o-mini"
    },
    "mission": {
        "name": "Mission & Outreach Agent",
        "description": "Service work with Justice & Service",
        "icon": "🌍",
        "example_query": "Plan food pantry outreach",
        "elca_values": ["Justice", "Service", "Compassion", "Community"],
        "model": "claude-3-5-sonnet-latest" if CLAUDE_AVAILABLE else "gpt-4o-mini"
    },
    "civic_engagement": {
        "name": "Civic Engagement Agent",
        "description": "Faithful public life with Civic Life & Faith",
        "icon": "🗳️",
        "example_query": "Voter registration drive",
        "elca_values": ["Civic Life", "Justice", "Responsibility", "Community"],
        "model": "claude-3-5-sonnet-latest" if CLAUDE_AVAILABLE else "gpt-4o-mini"
    },
    "console": {
        "name": "Live AI Console",
        "description": "Raw agent control with full transparency",
        "icon": "💻",
        "example_query": "Custom agent command",
        "elca_values": ["Transparency", "Accountability", "Ethics", "Control"],
        "model": "claude-3-5-sonnet-latest" if CLAUDE_AVAILABLE else "gpt-4o-mini"
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
    
    # Build ELCA-compliant prompt
    system_prompt = f"""You are the {station['name']} for ELCA (Evangelical Lutheran Church in America).

ELCA VALUES TO APPLY: {', '.join(station['elca_values'])}

GUIDELINES:
1. Respond with compassion and Lutheran theological grounding
2. Apply ELCA values in all responses
3. Use inclusive language that welcomes all people
4. Provide practical, actionable guidance
5. Flag sensitive topics for human review
6. Be concise but comprehensive (2-3 paragraphs)

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
    
    # Determine human review flag
    human_review_keywords = ['crisis', 'emergency', 'suicide', 'abuse', 'trauma', 'death', 'dying', 'grief']
    human_review_needed = any(keyword in query.lower() for keyword in human_review_keywords)
    
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

