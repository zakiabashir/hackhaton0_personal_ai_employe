# AI Employee - Complete Connection Setup Guide

## 🎯 All Services MUST Be Connected

Your AI Employee needs ALL these connections to work autonomously:

| Service | Purpose | Priority |
|---------|---------|----------|
| **Gmail** | Send emails, customer support | 🔴 REQUIRED |
| **LinkedIn** | Auto-post content | 🔴 REQUIRED |
| **WhatsApp** | Customer support, monitoring | 🔴 REQUIRED |
| **Facebook** | Auto-post to page | 🔴 REQUIRED |
| **Instagram** | Auto-post stories, posts | 🔴 REQUIRED |
| **Twitter/X** | Auto-post tweets | 🔴 REQUIRED |
| **Odoo** | Accounting, invoicing | 🔴 REQUIRED |

---

## 📧 1. GMAIL API SETUP (Email Sending)

### Step 1: Create Google Cloud Project
1. Go to: https://console.cloud.google.com/
2. Create new project: `ai-employee-gmail`
3. Go to: APIs & Services → Library
4. Search and enable: **Gmail API**

### Step 2: Create OAuth Credentials
1. Go to: APIs & Services → Credentials
2. Click: **Create Credentials** → **OAuth client ID**
3. Application type: **Desktop app**
4. Name: `AI Employee Gmail`
5. Click **Create**

### Step 3: Get Refresh Token (First Time Only)

Run this Python script to get your refresh token:

```python
# get_gmail_token.py - Run this once to get credentials
import flow_from_clientsecrets
from oauth2client.client import OAuth2WebServerFlow
import webbrowser

CLIENT_ID = 'your_client_id'
CLIENT_SECRET = 'your_client_secret'

flow = OAuth2WebServerFlow(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    scope='https://www.googleapis.com/auth/gmail.send',
    redirect_uri='urn:ietf:wg:oauth:2.0:oob'
)

auth_url = flow.step1_get_authorize_url()
print('Go to this URL:', auth_url)
webbrowser.open(auth_url)

code = input('Enter the code: ')
credentials = flow.step2_exchange(code)

print('REFRESH_TOKEN:', credentials.refresh_token)
print('ACCESS_TOKEN:', credentials.access_token)
```

### Step 4: Add to .env
```bash
GMAIL_CLIENT_ID=your_actual_client_id
GMAIL_CLIENT_SECRET=your_actual_client_secret
GMAIL_REFRESH_TOKEN=your_actual_refresh_token
GMAIL_FROM_EMAIL=your_email@gmail.com
```

---

## 💼 2. LINKEDIN AUTO-POST SETUP

### Option A: Using LinkedIn API (Recommended)

1. Go to: https://www.linkedin.com/developers/
2. Create App: `AI Employee Poster`
3. Get:
   - Client ID
   - Client Secret
   - Redirect URL: `http://localhost:8080/callback`

4. Add to .env:
```bash
LINKEDIN_CLIENT_ID=your_client_id
LINKEDIN_CLIENT_SECRET=your_client_secret
LINKEDIN_ACCESS_TOKEN=your_access_token
LINKEDIN_PROFILE_URN=urn:li:person:abc123
```

### Option B: Using Playwright (Auto-Login)

1. Install Playwright browsers:
```bash
playwright install chromium
```

2. Add to .env:
```bash
LINKEDIN_EMAIL=your_email@example.com
LINKEDIN_PASSWORD=your_password
LINKEDIN_SESSION_COOKIE=li_at_value_from_browser
```

3. Run setup script to get session cookie:
```bash
python scripts/setup_linkedin_session.py
```

---

## 📱 3. WHATSAPP SETUP

### Step 1: Install WhatsApp Web Requirements
```bash
npm install -g playwright
playwright install chromium
```

### Step 2: Get Session (First Time Only)
```bash
# Run the WhatsApp setup script
python scripts/setup_whatsapp_session.py
```

This will:
1. Open WhatsApp Web in browser
2. Show QR code
3. Scan with your phone
4. Save session to `.whatsapp_session/`

### Step 3: Add to .env
```bash
WHATSAPP_PHONE_NUMBER=923001234567
WHATSAPP_BUSINESS_NUMBER=923001234567
WHATSAPP_WEB_SESSION_PATH=./.whatsapp_session/
```

---

## 📘 4. FACEBOOK AUTO-POST SETUP

