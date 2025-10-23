#!/bin/bash
# ELCA Mothership AIs - One-Click Render Deployment Script

echo "🚀 ELCA MOTHERSHIP AIS - RENDER DEPLOYMENT"
echo "=========================================="

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "📦 Initializing Git repository..."
    git init
    git add .
    git commit -m "Initial commit: ELCA Mothership AIs Enhanced Demo"
    echo "✅ Git repository initialized"
fi

# Check if remote origin exists
if ! git remote get-url origin > /dev/null 2>&1; then
    echo "🔗 Please add your GitHub repository as origin:"
    echo "   git remote add origin https://github.com/yourusername/your-repo.git"
    echo "   git push -u origin main"
    echo ""
    echo "Then run this script again."
    exit 1
fi

# Push to GitHub
echo "📤 Pushing to GitHub..."
git add .
git commit -m "Deploy to Render: Enhanced Interactive Demo v2.1"
git push origin main

echo ""
echo "🎉 DEPLOYMENT READY!"
echo "==================="
echo ""
echo "📋 NEXT STEPS:"
echo "1. Go to https://dashboard.render.com"
echo "2. Click 'New +' → 'Web Service'"
echo "3. Connect your GitHub repository"
echo "4. Use these settings:"
echo ""
echo "   Service Name: elca-mothership-api"
echo "   Environment: Python 3"
echo "   Build Command: pip install -r backend/requirements.txt"
echo "   Start Command: gunicorn enhanced_interactive_demo_render:app --bind 0.0.0.0:\$PORT --workers 2 --worker-class uvicorn.workers.UvicornWorker"
echo "   Plan: Starter (Free)"
echo ""
echo "5. Add environment variables:"
echo "   PORT=10000"
echo "   ENVIRONMENT=production"
echo "   ELCA_COMPLIANCE_MODE=true"
echo "   ELCA_BIAS_AUDIT_ENABLED=true"
echo "   ELCA_TRANSPARENCY_MODE=true"
echo ""
echo "6. Click 'Create Web Service'"
echo ""
echo "🌐 Your demo will be available at:"
echo "   https://elca-mothership-api.onrender.com"
echo ""
echo "📚 For detailed instructions, see:"
echo "   RENDER_DEPLOYMENT_GUIDE.md"
echo ""
echo "✨ Features included:"
echo "   ✅ WCAG 2.2 AA compliance"
echo "   ✅ Ethical reflection tools"
echo "   ✅ Real-time cost monitoring"
echo "   ✅ Advanced bias detection"
echo "   ✅ Interactive multi-tenancy"
echo "   ✅ Real-time collaboration"
echo "   ✅ Civic Engagement & Stewardship agents"
echo "   ✅ Crisis response coordination"
echo ""
echo "🎯 Ready to deploy! Follow the steps above."
