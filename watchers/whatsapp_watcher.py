"""
WhatsApp Watcher - Monitors WhatsApp Web for important messages
Uses Playwright for browser automation with session persistence
"""
import time
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from base_watcher import BaseWatcher

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("Playwright not available. Install with: pip install playwright && playwright install chromium")


class WhatsAppWatcher(BaseWatcher):
    """
    Watches WhatsApp Web for new messages and creates action files
    Uses persistent browser context for session management
    """

    # Keywords that trigger high priority
    URGENT_KEYWORDS = ['urgent', 'asap', 'emergency', 'immediately', 'now', 'help']
    BUSINESS_KEYWORDS = ['invoice', 'payment', 'order', 'price', 'quote', 'contract', 'deal']
    QUESTION_KEYWORDS = ['?', 'can you', 'will you', 'how to', 'what is', 'when']

    def __init__(self, vault_path: str, session_path: str = None, check_interval: int = 60):
        super().__init__(vault_path, check_interval)

        if not PLAYWRIGHT_AVAILABLE:
            self.logger.error("Playwright not available")
            return

        self.session_path = Path(session_path) if session_path else self.vault_path / '.whatsapp_session'
        self.session_path.mkdir(parents=True, exist_ok=True)

        self.business = self.vault_path / 'Business'
        self.personal = self.vault_path / 'Personal'
        self.business.mkdir(exist_ok=True)
        self.personal.mkdir(exist_ok=True)

        self.processed_messages = set()
        self._load_processed_state()

        self.logger.info(f"WhatsApp Watcher initialized with session: {self.session_path}")

    def _load_processed_state(self):
        """Load processed message IDs"""
        state_file = self.vault_path / '.whatsapp_state.json'
        if state_file.exists():
            try:
                with open(state_file, 'r') as f:
                    data = json.load(f)
                    self.processed_messages = set(data.get('processed_messages', []))
            except Exception as e:
                self.logger.error(f"Error loading state: {e}")

    def _save_processed_state(self):
        """Save processed message IDs"""
        state_file = self.vault_path / '.whatsapp_state.json'
        try:
            with open(state_file, 'w') as f:
                json.dump({
                    'processed_messages': list(self.processed_messages),
                    'last_update': datetime.now().isoformat()
                }, f)
        except Exception as e:
            self.logger.error(f"Error saving state: {e}")

    def _is_business_message(self, sender: str, message: str) -> bool:
        """Determine if message is business-related"""
        sender_lower = sender.lower()
        message_lower = message.lower()

        # Check for business keywords in message
        if any(kw in message_lower for kw in self.BUSINESS_KEYWORDS):
            return True

        # Check for business-like sender names
        business_indicators = ['shop', 'store', 'business', 'company', 'service', 'delivery']
        if any(ind in sender_lower for ind in business_indicators):
            return True

        return False

    def _determine_priority(self, sender: str, message: str) -> str:
        """Determine message priority"""
        message_lower = message.lower()

        # Check for urgent keywords
        if any(kw in message_lower for kw in self.URGENT_KEYWORDS):
            return 'high'

        # Check for questions (need response)
        if any(kw in message_lower for kw in self.QUESTION_KEYWORDS):
            return 'medium'

        # Business messages are at least medium priority
        if self._is_business_message(sender, message):
            return 'medium'

        return 'low'

    def _suggest_actions(self, sender: str, message: str) -> list:
        """Suggest actions based on message content"""
        actions = []
        message_lower = message.lower()

        # Common actions
        actions.append('- [ ] Read and understand message')
        actions.append('- [ ] Determine appropriate response')

        # Context-specific actions
        if any(kw in message_lower for kw in self.BUSINESS_KEYWORDS):
            actions.append('- [ ] Check business records if needed')
            actions.append('- [ ] Consider business impact')
            actions.append('- [ ] Draft professional response')

        elif any(kw in message_lower for kw in self.URGENT_KEYWORDS):
            actions.append('- [ ] URGENT: Prioritize immediate response')
            actions.append('- [ ] Escalate if needed')

        elif any(kw in message_lower for kw in ['meeting', 'call', 'schedule']):
            actions.append('- [ ] Check calendar availability')
            actions.append('- [ ] Propose time options')

        elif '?' in message:
            actions.append('- [ ] Formulate helpful answer')
            actions.append('- [ ] Ask clarifying questions if needed')

        actions.append('- [ ] Send response (requires approval)')
        actions.append('- [ ] Mark as complete after responding')

        return actions

    def _extract_sender_info(self, chat_element) -> dict:
        """Extract sender information from chat element"""
        try:
            # Try to get sender name from chat
            name = chat_element.inner_text().split('\n')[0].strip()
            return {'name': name, 'type': 'contact'}
        except Exception:
            return {'name': 'Unknown', 'type': 'unknown'}

    def check_for_updates(self) -> list:
        """Check for new WhatsApp messages"""
        if not PLAYWRIGHT_AVAILABLE:
            return []

        new_messages = []

        try:
            with sync_playwright() as p:
                # Launch browser with persistent context
                browser = p.chromium.launch_persistent_context(
                    user_data_dir=str(self.session_path),
                    headless=True,
                    args=['--no-sandbox', '--disable-setuid-sandbox']
                )

                page = browser.new_page()

                # Navigate to WhatsApp Web
                page.goto('https://web.whatsapp.com', timeout=60000)

                # Wait for either login screen or chat list
                try:
                    # Wait up to 10 seconds for QR code or chat list
                    page.wait_for_selector('[data-testid="chat-list"]', timeout=10000)
                except PlaywrightTimeout:
                    self.logger.warning("WhatsApp Web not loaded - may need to scan QR code")
                    browser.close()
                    return []

                # Look for unread chats
                unread_chats = page.query_selector_all('[data-testid="chat-list"] [data-testid="unread-count"]')

                for chat in unread_chats:
                    try:
                        # Get parent chat element
                        chat_element = chat.query_selector('xpath=../../..')

                        # Extract chat info
                        sender_name = chat_element.query_selector('span[title]')
                        if sender_name:
                            sender = sender_name.get_attribute('title') or 'Unknown'

                            # Get last message
                            last_message = chat_element.query_selector('[data-testid="last-message"]')
                            message_text = last_message.inner_text() if last_message else ''

                            # Create message ID
                            message_id = f"{sender}_{message_text[:50]}"

                            if message_id not in self.processed_messages:
                                message_info = {
                                    'id': message_id,
                                    'sender': sender,
                                    'message': message_text,
                                    'timestamp': datetime.now().isoformat(),
                                    'is_business': self._is_business_message(sender, message_text)
                                }

                                new_messages.append(message_info)
                                self.processed_messages.add(message_id)

                    except Exception as e:
                        self.logger.debug(f"Error processing chat: {e}")
                        continue

                browser.close()

                # Save state if new messages found
                if new_messages:
                    self._save_processed_state()

                return new_messages

        except Exception as e:
            self.logger.error(f"Error checking WhatsApp: {e}")
            return []

    def create_action_file(self, item: dict) -> Path:
        """Create action file for WhatsApp message"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_sender = item['sender'][:30].replace(' ', '_').replace('/', '_')
        action_filename = f'WHATSAPP_{timestamp}_{safe_sender}.md'

        # Route to appropriate folder
        if item.get('is_business'):
            action_path = self.business / action_filename
        else:
            action_path = self.personal / action_filename

        priority = self._determine_priority(item['sender'], item['message'])
        actions = self._suggest_actions(item['sender'], item['message'])

        content = f'''---
type: whatsapp_message
message_id: {item['id']}
sender: {item['sender']}
is_business: {item.get('is_business', False)}
timestamp: {item['timestamp']}
priority: {priority}
status: pending
created: {datetime.now().isoformat()}
---

# WhatsApp Message: {item['sender']}

## Message Information
- **From:** {item['sender']}
- **Time:** {item['timestamp']}
- **Priority:** {priority.upper()}
- **Type:** {'Business' if item.get('is_business') else 'Personal'}
- **Message ID:** {item['id']}

## Message Content
{item['message']}

## Suggested Actions
{chr(10).join(actions)}

## Response Draft
To draft a response, create a file in /Drafts/ folder with format:
- Type: whatsapp_reply
- To: {item['sender']}
- Body: Your response here

Then move to /Approved/ for sending.

---
*Detected by WhatsAppWatcher*
'''

        action_path.write_text(content, encoding='utf-8')
        return action_path

    def send_message(self, recipient: str, message: str) -> bool:
        """Send a WhatsApp message (requires approval workflow)"""
        if not PLAYWRIGHT_AVAILABLE:
            self.logger.error("Playwright not available")
            return False

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch_persistent_context(
                    user_data_dir=str(self.session_path),
                    headless=False  # Show browser for manual confirmation
                )

                page = browser.new_page()
                page.goto('https://web.whatsapp.com')

                # Wait for chat list
                page.wait_for_selector('[data-testid="chat-list"]', timeout=30000)

                # Search for contact
                search_box = page.query_selector('[data-testid="chat-list-search"]')
                if search_box:
                    search_box.click()
                    search_box.fill(recipient)
                    time.sleep(2)

                    # Click on the contact
                    page.click(f'text={recipient}', timeout=5000)
                    time.sleep(1)

                    # Type message
                    message_box = page.query_selector('[data-testid="conversation-panel-body"] [contenteditable="true"]')
                    if message_box:
                        message_box.fill(message)
                        time.sleep(1)

                        # Send (requires manual confirmation)
                        send_button = page.query_selector('[data-testid="send"]')
                        if send_button:
                            self.logger.info(f"Message ready to send to {recipient}. Click send button to confirm.")
                            # Don't auto-send - wait for user confirmation
                            browser.close()
                            return True

                browser.close()
                return False

        except Exception as e:
            self.logger.error(f"Error sending message: {e}")
            return False


def main():
    """Run the WhatsApp watcher"""
    import argparse

    parser = argparse.ArgumentParser(description='WhatsApp Watcher for AI Employee')
    parser.add_argument('--vault', default='E:/hackhaton0_personal_ai_employe/AI_Employee_Vault',
                        help='Path to Obsidian vault')
    parser.add_argument('--session', help='Path to browser session directory')
    parser.add_argument('--interval', type=int, default=60,
                        help='Check interval in seconds')

    args = parser.parse_args()

    print(f"""
    ============================================
    WhatsApp Watcher Started
    ============================================
    Vault: {args.vault}
    Session: {args.session or 'Default'}
    Check Interval: {args.interval} seconds
    ============================================
    First run: Scan QR code in browser window
    Subsequent runs: Uses saved session
    ============================================
    Press Ctrl+C to stop
    ============================================
    """)

    watcher = WhatsAppWatcher(
        vault_path=args.vault,
        session_path=args.session,
        check_interval=args.interval
    )

    try:
        watcher.run()
    except KeyboardInterrupt:
        print("\nWhatsApp Watcher stopped by user")
        watcher.log_activity('WhatsApp Watcher stopped by user')


if __name__ == '__main__':
    main()