### Step 1: Create Facebook App
1. Go to: https://developers.facebook.com/apps/
2. Create App: **Business** type
3. App Name: `AI Employee Social Poster`

### Step 2: Get Page Access Token
1. Go to: Tools & APIs → Graph API Explorer
2. Select your app
3. Get User Token with: `pages_manage_posts`, `pages_read_engagement`
4. Get Page Access Token for your page

### Step 3: Add to .env
```bash
FACEBOOK_PAGE_ID=123456789
FACEBOOK_ACCESS_TOKEN=EAAxxxxx...
FACEBOOK_PAGE_URL=https://facebook.com/GlowCareStudio
```

---

## 📸 5. INSTAGRAM AUTO-POST SETUP

### Step 1: Connect Instagram to Facebook Page
1. Go to your Facebook Page
2. Settings → Instagram
3. Connect your Instagram account (@heavensbags)

### Step 2: Get Instagram Business ID
```bash
curl "https://graph.facebook.com/v18.0/me/accounts?access_token=YOUR_ACCESS_TOKEN"
```

### Step 3: Add to .env
```bash
INSTAGRAM_USERNAME=heavensbags
INSTAGRAM_BUSINESS_ID=123456789
INSTAGRAM_ACCESS_TOKEN=EAAxxxxx...
```

---

## 🐦 6. TWITTER/X AUTO-POST SETUP

### Step 1: Create Twitter App
1. Go to: https://developer.twitter.com/en/portal/dashboard
2. Create Project: `AI Employee`
3. Create App: `Social Poster`

### Step 2: Get API Keys
1. Get your API Key, API Secret
2. Generate Access Token & Secret

### Step 3: Add to .env
```bash
TWITTER_API_KEY=your_api_key
TWITTER_API_SECRET=your_api_secret
TWITTER_ACCESS_TOKEN=your_access_token
TWITTER_ACCESS_SECRET=your_access_secret
TWITTER_BEARER_TOKEN=your_bearer_token
TWITTER_HANDLE=ZakiaBashi8590
```

---

## 📊 7. ODOO ACCOUNTING SETUP

### Step 1: Install Odoo (Local or Cloud)

**Option A: Docker (Easiest)**
```bash
docker run -d \
  -e POSTGRES_USER=odoo \
  -e POSTGRES_PASSWORD=odoo \
  -p 8069:8069 \
  --name odoo \
  odoo:17
```

**Option B: Local Install**
```bash
# Download Odoo 17
wget https://nightly.odoo.com/17.0/odoo_17.0_latest.deb
sudo dpkg -i odoo_17.0_latest.deb
sudo apt-get install -f
```

### Step 2: Configure Odoo
1. Open: http://localhost:8069
2. Create database: `ai_employee_db`
3. Install apps: Accounting, Invoicing, Sales

### Step 3: Get API Access
1. Settings → API Keys
2. Create API key for AI Employee

### Step 4: Add to .env
```bash
ODOO_URL=http://localhost:8069
ODOO_DB_NAME=ai_employee_db
ODOO_USERNAME=admin
ODOO_PASSWORD=admin_password
ODOO_API_KEY=odoo_api_key_here
```

---

## 🚀 FINAL SETUP - Run Configuration Script

```bash
# Copy example .env
cp .env.example .env

# Edit with your credentials
notepad .env  # Windows
# or
nano .env     # Linux/Mac

# Run setup wizard
python scripts/setup_all_connections.py
```

---

## ✅ TEST ALL CONNECTIONS

```bash
# Test all services
python scripts/test_all_connections.py
```

Expected output:
```
✅ Gmail API: Connected
✅ LinkedIn: Ready to post
✅ WhatsApp: Session active
✅ Facebook: Access token valid
✅ Instagram: Business account connected
✅ Twitter: API keys valid
✅ Odoo: Connected to database
```

---

## 🔧 SECURITY NOTES

1. **NEVER commit .env to git**
2. **Keep API keys secret**
3. **Rotate keys regularly**
4. **Use separate app passwords**
5. **Enable 2FA where possible**

---

## 📝 NEXT STEPS

After all connections are setup:

1. ✅ Start watchers: `python watchers/start_all.py`
2. ✅ Test email sending
3. ✅ Test LinkedIn post
4. ✅ Test WhatsApp message
5. ✅ Test Odoo invoice creation

Your AI Employee is now fully connected! 🎉
