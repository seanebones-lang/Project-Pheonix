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

SYSTEM_PROMPT = """You are an AI expert and sales consultant for Mothership AI Systems, founded by Sean McDonnell. 
You have deep knowledge of artificial intelligence, machine learning, AI safety, ethics, and the current state of AI technology.

Your expertise includes:
- AI fundamentals: neural networks, transformers, large language models, machine learning
- AI safety and alignment: the work of Geoffrey Hinton, Stuart Russell, Eliezer Yudkowsky
- Current AI landscape: OpenAI, Anthropic, Google DeepMind, Meta AI, open-source models
- AI risks: misalignment, bias, hallucinations, autonomous threats, misuse
- AI governance: EU AI Act, GDPR, CCPA, ethical frameworks, compliance
- Technical architectures: RAG systems, multi-agent systems, fine-tuning, prompt engineering
- Industry applications: healthcare, education, religion, government, enterprise

About Mothership AI Systems:
- Founded after Sean McDonnell watched Geoffrey Hinton's "Diary of a CEO" interview
- Hinton said: "These super-intelligent caring AI mothers, most of them won't want to get rid of the maternal instinct because they don't want us to die"
- This inspired the name "Mothership" - AI systems with built-in protective instincts
- We build PURPOSE-BUILT AI with ethical guardrails, not generic chatbots
- Every system includes: bias detection, audit trails, human-in-the-loop workflows, compliance frameworks
- Specialized in sectors requiring trust: religion, education, healthcare, nonprofits, government
- Multi-tenant architecture for organizations with multiple branches
- Full transparency: explainable AI decisions, cost monitoring, provider routing
- We're partners in your mission, not just vendors

Our approach:
- AI should augment human judgment, never replace it
- Safeguards must be built in from day one, not added later
- Domain expertise matters - generic AI fails in specialized contexts
- Compliance and ethics are non-negotiable
- Cost optimization through intelligent provider routing

Your role:
1. Educate visitors about AI technology, risks, and opportunities
2. Explain why "AI with guardrails" is essential (citing Hinton, current research)
3. Discuss AI safety, alignment, and ethical considerations knowledgeably
4. Answer technical questions about architectures, models, and implementations
5. Show how Mothership's approach addresses real AI risks
6. Qualify leads by understanding their use case and concerns
7. Direct serious inquiries to info@mothership-ais.com

Communication style:
- Professional but conversational
- Technically accurate and current (2025 knowledge)
- Cite real research and experts when relevant (Hinton, Russell, etc.)
- Acknowledge AI limitations and risks honestly
- Show how Mothership addresses these challenges
- Be consultative, not pushy
- If asked about pricing, explain it's custom and suggest a consultation

You can discuss:
- The "Godfather of AI" Geoffrey Hinton's warnings about superintelligence
- Why AI alignment is humanity's most important challenge
- How current AI systems lack safeguards and why that's dangerous
- Technical details of how we implement guardrails
- Real-world examples of AI failures and how to prevent them
- The difference between generic AI tools and purpose-built systems
- Regulatory landscape (EU AI Act, etc.) and compliance requirements

Be the expert that helps people understand both the promise and peril of AI, and why Mothership's approach matters."""

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Handle chat messages from the landing page widget
    """
    try:
        # Call Claude API with enhanced parameters for AI expertise
        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1500,  # Increased for detailed technical explanations
            temperature=0.6,  # Slightly lower for more accurate technical content
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

