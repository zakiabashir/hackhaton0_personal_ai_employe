#!/usr/bin/env python3
"""
setup_whatsapp_session.py - Setup WhatsApp Web session for AI Employee
This opens WhatsApp Web and saves the session for automated use
"""
import asyncio
import os
import sys
from pathlib import Path

try:
    from playwright.async_api import async_playwright
except ImportError:
    print("Installing playwright...")
    os.system("pip install playwright")
    os.system("playwright install chromium")
    from playwright.async_api import async_playwright

# Load environment
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Default session path
SESSION_PATH = os.getenv('WHATSAPP_WEB_SESSION_PATH', './.whatsapp_session/')
SESSION_FILE = os.path.join(SESSION_PATH, 'whatsapp_session.json')


async def setup_whatsapp():
    """Setup WhatsApp Web session"""

    print("""
╔══════════════════════════════════════════════════════════╗
║         WHATSAPP WEB SESSION SETUP                      ║
╚══════════════════════════════════════════════════════════╝

This will:
1. Open WhatsApp Web in a browser
2. Show you a QR code
3. You scan it with your phone
4. Save the session for AI Employee

Instructions:
- Open WhatsApp on your phone
- Go to Settings → Linked Devices
- Tap "Link a Device"
- Scan the QR code when it appears

Press Enter to continue...
""")
    input()

    # Create session directory
    Path(SESSION_PATH).mkdir(parents=True, exist_ok=True)

    async with async_playwright() as p:
        print("\n📱 Opening WhatsApp Web...")

        # Launch browser with persistent context
        context = await p.chromium.launch_persistent_context(
            user_data_dir=SESSION_PATH,
            headless=False,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
            ]
        )

        page = await context.new_page()
        await page.goto('https://web.whatsapp.com')

        print("\n⏳ Waiting for QR code scan...")
        print("📲 Scan the QR code with your phone now!")

        # Wait for login - check for success indicators
        try:
            # Wait for either QR code or successful login
            await page.wait_for_selector(
                'canvas[aria-label="Scan this QR code to link a device!"], '
                'div[contenteditable="true"][data-tab="0"]',
                timeout=120000  # 2 minutes
            )

            # Check if we're logged in (chat input is present)
            chat_input = await page.query_selector('div[contenteditable="true"][data-tab="0"]')

            if chat_input:
                print("\n✅ WhatsApp session created successfully!")

                # Get page title to confirm
                title = await page.title()
                print(f"📊 Page: {title}")

                # Save session info
                session_info = {
                    "setup_date": str(Path(__file__).stat().st_mtime),
                    "session_path": SESSION_PATH,
                    "status": "active"
                }

                with open(SESSION_FILE, 'w') as f:
                    import json
                    json.dump(session_info, f, indent=2)

                print(f"\n💾 Session saved to: {SESSION_PATH}")
                print("\n" + "="*60)
                print("✨ SETUP COMPLETE!")
                print("="*60)
                print("\nYour AI Employee can now:")
                print("  ✅ Read incoming WhatsApp messages")
                print("  ✅ Detect customer queries")
                print("  ✅ Draft replies for approval")
                print("  ✅ Monitor business messages 24/7")
                print("\nTo test:")
                print("  python scripts/test_whatsapp_connection.py")
                print("\nPress Enter to close browser...")
                input()

            else:
                print("\n⚠️  QR code detected but not yet scanned.")
                print("Please scan the QR code and run this script again.")

        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("Please try again.")

        await context.close()


if __name__ == '__main__':
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║           AI EMPLOYEE - WHATSAPP SETUP WIZARD            ║
    ╠═══════════════════════════════════════════════════════════╣
    ║  This will setup WhatsApp Web session for your AI         ║
    ║  Employee to monitor and respond to messages.             ║
    ╚═══════════════════════════════════════════════════════════╝
    """)

    asyncio.run(setup_whatsapp())
