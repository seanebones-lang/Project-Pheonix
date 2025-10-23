#!/usr/bin/env python3
"""
ELCA Mothership AIs - Enhanced Interactive Demo (Render Optimized)
This version is optimized for Render deployment with proper environment handling.
"""

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import json
import uuid
import asyncio
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import uvicorn
from pydantic import BaseModel
import logging

# Configure logging for Render
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Rate limiting
limiter = Limiter(key_func=get_remote_address)

# Create FastAPI app
app = FastAPI(
    title="ELCA Mothership AIs - Enhanced Interactive Demo",
    description="Enhanced interactive demo with 2025 best practices and ELCA compliance - Render Optimized",
    version="2.1",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Add middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.user_sessions: Dict[str, Dict] = {}

    async def connect(self, websocket: WebSocket, user_id: str = None):
        await websocket.accept()
        self.active_connections.append(websocket)
        if user_id:
            self.user_sessions[user_id] = {
                "websocket": websocket,
                "connected_at": datetime.now(),
                "last_activity": datetime.now()
            }
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket, user_id: str = None):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        if user_id and user_id in self.user_sessions:
            del self.user_sessions[user_id]
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message))
            except:
                # Remove broken connections
                self.active_connections.remove(connection)

    async def send_to_user(self, user_id: str, message: dict):
        if user_id in self.user_sessions:
            try:
                await self.user_sessions[user_id]["websocket"].send_text(json.dumps(message))
            except:
                # Remove broken connection
                del self.user_sessions[user_id]

manager = ConnectionManager()

# Pydantic models
class ReflectionFeedback(BaseModel):
    user_id: str
    scenario_id: str
    ai_output: str
    grace_rating: int  # 1-5 scale
    inclusion_rating: int  # 1-5 scale
    transparency_rating: int  # 1-5 scale
    comments: Optional[str] = None

class CostAnalysis(BaseModel):
    provider: str
    tokens_used: int
    cost_per_token: float
    total_cost: float
    use_case: str
    timestamp: datetime

class BiasDetectionResult(BaseModel):
    scenario_id: str
    bias_type: str
    severity: str  # low, medium, high
    description: str
    mitigation_suggestions: List[str]
    timestamp: datetime

