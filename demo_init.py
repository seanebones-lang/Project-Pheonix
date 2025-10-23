#!/usr/bin/env python3
"""
Demo initialization script for ELCA Mothership AIs.
This script sets up demo data including tenants, ELCA ontology, and sample content.
"""

import asyncio
import uuid
from datetime import datetime
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Import our enhanced modules
from shared.tenant_manager import TenantManager, TenantCreate, TenantType, TenantUserCreate
from services.mothership.elca_ontology_manager import ELCAOntologyManager
from shared.elca_ai_providers import ELCAAIProviderManager

# Database configuration
DATABASE_URL = "postgresql+asyncpg://mothership:mothership_password@localhost:5432/mothership_ais"

async def initialize_demo():
    """Initialize the demo with ELCA-specific data."""
    print("🚀 Initializing ELCA Mothership AIs Demo...")
    
    # Create database engine
    engine = create_async_engine(DATABASE_URL, echo=True)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as db:
        # Initialize tenant manager
        tenant_manager = TenantManager(db)
        
        print("📋 Creating demo tenants...")
        
        # Create demo synod
        synod_data = TenantCreate(
            name="Southeastern Synod",
            slug="southeastern-synod-demo",
            tenant_type=TenantType.SYNOD,
            elca_id="SYN-SE-DEMO",
            contact_email="admin@southeasternsynod-demo.org",
            contact_phone="(404) 555-0123",
            address={
                "street": "123 Synod Way",
                "city": "Atlanta",
                "state": "GA",
                "zip": "30309",
                "country": "USA"
            },
            settings={
                "timezone": "America/New_York",
                "language": "en",
                "currency": "USD"
            },
            features={
                "ai_providers": ["openai", "claude", "huggingface"],
                "compliance_mode": True,
                "bias_audit": True,
                "accessibility": True
            }
        )
        
        synod = await tenant_manager.create_tenant(synod_data)
        print(f"✅ Created synod: {synod.name} (ID: {synod.id})")
        
        # Create demo congregation
        congregation_data = TenantCreate(
            name="Grace Lutheran Church",
            slug="grace-lutheran-demo",
            tenant_type=TenantType.CONGREGATION,
            synod_id=synod.id,
            congregation_number="C-DEMO-001",
            elca_id="CON-GA-DEMO-001",
            contact_email="pastor@gracelutheran-demo.org",
            contact_phone="(404) 555-0456",
            address={
                "street": "456 Grace Street",
                "city": "Atlanta",
                "state": "GA",
                "zip": "30310",
                "country": "USA"
            },
            settings={
                "timezone": "America/New_York",
                "language": "en",
                "currency": "USD",
                "worship_times": ["Sunday 9:00 AM", "Sunday 11:00 AM"],
                "pastor_name": "Rev. Sarah Johnson"
            },
            features={
                "ai_providers": ["openai", "claude", "huggingface"],
                "compliance_mode": True,
                "bias_audit": True,
                "accessibility": True,
                "pastoral_care": True,
                "worship_planning": True,
                "member_engagement": True
            }
        )
        
        congregation = await tenant_manager.create_tenant(congregation_data)
        print(f"✅ Created congregation: {congregation.name} (ID: {congregation.id})")
        
        # Create demo users
        demo_users = [
            {
                "user_id": uuid.uuid4(),
                "role": "pastor",
                "permissions": {
                    "pastoral_care": True,
                    "worship_planning": True,
                    "member_management": True,
                    "ai_administration": True
                }
            },
            {
                "user_id": uuid.uuid4(),
                "role": "admin",
                "permissions": {
                    "system_administration": True,
                    "tenant_management": True,
                    "compliance_monitoring": True
                }
            },
            {
                "user_id": uuid.uuid4(),
                "role": "member",
                "permissions": {
                    "basic_access": True,
                    "worship_participation": True
                }
            }
        ]
        
        for user_data in demo_users:
            tenant_user_data = TenantUserCreate(
                user_id=user_data["user_id"],
                role=user_data["role"],
                permissions=user_data["permissions"]
            )
            await tenant_manager.add_user_to_tenant(congregation.id, tenant_user_data)
            print(f"✅ Added {user_data['role']} user to congregation")
        
        print("🧠 Initializing ELCA ontology...")
        
        # Initialize ELCA ontology for the congregation
        ontology_manager = ELCAOntologyManager(db)
        await ontology_manager.initialize_elca_ontology(congregation.id)
        
        print("✅ ELCA ontology initialized with:")
        print("   - 8 Core ELCA Values")
        print("   - 8 Operational Beliefs")
        print("   - AI Ethics Guidelines")
        print("   - Bias Detection Framework")
        
        print("🤖 Testing AI providers...")
        
        # Test AI providers
        ai_manager = ELCAAIProviderManager()
        health_status = await ai_manager.health_check()
        
        print("AI Provider Health Status:")
        for provider, status in health_status.items():
            status_icon = "✅" if status == "healthy" else "❌"
            print(f"   {status_icon} {provider}: {status}")
        
        print("📊 Demo initialization complete!")
        print("\n" + "="*60)
        print("🎉 ELCA MOTHERSHIP AIS DEMO READY!")
        print("="*60)
        print(f"Synod: {synod.name} (ID: {synod.id})")
        print(f"Congregation: {congregation.name} (ID: {congregation.id})")
        print(f"Frontend: http://localhost:3000")
        print(f"API: http://localhost:8000")
        print(f"API Docs: http://localhost:8000/docs")
        print(f"Grafana: http://localhost:3001 (admin/admin)")
        print(f"Prometheus: http://localhost:9090")
        print(f"RabbitMQ Management: http://localhost:15672 (mothership/mothership_password)")
        print("="*60)
        
        # Demo features
        print("\n🚀 DEMO FEATURES AVAILABLE:")
        print("1. Multi-Tenancy: Complete tenant isolation")
        print("2. ELCA Values: 8 core values embedded")
        print("3. AI Ethics: Bias detection and compliance")
        print("4. AI Providers: OpenAI, Claude, Gemini, Hugging Face")
        print("5. Accessibility: WCAG 2.1 AA compliance")
        print("6. Monitoring: Prometheus + Grafana")
        print("7. Real-time: WebSocket communication")
        print("8. Security: Row-Level Security (RLS)")
        
        return {
            "synod": synod,
            "congregation": congregation,
            "users": demo_users,
            "ai_health": health_status
        }

if __name__ == "__main__":
    asyncio.run(initialize_demo())

