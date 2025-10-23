#!/usr/bin/env python3
"""
Local Demo Setup for ELCA Mothership AIs (No Docker Required)
This script sets up a local development environment using Python's built-in capabilities.
"""

import asyncio
import subprocess
import sys
import os
from pathlib import Path

def check_requirements():
    """Check if required tools are installed."""
    print("🔍 Checking requirements...")
    
    requirements = {
        "python": "python3 --version",
        "pip": "pip3 --version",
        "node": "node --version",
        "npm": "npm --version"
    }
    
    missing = []
    for tool, command in requirements.items():
        try:
            result = subprocess.run(command.split(), capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ {tool}: {result.stdout.strip()}")
            else:
                missing.append(tool)
                print(f"❌ {tool}: Not found")
        except FileNotFoundError:
            missing.append(tool)
            print(f"❌ {tool}: Not found")
    
    if missing:
        print(f"\n❌ Missing requirements: {', '.join(missing)}")
        print("Please install the missing tools and try again.")
        return False
    
    return True

def setup_backend():
    """Set up the backend environment."""
    print("\n🐍 Setting up Python backend...")
    
    backend_dir = Path("backend")
    if not backend_dir.exists():
        print("❌ Backend directory not found!")
        return False
    
    # Install Python dependencies
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "backend/requirements.txt"], check=True)
        print("✅ Python dependencies installed")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install Python dependencies: {e}")
        return False
    
    return True

def setup_frontend():
    """Set up the frontend environment."""
    print("\n🌐 Setting up Node.js frontend...")
    
    frontend_dir = Path("frontend")
    if not frontend_dir.exists():
        print("❌ Frontend directory not found!")
        return False
    
    # Install Node.js dependencies
    try:
        subprocess.run(["npm", "install"], cwd="frontend", check=True)
        print("✅ Node.js dependencies installed")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install Node.js dependencies: {e}")
        return False
    
    return True

def create_demo_config():
    """Create demo configuration files."""
    print("\n⚙️ Creating demo configuration...")
    
    # Create .env file for demo
    env_content = """# Demo Environment Configuration
DATABASE_URL=sqlite+aiosqlite:///./demo.db
REDIS_URL=redis://localhost:6379
RABBITMQ_URL=amqp://localhost:5672

# Demo AI API Keys (replace with actual keys for real demo)
OPENAI_API_KEY=demo-openai-key
ANTHROPIC_API_KEY=demo-claude-key
GOOGLE_API_KEY=demo-gemini-key
HUGGINGFACE_API_KEY=demo-huggingface-key

# ELCA Configuration
ELCA_COMPLIANCE_MODE=true
ELCA_BIAS_AUDIT_ENABLED=true
ELCA_TRANSPARENCY_MODE=true

# Frontend Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
NEXT_PUBLIC_I18N_ENABLED=true
NEXT_PUBLIC_ACCESSIBILITY_MODE=true
NEXT_PUBLIC_DEMO_MODE=true

# Demo Settings
DEMO_MODE=true
LOG_LEVEL=INFO
DEBUG=true
"""
    
    with open(".env", "w") as f:
        f.write(env_content)
    
    print("✅ Demo configuration created")
    return True

