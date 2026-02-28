#!/usr/bin/env python3
"""
setup_gmail_token.py - Get Gmail API refresh token for AI Employee
Run this once to get your Gmail credentials
"""
import webbrowser
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.file import Storage
from oauth2client.tools import run_flow
import os
from pathlib import Path

# Load environment
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️  python-dotenv not found. Install: pip install python-dotenv")

print("""
╔═══════════════════════════════════════════════════════════╗
║           AI EMPLOYEE - GMAIL API SETUP                   ║
╠═══════════════════════════════════════════════════════════╣
║  This will help you get Gmail API credentials for        ║
║  your AI Employee to send emails automatically.           ║
╚═══════════════════════════════════════════════════════════╝

STEP 1: Create Google Cloud Project (if not done)
--------------------------------------------------
1. Go to: https://console.cloud.google.com/
2. Create project: "ai-employee-gmail"
3. Go to: APIs & Services → Library
4. Enable "Gmail API"

STEP 2: Create OAuth Credentials
----------------------------------
1. Go to: APIs & Services → Credentials
2. Create Credentials → OAuth client ID
3. Application type: Desktop app
4. Name: "AI Employee Gmail"
5. Create and copy Client ID and Secret

STEP 3: Enter your credentials below
--------------------------------------------------
""")

CLIENT_ID = input("Enter your Gmail Client ID: ").strip()
CLIENT_SECRET = input("Enter your Gmail Client Secret: ").strip()
FROM_EMAIL = input("Enter your Gmail address: ").strip()

if not CLIENT_ID or not CLIENT_SECRET or not FROM_EMAIL:
    print("\n❌ All fields are required!")
    exit(1)

print(f"\n📧 Using email: {FROM_EMAIL}")
print("\n⏳ Opening browser for OAuth authorization...")

# OAuth flow
SCOPES = 'https://www.googleapis.com/auth/gmail.send'
flow = OAuth2WebServerFlow(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    scope=SCOPES,
    redirect_uri='urn:ietf:wg:oauth:2.0:oob',
    user_agent='AI Employee Gmail/1.0'
)

# Open browser
auth_url = flow.step1_get_authorize_url()
print(f"\n🔗 Authorization URL: {auth_url}")
webbrowser.open(auth_url)

print("\n" + "="*60)
print("A browser window has opened.")
print("1. Sign in to your Google account")
print("2. Grant permissions to send email")
print("3. Copy the authorization code")
print("="*60)

AUTH_CODE = input("\nEnter the authorization code: ").strip()

if not AUTH_CODE:
    print("\n❌ Authorization code is required!")
    exit(1)

# Exchange code for credentials
try:
    credentials = flow.step2_exchange(AUTH_CODE)

    print("\n" + "="*60)
    print("✅ SUCCESS! Your Gmail credentials:")
    print("="*60)

    print(f"\n# Add these to your .env file:\n")
    print(f"GMAIL_CLIENT_ID={CLIENT_ID}")
    print(f"GMAIL_CLIENT_SECRET={CLIENT_SECRET}")
    print(f"GMAIL_REFRESH_TOKEN={credentials.refresh_token}")
    print(f"GMAIL_FROM_EMAIL={FROM_EMAIL}")
    print(f"GMAIL_SEND_NAME=AI Employee")

    # Save to file for reference
    creds_file = Path(__file__).parent.parent / 'gmail_credentials.txt'
    with open(creds_file, 'w') as f:
        f.write(f"# Gmail API Credentials for AI Employee\n")
        f.write(f"# Add these to your .env file\n\n")
        f.write(f"GMAIL_CLIENT_ID={CLIENT_ID}\n")
        f.write(f"GMAIL_CLIENT_SECRET={CLIENT_SECRET}\n")
        f.write(f"GMAIL_REFRESH_TOKEN={credentials.refresh_token}\n")
        f.write(f"GMAIL_FROM_EMAIL={FROM_EMAIL}\n")
        f.write(f"GMAIL_SEND_NAME=AI Employee\n")

    print(f"\n💾 Also saved to: {creds_file}")

    print("\n" + "="*60)
    print("✨ SETUP COMPLETE!")
    print("="*60)
    print("\nYour AI Employee can now:")
    print("  ✅ Send emails automatically")
    print("  ✅ Monitor Gmail inbox")
    print("  ✅ Draft email replies")
    print("  ✅ Handle customer support via email")

    print("\nNext steps:")
    print("  1. Copy the credentials above to your .env file")
    print("  2. Run: python scripts/test_gmail_connection.py")

    print("\n")

except Exception as e:
    print(f"\n❌ Error getting credentials: {e}")
    print("\nPlease check:")
    print("  - Client ID and Secret are correct")
    print("  - Authorization code is complete")
    print("  - Gmail API is enabled in Google Console")
