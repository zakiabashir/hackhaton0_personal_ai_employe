# AI Employee - All Services Setup Quick Start

## 🔗 REQUIRED CONNECTIONS

Your AI Employee needs **ALL 7 services** connected for full autonomy:

| # | Service | Status | Command to Setup |
|---|---------|--------|------------------|
| 1 | **Gmail** | 🔴 REQUIRED | `python scripts/setup_gmail_token.py` |
| 2 | **LinkedIn** | 🔴 REQUIRED | See SETUP_CONNECTIONS.md |
| 3 | **WhatsApp** | 🔴 REQUIRED | `python scripts/setup_whatsapp_session.py` |
| 4 | **Facebook** | 🔴 REQUIRED | See SETUP_CONNECTIONS.md |
| 5 | **Instagram** | 🔴 REQUIRED | See SETUP_CONNECTIONS.md |
| 6 | **Twitter/X** | 🔴 REQUIRED | See SETUP_CONNECTIONS.md |
| 7 | **Odoo** | 🔴 REQUIRED | Install Odoo + configure .env |

---

## 🚀 QUICK SETUP (5 minutes)

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
playwright install chromium
```

### Step 2: Create .env File
```bash
cp .env.example .env
notepad .env  # Edit with your credentials
```

### Step 3: Setup Gmail (1 min)
```bash
python scripts/setup_gmail_token.py
```
→ Follow prompts, get credentials, add to .env

### Step 4: Setup WhatsApp (2 min)
```bash
python scripts/setup_whatsapp_session.py
```
→ Scan QR code with your phone

### Step 5: Configure Social Media
Get API keys from:
- LinkedIn: https://www.linkedin.com/developers/
- Facebook: https://developers.facebook.com/apps/
- Instagram: Connect to Facebook Page
- Twitter: https://developer.twitter.com/en/portal

Add to .env:
```bash
LINKEDIN_ACCESS_TOKEN=your_token
FACEBOOK_PAGE_ID=your_id
FACEBOOK_ACCESS_TOKEN=your_token
INSTAGRAM_BUSINESS_ID=your_id
INSTAGRAM_ACCESS_TOKEN=your_token
TWITTER_API_KEY=your_key
TWITTER_ACCESS_TOKEN=your_token
```

### Step 6: Install Odoo (Optional - for accounting)
```bash
# Docker (easiest)
docker run -d -p 8069:8069 --name odoo odoo:17
```

### Step 7: Test All Connections
```bash
python scripts/test_all_connections.py
```

Expected output:
```
✅ Environment: Configured
✅ Gmail API: Connected
✅ LinkedIn: Ready
✅ WhatsApp: Session active
✅ Facebook: Connected
✅ Instagram: Connected
✅ Twitter: Connected
✅ Odoo: Connected
```

---

## 🎯 START AI EMPLOYEE

Once all connections are configured:

```bash
python scripts/start_all.py
```

This starts:
- ✅ Email monitoring & sending
- ✅ WhatsApp monitoring
- ✅ Social media auto-posting
- ✅ Odoo accounting
- ✅ Approval workflow
- ✅ Task processing

---

## 📋 CONNECTION CHECKLIST

Use this checklist to verify all services:

### Gmail ✅
- [ ] Client ID configured
- [ ] Client Secret configured
- [ ] Refresh Token obtained
- [ ] Test email sent successfully

### LinkedIn ✅
- [ ] Access Token OR Email+Password configured
- [ ] Profile URL correct
- [ ] Test post created in Drafts

### WhatsApp ✅
- [ ] Session file created (.whatsapp_session/)
- [ ] Phone number configured
- [ ] Can read messages

### Facebook ✅
- [ ] Page ID configured
- [ ] Access Token valid
- [ ] Can post to page

### Instagram ✅
- [ ] Business Account ID configured
- [ ] Connected to Facebook Page
- [ ] Access Token valid

### Twitter ✅
- [ ] API Key & Secret configured
- [ ] Access Token & Secret configured
- [ ] Bearer Token configured

### Odoo ✅
- [ ] Odoo installed and running
- [ ] Database created
- [ ] Username/password configured
- [ ] Can connect via API

---

## 🆘 TROUBLESHOOTING

### Gmail Issues
**Problem:** "Invalid credentials"
**Solution:** Run `python scripts/setup_gmail_token.py` again

### WhatsApp Issues
**Problem:** "Session not found"
**Solution:** Run `python scripts/setup_whatsapp_session.py` and scan QR code

### LinkedIn Issues
**Problem:** "Cannot post"
**Solution:** Get fresh Access Token from LinkedIn Developers

### Odoo Issues
**Problem:** "Connection refused"
**Solution:** Check Odoo is running: `http://localhost:8069`

---

## 📚 DETAILED GUIDES

For detailed setup instructions for each service, see:
**SETUP_CONNECTIONS.md**

---

## ✅ NEXT STEPS

1. Install dependencies: `pip install -r requirements.txt`
2. Copy and edit .env: `cp .env.example .env`
3. Run setup scripts for each service
4. Test connections: `python scripts/test_all_connections.py`
5. Start AI Employee: `python scripts/start_all.py`

Your AI Employee will then work **24/7** handling:
- 📧 Emails
- 📱 WhatsApp messages
- 📢 Social media posts
- 💰 Accounting (Odoo)
- ✅ Approvals & tasks

**Welcome to the future of work!** 🚀
