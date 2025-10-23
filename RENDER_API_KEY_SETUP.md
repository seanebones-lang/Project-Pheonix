# 🔐 Secure API Key Setup for Render

## ⚠️ IMPORTANT: Never Commit API Keys to Git!

Your Claude API key should be added directly in Render's dashboard, NOT in code files.

## 🚀 How to Add Your Claude API Key to Render

### Step 1: Go to Render Dashboard
1. Visit https://dashboard.render.com
2. Find your service: `elca-mothership-api`
3. Click on the service name

### Step 2: Add Environment Variable
1. Click on **"Environment"** in the left sidebar
2. Scroll down to **"Environment Variables"** section
3. Click **"Add Environment Variable"**

### Step 3: Enter Your API Key
```
Key:   ANTHROPIC_API_KEY
Value: [Your Claude API key starting with sk-ant-api03-...]
```

### Step 4: Save and Redeploy
1. Click **"Save Changes"**
2. Render will automatically redeploy your service (takes 2-3 minutes)
3. Your demo will now have live AI responses!

---

## ✅ What This Fixes

**Before**: "AI providers not available. Please configure API keys."

**After**: Real Claude AI responses with:
- ✅ Compassionate pastoral care guidance
- ✅ Liturgical worship planning
- ✅ Community engagement strategies
- ✅ Educational curriculum
- ✅ And all other 8 stations working live!

---

## 🔒 Security Best Practices

✅ **DO**: Add API keys in Render dashboard
✅ **DO**: Use environment variables
✅ **DO**: Keep keys in `.env` files (never commit these)

❌ **DON'T**: Commit API keys to Git
❌ **DON'T**: Share keys in public repositories
❌ **DON'T**: Hardcode keys in source files

---

## 📝 Alternative: Use .env File Locally

For local testing, create a `.env` file in the project root:

```bash
# .env (this file is in .gitignore)
ANTHROPIC_API_KEY=your_claude_api_key_here
```

Then run locally:
```bash
python3 elca_live_demo.py
```

---

## 🎯 Quick Summary

1. **Never commit API keys** ✅
2. **Add key in Render dashboard** → Environment Variables
3. **Wait 2-3 minutes** for redeploy
4. **Test your demo** → All 8 stations will have live AI!

Your presentation will have REAL AI responses showing the power of ELCA-compliant agents! 🎉
