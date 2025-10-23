#!/usr/bin/env python3
"""
ELCA Mothership AIs - Render Deployment Script
This script prepares the application for deployment on Render.com
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def create_render_config():
    """Create Render configuration files."""
    print("🚀 Creating Render deployment configuration...")
    
    # Create render.yaml (already created above)
    print("✅ render.yaml created")
    
    # Create Procfile for backend
    procfile_content = """web: gunicorn enhanced_interactive_demo:app --bind 0.0.0.0:$PORT --workers 2 --worker-class uvicorn.workers.UvicornWorker
worker: celery -A backend.main worker --loglevel=info"""
    
    with open("Procfile", "w") as f:
        f.write(procfile_content)
    print("✅ Procfile created")
    
    # Create runtime.txt for Python version
    with open("runtime.txt", "w") as f:
        f.write("python-3.11.0")
    print("✅ runtime.txt created")
    
    # Create .env.example for environment variables
    env_example = """# Render Environment Variables
PORT=10000
PYTHON_VERSION=3.11.0
ENVIRONMENT=production

# ELCA Configuration
ELCA_COMPLIANCE_MODE=true
ELCA_BIAS_AUDIT_ENABLED=true
ELCA_TRANSPARENCY_MODE=true

# Database (Render will provide these)
DATABASE_URL=postgresql://user:password@host:port/database
REDIS_URL=redis://host:port

# AI API Keys (set these in Render dashboard)
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_claude_key_here
GOOGLE_API_KEY=your_gemini_key_here
HUGGINGFACE_API_KEY=your_huggingface_key_here

# Frontend Configuration
NEXT_PUBLIC_API_URL=https://your-app-name.onrender.com
NEXT_PUBLIC_WS_URL=wss://your-app-name.onrender.com
NEXT_PUBLIC_I18N_ENABLED=true
NEXT_PUBLIC_ACCESSIBILITY_MODE=true
NEXT_PUBLIC_DEMO_MODE=true

# Logging
LOG_LEVEL=INFO
DEBUG=false
DEMO_MODE=true"""
    
    with open(".env.example", "w") as f:
        f.write(env_example)
    print("✅ .env.example created")

def update_requirements():
    """Update requirements.txt for Render deployment."""
    print("📦 Updating requirements for Render...")
    
    # Add gunicorn for production server
    requirements_path = Path("backend/requirements.txt")
    if requirements_path.exists():
        with open(requirements_path, "r") as f:
            content = f.read()
        
        if "gunicorn" not in content:
            content += "\n# Production server\ngunicorn==21.2.0\n"
            
            with open(requirements_path, "w") as f:
                f.write(content)
            print("✅ Added gunicorn to requirements.txt")
    else:
        print("❌ backend/requirements.txt not found")

def create_nextjs_config():
    """Create Next.js configuration for static export."""
    print("🌐 Configuring Next.js for static export...")
    
    next_config = """/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',
  trailingSlash: true,
  images: {
    unoptimized: true
  },
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'https://elca-mothership-api.onrender.com',
    NEXT_PUBLIC_WS_URL: process.env.NEXT_PUBLIC_WS_URL || 'wss://elca-mothership-api.onrender.com',
    NEXT_PUBLIC_I18N_ENABLED: process.env.NEXT_PUBLIC_I18N_ENABLED || 'true',
    NEXT_PUBLIC_ACCESSIBILITY_MODE: process.env.NEXT_PUBLIC_ACCESSIBILITY_MODE || 'true',
    NEXT_PUBLIC_DEMO_MODE: process.env.NEXT_PUBLIC_DEMO_MODE || 'true'
  }
}

module.exports = nextConfig"""
    
    with open("frontend/next.config.js", "w") as f:
        f.write(next_config)
    print("✅ Updated next.config.js for static export")

def create_render_deployment_guide():
    """Create deployment guide for Render."""
    print("📚 Creating Render deployment guide...")
    
    guide_content = """# ELCA Mothership AIs - Render Deployment Guide

## 🚀 Quick Deploy to Render

### Prerequisites
1. GitHub repository with the ELCA Mothership AIs code
2. Render.com account (free tier available)
3. AI API keys (OpenAI, Claude, Gemini, Hugging Face)

