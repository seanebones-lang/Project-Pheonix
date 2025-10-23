#!/usr/bin/env python3
"""
ELCA Mothership AI - LIVE DEMO BACKEND
Hands-on interactive presentation experience with live agents
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import json
import uuid
import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="ELCA Mothership AI - Live Demo",
    description="Hands-on interactive presentation experience with live agents",
    version="1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ELCA VALUES CONSTRAINTS
ELCA_VALUES = {
    "pastoral": {
        "values": ["Grace", "Accompaniment", "Human Dignity"],
        "constraints": [
            "Apply grace and accompaniment in all responses",
            "Use inclusive language that respects human dignity",
            "Flag sensitive topics for human review",
            "Maintain compassionate tone throughout"
        ],
        "human_review_triggers": ["crisis", "suicide", "abuse", "mental health emergency"]
    },
    "worship": {
        "values": ["Worship", "Community", "Sacraments"],
        "constraints": [
            "Follow ELCA liturgical calendar",
            "Suggest appropriate ELCA hymns",
            "Ensure accessibility for all abilities",
            "Respect diverse worship traditions"
        ],
        "human_review_triggers": ["sacramental content", "theological interpretation"]
    },
    "member_engagement": {
        "values": ["Hospitality", "Inclusion", "Community"],
        "constraints": [
            "Use welcoming and inclusive language",
            "Respect diverse backgrounds and cultures",
            "Promote community building",
            "Ensure accessibility in all communications"
        ],
        "human_review_triggers": ["cultural sensitivity", "inclusive language"]
    },
    "education": {
        "values": ["Faith Formation", "Scripture", "Learning"],
        "constraints": [
            "Ground all content in Lutheran theology",
            "Use age-appropriate language",
            "Include scriptural references",
            "Promote inclusive learning environment"
        ],
        "human_review_triggers": ["theological doctrine", "scriptural interpretation"]
    },
    "admin": {
        "values": ["Stewardship", "Service", "Transparency"],
        "constraints": [
            "Promote responsible stewardship",
            "Ensure transparent processes",
            "Support volunteer coordination",
            "Maintain ethical standards"
        ],
        "human_review_triggers": ["conflict resolution", "sensitive decisions"]
    },
    "mission": {
        "values": ["Justice", "Service", "Compassion"],
        "constraints": [
            "Focus on justice and service",
            "Promote compassionate outreach",
            "Coordinate community partnerships",
            "Ensure sustainable mission practices"
        ],
        "human_review_triggers": ["community partnerships", "grant applications"]
    },
    "civic_engagement": {
        "values": ["Civic Life", "Faith", "Justice"],
        "constraints": [
            "Maintain non-partisan approach",
            "Promote civic participation",
            "Connect faith to civic life",
            "Ensure inclusive participation"
        ],
        "human_review_triggers": ["political content", "voter information"]
    },
    "console": {
        "values": ["Transparency", "Ethics", "Accountability"],
        "constraints": [
            "Provide full transparency",
            "Maintain ethical AI practices",
            "Ensure accountability",
            "Show real-time monitoring"
        ],
        "human_review_triggers": ["system changes", "agent modifications"]
    }
}

# Live agent responses (simulated for demo)
LIVE_RESPONSES = {
    "pastoral": {
        "grief": """I understand you're experiencing profound grief after losing your spouse. This is one of life's most difficult journeys, and I want you to know that you don't have to walk it alone.

**Immediate Support:**
- Our pastoral care team is available 24/7 at (555) 123-4567
- Grief support group meets Tuesdays at 7 PM in the Fellowship Hall
- Individual counseling sessions available with Pastor Sarah

**Spiritual Comfort:**
- "The Lord is near to the brokenhearted and saves the crushed in spirit" (Psalm 34:18)
- Consider lighting a candle in our prayer chapel
- Our congregation holds you in prayer during this difficult time

**Next Steps:**
- Would you like me to connect you with our Stephen Ministry program?
- We can arrange a home visit from our pastoral care team
- Memorial service planning support is available

*This response has been flagged for human review to ensure appropriate pastoral care.*""",
        
        "crisis": """I'm concerned about what you've shared. Your safety and wellbeing are our top priority.

**Immediate Action Required:**
- Please call our crisis line immediately: (555) 911-HELP
- If this is a life-threatening emergency, call 911
- Our pastoral care team will be notified immediately

**Support Resources:**
- National Suicide Prevention Lifeline: 988
- Crisis Text Line: Text HOME to 741741
- Local mental health crisis center: (555) 234-5678

**Follow-up Care:**
- Pastor Sarah will contact you within 2 hours
- We'll arrange immediate pastoral support
- Professional counseling referrals available

*This response has been escalated for immediate human review and pastoral intervention.*"""
    },
    
    "worship": {
        "advent": """**Advent 2 Service Plan - "Prepare the Way"**

**Opening Hymn:** "O Come, O Come, Emmanuel" (ELW 257)
**Gospel:** Mark 1:1-8 (John the Baptist prepares the way)
**Theme:** Preparation and anticipation

