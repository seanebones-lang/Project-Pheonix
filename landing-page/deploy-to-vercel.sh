#!/bin/bash

# Mothership AI Landing Page - One-Click Vercel Deployment
# This script deploys your landing page to Vercel with custom domain setup

echo "🚀 Mothership AI Landing Page Deployment"
echo "=========================================="
echo ""

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null
then
    echo "📦 Installing Vercel CLI..."
    npm install -g vercel
fi

echo "✅ Vercel CLI ready"
echo ""

# Navigate to landing page directory
cd "$(dirname "$0")"

echo "📁 Current directory: $(pwd)"
echo ""

# Create vercel.json for configuration
cat > vercel.json << 'EOF'
{
  "version": 2,
  "name": "mothership-landing",
  "builds": [
    {
      "src": "index.html",
      "use": "@vercel/static"
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "https://mothership-landing-api.onrender.com/api/$1"
    },
    {
      "src": "/(.*)",
      "dest": "/$1"
    }
  ]
}
EOF

echo "✅ Created vercel.json configuration"
echo ""

# Deploy to Vercel
echo "🚀 Deploying to Vercel..."
echo ""
vercel --prod

echo ""
echo "=========================================="
echo "✅ Deployment Complete!"
echo ""
echo "Next Steps:"
echo "1. Copy the deployment URL from above"
echo "2. Go to Vercel dashboard: https://vercel.com/dashboard"
echo "3. Click on your project → Settings → Domains"
echo "4. Add custom domain: mothership-ais.com"
echo "5. Copy the DNS records Vercel provides"
echo "6. Add those records to IONOS DNS settings"
echo ""
echo "Your landing page will be live at mothership-ais.com in ~15 minutes!"
echo "=========================================="

