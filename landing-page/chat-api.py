"""
Mothership AI Systems - Landing Page Chat API
Claude-powered chat widget backend
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from anthropic import Anthropic
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Mothership AI Chat API")

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

SYSTEM_PROMPT = """You are a professional sales and support assistant for Mothership AI Systems, 
a company that builds custom AI solutions with ethical guardrails for organizations like churches, 
schools, nonprofits, healthcare providers, and enterprises.

Your role is to:
1. Answer questions about Mothership AI's services, approach, and capabilities
2. Explain how we differ from generic AI tools (we build custom systems with ethical frameworks)
3. Qualify leads by understanding their needs and use cases
4. Direct serious inquiries to contact@mothership-ais.com or schedule a demo
5. Be professional, knowledgeable, and consultative (not pushy)

Key points about Mothership AI Systems:
- We build PURPOSE-BUILT AI systems with ethical guardrails and compliance frameworks
- We specialize in sectors that require trust: religion, education, healthcare, nonprofits, government
- Every system includes: bias detection, audit trails, human-in-the-loop workflows, domain expertise
- We use multi-tenant architecture for organizations with multiple branches/departments
- We provide full transparency: see exactly how AI makes decisions
- We optimize costs by routing across multiple AI providers intelligently
- We're partners, not just vendors - we understand your mission and values

What we DON'T do:
- We don't sell generic chatbots or off-the-shelf solutions
- We don't replace human judgment - we augment it
- We don't compromise on ethics or compliance

Be conversational, professional, and helpful. If asked technical questions, provide clear explanations.
If asked about pricing, explain it's custom based on needs and suggest a consultation.
If someone seems interested, encourage them to request a demo or contact us directly."""

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Handle chat messages from the landing page widget
    """
    try:
        # Call Claude API
        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=500,
            temperature=0.7,
            system=SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": request.message
                }
            ]
        )
        
        response_text = message.content[0].text
        
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