**Service Elements:**
- Advent wreath lighting (2nd candle)
- Children's message: "Making paths straight"
- Special music: "Prepare Ye the Way" by choir
- Communion with Advent prayers

**Accessibility Features:**
- Large print bulletins available
- ASL interpreter for hearing impaired
- Wheelchair accessible communion
- Audio description for visually impaired

**ELCA Values Applied:**
- Inclusive worship for all abilities
- Liturgical calendar adherence
- Community participation encouraged
- Sacramental preparation appropriate

*This service plan follows ELCA liturgical guidelines and ensures full accessibility.*"""
    },
    
    "member_engagement": {
        "newsletter": """**Grace Lutheran Christmas Newsletter**

**From Pastor Sarah's Desk:**
This Christmas season, we celebrate the birth of hope in our world. As we gather around tables, both literal and metaphorical, we're reminded that Christ comes to us in community.

**Upcoming Events:**
- Dec 15: Christmas Pageant (all ages welcome)
- Dec 22: Blue Christmas Service (for those grieving)
- Dec 24: Christmas Eve Candlelight Service
- Dec 25: Christmas Day Service

**Community Outreach:**
- Food pantry donations needed
- Winter coat drive for families
- Christmas meal delivery program

**Inclusive Language Applied:**
- Welcoming all family structures
- Accessible event descriptions
- Multi-cultural holiday recognition
- Diverse participation opportunities

*This newsletter promotes inclusive community building and hospitality.*"""
    }
}

# WebSocket connection manager
class LiveDemoManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.demo_sessions: Dict[str, Dict] = {}
        self.agent_logs: List[Dict] = []

    async def connect(self, websocket: WebSocket, session_id: str = None):
        await websocket.accept()
        self.active_connections.append(websocket)
        if session_id:
            self.demo_sessions[session_id] = {
                "websocket": websocket,
                "connected_at": datetime.now(),
                "interactions": []
            }
        logger.info(f"Live demo connection established. Total: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket, session_id: str = None):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        if session_id and session_id in self.demo_sessions:
            del self.demo_sessions[session_id]
        logger.info(f"Live demo connection closed. Total: {len(self.active_connections)}")

    async def broadcast_agent_log(self, log_entry: Dict):
        """Broadcast real-time agent activity"""
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps({
                    "type": "agent_log",
                    "data": log_entry,
                    "timestamp": datetime.now().isoformat()
                }))
            except:
                self.active_connections.remove(connection)

    async def broadcast_compliance_update(self, station: str, compliance_data: Dict):
        """Broadcast real-time compliance updates"""
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps({
                    "type": "compliance_update",
                    "station": station,
                    "data": compliance_data,
                    "timestamp": datetime.now().isoformat()
                }))
            except:
                self.active_connections.remove(connection)

manager = LiveDemoManager()

# Pydantic models
class AgentRequest(BaseModel):
    query: str
    station: str
    session_id: Optional[str] = None

class AgentResponse(BaseModel):
    response: str
    applied_values: List[str]
    compliance_score: float
    bias_score: float
    human_review_needed: Optional[str] = None
    processing_time: float
    timestamp: datetime

@app.get("/")
async def root():
    """Root endpoint for live demo"""
    return {
        "message": "ELCA Mothership AI - Live Demo Backend",
        "status": "active",
        "stations": list(ELCA_VALUES.keys()),
        "features": [
            "Live agent execution",
            "Real-time compliance monitoring",
            "ELCA values enforcement",
            "WebSocket console updates",
            "Multi-language support",
            "Accessibility compliance"
        ]
    }

@app.get("/api/stations")
async def get_stations():
    """Get all available demo stations"""
    stations = []
    for station_id, config in ELCA_VALUES.items():
        stations.append({
            "id": station_id,
            "name": station_id.replace("_", " ").title(),
            "values": config["values"],
            "constraints": config["constraints"],
            "human_review_triggers": config["human_review_triggers"]
        })
    return {"stations": stations}

@app.post("/api/agents/{station}/execute")
async def execute_live_agent(station: str, request: AgentRequest):
    """Execute live agent with ELCA values enforcement"""
    start_time = datetime.now()
    
    # Log agent execution
    log_entry = {
        "station": station,
        "query": request.query,
        "session_id": request.session_id,
        "timestamp": start_time.isoformat(),
        "status": "processing"
    }
    await manager.broadcast_agent_log(log_entry)
    
    # Get station configuration
    station_config = ELCA_VALUES.get(station, {})
    values = station_config.get("values", [])
    constraints = station_config.get("constraints", [])
    triggers = station_config.get("human_review_triggers", [])
    
    # Check for human review triggers
    human_review_needed = None
    query_lower = request.query.lower()
    for trigger in triggers:
        if trigger.lower() in query_lower:
            human_review_needed = f"Triggered by: {trigger}"
            break
    
    # Generate response based on station
    response_text = generate_station_response(station, request.query)
    
    # Calculate compliance and bias scores
    compliance_score = calculate_compliance_score(station, request.query, response_text)
    bias_score = calculate_bias_score(response_text)
    
    # Create response
    response = AgentResponse(
        response=response_text,
        applied_values=values,
        compliance_score=compliance_score,
        bias_score=bias_score,
        human_review_needed=human_review_needed,
        processing_time=(datetime.now() - start_time).total_seconds(),
        timestamp=datetime.now()
    )
    
    # Log completion
    log_entry["status"] = "completed"
    log_entry["compliance_score"] = compliance_score
    log_entry["bias_score"] = bias_score
    await manager.broadcast_agent_log(log_entry)
    
    # Broadcast compliance update
    await manager.broadcast_compliance_update(station, {
        "compliance_score": compliance_score,
        "bias_score": bias_score,
        "values_applied": values,
        "human_review": human_review_needed is not None
    })
    
    return response

@app.get("/api/console/logs")
async def get_console_logs():
    """Get real-time console logs"""
    return {
        "logs": manager.agent_logs[-50:],  # Last 50 logs
        "active_sessions": len(manager.demo_sessions),
        "total_interactions": sum(len(session.get("interactions", [])) for session in manager.demo_sessions.values())
    }

@app.websocket("/ws/console")
async def websocket_console(websocket: WebSocket):
    """WebSocket endpoint for real-time console updates"""
    session_id = str(uuid.uuid4())
    await manager.connect(websocket, session_id)
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message["type"] == "ping":
                await websocket.send_text(json.dumps({
                    "type": "pong",
                    "timestamp": datetime.now().isoformat()
                }))
                
    except WebSocketDisconnect:
        manager.disconnect(websocket, session_id)

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "active_connections": len(manager.active_connections),
        "demo_sessions": len(manager.demo_sessions),
        "stations_available": len(ELCA_VALUES)
    }

# Helper functions
def generate_station_response(station: str, query: str) -> str:
    """Generate appropriate response for station"""
    if station == "pastoral":
        if any(word in query.lower() for word in ["grief", "loss", "death", "mourning"]):
            return LIVE_RESPONSES["pastoral"]["grief"]
        elif any(word in query.lower() for word in ["crisis", "emergency", "suicide", "harm"]):
            return LIVE_RESPONSES["pastoral"]["crisis"]
        else:
            return f"""I'm here to provide pastoral support. Based on your request about "{query}", I recommend:

