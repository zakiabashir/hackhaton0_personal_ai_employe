#!/usr/bin/env python3
"""
start_all.py - Start all AI Employee watchers with proper connections
This starts the full autonomous AI Employee with all services
"""
import os
import sys
import time
import signal
import subprocess
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️  python-dotenv not installed. Install: pip install python-dotenv")

# ANSI colors
GREEN = "\033[92m"
BLUE = "\033[94m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"

# Watcher processes
watchers = []

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

def check_connections():
    """Check all service connections before starting"""
    print_header("CHECKING CONNECTIONS")

    required = {
        'GMAIL': ['GMAIL_CLIENT_ID', 'GMAIL_CLIENT_SECRET', 'GMAIL_REFRESH_TOKEN'],
        'LINKEDIN': ['LINKEDIN_ACCESS_TOKEN'],  # or LINKEDIN_EMAIL
        'WHATSAPP': ['WHATSAPP_PHONE_NUMBER'],
        'FACEBOOK': ['FACEBOOK_PAGE_ID', 'FACEBOOK_ACCESS_TOKEN'],
        'INSTAGRAM': ['INSTAGRAM_USERNAME', 'INSTAGRAM_ACCESS_TOKEN'],
        'TWITTER': ['TWITTER_API_KEY', 'TWITTER_ACCESS_TOKEN'],
        'ODOO': ['ODOO_URL', 'ODOO_DB_NAME', 'ODOO_USERNAME'],
    }

    all_good = True

    for service, env_vars in required.items():
        # Check if any of the required vars are set
        found = any(os.getenv(v) and os.getenv(v) != f'your_{v.lower()}' for v in env_vars)

        if found:
            print_success(f"{service}: Configured")
        else:
            print_warning(f"{service}: Not configured (optional)")
            # Don't fail if some services are not configured

    return all_good

def start_watcher(name, script_path, vault_path):
    """Start a watcher process"""
    try:
        script = Path(__file__).parent.parent / script_path

        if not script.exists():
            print_warning(f"{name}: Script not found ({script})")
            return None

        # Set environment variables
        env = os.environ.copy()
        env['VAULT_PATH'] = str(vault_path)
        env['PYTHONUNBUFFERED'] = '1'

        process = subprocess.Popen(
            [sys.executable, str(script)],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        print_success(f"{name}: Started (PID: {process.pid})")
        return {'name': name, 'process': process, 'path': str(script)}

    except Exception as e:
        print_error(f"{name}: Failed to start - {e}")
        return None

def stop_all_watchers():
    """Stop all running watchers"""
    print_header("STOPPING ALL WATCHERS")

    for watcher in watchers:
        try:
            watcher['process'].terminate()
            watcher['process'].wait(timeout=5)
            print_success(f"{watcher['name']}: Stopped")
        except Exception as e:
            print_error(f"{watcher['name']}: Error stopping - {e}")

def signal_handler(signum, frame):
    """Handle Ctrl+C"""
    print("\n\nReceived stop signal...")
    stop_all_watchers()
    sys.exit(0)

def main():
    """Main entry point"""
    print(f"""
{BLUE}╔{'='*58}╗{RESET}
{BLUE}║{'AI EMPLOYEE - STARTING ALL SERVICES'.center(58)}║{RESET}
{BLUE}╚{'='*58}╝{RESET}
""")

    # Register signal handler
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Get vault path
    vault_path = Path(os.getenv('VAULT_PATH',
        Path(__file__).parent.parent / 'AI_Employee_Vault'))

    print_success(f"Vault: {vault_path}")

    # Check connections
    check_connections()

    # Start watchers
    print_header("STARTING WATCHERS")

    # Core watchers
    watcher_scripts = [
        ("FileSystem Watcher", "watchers/filesystem_watcher.py"),
        ("Gmail Watcher", "watchers/gmail_watcher.py"),
        ("WhatsApp Watcher", "watchers/whatsapp_watcher.py"),
        ("LinkedIn Poster", "watchers/linkedin_poster.py"),
        ("Social Media Poster", "watchers/social_poster.py"),
        ("Odoo Watcher", "watchers/odoo_watcher.py"),
        ("Approval Watcher", "watchers/approval_watcher.py"),
        ("Reasoning Loop", "watchers/reasoning_loop.py"),
    ]

    for name, script in watcher_scripts:
        watcher = start_watcher(name, script, vault_path)
        if watcher:
            watchers.append(watcher)
        time.sleep(0.5)  # Stagger starts

    print_header("SUMMARY")

    if watchers:
        print_success(f"Started {len(watchers)} watcher(s)")

        print(f"\n{YELLOW}Running Watchers:{RESET}")
        for w in watchers:
            print(f"  • {w['name']} (PID: {w['process'].pid})")

        print(f"""
{BLUE}╔{'='*58}╗{RESET}
{BLUE}║{'AI EMPLOYEE IS RUNNING'.center(58)}║{RESET}
{BLUE}║{'Press Ctrl+C to stop'.center(58)}║{RESET}
{BLUE}╚{'='*58}╝{RESET}

{GREEN}Your AI Employee is now:{RESET}
  ✅ Monitoring emails (Gmail)
  ✅ Watching for WhatsApp messages
  ✅ Ready to post to LinkedIn
  ✅ Ready to post to Facebook/Instagram/Twitter
  ✅ Monitoring Odoo for accounting
  ✅ Processing approvals
  ✅ Generating execution plans

{YELLOW}Files dropped in Inbox/ will be processed automatically.{RESET}
{YELLOW}Check Needs_Action/ for tasks requiring attention.{RESET}

Logs: {vault_path / 'Logs'}
Dashboard: {vault_path / 'Dashboard.md'}
""")

        # Keep running
        try:
            while True:
                # Check if any watcher died
                for watcher in watchers[:]:
                    ret = watcher['process'].poll()
                    if ret is not None:
                        print_error(f"{watcher['name']} died (exit: {ret})")
                        watchers.remove(watcher)

                time.sleep(5)

        except KeyboardInterrupt:
            signal_handler(None, None)
    else:
        print_error("No watchers started!")
        print("\nCheck:")
        print("  - .env file exists")
        print("  - Dependencies installed: pip install -r requirements.txt")
        print("  - Run: python scripts/test_all_connections.py")

if __name__ == '__main__':
    main()
