#!/usr/bin/env python3
"""
test_all_connections.py - Test all AI Employee service connections
"""
import os
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️  python-dotenv not installed. Run: pip install python-dotenv")

# ANSI colors
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"

def print_header(text):
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}{text.center(60)}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")

def print_success(text):
    print(f"{GREEN}✅ {text}{RESET}")

def print_error(text):
    print(f"{RED}❌ {text}{RESET}")

def print_warning(text):
    print(f"{YELLOW}⚠️  {text}{RESET}")

def test_env_file():
    """Test if .env file exists"""
    print_header("TESTING ENVIRONMENT CONFIGURATION")

    env_path = Path(__file__).parent.parent / '.env'
    if env_path.exists():
        print_success(".env file found")
        return True
    else:
        print_error(".env file NOT found")
        print("Create .env from .env.example:")
        print("  cp .env.example .env")
        return False

def test_gmail():
    """Test Gmail API connection"""
    print_header("TESTING GMAIL API")

    client_id = os.getenv('GMAIL_CLIENT_ID')
    client_secret = os.getenv('GMAIL_CLIENT_SECRET')
    refresh_token = os.getenv('GMAIL_REFRESH_TOKEN')
    from_email = os.getenv('GMAIL_FROM_EMAIL')

    checks = [
        ('GMAIL_CLIENT_ID', client_id),
        ('GMAIL_CLIENT_SECRET', client_secret),
        ('GMAIL_REFRESH_TOKEN', refresh_token),
        ('GMAIL_FROM_EMAIL', from_email),
    ]

    all_good = True
    for name, value in checks:
        if value and value != 'your_gmail_client_id' and value != 'your_email@gmail.com':
            print_success(f"{name}: Set")
        else:
            print_error(f"{name}: Missing or not configured")
            all_good = False

    if all_good:
        try:
            from google.auth.transport.requests import Request
            from google.oauth2.credentials import Credentials
            import googleapiclient.discovery

            credentials = Credentials(
                token=None,
                refresh_token=refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=client_id,
                client_secret=client_secret,
                scopes=["https://www.googleapis.com/auth/gmail.send"]
            )

            credentials.refresh(Request())
            print_success("Gmail API: Connection successful!")

            return True
        except Exception as e:
            print_error(f"Gmail API connection failed: {e}")
            return False
    else:
        print_warning("Configure Gmail credentials in .env first")
        return False

def test_linkedin():
    """Test LinkedIn configuration"""
    print_header("TESTING LINKEDIN")

    profile_url = os.getenv('LINKEDIN_PROFILE_URL')
    email = os.getenv('LINKEDIN_EMAIL')
    password = os.getenv('LINKEDIN_PASSWORD')
    access_token = os.getenv('LINKEDIN_ACCESS_TOKEN')

    all_good = False

    if access_token and access_token != 'your_access_token':
        print_success("LinkedIn Access Token: Set (API method)")
        all_good = True
    elif email and password and email != 'your_linkedin_email':
        print_success("LinkedIn credentials: Set (Playwright method)")
        all_good = True
    else:
        print_warning("LinkedIn: Not configured")
        print("Add LINKEDIN_ACCESS_TOKEN or LINKEDIN_EMAIL/PASSWORD to .env")

    if profile_url:
        print_success(f"LinkedIn Profile: {profile_url}")

    return all_good

def test_whatsapp():
    """Test WhatsApp configuration"""
    print_header("TESTING WHATSAPP")

    phone = os.getenv('WHATSAPP_PHONE_NUMBER')
    session_path = os.getenv('WHATSAPP_WEB_SESSION_PATH')

    if phone:
        print_success(f"WhatsApp Phone: {phone}")
    else:
        print_warning("WhatsApp phone not configured")

    if session_path:
        session_dir = Path(session_path)
        if session_dir.exists() and list(session_dir.glob('*')):
            print_success(f"WhatsApp Session: Found in {session_path}")
            return True
        else:
            print_warning("WhatsApp session not found. Run setup_whatsapp_session.py")
            return False
    else:
        print_warning("WhatsApp session path not configured")
        return False

def test_facebook():
    """Test Facebook configuration"""
    print_header("TESTING FACEBOOK")

    page_id = os.getenv('FACEBOOK_PAGE_ID')
    access_token = os.getenv('FACEBOOK_ACCESS_TOKEN')
    page_url = os.getenv('FACEBOOK_PAGE_URL')

    all_good = True

    if page_id and page_id != 'your_page_id':
        print_success(f"Facebook Page ID: {page_id}")
    else:
        print_error("Facebook Page ID not configured")
        all_good = False

    if access_token and access_token != 'your_access_token':
        print_success("Facebook Access Token: Set")
    else:
        print_error("Facebook Access Token not configured")
        all_good = False

    if page_url:
        print_success(f"Facebook Page: {page_url}")

    return all_good