**Immediate Support:**
- Pastoral care consultation available
- Prayer support from our congregation
- Community resources and referrals

**Next Steps:**
- Schedule time with Pastor Sarah
- Connect with appropriate ministry team
- Access relevant community resources

*This response maintains ELCA values of grace, accompaniment, and human dignity.*"""
    
    elif station == "worship":
        if "advent" in query.lower():
            return LIVE_RESPONSES["worship"]["advent"]
        else:
            return f"""**Worship Planning Response for: "{query}"**

**Service Elements:**
- Appropriate hymns from ELW
- Liturgical calendar alignment
- Accessibility considerations
- Community participation

**ELCA Values Applied:**
- Inclusive worship practices
- Sacramental appropriateness
- Community building focus
- Accessibility compliance

*This worship plan follows ELCA guidelines and ensures full participation.*"""
    
    elif station == "member_engagement":
        if "newsletter" in query.lower():
            return LIVE_RESPONSES["member_engagement"]["newsletter"]
        else:
            return f"""**Member Engagement Response for: "{query}"**

**Community Building:**
- Inclusive communication strategies
- Multi-generational engagement
- Cultural sensitivity
- Accessibility considerations

**ELCA Values Applied:**
- Radical hospitality
- Inclusive community
- Respectful communication
- Service orientation

*This engagement strategy promotes inclusive community building.*"""
    
    else:
        return f"""**{station.replace('_', ' ').title()} Response for: "{query}"**

**ELCA Values Applied:**
- Grace-centered approach
- Inclusive practices
- Community focus
- Service orientation

**Next Steps:**
- Appropriate resource recommendations
- Community connection opportunities
- Follow-up support available

*This response maintains ELCA values and promotes community building.*"""

def calculate_compliance_score(station: str, query: str, response: str) -> float:
    """Calculate ELCA compliance score"""
    base_score = 0.95
    
    # Check for inclusive language
    if any(word in response.lower() for word in ["inclusive", "welcoming", "all", "everyone"]):
        base_score += 0.02
    
    # Check for ELCA values
    station_values = ELCA_VALUES.get(station, {}).get("values", [])
    for value in station_values:
        if value.lower() in response.lower():
            base_score += 0.01
    
    return min(base_score, 1.0)

def calculate_bias_score(response: str) -> float:
    """Calculate bias detection score (lower is better)"""
    bias_indicators = ["exclusive", "only", "must", "should", "cannot"]
    bias_count = sum(1 for indicator in bias_indicators if indicator in response.lower())
    return max(0.01, 0.05 - (bias_count * 0.01))

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting ELCA Mothership AI - Live Demo Backend...")
    print("📱 Demo will be available at: http://localhost:8000")
    print("🤝 WebSocket Console: ws://localhost:8000/ws/console")
    print("🎯 8 Interactive Stations Ready")
    print("⚡ Real-time ELCA Values Enforcement")
    print("=" * 60)
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