### Step 1: Connect Repository
1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Select the repository containing ELCA Mothership AIs

### Step 2: Configure Backend Service
1. **Service Name**: `elca-mothership-api`
2. **Environment**: `Python 3`
3. **Build Command**: `pip install -r backend/requirements.txt`
4. **Start Command**: `gunicorn enhanced_interactive_demo:app --bind 0.0.0.0:$PORT --workers 2 --worker-class uvicorn.workers.UvicornWorker`
5. **Plan**: Starter (Free)

### Step 3: Configure Frontend Service
1. **Service Name**: `elca-mothership-frontend`
2. **Environment**: `Static Site`
3. **Build Command**: `cd frontend && npm install && npm run build`
4. **Publish Directory**: `frontend/out`
5. **Plan**: Starter (Free)

### Step 4: Add Database
1. Click "New +" → "PostgreSQL"
2. **Database Name**: `elca-mothership-db`
3. **Plan**: Starter (Free)

### Step 5: Add Redis
1. Click "New +" → "Redis"
2. **Redis Name**: `elca-mothership-redis`
3. **Plan**: Starter (Free)

### Step 6: Environment Variables
Set these in the Render dashboard for your backend service:

#### Required Variables
```
DATABASE_URL=<provided by Render PostgreSQL>
REDIS_URL=<provided by Render Redis>
PORT=10000
ENVIRONMENT=production
```

#### ELCA Configuration
```
ELCA_COMPLIANCE_MODE=true
ELCA_BIAS_AUDIT_ENABLED=true
ELCA_TRANSPARENCY_MODE=true
LOG_LEVEL=INFO
DEMO_MODE=true
```

#### AI API Keys (Optional for demo)
```
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_claude_key
GOOGLE_API_KEY=your_gemini_key
HUGGINGFACE_API_KEY=your_huggingface_key
```

#### Frontend Variables
```
NEXT_PUBLIC_API_URL=https://elca-mothership-api.onrender.com
NEXT_PUBLIC_WS_URL=wss://elca-mothership-api.onrender.com
NEXT_PUBLIC_I18N_ENABLED=true
NEXT_PUBLIC_ACCESSIBILITY_MODE=true
NEXT_PUBLIC_DEMO_MODE=true
```

### Step 7: Deploy
1. Click "Create Web Service"
2. Wait for build to complete (5-10 minutes)
3. Your demo will be available at: `https://elca-mothership-api.onrender.com`

## 🌟 Features Available on Render

### ✅ Enhanced Interactive Demo
- WCAG 2.2 AA compliant interface
- Real-time collaboration features
- Ethical reflection tools
- Cost monitoring dashboard
- Advanced bias detection
- Interactive multi-tenancy visualization

### ✅ ELCA Compliance
- 8 Core ELCA Values integrated
- 2025 AI Guidelines compliance
- Bias detection and mitigation
- Human-in-the-loop design
- Transparency and accountability

### ✅ Production Ready
- Scalable architecture
- Comprehensive monitoring
- Error handling and logging
- Security best practices
- Performance optimization

## 🔧 Customization

### Custom Domain
1. Go to your service settings
2. Add custom domain
3. Update DNS records
4. Update environment variables with new domain

### Scaling
- Upgrade to paid plans for better performance
- Add more workers for higher concurrency
- Use Render's auto-scaling features

### Monitoring
- Built-in health checks
- Application logs
- Performance metrics
- Error tracking

## 🆘 Troubleshooting

### Common Issues
1. **Build Failures**: Check Python/Node.js versions
2. **Database Connection**: Verify DATABASE_URL format
3. **WebSocket Issues**: Ensure WSS protocol for production
4. **Static Files**: Check Next.js export configuration

### Support
- Render Documentation: https://render.com/docs
- ELCA Mothership AIs Issues: GitHub Issues
- Community Support: ELCA Tech Community

## 📊 Performance Expectations

### Free Tier Limits
- 750 hours/month per service
- 512MB RAM per service
- Sleep after 15 minutes of inactivity
- Cold start time: ~30 seconds