def create_demo_script():
    """Create a demo script to showcase features."""
    demo_script = '''#!/usr/bin/env python3
"""
ELCA Mothership AIs Demo Script
This script demonstrates the key features of the enhanced system.
"""

import asyncio
import json
from datetime import datetime

class MothershipDemo:
    def __init__(self):
        self.demo_data = {
            "tenants": {
                "synod": {
                    "name": "Southeastern Synod",
                    "slug": "southeastern-synod-demo",
                    "type": "synod",
                    "elca_id": "SYN-SE-DEMO"
                },
                "congregation": {
                    "name": "Grace Lutheran Church",
                    "slug": "grace-lutheran-demo",
                    "type": "congregation",
                    "elca_id": "CON-GA-DEMO-001"
                }
            },
            "elca_values": [
                "Radical Hospitality",
                "Grace-Centered Faith", 
                "Justice and Advocacy",
                "Stewardship of Creation",
                "Transparency and Accountability",
                "Inclusion and Diversity",
                "Human Dignity",
                "Community and Connection"
            ],
            "ai_providers": {
                "pastoral_care": "Claude (better for sensitive conversations)",
                "worship_planning": "OpenAI (good for creative content)",
                "member_engagement": "Hugging Face (cost-effective)",
                "translation": "Hugging Face (open-source models)"
            },
            "features": [
                "Multi-Tenancy with Row-Level Security",
                "ELCA 2025 AI Guidelines Integration",
                "AI Provider Diversification",
                "Bias Detection and Mitigation",
                "Accessibility Compliance (WCAG 2.1 AA)",
                "Real-time WebSocket Communication",
                "Comprehensive Monitoring",
                "Cost Optimization"
            ]
        }
    
    def show_welcome(self):
        """Show welcome message."""
        print("=" * 80)
        print("🎉 WELCOME TO ELCA MOTHERSHIP AIS DEMO")
        print("=" * 80)
        print("This demo showcases the enhanced Mothership AIs system with:")
        print("• ELCA-specific features and values")
        print("• Multi-tenancy for congregations and synods")
        print("• AI ethics and compliance")
        print("• Scalability for thousands of churches")
        print("=" * 80)
    
    def show_tenants(self):
        """Show tenant information."""
        print("\\n📋 MULTI-TENANCY DEMO")
        print("-" * 40)
        
        for tenant_type, tenant_info in self.demo_data["tenants"].items():
            print(f"\\n{tenant_type.upper()}:")
            for key, value in tenant_info.items():
                print(f"  {key}: {value}")
    
    def show_elca_values(self):
        """Show ELCA values integration."""
        print("\\n🧠 ELCA VALUES INTEGRATION")
        print("-" * 40)
        print("The system embeds these ELCA values throughout:")
        
        for i, value in enumerate(self.demo_data["elca_values"], 1):
            print(f"  {i}. {value}")
        
        print("\\nThese values guide AI decision-making and ensure")
        print("all AI interactions align with ELCA principles.")
    
    def show_ai_providers(self):
        """Show AI provider strategy."""
        print("\\n🤖 AI PROVIDER STRATEGY")
        print("-" * 40)
        print("Intelligent provider selection based on use case:")
        
        for use_case, provider in self.demo_data["ai_providers"].items():
            print(f"  {use_case.replace('_', ' ').title()}: {provider}")
        
        print("\\nThis ensures optimal performance and cost efficiency.")
    
    def show_features(self):
        """Show key features."""
        print("\\n🚀 KEY FEATURES")
        print("-" * 40)
        
        for i, feature in enumerate(self.demo_data["features"], 1):
            print(f"  {i}. {feature}")
    
    def show_demo_scenarios(self):
        """Show demo scenarios."""
        print("\\n🎭 DEMO SCENARIOS")
        print("-" * 40)
        
        scenarios = [
            {
                "title": "Pastoral Care Assistant",
                "description": "AI helps with member support while maintaining human dignity",
                "provider": "Claude",
                "compliance": "Human review required for sensitive topics"
            },
            {
                "title": "Worship Planning",
                "description": "AI assists with liturgy and music selection",
                "provider": "OpenAI", 
                "compliance": "Accessibility and inclusion checks"
            },
            {
                "title": "Member Engagement",
                "description": "AI helps with routine communications",
                "provider": "Hugging Face",
                "compliance": "Cost-optimized for high volume"
            },
            {
                "title": "Bias Detection",
                "description": "Regular audits ensure fair AI decisions",
                "provider": "All providers",
                "compliance": "ELCA 2025 guidelines compliance"
            }
        ]
        
        for i, scenario in enumerate(scenarios, 1):
            print(f"\\n{i}. {scenario['title']}")
            print(f"   Description: {scenario['description']}")
            print(f"   Provider: {scenario['provider']}")
            print(f"   Compliance: {scenario['compliance']}")
    
    def show_technical_specs(self):
        """Show technical specifications."""
        print("\\n⚙️ TECHNICAL SPECIFICATIONS")
        print("-" * 40)
        
        specs = {
            "Backend": "Python 3.13, FastAPI 0.119.1, SQLAlchemy 2.0.44",
            "Frontend": "Next.js 16.0.0, React 19.2.0, TypeScript 5.9.3",
            "Database": "PostgreSQL with pgvector, Row-Level Security",
            "AI/ML": "LangChain 1.0.2, OpenAI 2.6.0, Claude, Gemini, Hugging Face",
            "Monitoring": "Prometheus, Grafana, OpenTelemetry",
            "Security": "Zero-trust architecture, encryption at rest/transit",
            "Scalability": "Kubernetes, auto-scaling, multi-region support"
        }
        
        for category, spec in specs.items():
            print(f"  {category}: {spec}")
    
    def show_next_steps(self):
        """Show next steps."""
        print("\\n🎯 NEXT STEPS")
        print("-" * 40)
        print("1. Install Docker and run: docker-compose -f docker-compose.enhanced.yml up")
        print("2. Or run locally: python demo_init.py")
        print("3. Access the system:")
        print("   • Frontend: http://localhost:3000")
        print("   • API: http://localhost:8000")
        print("   • API Docs: http://localhost:8000/docs")
        print("   • Grafana: http://localhost:3001")
        print("4. Explore the features and ELCA integrations")
        print("5. Review the comprehensive documentation")
    
    def run_demo(self):
        """Run the complete demo."""
        self.show_welcome()
        self.show_tenants()
        self.show_elca_values()
        self.show_ai_providers()
        self.show_features()
        self.show_demo_scenarios()
        self.show_technical_specs()
        self.show_next_steps()
        
        print("\\n" + "=" * 80)
        print("🎉 DEMO COMPLETE!")
        print("=" * 80)
        print("The ELCA Mothership AIs system is ready for deployment")
        print("and can scale to serve thousands of congregations worldwide.")
        print("=" * 80)

if __name__ == "__main__":
    demo = MothershipDemo()
    demo.run_demo()
'''
    
    with open("demo.py", "w") as f:
        f.write(demo_script)
    
    print("✅ Demo script created")
    return True

