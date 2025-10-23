# Mothership AI Systems - Landing Page

Professional corporate landing page for mothership-ais.com

## Features

- Modern, minimalist design (black/white/grey with blue accent)
- Light/Dark mode toggle
- Geoffrey Hinton "Diary of a CEO" origin story
- Contact form for project inquiries
- Claude-powered floating chat widget
- Fully responsive design
- Professional corporate tone

## Quick Start

### Local Development

1. **Set up environment variables:**
   ```bash
   export ANTHROPIC_API_KEY="your_claude_api_key_here"
   export PORT=8080
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the backend API:**
   ```bash
   python chat-api.py
   ```

4. **Open the landing page:**
   ```bash
   open index.html
   ```
   Or serve it with a simple HTTP server:
   ```bash
   python -m http.server 8000
   ```
   Then visit: http://localhost:8000

## Deployment Options

### Option 1: Render (Recommended for Backend API)

Deploy the chat API to Render:

1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Configure:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python chat-api.py`
   - **Environment Variables:**
     - `ANTHROPIC_API_KEY`: Your Claude API key
     - `PORT`: 10000 (or leave default)

### Option 2: Vercel (Recommended for Frontend)

Deploy the static HTML to Vercel:

1. Install Vercel CLI: `npm i -g vercel`
2. Run: `vercel`
3. Follow prompts

### Option 3: IONOS (Your Domain Provider)

Upload `index.html` to your IONOS hosting:

1. Log in to IONOS
2. Go to Hosting → File Manager
3. Upload `index.html` to public_html/
4. Configure API endpoint in index.html to point to your Render backend

## Domain Setup

### Root Domain (mothership-ais.com)

1. **At IONOS:**
   - Point A record to your hosting provider's IP
   - Or add CNAME to hosting provider

2. **Upload index.html** to root directory

### API Subdomain (api.mothership-ais.com)

1. **At IONOS:**
   ```
   Type: CNAME
   Hostname: api
   Points to: your-api-service.onrender.com
   ```

2. **Update index.html:**
   Change API endpoints from `/api/chat` to `https://api.mothership-ais.com/api/chat`

## File Structure

```
landing-page/
├── index.html          # Main landing page (standalone, no dependencies)
├── chat-api.py         # Backend API for chat widget and contact form
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## Customization

### Update Geoffrey Hinton YouTube Link

In `index.html`, find:
```html
<a href="https://www.youtube.com/watch?v=example" target="_blank">
```

Replace with actual Diary of a CEO episode URL when you find it.

### Configure Email Notifications

In `chat-api.py`, add email sending logic:

```python
import smtplib
from email.mime.text import MIMEText

@app.post("/api/contact")
async def contact_form(request: ContactRequest):
    # Send email notification
    msg = MIMEText(f"New inquiry from {request.name}...")
    msg['Subject'] = 'New Mothership AI Inquiry'
    msg['From'] = 'noreply@mothership-ais.com'
    msg['To'] = 'info@mothership-ais.com'
    
    with smtplib.SMTP('smtp.your-provider.com', 587) as server:
        server.starttls()
        server.login('your-email', 'your-password')
        server.send_message(msg)
    
    return {"status": "success"}
```

### Customize Chat Widget Prompt

In `chat-api.py`, modify `SYSTEM_PROMPT` to adjust the AI assistant's behavior.

## Testing

### Test Contact Form
```bash
curl -X POST http://localhost:8080/api/contact \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "email": "test@example.com",
    "organization": "Test Org",
    "industry": "education",
    "message": "Test inquiry"
  }'
```

### Test Chat Widget
```bash
curl -X POST http://localhost:8080/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is Mothership AI?"}'
```

## Production Checklist

- [ ] Add actual Geoffrey Hinton YouTube link
- [ ] Configure email notifications for contact form
- [ ] Set up database to store inquiries
- [ ] Add Google Analytics or privacy-respecting alternative
- [ ] Configure CORS properly for production domains
- [ ] Add rate limiting to API endpoints
- [ ] Set up SSL certificate (automatic with Render/Vercel)
- [ ] Test on mobile devices
- [ ] Run accessibility audit (WCAG 2.2)
- [ ] Add privacy policy and terms of service pages
- [ ] Configure CDN for faster global delivery

## Support

For questions or issues, contact: info@mothership-ais.com

## Email Configuration

The domain supports catch-all email routing:
- `info@mothership-ais.com` - Primary contact
- `sales@mothership-ais.com` - Sales inquiries
- `support@mothership-ais.com` - Technical support
- `anything@mothership-ais.com` - All emails route to your inbox