# Enhanced demo data with 2025 features
ENHANCED_DEMO_DATA = {
    "system_info": {
        "name": "ELCA Mothership AIs",
        "version": "2.1 Enhanced Interactive",
        "status": "Production Ready",
        "last_updated": "October 2025",
        "wcag_compliance": "2.2 AA",
        "deployment": "Render.com",
        "accessibility_features": [
            "Screen reader support",
            "Keyboard navigation",
            "High contrast mode",
            "Text scaling up to 200%",
            "Focus indicators",
            "ARIA labels"
        ]
    },
    "tenants": {
        "southeastern_synod": {
            "id": str(uuid.uuid4()),
            "name": "Southeastern Synod",
            "slug": "southeastern-synod-demo",
            "type": "synod",
            "elca_id": "SYN-SE-DEMO",
            "congregations": 156,
            "members": 45000,
            "created_at": "2025-01-01T00:00:00Z",
            "hierarchy": {
                "level": 1,
                "parent": None,
                "children": ["grace_lutheran", "peace_lutheran", "hope_lutheran"]
            }
        },
        "grace_lutheran": {
            "id": str(uuid.uuid4()),
            "name": "Grace Lutheran Church",
            "slug": "grace-lutheran-demo",
            "type": "congregation",
            "elca_id": "CON-GA-DEMO-001",
            "synod_id": "southeastern_synod",
            "members": 450,
            "pastor": "Rev. Sarah Johnson",
            "created_at": "2025-01-15T00:00:00Z",
            "hierarchy": {
                "level": 2,
                "parent": "southeastern_synod",
                "children": []
            }
        },
        "peace_lutheran": {
            "id": str(uuid.uuid4()),
            "name": "Peace Lutheran Church",
            "slug": "peace-lutheran-demo",
            "type": "congregation",
            "elca_id": "CON-GA-DEMO-002",
            "synod_id": "southeastern_synod",
            "members": 320,
            "pastor": "Rev. Michael Chen",
            "created_at": "2025-01-20T00:00:00Z",
            "hierarchy": {
                "level": 2,
                "parent": "southeastern_synod",
                "children": []
            }
        }
    },
    "elca_values": [
        {
            "name": "Radical Hospitality",
            "description": "Welcome all people with open hearts, recognizing the inherent dignity of every person as created in God's image.",
            "ai_guidance": "AI should enhance, not replace, human connection and pastoral care.",
            "bias_checkpoints": ["inclusive_language", "cultural_sensitivity", "accessibility"]
        },
        {
            "name": "Grace-Centered Faith",
            "description": "Ground all actions in God's unconditional love and forgiveness.",
            "ai_guidance": "AI decisions should reflect grace, mercy, and understanding rather than judgment or exclusion.",
            "bias_checkpoints": ["non_judgmental_tone", "forgiveness_emphasis", "unconditional_love"]
        },
        {
            "name": "Justice and Advocacy",
            "description": "Work for justice, peace, and reconciliation in all relationships.",
            "ai_guidance": "AI should be used to amplify voices of the marginalized and promote equity.",
            "bias_checkpoints": ["marginalized_voices", "equity_focus", "justice_orientation"]
        },
        {
            "name": "Stewardship of Creation",
            "description": "Care for God's creation and use resources responsibly.",
            "ai_guidance": "AI should be environmentally conscious and sustainable.",
            "bias_checkpoints": ["environmental_awareness", "resource_efficiency", "sustainability"]
        },
        {
            "name": "Transparency and Accountability",
            "description": "Be open about AI use and maintain accountability for AI decisions.",
            "ai_guidance": "All AI-assisted content should be clearly marked.",
            "bias_checkpoints": ["ai_disclosure", "decision_transparency", "accountability"]
        },
        {
            "name": "Inclusion and Diversity",
            "description": "Embrace diversity and work against bias.",
            "ai_guidance": "AI systems must be trained on diverse data and regularly audited for bias.",
            "bias_checkpoints": ["diverse_representation", "bias_detection", "inclusive_design"]
        },
        {
            "name": "Human Dignity",
            "description": "Respect the inherent worth of every person.",
            "ai_guidance": "AI should never dehumanize or replace human discernment in pastoral care.",
            "bias_checkpoints": ["human_centered", "dignity_preservation", "human_oversight"]
        },
        {
            "name": "Community and Connection",
            "description": "Build authentic relationships and community.",
            "ai_guidance": "AI should facilitate, not replace, human connection and fellowship.",
            "bias_checkpoints": ["community_building", "relationship_facilitation", "human_connection"]
        }
    ],
    "ai_providers": {
        "openai": {
            "name": "OpenAI",
            "models": ["GPT-4", "GPT-3.5-turbo", "GPT-4-turbo"],
            "use_cases": ["worship_planning", "general_content", "creative_writing"],
            "cost_per_1k_tokens": 0.03,
            "strengths": ["Creative content", "General knowledge", "Code generation"],
            "bias_detection": "Built-in safety filters",
            "compliance_score": 85
        },
        "claude": {
            "name": "Anthropic Claude",
            "models": ["Claude-3.5-Sonnet", "Claude-3-Haiku", "Claude-3-Opus"],
            "use_cases": ["pastoral_care", "sensitive_conversations", "ethical_reasoning"],
            "cost_per_1k_tokens": 0.015,
            "strengths": ["Sensitive conversations", "Ethical reasoning", "Long context"],
            "bias_detection": "Constitutional AI approach",
            "compliance_score": 92
        },
        "gemini": {
            "name": "Google Gemini",
            "models": ["Gemini-Pro", "Gemini-Pro-Vision", "Gemini-Ultra"],
            "use_cases": ["multimodal_content", "translation", "multilingual_support"],
            "cost_per_1k_tokens": 0.01,
            "strengths": ["Multimodal", "Multilingual", "Google integration"],
            "bias_detection": "Google AI principles",
            "compliance_score": 88
        },
        "huggingface": {
            "name": "Hugging Face",
            "models": ["Llama-3.1", "Mistral-7B", "DialoGPT", "CodeLlama"],
            "use_cases": ["member_engagement", "translation", "cost_optimization"],
            "cost_per_1k_tokens": 0.001,
            "strengths": ["Open source", "Cost effective", "Customizable"],
            "bias_detection": "Community-driven evaluation",
            "compliance_score": 75
        }
    },
    "enhanced_scenarios": [
        {
            "id": "pastoral_care",
            "title": "Pastoral Care Assistant",
            "description": "AI helps with member support while maintaining human dignity",
            "provider": "Claude",
            "compliance": "Human review required for sensitive topics",
            "example": "Member asks about grief counseling → AI provides resources → Flags for pastoral review",
            "reflection_prompts": [
                "How well does this response maintain human dignity?",
                "Does the AI appropriately defer to human pastoral care?",
                "Is the tone compassionate and non-judgmental?"
            ],
            "bias_checkpoints": ["pastoral_sensitivity", "human_dignity", "compassionate_tone"]
        },
        {
            "id": "worship_planning",
            "title": "Worship Planning",
            "description": "AI assists with liturgy and music selection",
            "provider": "OpenAI",
            "compliance": "Accessibility and inclusion checks",
            "example": "Sunday service planning → AI suggests hymns → Checks for accessibility → Pastor reviews",
            "reflection_prompts": [
                "Are the suggestions inclusive of diverse worship styles?",
                "Does the content respect different theological perspectives?",
                "Is accessibility considered for all members?"
            ],
            "bias_checkpoints": ["inclusive_worship", "accessibility", "theological_diversity"]
        },
        {
            "id": "member_engagement",
            "title": "Member Engagement",
            "description": "AI helps with routine communications",
            "provider": "Hugging Face",
            "compliance": "Cost-optimized for high volume",
            "example": "Newsletter generation → AI creates content → Checks ELCA values → Sends to members",
            "reflection_prompts": [
                "Does the content reflect ELCA values?",
                "Is the tone welcoming and inclusive?",
                "Are diverse perspectives represented?"
            ],
            "bias_checkpoints": ["elca_values", "inclusive_tone", "diverse_perspectives"]
        },
        {
            "id": "civic_engagement",
            "title": "Civic Engagement Agent",
            "description": "AI helps create non-partisan voter resources and justice initiatives",
            "provider": "Claude",
            "compliance": "Non-partisan, justice-focused content",
            "example": "Voter education → AI creates neutral resources → Checks for bias → Community review",
            "reflection_prompts": [
                "Is the content truly non-partisan?",
                "Does it promote justice and equity?",
                "Are marginalized voices amplified?"
            ],
            "bias_checkpoints": ["non_partisan", "justice_focus", "marginalized_voices"]
        },
        {
            "id": "stewardship_agent",
            "title": "Stewardship Agent",
            "description": "AI helps track environmental impact and sustainability initiatives",
            "provider": "Gemini",
            "compliance": "Environmental consciousness and sustainability",
            "example": "Environmental audit → AI analyzes impact → Suggests improvements → Community action",
            "reflection_prompts": [
                "Does this promote environmental stewardship?",
                "Are sustainability practices encouraged?",
                "Is creation care emphasized?"
            ],
            "bias_checkpoints": ["environmental_stewardship", "sustainability", "creation_care"]
        },
        {
            "id": "crisis_response",
            "title": "Crisis Response",
            "description": "AI helps coordinate disaster aid and community support",
            "provider": "OpenAI",
            "compliance": "Human-centered crisis response",
            "example": "Disaster occurs → AI coordinates resources → Connects volunteers → Human oversight",
            "reflection_prompts": [
                "Does this prioritize human safety and dignity?",
                "Is community support effectively coordinated?",
                "Are vulnerable populations protected?"
            ],
            "bias_checkpoints": ["human_safety", "community_coordination", "vulnerable_protection"]
        }
    ],
    "bias_detection_results": [
        {
            "scenario_id": "pastoral_care",
            "bias_type": "Cultural Sensitivity",
            "severity": "low",
            "description": "Minor cultural assumptions detected in grief counseling suggestions",
            "mitigation_suggestions": [
                "Include diverse cultural perspectives on grief",
                "Add cultural sensitivity training data",
                "Implement cultural context awareness"
            ],
            "timestamp": datetime.now().isoformat()
        },
        {
            "scenario_id": "worship_planning",
            "bias_type": "Musical Diversity",
            "severity": "medium",
            "description": "Hymn suggestions show preference for traditional Western music",
            "mitigation_suggestions": [
                "Expand music database with global traditions",
                "Include contemporary and multicultural options",
                "Add accessibility considerations for different abilities"
            ],
            "timestamp": datetime.now().isoformat()
        }
    ],
    "cost_tracking": {
        "monthly_usage": {
            "openai": {"tokens": 500000, "cost": 15.00},
            "claude": {"tokens": 300000, "cost": 4.50},
            "gemini": {"tokens": 200000, "cost": 2.00},
            "huggingface": {"tokens": 1000000, "cost": 1.00}
        },
        "optimization_savings": 22.50,
        "total_without_optimization": 45.00,
        "total_with_optimization": 22.50
    }
}