def main():
    """Main setup function."""
    print("🚀 ELCA MOTHERSHIP AIS LOCAL DEMO SETUP")
    print("=" * 50)
    
    if not check_requirements():
        return False
    
    if not setup_backend():
        return False
    
    if not setup_frontend():
        return False
    
    if not create_demo_config():
        return False
    
    if not create_demo_script():
        return False
    
    print("\n🎉 SETUP COMPLETE!")
    print("=" * 50)
    print("✅ All requirements checked")
    print("✅ Backend dependencies installed")
    print("✅ Frontend dependencies installed")
    print("✅ Demo configuration created")
    print("✅ Demo script created")
    
    print("\n🚀 TO START THE DEMO:")
    print("1. Run the demo script: python demo.py")
    print("2. Or start the services manually:")
    print("   • Backend: cd backend && python -m uvicorn main:app --reload")
    print("   • Frontend: cd frontend && npm run dev")
    
    print("\n📚 DOCUMENTATION:")
    print("• Implementation Roadmap: ELCA Documents/Mothership_AIs_ELCA_Enhancement_Roadmap.md")
    print("• Deployment Guide: ELCA Documents/Mothership_AIs_Enhanced_Deployment_Guide.md")
    print("• Technical Specs: ELCA Documents/Mothership_AIs_Technical_Specifications.md")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)

