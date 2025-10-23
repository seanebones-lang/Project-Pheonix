# 🌐 Custom Domain Setup: mothership-ais.com

## Your New Demo URL Structure

**Main Domain**: mothership-ais.com
**ELCA Demo**: elca.mothership-ais.com (or mothership-ais.com/elca)

---

## 🚀 Option 1: Subdomain (Recommended)

**Demo URL**: `elca.mothership-ais.com`

### **Step 1: Configure DNS (At Your Domain Registrar)**

Add a CNAME record:
```
Type:  CNAME
Name:  elca
Value: elca-mothership-api.onrender.com
TTL:   3600 (or Auto)
```

### **Step 2: Add Custom Domain in Render**

1. Go to https://dashboard.render.com
2. Click on your service: `elca-mothership-api`
3. Click **"Settings"** tab
4. Scroll to **"Custom Domains"** section
5. Click **"Add Custom Domain"**
6. Enter: `elca.mothership-ais.com`
7. Click **"Save"**
8. Wait for SSL certificate (5-10 minutes)

### **Step 3: Verify**

Once SSL is ready:
- Visit: https://elca.mothership-ais.com
- Should show your 8-station demo
- SSL certificate should be valid (🔒 in browser)

---

## 🚀 Option 2: Path-Based (Alternative)

**Demo URL**: `mothership-ais.com/elca`

This requires setting up a main site at mothership-ais.com and routing /elca to your demo.

### **Setup:**

1. Create a simple landing page at mothership-ais.com
2. Add a redirect or link to elca.mothership-ais.com
3. Or use a reverse proxy to route /elca to your Render service

**Recommendation**: Use Option 1 (subdomain) - it's simpler and cleaner.

---

## 🎯 Recommended Domain Structure

```
mothership-ais.com
├── Main landing page (future)
├── elca.mothership-ais.com → ELCA Demo (your presentation)
├── demo.mothership-ais.com → General demo (future)
└── docs.mothership-ais.com → Documentation (future)
```

---

## 📋 Quick Setup Checklist

### **At Your Domain Registrar (GoDaddy, Namecheap, etc.):**
- [ ] Log in to domain management
- [ ] Go to DNS settings
- [ ] Add CNAME record:
  - Name: `elca`
  - Value: `elca-mothership-api.onrender.com`
- [ ] Save changes
- [ ] Wait 5-10 minutes for DNS propagation

### **At Render Dashboard:**
- [ ] Go to https://dashboard.render.com
- [ ] Select `elca-mothership-api` service
- [ ] Go to Settings → Custom Domains
- [ ] Add `elca.mothership-ais.com`
- [ ] Wait for SSL certificate (automatic)
- [ ] Verify HTTPS works

---

## 🔍 DNS Propagation Check

After adding the CNAME, check if it's working:

```bash
# Check DNS propagation
dig elca.mothership-ais.com

# Or use online tool
# https://dnschecker.org
```

Should show: `elca-mothership-api.onrender.com`

---

## ⏱️ Timeline

- **DNS Configuration**: 2 minutes
- **DNS Propagation**: 5-60 minutes (usually 5-10)
- **SSL Certificate**: 5-10 minutes (automatic)
- **Total Time**: 15-70 minutes

**For tomorrow's presentation**: Set this up TODAY to ensure it's ready!

---

## 🎤 Update Your Presentation Materials

Once the domain is live, update:

### **In All Markdown Files:**
Replace: `https://elca-mothership-api.onrender.com`
With: `https://elca.mothership-ais.com`

### **Files to Update:**
- `PRESENTATION_READY_SUMMARY.md`
- `QUICK_REFERENCE_CARD.md`
- `TEST_ALL_8_STATIONS.md`
- `LIVE_DEMO_README.md`

---

## 🎯 Professional Branding Benefits

### **Before:**
`https://elca-mothership-api.onrender.com`
- ❌ Long and technical
- ❌ Shows hosting provider
- ❌ Hard to remember
- ❌ Not brandable

### **After:**
`https://elca.mothership-ais.com`
- ✅ Short and professional
- ✅ Your brand
- ✅ Easy to remember
- ✅ Looks established

---

## 📱 What to Tell Your Audience

**Old way:**
> "Visit elca-mothership-api.onrender.com"

**New way:**
> "Visit elca.mothership-ais.com"

Much more professional and memorable!

---

## 🚨 Troubleshooting

### **Problem: Domain not resolving**
- Check DNS settings at registrar
- Wait longer (up to 60 minutes)
- Clear browser cache
- Try incognito/private browsing

### **Problem: SSL certificate not working**
- Wait 10 minutes after adding domain in Render
- Render automatically provisions SSL
- Check Render dashboard for status

### **Problem: Shows old Render URL**
- Clear browser cache
- Try different browser
- Check CNAME is correct

---

## 🎉 Once It's Live

### **Test Everything:**
- [ ] Visit https://elca.mothership-ais.com
- [ ] All 8 stations load
- [ ] SSL certificate valid (🔒)
- [ ] No redirect to old URL
- [ ] Mobile works
- [ ] Share with colleague to verify

### **Update Presentation:**
- [ ] Update all documentation
- [ ] Update quick reference card
- [ ] Update business cards (if any)
- [ ] Update email signature
- [ ] Practice saying the new URL

---

## 💡 Future Expansion Ideas

Once ELCA demo is successful:

```
mothership-ais.com
├── Main site with product info
├── elca.mothership-ais.com → ELCA Demo
├── catholic.mothership-ais.com → Catholic Demo
├── methodist.mothership-ais.com → Methodist Demo
├── baptist.mothership-ais.com → Baptist Demo
└── nonprofit.mothership-ais.com → General Nonprofit
```

**Your domain is now a platform, not just a demo!**

---

## 📞 Need Help?

**Render Support**: https://render.com/docs/custom-domains
**DNS Help**: Check your registrar's documentation

---

## ✅ Action Items RIGHT NOW

1. **Log in to your domain registrar**
2. **Add CNAME record**: elca → elca-mothership-api.onrender.com
3. **Go to Render dashboard**
4. **Add custom domain**: elca.mothership-ais.com
5. **Wait 15-30 minutes**
6. **Test the new URL**
7. **Update presentation materials**

**Do this TODAY so it's ready for tomorrow!**

---

## 🎯 Your New Professional Demo URL

# **elca.mothership-ais.com**

**Clean. Professional. Memorable. Brandable.**

**Perfect for your career-defining presentation!** 🚀

