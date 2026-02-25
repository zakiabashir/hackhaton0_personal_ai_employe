"""
Gmail Watcher - Monitors Gmail for new important emails
Requires Google API credentials setup
"""
import time
import base64
import logging
from pathlib import Path
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from base_watcher import BaseWatcher

try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False
    print("Google libraries not available. Install with: pip install google-api-python-client google-auth-oauthlib")


class GmailWatcher(BaseWatcher):
    """Watches Gmail for new important emails and creates action files"""

    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.send']

    # Keywords that trigger high priority
    URGENT_KEYWORDS = ['urgent', 'asap', 'important', 'deadline', 'emergency', 'critical']
    BUSINESS_KEYWORDS = ['invoice', 'payment', 'contract', 'proposal', 'quote', 'order']

    def __init__(self, vault_path: str, credentials_path: str = None, token_path: str = None, check_interval: int = 120):
        super().__init__(vault_path, check_interval)

        self.credentials_path = Path(credentials_path) if credentials_path else None
        self.token_path = Path(token_path) if token_path else self.vault_path / '.gmail_token.json'
        self.drafts = self.vault_path / 'Drafts'
        self.drafts.mkdir(exist_ok=True)

        if GOOGLE_AVAILABLE and self.credentials_path:
            self.service = self._authenticate()
            self.processed_ids = set()
            self._load_processed_ids()
        else:
            self.service = None
            self.logger.warning("Gmail service not available - running in demo mode")

    def _load_processed_ids(self):
        """Load previously processed message IDs"""
        state_file = self.vault_path / '.gmail_state.json'
        if state_file.exists():
            import json
            with open(state_file, 'r') as f:
                data = json.load(f)
                self.processed_ids = set(data.get('processed_ids', []))

    def _save_processed_ids(self):
        """Save processed message IDs to state file"""
        import json
        state_file = self.vault_path / '.gmail_state.json'
        with open(state_file, 'w') as f:
            json.dump({'processed_ids': list(self.processed_ids)}, f)

    def _authenticate(self):
        """Authenticate with Gmail API"""
        creds = None

        # Load existing token
        if self.token_path.exists():
            creds = Credentials.from_authorized_user_file(str(self.token_path), self.SCOPES)

        # If no valid credentials, get new ones
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            elif self.credentials_path.exists():
                flow = InstalledAppFlow.from_client_secrets_file(str(self.credentials_path), self.SCOPES)
                creds = flow.run_local_server(port=0)
            else:
                self.logger.error("No Gmail credentials found")
                return None

            # Save credentials
            with open(self.token_path, 'w') as token:
                token.write(creds.to_json())

        return build('gmail', 'v1', credentials=creds)

    def _determine_priority(self, message: dict) -> str:
        """Determine email priority based on content"""
        subject = message.get('subject', '').lower()
        snippet = message.get('snippet', '').lower()
        from_addr = message.get('from', '').lower()

        # Check for urgent keywords
        text = f"{subject} {snippet}"
        if any(kw in text for kw in self.URGENT_KEYWORDS):
            return 'high'

        # Check for business keywords
        if any(kw in text for kw in self.BUSINESS_KEYWORDS):
            return 'high'

        # Check for VIP senders
        if any(domain in from_addr for domain in ['@ceo.', '@exec.', '@important.']):
            return 'high'

        return 'medium'

    def _suggest_actions(self, message: dict) -> list:
        """Suggest actions based on email content"""
        actions = []
        subject = message.get('subject', '').lower()
        snippet = message.get('snippet', '').lower()

        # Common actions
        actions.append('- [ ] Read and analyze email content')

        # Context-specific actions
        if any(kw in subject + snippet for kw in ['invoice', 'payment']):
            actions.append('- [ ] Check invoice details')
            actions.append('- [ ] Verify payment amount')
            actions.append('- [ ] Draft payment approval if needed')

        elif any(kw in subject + snippet for kw in ['meeting', 'schedule', 'calendar']):
            actions.append('- [ ] Check calendar availability')
            actions.append('- [ ] Propose meeting times')
            actions.append('- [ ] Add to calendar if approved')

        elif any(kw in subject + snippet for kw in ['proposal', 'contract', 'agreement']):
            actions.append('- [ ] Review terms and conditions')
            actions.append('- [ ] Identify key clauses')
            actions.append('- [ ] Flag concerns for review')

        elif any(kw in subject + snippet for kw in ['question', 'help', 'support']):
            actions.append('- [ ] Draft helpful response')
            actions.append('- [ ] Get approval before sending')

        actions.append('- [ ] Archive after processing')

        return actions

    def check_for_updates(self) -> list:
        """Check for new unread important emails"""
        if not self.service:
            # Demo mode - return empty list
            return []

        try:
            # Search for unread messages from last day
            since = (datetime.now() - timedelta(days=1)).strftime('%Y/%m/%d')
            results = self.service.users().messages().list(
                userId='me',
                q=f'is:unread after:{since}'
            ).execute()

            messages = results.get('messages', [])
            new_messages = []

            for msg in messages:
                msg_id = msg['id']
                if msg_id not in self.processed_ids:
                    # Get full message details
                    full_msg = self.service.users().messages().get(
                        userId='me',
                        id=msg_id,
                        format='metadata',
                        metadataHeaders=['From', 'To', 'Subject', 'Date']
                    ).execute()

                    # Extract headers
                    headers = {h['name']: h['value'] for h in full_msg['payload'].get('headers', [])}

                    message_info = {
                        'id': msg_id,
                        'from': headers.get('From', 'Unknown'),
                        'to': headers.get('To', ''),
                        'subject': headers.get('Subject', 'No Subject'),
                        'date': headers.get('Date', ''),
                        'snippet': full_msg.get('snippet', ''),
                        'thread_id': full_msg.get('threadId', '')
                    }

                    new_messages.append(message_info)
                    self.processed_ids.add(msg_id)

            # Save state
            if new_messages:
                self._save_processed_ids()

            return new_messages

        except HttpError as e:
            self.logger.error(f'Gmail API error: {e}')
            return []
        except Exception as e:
            self.logger.error(f'Error checking emails: {e}')
            return []

    def create_action_file(self, item: dict) -> Path:
        """Create action file for email"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_subject = item['subject'][:50].replace(' ', '_').replace('/', '_').replace(':', '_')
        action_filename = f'EMAIL_{timestamp}_{safe_subject}.md'
        action_path = self.needs_action / action_filename

        priority = self._determine_priority(item)
        actions = self._suggest_actions(item)

        content = f'''---
type: email
message_id: {item['id']}
thread_id: {item['thread_id']}
from: {item['from']}
to: {item['to']}
subject: {item['subject']}
date: {item['date']}
priority: {priority}
status: pending
created: {datetime.now().isoformat()}
---

# Email Processing: {item['subject']}

## Email Information
- **From:** {item['from']}
- **To:** {item['to']}
- **Subject:** {item['subject']}
- **Date:** {item['date']}
- **Priority:** {priority.upper()}
- **Message ID:** {item['id']}

## Preview
{item['snippet'][:500]}...

## Suggested Actions
{chr(10).join(actions)}

## Reply Draft
To draft a reply, create a file in /Drafts/ folder and ask for approval.

---
*Detected by GmailWatcher*
'''

        action_path.write_text(content, encoding='utf-8')
        return action_path

    def draft_reply(self, message_id: str, to: str, subject: str, body: str) -> Path:
        """Create a draft reply file for approval"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        draft_filename = f'REPLY_DRAFT_{timestamp}.md'
        draft_path = self.drafts / draft_filename

        content = f'''---
type: reply_draft
original_message_id: {message_id}
to: {to}
subject: Re: {subject}
created: {datetime.now().isoformat()}
status: pending_approval
---

# Reply Draft: {subject}

## To: {to}

## Subject: Re: {subject}

## Draft Body:

{body}

---

## Approval Instructions

**To Approve and Send:**
1. Review the draft above
2. Move this file to `/Approved/` folder
3. The approved action will be executed

**To Edit:**
1. Modify the body above
2. Save changes
3. Move to `/Approved/` when ready

**To Reject:**
- Move this file to `/Rejected/` folder

---
*Created by GmailWatcher*
'''

        draft_path.write_text(content, encoding='utf-8')
        return draft_path

    def send_approved_reply(self, draft_content: str):
        """Send an approved reply via Gmail API"""
        if not self.service:
            self.logger.error("Gmail service not available")
            return False

        try:
            import re
            # Extract metadata from draft
            to_match = re.search(r'to:\s*(.+?)(?:\n|$)', draft_content, re.IGNORECASE)
            subject_match = re.search(r'subject:\s*(.+?)(?:\n|$)', draft_content, re.IGNORECASE)
            body_match = re.search(r'## Draft Body:\s*\n\n(.+?)(?:\n---\n|\Z)', draft_content, re.DOTALL)

            if not all([to_match, subject_match, body_match]):
                self.logger.error("Could not parse draft content")
                return False

            to_addr = to_match.group(1).strip()
            subject = subject_match.group(1).strip()
            body = body_match.group(1).strip()

            # Create message
            message = MIMEText(body)
            message['to'] = to_addr
            message['subject'] = subject

            # Send
            raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
            self.service.users().messages().send(
                userId='me',
                body={'raw': raw}
            ).execute()

            self.logger.info(f"Email sent to {to_addr}")
            return True

        except Exception as e:
            self.logger.error(f"Error sending email: {e}")
            return False


def main():
    """Run the Gmail watcher"""
    import argparse

    parser = argparse.ArgumentParser(description='Gmail Watcher for AI Employee')
    parser.add_argument('--vault', default='E:/hackhaton0_personal_ai_employe/AI_Employee_Vault',
                        help='Path to Obsidian vault')
    parser.add_argument('--credentials', help='Path to Gmail credentials.json')
    parser.add_argument('--token', help='Path to token file')
    parser.add_argument('--interval', type=int, default=120,
                        help='Check interval in seconds')

    args = parser.parse_args()

    print(f"""
    ============================================
    Gmail Watcher Started
    ============================================
    Vault: {args.vault}
    Check Interval: {args.interval} seconds
    ============================================
    Press Ctrl+C to stop
    ============================================
    """)

    watcher = GmailWatcher(
        vault_path=args.vault,
        credentials_path=args.credentials,
        token_path=args.token,
        check_interval=args.interval
    )

    try:
        watcher.run()
    except KeyboardInterrupt:
        print("\nGmail Watcher stopped by user")
        watcher.log_activity('Gmail Watcher stopped by user')


if __name__ == '__main__':
    main()
