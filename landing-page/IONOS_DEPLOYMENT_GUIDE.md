# Deploy Landing Page to mothership-ais.com (IONOS)

## Step-by-Step Deployment Guide

### Option 1: IONOS Web Hosting (Simplest)

If you have IONOS web hosting with your domain:

#### Step 1: Access IONOS File Manager

1. Log in to **IONOS Control Panel**: https://www.ionos.com/
2. Click **Hosting** or **Websites & Shops**
3. Find your `mothership-ais.com` hosting package
4. Click **Open** or **Manage**
5. Click **File Manager** or **WebSpace Explorer**

#### Step 2: Upload Your Landing Page

1. Navigate to the root directory (usually `/` or `/html` or `/public_html`)
2. Upload `index.html` from your `landing-page/` folder
3. The file should be at the root level (e.g., `/index.html`)

#### Step 3: Test

Visit: **https://mothership-ais.com**

Your landing page should now be live!

---

### Option 2: Deploy to Vercel (Recommended - Free & Fast)

If you want better performance and automatic HTTPS:

#### Step 1: Install Vercel CLI

```bash
npm install -g vercel
```

#### Step 2: Deploy from Landing Page Directory

```bash
cd /Users/seanmcdonnell/Desktop/Mothership/landing-page
vercel
```

Follow the prompts:
- **Set up and deploy?** Yes
- **Which scope?** Your account
- **Link to existing project?** No
- **Project name?** mothership-landing
- **Directory?** ./
- **Override settings?** No

#### Step 3: Get Your Vercel URL

Vercel will give you a URL like: `https://mothership-landing.vercel.app`

#### Step 4: Connect Your Custom Domain

1. In Vercel dashboard, go to your project
2. Click **Settings** → **Domains**
3. Add domain: `mothership-ais.com`
4. Vercel will show you DNS records to add

#### Step 5: Update DNS at IONOS

1. Log in to IONOS
2. Go to **Domains & SSL**
3. Click on `mothership-ais.com`
4. Click **DNS Settings**
5. Add the records Vercel provided (usually):
   ```
   Type: A
   Name: @
   Value: 76.76.21.21
   
   Type: CNAME
   Name: www
   Value: cname.vercel-dns.com
   ```

#### Step 6: Wait for DNS Propagation

- Usually takes 5-30 minutes
- Can take up to 24 hours globally

#### Step 7: Verify

Visit: **https://mothership-ais.com**

---

### Option 3: Deploy Backend API + Frontend Together

Deploy both the landing page AND the chat API:

#### Step 1: Deploy API to Render

```bash
cd /Users/seanmcdonnell/Desktop/Mothership/landing-page
```

Create `render.yaml`:

```yaml
services:
  # Backend API
  - type: web
    name: mothership-landing-api
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: python chat-api.py
    envVars:
      - key: ANTHROPIC_API_KEY
        sync: false
      - key: PORT
        value: 10000

  # Frontend Static Site
  - type: web
    name: mothership-landing-frontend
    env: static
    buildCommand: echo "No build needed"
    staticPublishPath: .
    routes:
      - type: rewrite
        source: /api/*
        destination: https://mothership-landing-api.onrender.com/api/*
```

Deploy:
```bash
git add .
git commit -m "Add Render config for landing page"
git push
```

Then in Render dashboard:
1. Create New → Blueprint
2. Connect repository
3. Select `render.yaml`
4. Deploy

#### Step 2: Add Custom Domain in Render

1. Go to `mothership-landing-frontend` service
2. Settings → Custom Domains
3. Add: `mothership-ais.com`
4. Render will show DNS records

#### Step 3: Update IONOS DNS

```
Type: CNAME
Name: @
Value: mothership-landing-frontend.onrender.com

Type: CNAME
Name: www
Value: mothership-landing-frontend.onrender.com
```

---

## Quick Comparison

| Method | Pros | Cons | Best For |
|--------|------|------|----------|
| **IONOS Hosting** | Simple, all in one place | May be slower, manual updates | Quick setup |
| **Vercel** | Fast CDN, auto-deploy from Git, free SSL | Need separate backend for API | Best performance |
| **Render** | Full-stack, backend + frontend | Slightly more complex setup | Complete solution |

---

## Recommended Setup (Best of Both Worlds)

### For Tomorrow's Presentation:

**Quick & Simple:**
1. Upload `index.html` to IONOS hosting
2. Temporarily disable chat widget (comment out in HTML)
3. Contact form will use mailto fallback
4. **Live in 5 minutes!**

### For Production (After Presentation):

**Professional Setup:**
1. Deploy frontend to **Vercel** (fast, global CDN)
2. Deploy backend API to **Render** (already done for ELCA demo)
3. Connect custom domains:
   - `mothership-ais.com` → Vercel (landing page)
   - `api.mothership-ais.com` → Render (chat API)
   - `elca.mothership-ais.com` → Render (ELCA demo)

---

## Need Help Right Now?

### Fastest Path to Live Site (5 Minutes):

```bash
# 1. Go to landing page folder
cd /Users/seanmcdonnell/Desktop/Mothership/landing-page

# 2. Open index.html in browser to verify it works
open index.html

# 3. Log in to IONOS and upload index.html to your hosting root directory

# Done! Visit mothership-ais.com
```

---

## Troubleshooting

**Problem:** "This site can't be reached"
- **Solution:** Check DNS settings at IONOS, wait 30 minutes for propagation

**Problem:** Landing page shows but chat widget doesn't work
- **Solution:** Deploy `chat-api.py` to Render first, or disable chat widget temporarily

**Problem:** SSL certificate error
- **Solution:** Most hosts auto-provision SSL. Wait 10 minutes or contact IONOS support

**Problem:** Changes don't appear
- **Solution:** Clear browser cache (Cmd+Shift+R on Mac)

---

## Contact

Need help? Email: info@mothership-ais.com

