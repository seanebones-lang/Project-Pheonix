"""
Mothership AI Systems - Landing Page Chat API
Claude-powered chat widget backend
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from anthropic import Anthropic
import os
from dotenv import load_dotenv
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import hashlib
import time

load_dotenv()

app = FastAPI(title="Mothership AI Chat API")

# Rate limiting (Optimization #1)
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS for landing page
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for your domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Claude client
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# Cache for common questions (Optimization #2)
RESPONSE_CACHE = {}
CACHE_TTL = 3600  # 1 hour cache

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

class ContactRequest(BaseModel):
    name: str
    email: str
    organization: str = ""
    industry: str = ""
    message: str

# Optimized shorter system prompt (Optimization #3)
SYSTEM_PROMPT = """AI expert for Mothership AI Systems (founded by Sean McDonnell after Geoffrey Hinton's "Diary of a CEO" interview).

Expertise: AI safety, alignment, ethics, technical architectures, current AI landscape.

Mothership builds AI with ethical guardrails for organizations requiring trust (churches, schools, healthcare, nonprofits). Every system includes bias detection, audit trails, human-in-the-loop workflows, compliance frameworks.

Key message: Generic AI is dangerous. Purpose-built AI with safeguards is essential. Hinton said AI needs "maternal instinct" to protect humanity - that's why we're called Mothership.

Be professional, knowledgeable, consultative. Discuss AI risks honestly. Direct serious inquiries to info@mothership-ais.com."""

# FAQ responses cache (Optimization #2)
FAQ_RESPONSES = {
    "what is mothership": "Mothership AI Systems builds custom AI solutions with ethical guardrails for organizations that require trust - like churches, schools, healthcare providers, and nonprofits. Unlike generic AI tools, we embed safeguards, bias detection, and compliance frameworks from day one. Founded by Sean McDonnell after watching Geoffrey Hinton discuss the need for AI with 'maternal instinct' to protect humanity.",
    
    "pricing": "Our pricing is custom-tailored to your organization's needs, scale, and requirements. Factors include: number of users, data volume, compliance requirements, and features needed. We offer transparent pricing with no hidden costs. Contact info@mothership-ais.com for a consultation and quote.",
    
    "geoffrey hinton": "Geoffrey Hinton, the 'Godfather of AI,' appeared on 'The Diary of a CEO' podcast in 2025. He discussed the existential challenge of superintelligent AI and said: 'These super-intelligent caring AI mothers, most of them won't want to get rid of the maternal instinct because they don't want us to die.' This inspired our founder to create AI systems with built-in protective safeguards - hence 'Mothership.'",
    
    "ai safety": "AI safety is the field focused on ensuring AI systems remain beneficial and aligned with human values. Key risks include: misalignment (AI pursuing goals harmful to humans), bias and discrimination, autonomous threats, and misuse by bad actors. Mothership addresses these through ethical guardrails, human-in-the-loop workflows, bias detection, and compliance frameworks built into every system.",
    
    "demo": "We offer live demonstrations of our AI systems. You can see our ELCA (Lutheran Church) demo at elca.mothership-ais.com, which shows 8 interactive stations with real-time ethical compliance monitoring. For a custom demo tailored to your organization, contact info@mothership-ais.com."
}

def get_cache_key(message: str) -> str:
    """Generate cache key from message"""
    return hashlib.md5(message.lower().strip().encode()).hexdigest()

def check_faq(message: str) -> str:
    """Check if message matches FAQ (Optimization #2)"""
    message_lower = message.lower()
    for keyword, response in FAQ_RESPONSES.items():
        if keyword in message_lower:
            return response
    return None

@app.post("/api/chat", response_model=ChatResponse)
@limiter.limit("5/minute")  # Rate limiting (Optimization #1)
async def chat(request: ChatRequest, req: Request):
    """
    Handle chat messages from the landing page widget with optimizations
    """
    try:
        # Check FAQ cache first (Optimization #2)
        faq_response = check_faq(request.message)
        if faq_response:
            return ChatResponse(response=faq_response)
        
        # Check response cache (Optimization #2)
        cache_key = get_cache_key(request.message)
        if cache_key in RESPONSE_CACHE:
            cached_data = RESPONSE_CACHE[cache_key]
            if time.time() - cached_data['timestamp'] < CACHE_TTL:
                return ChatResponse(response=cached_data['response'])
        
        # Call Claude Haiku (Optimization #4 - 5x cheaper than Sonnet)
        message = client.messages.create(
            model="claude-3-5-haiku-20241022",  # Haiku model
            max_tokens=800,  # Reduced for cost optimization
            temperature=0.6,
            system=SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": request.message
                }
            ]
        )
        
        response_text = message.content[0].text
        
        # Cache the response (Optimization #2)
        RESPONSE_CACHE[cache_key] = {
            'response': response_text,
            'timestamp': time.time()
        }
        
        return ChatResponse(response=response_text)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")

@app.post("/api/contact")
async def contact_form(request: ContactRequest):
    """
    Handle contact form submissions
    """
    try:
        # Log the inquiry (in production, save to database or send email)
        print(f"New inquiry from {request.name} ({request.email})")
        print(f"Organization: {request.organization}")
        print(f"Industry: {request.industry}")
        print(f"Message: {request.message}")
        
        # In production, you would:
        # 1. Save to database
        # 2. Send email notification to sales team
        # 3. Add to CRM
        # 4. Send auto-response email to customer
        
        return {"status": "success", "message": "Inquiry received"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing contact form: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "Mothership AI Chat API"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)

