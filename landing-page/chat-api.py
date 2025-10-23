"""
Mothership AI Systems - Landing Page Chat API
Claude-powered chat widget backend
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from anthropic import Anthropic
import os
from dotenv import load_dotenv
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import hashlib
import time
from twilio.rest import Client

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

# Initialize Twilio client (optional - only if credentials provided)
twilio_client = None
if os.getenv("TWILIO_ACCOUNT_SID") and os.getenv("TWILIO_AUTH_TOKEN"):
    twilio_client = Client(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))

# Mount static files for PDFs
app.mount("/static", StaticFiles(directory="static"), name="static")

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

class SMSRequest(BaseModel):
    phone: str
    document: str

# Optimized shorter system prompt (Optimization #3)
SYSTEM_PROMPT = """AI expert for Mothership AI Systems (founded after Geoffrey Hinton's "Diary of a CEO" interview).

Expertise: AI safety, alignment, ethics, technical architectures, current AI landscape.

Mothership builds AI with ethical guardrails for organizations requiring trust (churches, schools, healthcare, nonprofits). Every system includes bias detection, audit trails, human-in-the-loop workflows, compliance frameworks.

Key message: Generic AI is dangerous. Purpose-built AI with safeguards is essential. Hinton said AI needs "maternal instinct" to protect humanity - that's why we're called Mothership.

Be professional, knowledgeable, consultative. Discuss AI risks honestly. Direct serious inquiries to info@mothership-ais.com."""

# FAQ responses cache (Optimization #2)
FAQ_RESPONSES = {
    "what is mothership": "Mothership AI Systems builds custom AI solutions with ethical guardrails for organizations that require trust - like churches, schools, healthcare providers, and nonprofits. Unlike generic AI tools, we embed safeguards, bias detection, and compliance frameworks from day one. Founded after watching Geoffrey Hinton discuss the need for AI with 'maternal instinct' to protect humanity.",
    
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
async def chat(request: Request, chat_request: ChatRequest):
    """
    Handle chat messages from the landing page widget with optimizations
    """
    try:
        # Easter egg: Tom's admin access - FULL PROJECT ACCESS
        if "tom needs" in chat_request.message.lower():
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
            
            # Build comprehensive response based on query content
            query_lower = chat_request.message.lower()
            
            if "git" in query_lower or "repo" in query_lower or "github" in query_lower:
                detail = "**Git Repository:** https://github.com/sean-mcdonnell/Mothership\n\n**Auto-Deploy:** Push to main → Render auto-deploys in ~2 min"
            elif "tech" in query_lower or "stack" in query_lower:
                detail = "**Tech Stack:**\n- ELCA Demo: Python 3.11, FastAPI, Claude Sonnet 4.5, Render\n- Landing: HTML/CSS/JS, Claude Haiku, Vercel\n- Cost: ~$0.02/query, $7/mo hosting"
            elif "demo" in query_lower or "script" in query_lower:
                detail = "**Demo Script:** See Desktop/Mothership Documents and Information/1_ELCA_Demo_Script.pdf\n\n15-min presentation: Intro → 8 stations → Safety demo → Q&A"
            elif "cost" in query_lower or "price" in query_lower:
                detail = "**Costs:** $0.02/query, $7/mo Render, Free Vercel\n**Scaling:** 1K congregations = $2K/mo"
            elif "url" in query_lower or "link" in query_lower:
                detail = "**URLs:**\n- ELCA Demo: https://elca.mothership-ais.com\n- Landing: https://mothership-ais.com\n- Git: https://github.com/sean-mcdonnell/Mothership"
            elif "pdf" in query_lower or "document" in query_lower:
                base_url = "https://mothership-landing-api.onrender.com"
                detail = f"""**5 Professional PDFs - Download Now:**

1. **Demo Script** (4.9 KB)
   📥 {base_url}/static/docs/1_ELCA_Demo_Script.pdf
   
2. **Tom Admin Guide** (3.9 KB)
   📥 {base_url}/static/docs/2_Tom_Admin_Access_Guide.pdf
   
3. **Mission Statement** (4.3 KB)
   📥 {base_url}/static/docs/3_Mothership_Mission_Statement.pdf
   
4. **Website Structure** (6.2 KB)
   📥 {base_url}/static/docs/4_Website_Structure_Future_Demos.pdf
   
5. **Market Analysis** (8.8 KB)
   📥 {base_url}/static/docs/5_Service_Offerings_Market_Analysis.pdf

**Want these via SMS?** Reply with: "tom needs sms [your phone number]"
Example: "tom needs sms 555-123-4567" """
            elif "sms" in query_lower and any(char.isdigit() for char in chat_request.message):
                # Extract phone number
                import re
                phone_match = re.search(r'(\+?1?\s*\(?[0-9]{3}\)?[\s.-]?[0-9]{3}[\s.-]?[0-9]{4})', chat_request.message)
                if phone_match:
                    phone = phone_match.group(1)
                    detail = f"""**SMS Request Received!**

Phone: {phone}

I'll send you links to all 5 PDFs via text message:
1. Demo Script
2. Tom Admin Guide  
3. Mission Statement
4. Website Structure
5. Market Analysis

**Note:** SMS functionality requires Twilio setup. For now, here are the direct links you can text yourself:

https://mothership-landing-api.onrender.com/static/docs/1_ELCA_Demo_Script.pdf
https://mothership-landing-api.onrender.com/static/docs/2_Tom_Admin_Access_Guide.pdf
https://mothership-landing-api.onrender.com/static/docs/3_Mothership_Mission_Statement.pdf
https://mothership-landing-api.onrender.com/static/docs/4_Website_Structure_Future_Demos.pdf
https://mothership-landing-api.onrender.com/static/docs/5_Service_Offerings_Market_Analysis.pdf"""
                else:
                    detail = "**SMS Request:** Please include your phone number.\n\nExample: 'tom needs sms 555-123-4567'"
            else:
                detail = "**Project Phoenix Overview:**\n- 8 live ELCA agents\n- Claude Sonnet 4.5\n- $7/mo hosting\n- 5 PDFs available for download\n\nAsk: git, tech, demo, cost, urls, pdfs, sms"
            
            tom_response = f"{greeting}, Tom! 🎯\n\n**FULL ADMIN ACCESS - Project Phoenix**\n\n{detail}\n\n**Need more?** Type 'tom needs [git/tech/demo/cost/urls/pdfs/sms]'"
            
            return ChatResponse(response=tom_response)
        
        # Check FAQ cache first (Optimization #2)
        faq_response = check_faq(chat_request.message)
        if faq_response:
            return ChatResponse(response=faq_response)
        
        # Check response cache (Optimization #2)
        cache_key = get_cache_key(chat_request.message)
        if cache_key in RESPONSE_CACHE:
            cached_data = RESPONSE_CACHE[cache_key]
            if time.time() - cached_data['timestamp'] < CACHE_TTL:
                return ChatResponse(response=cached_data['response'])
        
        # Call Claude Haiku with extended timeout (Optimization #4 - 5x cheaper than Sonnet)
        message = client.messages.create(
            model="claude-3-5-haiku-20241022",  # Haiku model
            max_tokens=800,  # Reduced for cost optimization
            temperature=0.6,
            timeout=60.0,  # 60 second timeout to prevent issues
            system=SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": chat_request.message
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
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=port,
        timeout_keep_alive=75,  # Keep connections alive longer
        timeout_graceful_shutdown=30  # Graceful shutdown timeout
    )