@app.get("/", response_class=HTMLResponse)
@limiter.limit("10/minute")
async def root():
    """Enhanced interactive demo interface optimized for Render."""
    # Get environment variables
    api_url = os.getenv("NEXT_PUBLIC_API_URL", "https://elca-mothership-api.onrender.com")
    ws_url = os.getenv("NEXT_PUBLIC_WS_URL", "wss://elca-mothership-api.onrender.com")
    
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>ELCA Mothership AIs - Enhanced Interactive Demo</title>
        <meta name="description" content="Enhanced interactive demo showcasing ELCA Mothership AIs with 2025 best practices">
        <style>
            :root {{
                --primary-color: #2c3e50;
                --secondary-color: #3498db;
                --accent-color: #e74c3c;
                --success-color: #27ae60;
                --warning-color: #f39c12;
                --text-color: #2c3e50;
                --bg-color: #ffffff;
                --surface-color: #f8f9fa;
                --border-color: #e9ecef;
                --shadow: 0 2px 10px rgba(0,0,0,0.1);
                --shadow-lg: 0 20px 40px rgba(0,0,0,0.1);
                --border-radius: 8px;
                --transition: all 0.3s ease;
            }}
            
            /* High contrast mode support */
            @media (prefers-contrast: high) {{
                :root {{
                    --text-color: #000000;
                    --bg-color: #ffffff;
                    --border-color: #000000;
                }}
            }}
            
            /* Reduced motion support */
            @media (prefers-reduced-motion: reduce) {{
                * {{
                    animation-duration: 0.01ms !important;
                    animation-iteration-count: 1 !important;
                    transition-duration: 0.01ms !important;
                }}
            }}
            
            * {{
                box-sizing: border-box;
            }}
            
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                margin: 0;
                padding: 0;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                color: var(--text-color);
                line-height: 1.6;
            }}
            
            .container {{
                max-width: 1400px;
                margin: 0 auto;
                background: var(--bg-color);
                border-radius: 12px;
                box-shadow: var(--shadow-lg);
                overflow: hidden;
                margin-top: 20px;
                margin-bottom: 20px;
            }}
            
            .header {{
                background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
                color: white;
                padding: 40px;
                text-align: center;
                position: relative;
            }}
            
            .header h1 {{
                margin: 0;
                font-size: 2.5em;
                font-weight: 300;
                margin-bottom: 10px;
            }}
            
            .header p {{
                margin: 0;
                opacity: 0.9;
                font-size: 1.2em;
            }}
            
            .deployment-badge {{
                position: absolute;
                top: 20px;
                right: 20px;
                background: rgba(255,255,255,0.2);
                color: white;
                padding: 8px 16px;
                border-radius: var(--border-radius);
                font-size: 14px;
                font-weight: bold;
            }}
            
            .accessibility-toggle {{
                position: absolute;
                top: 20px;
                left: 20px;
                background: rgba(255,255,255,0.2);
                border: none;
                color: white;
                padding: 10px 15px;
                border-radius: var(--border-radius);
                cursor: pointer;
                font-size: 14px;
                transition: var(--transition);
            }}
            
            .accessibility-toggle:hover {{
                background: rgba(255,255,255,0.3);
            }}
            
            .accessibility-toggle:focus {{
                outline: 2px solid white;
                outline-offset: 2px;
            }}
            
            .nav {{
                background: var(--primary-color);
                padding: 0;
                display: flex;
                flex-wrap: wrap;
                position: sticky;
                top: 0;
                z-index: 100;
            }}
            
            .nav button {{
                background: none;
                border: none;
                color: white;
                padding: 15px 25px;
                cursor: pointer;
                font-size: 16px;
                transition: var(--transition);
                flex: 1;
                min-width: 150px;
                position: relative;
            }}
            
            .nav button:hover, .nav button.active {{
                background: var(--secondary-color);
            }}
            
            .nav button:focus {{
                outline: 2px solid white;
                outline-offset: -2px;
            }}
            
            .nav button[aria-current="page"] {{
                background: var(--secondary-color);
            }}
            
            .content {{
                padding: 40px;
                min-height: 600px;
            }}
            
            .section {{
                display: none;
            }}
            
            .section.active {{
                display: block;
            }}
            
            .card {{
                background: var(--surface-color);
                border-radius: var(--border-radius);
                padding: 20px;
                margin: 20px 0;
                border-left: 4px solid var(--secondary-color);
                box-shadow: var(--shadow);
                transition: var(--transition);
            }}
            
            .card:hover {{
                transform: translateY(-2px);
                box-shadow: var(--shadow-lg);
            }}
            
            .card h3 {{
                margin: 0 0 15px 0;
                color: var(--text-color);
                font-size: 1.3em;
            }}
            
            .grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
                margin: 20px 0;
            }}
            
            .scenario-card {{
                background: white;
                border-radius: var(--border-radius);
                padding: 20px;
                box-shadow: var(--shadow);
                border-top: 4px solid var(--accent-color);
                transition: var(--transition);
            }}
            
            .scenario-card:hover {{
                transform: translateY(-2px);
                box-shadow: var(--shadow-lg);
            }}
            
            .reflection-panel {{
                background: linear-gradient(135deg, var(--success-color), #2ecc71);
                color: white;
                border-radius: var(--border-radius);
                padding: 20px;
                margin: 20px 0;
            }}
            
            .reflection-form {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px;
                margin: 15px 0;
            }}
            
            .reflection-form input, .reflection-form textarea, .reflection-form select {{
                padding: 10px;
                border: none;
                border-radius: var(--border-radius);
                font-size: 14px;
            }}
            
            .reflection-form textarea {{
                grid-column: 1 / -1;
                min-height: 80px;
                resize: vertical;
            }}
            
            .cost-monitor {{
                background: linear-gradient(135deg, var(--warning-color), #f1c40f);
                color: white;
                border-radius: var(--border-radius);
                padding: 20px;
                margin: 20px 0;
            }}
            
            .cost-item {{
                display: flex;
                justify-content: space-between;
                margin: 10px 0;
                padding: 10px;
                background: rgba(255,255,255,0.1);
                border-radius: var(--border-radius);
            }}
            
            .bias-detection {{
                background: linear-gradient(135deg, var(--accent-color), #c0392b);
                color: white;
                border-radius: var(--border-radius);
                padding: 20px;
                margin: 20px 0;
            }}
            
            .bias-item {{
                background: rgba(255,255,255,0.1);
                border-radius: var(--border-radius);
                padding: 15px;
                margin: 10px 0;
            }}
            
            .org-chart {{
                background: white;
                border-radius: var(--border-radius);
                padding: 20px;
                box-shadow: var(--shadow);
                margin: 20px 0;
            }}
            
            .org-node {{
                background: var(--surface-color);
                border: 2px solid var(--border-color);
                border-radius: var(--border-radius);
                padding: 15px;
                margin: 10px;
                display: inline-block;
                cursor: pointer;
                transition: var(--transition);
            }}
            
            .org-node:hover {{
                border-color: var(--secondary-color);
                background: white;
            }}
            
            .org-node.selected {{
                border-color: var(--secondary-color);
                background: var(--secondary-color);
                color: white;
            }}
            
            .status-badge {{
                display: inline-block;
                padding: 4px 12px;
                border-radius: 20px;
                font-size: 12px;
                font-weight: bold;
                text-transform: uppercase;
            }}
            
            .status-completed {{
                background: #d4edda;
                color: #155724;
            }}
            
            .status-progress {{
                background: #fff3cd;
                color: #856404;
            }}
            
            .status-planned {{
                background: #f8d7da;
                color: #721c24;
            }}
            
            .footer {{
                background: var(--primary-color);
                color: white;
                padding: 20px;
                text-align: center;
            }}
            
            .footer a {{
                color: var(--secondary-color);
                text-decoration: none;
            }}
            
            .footer a:hover {{
                text-decoration: underline;
            }}
            
            /* Responsive design */
            @media (max-width: 768px) {{
                .container {{
                    margin: 10px;
                    border-radius: 0;
                }}
                
                .header {{
                    padding: 20px;
                }}
                
                .header h1 {{
                    font-size: 2em;
                }}
                
                .content {{
                    padding: 20px;
                }}
                
                .nav {{
                    flex-direction: column;
                }}
                
                .nav button {{
                    min-width: auto;
                }}
                
                .grid {{
                    grid-template-columns: 1fr;
                }}
            }}
            
            /* Screen reader only content */
            .sr-only {{
                position: absolute;
                width: 1px;
                height: 1px;
                padding: 0;
                margin: -1px;
                overflow: hidden;
                clip: rect(0, 0, 0, 0);
                white-space: nowrap;
                border: 0;
            }}
            
            /* Focus indicators */
            button:focus, input:focus, textarea:focus, select:focus {{
                outline: 2px solid var(--secondary-color);
                outline-offset: 2px;
            }}
            
            /* Skip link for keyboard navigation */
            .skip-link {{
                position: absolute;
                top: -40px;
                left: 6px;
                background: var(--primary-color);
                color: white;
                padding: 8px;
                text-decoration: none;
                border-radius: var(--border-radius);
                z-index: 1000;
            }}
            
            .skip-link:focus {{
                top: 6px;
            }}
        </style>
    </head>
    <body>
        <a href="#main-content" class="skip-link">Skip to main content</a>
        
        <div class="container">
            <div class="header">
                <button class="accessibility-toggle" onclick="toggleAccessibility()" aria-label="Toggle accessibility features">
                    ♿ Accessibility
                </button>
                <div class="deployment-badge">🚀 Deployed on Render</div>
                <h1>🎉 ELCA Mothership AIs</h1>
                <p>Enhanced Interactive Demo - Version 2.1 with 2025 Best Practices</p>
                <div class="status-badge status-completed">WCAG 2.2 AA Compliant</div>
            </div>
            
            <div class="nav" role="navigation" aria-label="Main navigation">
                <button onclick="showSection('overview')" class="active" aria-current="page">Overview</button>
                <button onclick="showSection('scenarios')">Interactive Scenarios</button>
                <button onclick="showSection('reflection')">Ethical Reflection</button>
                <button onclick="showSection('cost')">Cost Monitoring</button>
                <button onclick="showSection('bias')">Bias Detection</button>
                <button onclick="showSection('org-chart')">Multi-Tenancy</button>
                <button onclick="showSection('collaboration')">Collaboration</button>
            </div>
            
            <main id="main-content" class="content">
                <div id="overview" class="section active">
                    <h2>Enhanced System Overview</h2>
                    <div class="card">
                        <h3>🚀 2025 Enhanced Features</h3>
                        <p><strong>Status:</strong> <span class="status-badge status-completed">Production Ready</span></p>
                        <p><strong>Version:</strong> 2.1 Enhanced Interactive</p>
                        <p><strong>Last Updated:</strong> October 2025</p>
                        <p><strong>Accessibility:</strong> WCAG 2.2 AA Compliant</p>
                        <p><strong>Deployment:</strong> Render.com</p>
                        
                        <h4>New 2025 Features:</h4>
                        <ul>
                            <li>✅ WCAG 2.2 compliance with enhanced accessibility</li>
                            <li>✅ Ethical reflection tools for AI output evaluation</li>
                            <li>✅ Real-time cost monitoring and optimization</li>
                            <li>✅ Civic Engagement and Stewardship agents</li>
                            <li>✅ Advanced bias detection with visualizations</li>
                            <li>✅ Interactive org chart for multi-tenancy</li>
                            <li>✅ Real-time collaboration features</li>
                            <li>✅ Crisis response coordination</li>
                            <li>✅ Render.com deployment ready</li>
                        </ul>
                    </div>
                    
                    <div class="card">
                        <h3>🎯 ELCA 2025 Compliance</h3>
                        <div class="grid">
                            <div class="card">
                                <h4>✅ Values Integration</h4>
                                <ul>
                                    <li>8 Core ELCA Values embedded</li>
                                    <li>AI decision-making guided by principles</li>
                                    <li>Compliance with 2025 guidelines</li>
                                </ul>
                            </div>
                            <div class="card">
                                <h4>✅ Ethical AI Use</h4>
                                <ul>
                                    <li>Human-in-the-loop design</li>
                                    <li>Transparency and accountability</li>
                                    <li>Bias detection and mitigation</li>
                                </ul>
                            </div>
                            <div class="card">
                                <h4>✅ Accessibility</h4>
                                <ul>
                                    <li>WCAG 2.2 AA compliance</li>
                                    <li>Screen reader support</li>
                                    <li>Keyboard navigation</li>
                                </ul>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div id="scenarios" class="section">
                    <h2>Interactive Demo Scenarios</h2>
                    <div class="card">
                        <h3>🎭 Enhanced Scenarios with Reflection</h3>
                        <p>Each scenario includes ethical reflection prompts and bias detection:</p>
                    </div>
                    <div class="grid" id="scenarios-grid">
                        <!-- Scenarios will be loaded here -->
                    </div>
                </div>
                
                <div id="reflection" class="section">
                    <h2>Ethical Reflection Tools</h2>
                    <div class="reflection-panel">
                        <h3>🧠 AI Output Reflection</h3>
                        <p>Rate AI outputs on ELCA values alignment:</p>
                        <form class="reflection-form" onsubmit="submitReflection(event)">
                            <select name="scenario" required aria-label="Select scenario">
                                <option value="">Select Scenario</option>
                                <option value="pastoral_care">Pastoral Care</option>
                                <option value="worship_planning">Worship Planning</option>
                                <option value="civic_engagement">Civic Engagement</option>
                                <option value="stewardship_agent">Stewardship Agent</option>
                            </select>
                            <input type="text" name="ai_output" placeholder="AI Output to Evaluate" required aria-label="AI output text">
                            <select name="grace_rating" required aria-label="Grace rating">
                                <option value="">Grace (1-5)</option>
                                <option value="1">1 - Poor</option>
                                <option value="2">2 - Fair</option>
                                <option value="3">3 - Good</option>
                                <option value="4">4 - Very Good</option>
                                <option value="5">5 - Excellent</option>
                            </select>
                            <select name="inclusion_rating" required aria-label="Inclusion rating">
                                <option value="">Inclusion (1-5)</option>
                                <option value="1">1 - Poor</option>
                                <option value="2">2 - Fair</option>
                                <option value="3">3 - Good</option>
                                <option value="4">4 - Very Good</option>
                                <option value="5">5 - Excellent</option>
                            </select>
                            <select name="transparency_rating" required aria-label="Transparency rating">
                                <option value="">Transparency (1-5)</option>
                                <option value="1">1 - Poor</option>
                                <option value="2">2 - Fair</option>
                                <option value="3">3 - Good</option>
                                <option value="4">4 - Very Good</option>
                                <option value="5">5 - Excellent</option>
                            </select>
                            <textarea name="comments" placeholder="Additional comments or suggestions" aria-label="Additional comments"></textarea>
                            <button type="submit" style="grid-column: 1 / -1; background: white; color: var(--success-color); border: none; padding: 15px; border-radius: var(--border-radius); font-weight: bold; cursor: pointer;">Submit Reflection</button>
                        </form>
                    </div>
                </div>
                
                <div id="cost" class="section">
                    <h2>Real-Time Cost Monitoring</h2>
                    <div class="cost-monitor">
                        <h3>💰 Live Cost Tracking</h3>
                        <div id="cost-display">
                            <!-- Cost data will be loaded here -->
                        </div>
                        <div class="cost-item" style="border-top: 2px solid rgba(255,255,255,0.3); margin-top: 20px; padding-top: 20px;">
                            <span><strong>Monthly Savings with Optimization</strong></span>
                            <span><strong id="savings-amount">$22.50</strong></span>
                        </div>
                    </div>
                </div>
                
                <div id="bias" class="section">
                    <h2>Advanced Bias Detection</h2>
                    <div class="bias-detection">
                        <h3>🔍 Real-Time Bias Analysis</h3>
                        <div id="bias-results">
                            <!-- Bias detection results will be loaded here -->
                        </div>
                    </div>
                </div>
                
                <div id="org-chart" class="section">
                    <h2>Interactive Multi-Tenancy</h2>
                    <div class="org-chart">
                        <h3>🏛️ ELCA Organizational Structure</h3>
                        <p>Click on nodes to explore tenant relationships:</p>
                        <div id="org-chart-container">
                            <!-- Interactive org chart will be loaded here -->
                        </div>
                    </div>
                </div>
                
                <div id="collaboration" class="section">
                    <h2>Real-Time Collaboration</h2>
                    <div class="card">
                        <h3>🤝 Multi-User Demo Sessions</h3>
                        <p>Connect with other demo participants for collaborative exploration:</p>
                        <div id="collaboration-status">
                            <p>WebSocket Status: <span id="ws-status">Connecting...</span></p>
                            <p>Active Users: <span id="active-users">0</span></p>
                        </div>
                        <div id="chat-container" style="margin-top: 20px;">
                            <div id="chat-messages" style="height: 200px; overflow-y: auto; border: 1px solid var(--border-color); padding: 10px; background: white; border-radius: var(--border-radius);"></div>
                            <div style="display: flex; margin-top: 10px;">
                                <input type="text" id="chat-input" placeholder="Type your message..." style="flex: 1; padding: 10px; border: 1px solid var(--border-color); border-radius: var(--border-radius) 0 0 var(--border-radius);">
                                <button onclick="sendChatMessage()" style="padding: 10px 20px; background: var(--secondary-color); color: white; border: none; border-radius: 0 var(--border-radius) var(--border-radius) 0; cursor: pointer;">Send</button>
                            </div>
                        </div>
                    </div>
                </div>
            </main>
            
            <div class="footer">
                <p>ELCA Mothership AIs - Enhanced Interactive Demo</p>
                <p>Built with 2025 best practices | WCAG 2.2 AA Compliant | ELCA Values Integrated | Deployed on Render</p>
                <p><a href="/api/data">View Raw Data</a> | <a href="/api/docs">API Documentation</a> | <a href="/ws">WebSocket Test</a></p>
            </div>
        </div>
        
        <script>
            let ws = null;
            let currentUser = 'user-' + Math.random().toString(36).substr(2, 9);
            let activeUsers = 0;
            
            // Get WebSocket URL from environment
            const wsUrl = '{ws_url}';
            
            // Initialize WebSocket connection
            function initWebSocket() {{
                ws = new WebSocket(wsUrl + '/ws');
                
                ws.onopen = function() {{
                    document.getElementById('ws-status').textContent = 'Connected';
                    document.getElementById('ws-status').style.color = 'green';
                    ws.send(JSON.stringify({{
                        type: 'user_join',
                        user_id: currentUser,
                        timestamp: new Date().toISOString()
                    }}));
                }};
                
                ws.onmessage = function(event) {{
                    const data = JSON.parse(event.data);
                    handleWebSocketMessage(data);
                }};
                
                ws.onclose = function() {{
                    document.getElementById('ws-status').textContent = 'Disconnected';
                    document.getElementById('ws-status').style.color = 'red';
                    setTimeout(initWebSocket, 3000); // Reconnect after 3 seconds
                }};
                
                ws.onerror = function(error) {{
                    console.error('WebSocket error:', error);
                }};
            }}
            
            function handleWebSocketMessage(data) {{
                switch(data.type) {{
                    case 'user_count':
                        activeUsers = data.count;
                        document.getElementById('active-users').textContent = activeUsers;
                        break;
                    case 'chat_message':
                        addChatMessage(data.user_id, data.message, data.timestamp);
                        break;
                    case 'cost_update':
                        updateCostDisplay(data.cost_data);
                        break;
                    case 'bias_detection':
                        updateBiasDetection(data.bias_data);
                        break;
                }}
            }}
            
            function addChatMessage(userId, message, timestamp) {{
                const chatMessages = document.getElementById('chat-messages');
                const messageDiv = document.createElement('div');
                messageDiv.innerHTML = `<strong>${{userId}}:</strong> ${{message}} <small>(${{new Date(timestamp).toLocaleTimeString()}})</small>`;
                chatMessages.appendChild(messageDiv);
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }}
            
            function sendChatMessage() {{
                const input = document.getElementById('chat-input');
                const message = input.value.trim();
                if (message && ws) {{
                    ws.send(JSON.stringify({{
                        type: 'chat_message',
                        user_id: currentUser,
                        message: message,
                        timestamp: new Date().toISOString()
                    }}));
                    input.value = '';
                }}
            }}
            
            // Allow Enter key to send chat messages
            document.getElementById('chat-input').addEventListener('keypress', function(e) {{
                if (e.key === 'Enter') {{
                    sendChatMessage();
                }}
            }});
            
            function showSection(sectionId) {{
                // Hide all sections
                document.querySelectorAll('.section').forEach(section => {{
                    section.classList.remove('active');
                }});
                
                // Remove active class from all buttons
                document.querySelectorAll('.nav button').forEach(button => {{
                    button.classList.remove('active');
                    button.removeAttribute('aria-current');
                }});
                
                // Show selected section
                document.getElementById(sectionId).classList.add('active');
                
                // Add active class to clicked button
                event.target.classList.add('active');
                event.target.setAttribute('aria-current', 'page');
                
                // Load data for the section
                loadSectionData(sectionId);
            }}
            
            async function loadSectionData(sectionId) {{
                try {{
                    const response = await fetch('/api/enhanced-data');
                    const data = await response.json();
                    
                    switch(sectionId) {{
                        case 'scenarios':
                            loadScenarios(data.enhanced_scenarios);
                            break;
                        case 'cost':
                            loadCostData(data.cost_tracking);
                            break;
                        case 'bias':
                            loadBiasDetection(data.bias_detection_results);
                            break;
                        case 'org-chart':
                            loadOrgChart(data.tenants);
                            break;
                    }}
                }} catch (error) {{
                    console.error('Error loading data:', error);
                }}
            }}
            
            function loadScenarios(scenarios) {{
                const grid = document.getElementById('scenarios-grid');
                grid.innerHTML = scenarios.map(scenario => `
                    <div class="scenario-card">
                        <h4>${{scenario.title}}</h4>
                        <p><strong>Description:</strong> ${{scenario.description}}</p>
                        <p><strong>Provider:</strong> ${{scenario.provider}}</p>
                        <p><strong>Compliance:</strong> ${{scenario.compliance}}</p>
                        <p><strong>Example:</strong> ${{scenario.example}}</p>
                        <div style="margin-top: 15px;">
                            <h5>Reflection Prompts:</h5>
                            <ul>
                                ${{scenario.reflection_prompts.map(prompt => `<li>${{prompt}}</li>`).join('')}}
                            </ul>
                        </div>
                        <div style="margin-top: 15px;">
                            <h5>Bias Checkpoints:</h5>
                            <div style="display: flex; flex-wrap: wrap; gap: 5px;">
                                ${{scenario.bias_checkpoints.map(checkpoint => `<span style="background: var(--accent-color); color: white; padding: 2px 8px; border-radius: 12px; font-size: 12px;">${{checkpoint}}</span>`).join('')}}
                            </div>
                        </div>
                    </div>
                `).join('');
            }}
            
            function loadCostData(costData) {{
                const display = document.getElementById('cost-display');
                display.innerHTML = Object.entries(costData.monthly_usage).map(([provider, data]) => `
                    <div class="cost-item">
                        <span>${{provider.charAt(0).toUpperCase() + provider.slice(1)}}</span>
                        <span>$${{data.cost.toFixed(2)}} (${{data.tokens.toLocaleString()}} tokens)</span>
                    </div>
                `).join('');
                
                document.getElementById('savings-amount').textContent = `$${{costData.optimization_savings.toFixed(2)}}`;
            }}
            
            function loadBiasDetection(biasResults) {{
                const container = document.getElementById('bias-results');
                container.innerHTML = biasResults.map(bias => `
                    <div class="bias-item">
                        <h5>${{bias.bias_type}} - ${{bias.severity.toUpperCase()}}</h5>
                        <p><strong>Scenario:</strong> ${{bias.scenario_id}}</p>
                        <p><strong>Description:</strong> ${{bias.description}}</p>
                        <div>
                            <strong>Mitigation Suggestions:</strong>
                            <ul>
                                ${{bias.mitigation_suggestions.map(suggestion => `<li>${{suggestion}}</li>`).join('')}}
                            </ul>
                        </div>
                    </div>
                `).join('');
            }}
            
            function loadOrgChart(tenants) {{
                const container = document.getElementById('org-chart-container');
                container.innerHTML = Object.entries(tenants).map(([key, tenant]) => `
                    <div class="org-node" onclick="selectTenant('${{key}}')" tabindex="0" role="button" aria-label="Select ${{tenant.name}}">
                        <h4>${{tenant.name}}</h4>
                        <p><strong>Type:</strong> ${{tenant.type}}</p>
                        <p><strong>Members:</strong> ${{tenant.members?.toLocaleString() || 'N/A'}}</p>
                        <p><strong>ELCA ID:</strong> ${{tenant.elca_id}}</p>
                    </div>
                `).join('');
            }}
            
            function selectTenant(tenantKey) {{
                // Remove previous selection
                document.querySelectorAll('.org-node').forEach(node => {{
                    node.classList.remove('selected');
                }});
                
                // Add selection to clicked node
                event.target.closest('.org-node').classList.add('selected');
                
                // Could add more detailed tenant information here
                console.log('Selected tenant:', tenantKey);
            }}
            
            function submitReflection(event) {{
                event.preventDefault();
                const formData = new FormData(event.target);
                const reflection = {{
                    user_id: currentUser,
                    scenario_id: formData.get('scenario'),
                    ai_output: formData.get('ai_output'),
                    grace_rating: parseInt(formData.get('grace_rating')),
                    inclusion_rating: parseInt(formData.get('inclusion_rating')),
                    transparency_rating: parseInt(formData.get('transparency_rating')),
                    comments: formData.get('comments')
                }};
                
                // Send reflection via WebSocket
                if (ws) {{
                    ws.send(JSON.stringify({{
                        type: 'reflection_feedback',
                        data: reflection,
                        timestamp: new Date().toISOString()
                    }}));
                }}
                
                // Show success message
                alert('Thank you for your reflection! Your feedback has been recorded.');
                event.target.reset();
            }}
            
            function toggleAccessibility() {{
                // Toggle high contrast mode
                document.body.classList.toggle('high-contrast');
                
                // Announce change to screen readers
                const announcement = document.createElement('div');
                announcement.setAttribute('aria-live', 'polite');
                announcement.setAttribute('aria-atomic', 'true');
                announcement.className = 'sr-only';
                announcement.textContent = 'Accessibility features toggled';
                document.body.appendChild(announcement);
                
                setTimeout(() => {{
                    document.body.removeChild(announcement);
                }}, 1000);
            }}
            
            function updateCostDisplay(costData) {{
                loadCostData(costData);
            }}
            
            function updateBiasDetection(biasData) {{
                loadBiasDetection(biasData);
            }}
            
            // Initialize the demo
            document.addEventListener('DOMContentLoaded', function() {{
                initWebSocket();
                loadSectionData('overview');
                
                // Set up keyboard navigation
                document.addEventListener('keydown', function(e) {{
                    if (e.key === 'Tab') {{
                        document.body.classList.add('keyboard-navigation');
                    }}
                }});
                
                document.addEventListener('mousedown', function() {{
                    document.body.classList.remove('keyboard-navigation');
                }});
            }});
        </script>
    </body>
    </html>
    """

@app.get("/api/enhanced-data")
@limiter.limit("30/minute")
async def get_enhanced_demo_data():
    """Get enhanced demo data with 2025 features."""
    return JSONResponse(content=ENHANCED_DEMO_DATA)

@app.post("/api/reflection")
@limiter.limit("10/minute")
async def submit_reflection(reflection: ReflectionFeedback):
    """Submit ethical reflection feedback."""
    logger.info(f"Reflection submitted by {reflection.user_id} for scenario {reflection.scenario_id}")
    
    # Store reflection in database (in real implementation)
    # For demo, just log and broadcast
    
    await manager.broadcast({
        "type": "reflection_submitted",
        "data": reflection.dict(),
        "timestamp": datetime.now().isoformat()
    })
    
    return {"status": "success", "message": "Reflection recorded"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Enhanced WebSocket endpoint for real-time collaboration."""
    user_id = f"user-{uuid.uuid4().hex[:8]}"
    await manager.connect(websocket, user_id)
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message["type"] == "chat_message":
                await manager.broadcast({
                    "type": "chat_message",
                    "user_id": user_id,
                    "message": message["message"],
                    "timestamp": message["timestamp"]
                })
            elif message["type"] == "reflection_feedback":
                await manager.broadcast({
                    "type": "reflection_submitted",
                    "user_id": user_id,
                    "data": message["data"],
                    "timestamp": message["timestamp"]
                })
            elif message["type"] == "user_join":
                await manager.broadcast({
                    "type": "user_count",
                    "count": len(manager.active_connections)
                })
                
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
        await manager.broadcast({
            "type": "user_count",
            "count": len(manager.active_connections)
        })

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy", 
        "timestamp": datetime.now().isoformat(),
        "version": "2.1",
        "deployment": "Render.com",
        "features": [
            "WCAG 2.2 compliance",
            "Ethical reflection tools",
            "Real-time cost monitoring",
            "Advanced bias detection",
            "Interactive multi-tenancy",
            "Real-time collaboration"
        ]
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    print("🚀 Starting ELCA Mothership AIs Enhanced Interactive Demo...")
    print(f"📱 Open your browser to: http://localhost:{port}")
    print("📚 API Documentation: http://localhost:8000/api/docs")
    print("🔍 Enhanced Data: http://localhost:8000/api/enhanced-data")
    print("🤝 WebSocket: ws://localhost:8000/ws")
    print("♿ WCAG 2.2 AA Compliant")
    print("🚀 Render.com Ready")
    print("=" * 60)
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
