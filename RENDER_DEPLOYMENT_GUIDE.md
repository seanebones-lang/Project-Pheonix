# ELCA Mothership AIs - Render Deployment Guide

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