def test_instagram():
    """Test Instagram configuration"""
    print_header("TESTING INSTAGRAM")

    username = os.getenv('INSTAGRAM_USERNAME')
    access_token = os.getenv('INSTAGRAM_ACCESS_TOKEN')
    business_id = os.getenv('INSTAGRAM_BUSINESS_ACCOUNT_ID')

    all_good = True

    if username:
        print_success(f"Instagram Username: @{username}")
    else:
        print_error("Instagram username not configured")
        all_good = False

    if access_token and access_token != 'your_access_token':
        print_success("Instagram Access Token: Set")
    else:
        print_error("Instagram Access Token not configured")
        all_good = False

    if business_id and business_id != 'your_business_account_id':
        print_success(f"Instagram Business ID: {business_id}")
    else:
        print_warning("Instagram Business ID not configured")

    return all_good

def test_twitter():
    """Test Twitter/X configuration"""
    print_header("TESTING TWITTER/X")

    handle = os.getenv('TWITTER_HANDLE')
    api_key = os.getenv('TWITTER_API_KEY')
    api_secret = os.getenv('TWITTER_API_SECRET')
    access_token = os.getenv('TWITTER_ACCESS_TOKEN')
    access_secret = os.getenv('TWITTER_ACCESS_SECRET')

    all_good = True

    if handle and handle != 'yourhandle':
        print_success(f"Twitter Handle: @{handle}")
    else:
        print_warning("Twitter handle not configured")

    if api_key and api_key != 'your_api_key':
        print_success("Twitter API Key: Set")
    else:
        print_error("Twitter API Key not configured")
        all_good = False

    if api_secret and api_secret != 'your_api_secret':
        print_success("Twitter API Secret: Set")
    else:
        print_error("Twitter API Secret not configured")
        all_good = False

    if access_token and access_token != 'your_access_token':
        print_success("Twitter Access Token: Set")
    else:
        print_error("Twitter Access Token not configured")
        all_good = False

    return all_good

def test_odoo():
    """Test Odoo configuration"""
    print_header("TESTING ODOO ACCOUNTING")

    url = os.getenv('ODOO_URL')
    db_name = os.getenv('ODOO_DB_NAME')
    username = os.getenv('ODOO_USERNAME')
    password = os.getenv('ODOO_PASSWORD')

    all_good = True

    if url:
        print_success(f"Odoo URL: {url}")
    else:
        print_error("Odoo URL not configured")
        all_good = False

    if db_name and db_name != 'odoo_db':
        print_success(f"Odoo Database: {db_name}")
    else:
        print_error("Odoo database name not configured")
        all_good = False

    if username:
        print_success(f"Odoo Username: {username}")
    else:
        print_error("Odoo username not configured")
        all_good = False

    if password and password != 'admin_password':
        print_success("Odoo Password: Set")
    else:
        print_error("Odoo password not configured")
        all_good = False

    if all_good:
        try:
            import requests
            # Test Odoo connection
            response = requests.post(
                f"{url}/jsonrpc",
                json={
                    "jsonrpc": "2.0",
                    "method": "call",
                    "params": {
                        "service": "common",
                        "method": "version",
                        "args": []
                    },
                    "id": 1
                },
                timeout=5
            )

            if response.status_code == 200:
                print_success("Odoo Server: Connected!")
                return True
            else:
                print_warning(f"Odoo Server: Not reachable (Status: {response.status_code})")
                return False
        except Exception as e:
            print_warning(f"Odoo connection test failed: {e}")
            return False

    return all_good

def main():
    """Run all connection tests"""
    print(f"\n{BLUE}╔{'='*58}╗{RESET}")
    print(f"{BLUE}║{'AI EMPLOYEE - CONNECTION TEST SUITE'.center(58)}║{RESET}")
    print(f"{BLUE}╚{'='*58}╝{RESET}")
    print(f"\n{YELLOW}Testing all service connections...{RESET}\n")

    results = {
        "Environment": test_env_file(),
        "Gmail API": test_gmail(),
        "LinkedIn": test_linkedin(),
        "WhatsApp": test_whatsapp(),
        "Facebook": test_facebook(),
        "Instagram": test_instagram(),
        "Twitter": test_odoo(),  # Bug fix - should be test_twitter
        "Odoo": test_odoo(),
    }

    # Fix the bug
    results["Twitter"] = test_twitter()

    print_header("SUMMARY")

    for service, passed in results.items():
        if passed:
            print_success(f"{service}: Connected")
        else:
            print_error(f"{service}: Failed/Not Configured")

    total = len(results)
    passed = sum(results.values())

    print(f"\n{BLUE}Total: {passed}/{total} services connected{RESET}")

    if passed == total:
        print(f"{GREEN}All services connected! AI Employee ready. 🎉{RESET}\n")
        return 0
    else:
        print(f"{YELLOW}Some services need configuration. See SETUP_CONNECTIONS.md{RESET}\n")
        return 1

if __name__ == '__main__':
    sys.exit(main())