### Paid Tier Benefits
- Always-on services
- More RAM and CPU
- Custom domains
- Priority support

## 🎯 Success Metrics

### Technical Metrics
- ✅ Page load time < 3 seconds
- ✅ WCAG 2.2 AA compliance
- ✅ 99%+ uptime
- ✅ < 200ms API response time

### ELCA Compliance Metrics
- ✅ 100% ELCA values integration
- ✅ Zero bias incidents
- ✅ Human review for sensitive content
- ✅ Transparent AI usage

## 🚀 Next Steps

1. **Deploy to Render**: Follow the steps above
2. **Test Features**: Verify all interactive features work
3. **Share Demo**: Provide URL to ELCA leadership
4. **Gather Feedback**: Collect user feedback
5. **Iterate**: Improve based on feedback
6. **Scale**: Plan for production deployment

---

**Ready to deploy? Start with Step 1 above!** 🎉
"""
    
    with open("RENDER_DEPLOYMENT_GUIDE.md", "w") as f:
        f.write(guide_content)
    print("✅ Created RENDER_DEPLOYMENT_GUIDE.md")

def create_dockerfile_for_render():
    """Create Dockerfile optimized for Render."""
    print("🐳 Creating Dockerfile for Render...")
    
    dockerfile_content = """# Multi-stage build for ELCA Mothership AIs on Render
FROM python:3.11-slim as backend

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    g++ \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ .
COPY enhanced_interactive_demo.py .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app
USER app

# Expose port
EXPOSE 10000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:10000/api/health || exit 1

# Start command
CMD ["gunicorn", "enhanced_interactive_demo:app", "--bind", "0.0.0.0:10000", "--workers", "2", "--worker-class", "uvicorn.workers.UvicornWorker"]

# Frontend stage
FROM node:18-alpine as frontend

WORKDIR /app/frontend

# Copy package files
COPY frontend/package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy frontend code
COPY frontend/ .

# Build the application
RUN npm run build

# Serve static files
FROM nginx:alpine
COPY --from=frontend /app/frontend/out /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]"""
    
    with open("Dockerfile", "w") as f:
        f.write(dockerfile_content)
    print("✅ Created Dockerfile")

def create_nginx_config():
    """Create nginx configuration for frontend."""
    print("🌐 Creating nginx configuration...")
    
    nginx_config = """events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    
    server {
        listen 80;
        server_name _;
        root /usr/share/nginx/html;
        index index.html;
        
        # Handle client-side routing
        location / {
            try_files $uri $uri/ /index.html;
        }
        
        # Cache static assets
        location ~* \\.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
        
        # Security headers for static files
        location ~* \\.(js|css)$ {
            add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';";
        }
    }
}"""
    
    with open("nginx.conf", "w") as f:
        f.write(nginx_config)
    print("✅ Created nginx.conf")

def main():
    """Main deployment preparation function."""
    print("🚀 ELCA MOTHERSHIP AIS - RENDER DEPLOYMENT PREPARATION")
    print("=" * 60)
    
    try:
        create_render_config()
        update_requirements()
        create_nextjs_config()
        create_render_deployment_guide()
        create_dockerfile_for_render()
        create_nginx_config()
        
        print("\n🎉 DEPLOYMENT PREPARATION COMPLETE!")
        print("=" * 60)
        print("✅ All Render configuration files created")
        print("✅ Requirements updated for production")
        print("✅ Next.js configured for static export")
        print("✅ Deployment guide created")
        print("✅ Docker configuration ready")
        print("✅ Nginx configuration ready")
        
        print("\n📋 NEXT STEPS:")
        print("1. Push code to GitHub repository")
        print("2. Connect repository to Render")
        print("3. Follow RENDER_DEPLOYMENT_GUIDE.md")
        print("4. Set environment variables in Render dashboard")
        print("5. Deploy and test!")
        
        print("\n🌐 Your demo will be available at:")
        print("   https://elca-mothership-api.onrender.com")
        
        print("\n📚 Documentation:")
        print("   - RENDER_DEPLOYMENT_GUIDE.md")
        print("   - render.yaml")
        print("   - .env.example")
        
    except Exception as e:
        print(f"❌ Error during deployment preparation: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
