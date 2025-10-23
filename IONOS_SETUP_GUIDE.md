# IONOS Domain Setup for ELCA Demo
## Quick Setup for Tomorrow's Presentation

### Step 1: Add CNAME Record in IONOS

1. **Log in to IONOS**: https://www.ionos.com/
2. **Navigate to Domains**:
   - Click "Domains & SSL" in the menu
   - Find `mothership-ais.com`
   - Click "Manage Subdomains" or "DNS"

3. **Add CNAME Record**:
   ```
   Type: CNAME
   Hostname: elca
   Points to: elca-mothership-api.onrender.com
   TTL: 3600 (or leave default)
   ```

4. **Save Changes**
   - IONOS typically propagates in 5-15 minutes
   - Can take up to 24 hours globally

### Step 2: Add Custom Domain in Render

1. **Go to Render Dashboard**: https://dashboard.render.com/
2. **Select your service**: `elca-mothership-api`
3. **Settings → Custom Domains**
4. **Click "Add Custom Domain"**
5. **Enter**: `elca.mothership-ais.com`
6. **Wait for SSL certificate** (5-10 minutes)
7. **Status will show**: ✅ Verified

### Step 3: Test Your Domain

After DNS propagates (15-30 minutes):

```bash
# Test DNS resolution
nslookup elca.mothership-ais.com

# Test HTTPS (should work)
curl -I https://elca.mothership-ais.com
```

Visit: **https://elca.mothership-ais.com**

### Troubleshooting IONOS-Specific Issues

**If CNAME doesn't work:**
- IONOS sometimes requires you to use `elca.mothership-ais.com.` (with trailing dot)
- Try removing any existing A records for `elca` subdomain
- Ensure no conflicting records exist

**If SSL fails:**
- Render auto-provisions Let's Encrypt SSL
- Wait 10 minutes after DNS propagates
- Check Render dashboard for SSL status

**IONOS DNS Propagation Check:**
```bash
dig elca.mothership-ais.com
```

Should show:
```
elca.mothership-ais.com. 3600 IN CNAME elca-mothership-api.onrender.com.
```

### Your Presentation URL Tomorrow

**Primary URL**: https://elca.mothership-ais.com

**Backup URL** (if DNS not propagated): https://elca-mothership-api.onrender.com

### Future Denominations

When ready to add more demos:

```
catholic.mothership-ais.com → CNAME → catholic-mothership-api.onrender.com
methodist.mothership-ais.com → CNAME → methodist-mothership-api.onrender.com
baptist.mothership-ais.com → CNAME → baptist-mothership-api.onrender.com
```

### Main Website (mothership-ais.com)

Your root domain can:
- Stay with IONOS hosting
- Use Vercel/Netlify for static site
- Point to a different Render service

**Do NOT point root domain to ELCA demo** - keep it for your main website!

---

## ⏰ Timeline for Tomorrow

- **NOW**: Add CNAME in IONOS (5 min)
- **NOW + 5 min**: Add custom domain in Render (2 min)
- **NOW + 15 min**: DNS propagates, SSL provisions
- **NOW + 30 min**: Test `https://elca.mothership-ais.com`
- **Tomorrow**: Present with professional branded URL! 🚀

---

**Questions? Check Render's custom domain docs**: https://render.com/docs/custom-domains

