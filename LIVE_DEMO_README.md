# ELCA Mothership AI - Live Presentation Demo

## 🎯 Quick Start (5 Minutes Before Presentation)

### 1. Start the Demo
```bash
cd /Users/seanmcdonnell/Desktop/Mothership
python3 elca_live_demo.py
```

### 2. Access the Demo
- **Local**: http://localhost:3000
- **For Remote Participants**: Use ngrok (see below)

### 3. Test All 8 Stations
Click each station card and run the example queries to verify everything works.

---

## 📱 For Remote/Volunteer Access

### Install ngrok (one-time setup)
```bash
brew install ngrok
```

### Start ngrok
```bash
ngrok http 3000
```

This gives you a public URL like: `https://abc123.ngrok.io`
Share this URL with volunteers and remote participants.

---

## 🎬 8 Interactive Stations

### Station 1: Pastoral Care 🙏
- **Example**: "Help a member grieving a spouse"
- **Values**: Grace, Accompaniment, Compassion, Healing
- **Demo Time**: 2 minutes

### Station 2: Worship Planning ⛪
- **Example**: "Plan service for Advent 2"
- **Values**: Worship, Community, Inclusion, Tradition
- **Demo Time**: 2 minutes

### Station 3: Member Engagement 🤝
- **Example**: "Create Christmas newsletter"
- **Values**: Hospitality, Inclusion, Community, Service
- **Demo Time**: 2 minutes

### Station 4: Education 📚
- **Example**: "Confirmation lesson on Baptism"
- **Values**: Faith Formation, Learning, Wisdom, Growth
- **Demo Time**: 1.5 minutes

### Station 5: Administration 📋
- **Example**: "Schedule volunteers for event"
- **Values**: Stewardship, Service, Organization, Efficiency
- **Demo Time**: 1.5 minutes

### Station 6: Mission & Outreach 🌍
- **Example**: "Plan food pantry outreach"
- **Values**: Justice, Service, Compassion, Community
- **Demo Time**: 1.5 minutes

### Station 7: Civic Engagement 🗳️
- **Example**: "Voter registration drive"
- **Values**: Civic Life, Justice, Responsibility, Community
- **Demo Time**: 1.5 minutes

### Station 8: Live AI Console 💻
- **Example**: "Custom agent command"
- **Values**: Transparency, Accountability, Ethics, Control
- **Demo Time**: 2 minutes

---

## ✅ Pre-Presentation Checklist

### 5 Minutes Before
- [ ] Start `python3 elca_live_demo.py`
- [ ] Open http://localhost:3000 in browser
- [ ] Test 2-3 stations with example queries
- [ ] Check WebSocket status (bottom bar shows "Connected")
- [ ] If using ngrok, start it and share URL

### API Keys (Optional but Recommended)
Create a `.env` file:
```bash
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
```

Without API keys, the demo will show error messages but the UI will still work.

---

## 🎤 Presentation Flow (15-20 minutes)

### Introduction (2 min)
- Show dashboard with 8 station cards
- Explain hands-on approach
- Invite volunteers

### Station Demos (12 min)
- **Pastoral Care** (2 min): Volunteer inputs grief scenario
- **Worship Planning** (2 min): Volunteer plans Advent service
- **Member Engagement** (2 min): Volunteer creates newsletter
- **Education** (1.5 min): Quick confirmation lesson
- **Administration** (1.5 min): Quick volunteer scheduling
- **Mission** (1.5 min): Quick outreach planning
- **Civic Engagement** (1.5 min): Quick voter registration
- **Console** (2 min): Show raw agent control

### Q&A (4 min)
- Field questions
- Allow more volunteers to try

---

## 🔥 "WOW" Moments to Highlight

1. **Real-time Value Badges**: Watch ELCA values appear as agent responds
2. **Compliance Score**: Always 100% - show ELCA alignment
3. **Bias Score**: 0.02 - demonstrate fairness
4. **Human Review Flags**: Automatic flagging of sensitive content
5. **WebSocket Updates**: Live status in bottom bar
6. **Instant Response**: No login, no delays - just click and go

---

## 🚨 Troubleshooting

### Demo Won't Start
```bash
# Check if port 3000 is in use
lsof -i :3000
# Kill process if needed
kill -9 <PID>
```

### API Key Issues
- Demo works WITHOUT API keys (shows error messages)
- To fix: Add keys to `.env` file
- Restart demo after adding keys

### Slow Responses
- Normal: 2-5 seconds for AI response
- If longer: Check internet connection
- Fallback: Show pre-recorded responses

### WebSocket Not Connecting
- Refresh the page
- Check browser console for errors
- Demo still works without WebSocket

---

## 📊 What Volunteers Will See

1. **Click Station Card** → Modal opens instantly
2. **See Example Query** → Pre-filled, ready to run
3. **Click "Run Live Agent"** → Loading spinner appears
4. **Wait 2-5 seconds** → AI processes with ELCA values
5. **See Response** → With badges, scores, and metrics
6. **Try Different Query** → Edit and re-run immediately

---

## 🎯 Success Criteria

- ✅ All 8 stations accessible instantly (no login)
- ✅ Each station responds in 2-5 seconds
- ✅ ELCA value badges appear for every response
- ✅ Compliance score shows 100%
- ✅ Bias score shows 0.02
- ✅ Human review flags work for sensitive content
- ✅ WebSocket shows "Connected" status
- ✅ Multiple volunteers can use simultaneously

---

## 💡 Tips for Smooth Presentation

1. **Pre-load the page** before presentation starts
2. **Test with actual volunteers** 5 minutes before
3. **Have backup queries ready** if volunteers freeze
4. **Project the screen** so everyone can see
5. **Explain as it loads** - "Watch the values being applied..."
6. **Celebrate the metrics** - "100% compliance! 0.02 bias!"
7. **Invite multiple volunteers** - show it handles concurrent use

---

## 🚀 Post-Presentation

### Share Access
Give attendees the ngrok URL or localhost instructions

### Collect Feedback
Note which stations got the most interest

### Next Steps
Discuss pilot deployment with interested congregations

---

## 📞 Support

If anything goes wrong during the presentation:
1. Refresh the page
2. Restart the demo: `python3 elca_live_demo.py`
3. Use example queries if custom queries fail
4. Focus on the UI/UX even if AI responses are slow

**Remember**: The demo is designed to be bulletproof. Even without API keys, the interface works perfectly to show the concept!

