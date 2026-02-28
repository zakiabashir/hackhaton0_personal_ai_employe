#!/usr/bin/env python3
"""
test_gmail_connection.py - Test Gmail API connection and send test email
"""
import os
import sys
from pathlib import Path
from email.mime.text import MIMEText
import base64

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️  python-dotenv not installed")
    sys.exit(1)

def test_gmail_connection():
    """Test Gmail API and send test email"""

    print("""
╔═══════════════════════════════════════════════════════════╗
║           GMAIL CONNECTION TEST                           ║
╚═══════════════════════════════════════════════════════════╝
""")

    # Get credentials from .env
    client_id = os.getenv('GMAIL_CLIENT_ID')
    client_secret = os.getenv('GMAIL_CLIENT_SECRET')
    refresh_token = os.getenv('GMAIL_REFRESH_TOKEN')
    from_email = os.getenv('GMAIL_FROM_EMAIL')

    if not all([client_id, client_secret, refresh_token, from_email]):
        print("❌ Gmail credentials not found in .env")
        print("\nRequired:")
        print("  GMAIL_CLIENT_ID")
        print("  GMAIL_CLIENT_SECRET")
        print("  GMAIL_REFRESH_TOKEN")
        print("  GMAIL_FROM_EMAIL")
        print("\nRun: python scripts/setup_gmail_token.py")
        return False

    print("✅ Credentials found in .env")
    print(f"📧 From: {from_email}")

    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        import googleapiclient.discovery

        print("\n⏳ Connecting to Gmail API...")

        # Create credentials
        credentials = Credentials(
            token=None,
            refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=client_id,
            client_secret=client_secret,
            scopes=["https://www.googleapis.com/auth/gmail.send"]
        )

        # Refresh to get access token
        credentials.refresh(Request())
        print("✅ Access token obtained")

        # Build Gmail service
        service = googleapiclient.discovery.build(
            'gmail', 'v1',
            credentials=credentials
        )
        print("✅ Gmail service connected")

        # Get profile
        profile = service.users().getProfile(userId='me').execute()
        print(f"✅ Gmail Profile: {profile.get('emailAddress')}")
        print(f"   Messages Total: {profile.get('messagesTotal')}")
        print(f"   Threads Total: {profile.get('threadsTotal')}")

        # Test sending email
        print("\n" + "="*60)
        test_to = input(f"Send test email to (or press Enter to skip): ").strip()

        if test_to:
            # Create message
            message = MIMEText("""
This is a test email from your AI Employee!

If you received this, your Gmail API connection is working perfectly.

Your AI Employee can now:
✅ Send emails automatically
✅ Monitor your inbox
✅ Draft replies for approval
✅ Handle customer support

--
AI Employee
Personal AI Employee - Platinum Tier
""")
            message['to'] = test_to
            message['from'] = from_email
            message['subject'] = 'AI Employee - Gmail Test ✅'

            # Encode message
            raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
            body = {'raw': raw}

            # Send
            print(f"\n📧 Sending test email to {test_to}...")
            sent = service.users().messages().send(
                userId='me', body=body
            ).execute()

            print("✅ Email sent successfully!")
            print(f"   Message ID: {sent.get('id')}")

        print("\n" + "="*60)
        print("✨ GMAIL CONNECTION SUCCESSFUL!")
        print("="*60)

        return True

    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nPossible issues:")
        print("  - Refresh token expired (run setup_gmail_token.py again)")
        print("  - Client ID/Secret incorrect")
        print("  - Gmail API not enabled")
        print("  - Network connection issue")
        return False

if __name__ == '__main__':
    success = test_gmail_connection()
    sys.exit(0 if success else 1)
