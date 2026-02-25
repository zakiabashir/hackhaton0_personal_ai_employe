"""
Approval Workflow Watcher - Monitors /Approved folder and executes approved actions
Implements Human-in-the-Loop approval workflow
"""
import time
import json
import logging
from pathlib import Path
from datetime import datetime
from base_watcher import BaseWatcher


class ApprovalWatcher(BaseWatcher):
    """
    Watches the /Approved folder and executes approved actions.
    Implements Human-in-the-Loop workflow for sensitive actions.
    """

    def __init__(self, vault_path: str, check_interval: int = 30):
        super().__init__(vault_path, check_interval)
        self.approved = self.vault_path / 'Approved'
        self.rejected = self.vault_path / 'Rejected'
        self.done = self.vault_path / 'Done'
        self.executed_log = self.vault_path / 'Logs' / 'executed_actions.jsonl'

        # Ensure folders exist
        self.approved.mkdir(exist_ok=True)
        self.rejected.mkdir(exist_ok=True)

        self.processed_approvals = set()
        self.logger.info(f"Monitoring Approved folder: {self.approved}")

    def check_for_updates(self) -> list:
        """Check for newly approved action files"""
        approved_items = []

        if not self.approved.exists():
            return approved_items

        for filepath in self.approved.glob('*.md'):
            if filepath.name not in self.processed_approvals:
                approved_items.append(filepath)
                self.processed_approvals.add(filepath.name)
                self.logger.info(f"Found approved action: {filepath.name}")

        return approved_items

    def create_action_file(self, item: Path) -> Path:
        """Process approved action and create execution record"""
        content = item.read_text(encoding='utf-8')

        # Parse frontmatter
        frontmatter = self._parse_frontmatter(content)

        action_type = frontmatter.get('type', 'unknown')
        status = frontmatter.get('status', 'approved')

        execution_record = self._create_execution_record(item, frontmatter, content)

        # Execute the action based on type
        result = self._execute_action(action_type, frontmatter, content)

        # Create execution record in Needs_Action for Claude to process
        record_filename = f'EXECUTED_{datetime.now().strftime("%Y%m%d_%H%M%S")}_{action_type}.md'
        record_path = self.needs_action / record_filename

        record_content = f'''---
type: executed_action
original_type: {action_type}
original_file: {item.name}
executed_at: {datetime.now().isoformat()}
result: {result['status']}
---

# Executed Action: {item.name}

## Original Request
**Type:** {action_type}
**Approved At:** {frontmatter.get('approved_at', 'unknown')}

## Action Details
{self._format_action_details(frontmatter)}

## Execution Result
**Status:** {result['status']}
**Message:** {result['message']}

## Next Steps
- [ ] Verify action completed successfully
- [ ] Move original file to /Done
- [ ] Update any relevant tracking

---
*Processed by ApprovalWatcher*
'''

        record_path.write_text(record_content, encoding='utf-8')

        # Log execution
        self._log_execution(item.name, action_type, result)

        return record_path

    def _parse_frontmatter(self, content: str) -> dict:
        """Parse YAML frontmatter from markdown file"""
        lines = content.split('\n')

        if not lines[0].startswith('---'):
            return {}

        frontmatter = {}
        i = 1
        while i < len(lines) and not lines[i].startswith('---'):
            line = lines[i].strip()
            if ':' in line:
                key, value = line.split(':', 1)
                frontmatter[key.strip()] = value.strip()
            i += 1

        return frontmatter

    def _create_execution_record(self, item: Path, frontmatter: dict, content: str) -> dict:
        """Create a record of the approved action"""
        return {
            'file': str(item),
            'type': frontmatter.get('type'),
            'timestamp': datetime.now().isoformat(),
            'frontmatter': frontmatter
        }

    def _format_action_details(self, frontmatter: dict) -> str:
        """Format action details for display"""
        details = []

        for key, value in frontmatter.items():
            if key not in ['type', 'status', 'created']:
                details.append(f'- **{key}:** {value}')

        return '\n'.join(details) if details else 'No additional details'

    def _execute_action(self, action_type: str, frontmatter: dict, content: str) -> dict:
        """Execute the approved action based on type"""

        try:
            if action_type == 'email_draft':
                return self._execute_email(frontmatter, content)
            elif action_type == 'linkedin_post_draft':
                return self._execute_linkedin_post(frontmatter, content)
            elif action_type == 'reply_draft':
                return self._execute_reply(frontmatter, content)
            elif action_type == 'payment':
                return self._execute_payment(frontmatter, content)
            else:
                return {
                    'status': 'pending_manual',
                    'message': f'Action type {action_type} requires manual execution or custom handler'
                }

        except Exception as e:
            self.logger.error(f"Error executing action: {e}")
            return {
                'status': 'error',
                'message': str(e)
            }

    def _execute_email(self, frontmatter: dict, content: str) -> dict:
        """Execute email sending (placeholder for MCP integration)"""
        to = frontmatter.get('to', 'unknown')
        subject = frontmatter.get('subject', 'no subject')

        self.logger.info(f"Would send email to: {to}")

        return {
            'status': 'executed',
            'message': f'Email queued for sending to {to}. Use Email MCP server to send.',
            'to': to,
            'subject': subject
        }

    def _execute_linkedin_post(self, frontmatter: dict, content: str) -> dict:
        """Execute LinkedIn post (placeholder for automation)"""
        topic = frontmatter.get('topic', 'General')

        self.logger.info(f"Would post to LinkedIn about: {topic}")

        return {
            'status': 'executed',
            'message': f'LinkedIn post queued for posting. Use LinkedIn automation to publish.',
            'topic': topic
        }

    def _execute_reply(self, frontmatter: dict, content: str) -> dict:
        """Execute email reply (placeholder for MCP integration)"""
        to = frontmatter.get('to', 'unknown')
        message_id = frontmatter.get('original_message_id', 'unknown')

        self.logger.info(f"Would send reply to: {to}")

        return {
            'status': 'executed',
            'message': f'Reply queued for sending. Use Gmail watcher to send.',
            'to': to,
            'message_id': message_id
        }

    def _execute_payment(self, frontmatter: dict, content: str) -> dict:
        """Execute payment (always requires manual confirmation)"""
        amount = frontmatter.get('amount', '0')
        recipient = frontmatter.get('recipient', 'unknown')

        return {
            'status': 'requires_manual_confirmation',
            'message': f'Payment of {amount} to {recipient} requires manual execution through banking portal.',
            'amount': amount,
            'recipient': recipient
        }

    def _log_execution(self, filename: str, action_type: str, result: dict):
        """Log execution to JSONL file"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'filename': filename,
            'action_type': action_type,
            'result': result
        }

        with open(self.executed_log, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')

        self.log_activity(f"Executed {action_type} from {filename}: {result['status']}")


def main():
    """Run the approval watcher"""
    import argparse

    parser = argparse.ArgumentParser(description='Approval Workflow Watcher')
    parser.add_argument('--vault', default='E:/hackhaton0_personal_ai_employe/AI_Employee_Vault',
                        help='Path to Obsidian vault')
    parser.add_argument('--interval', type=int, default=30,
                        help='Check interval in seconds')

    args = parser.parse_args()

    print(f"""
    ============================================
    Approval Workflow Watcher Started
    ============================================
    Vault: {args.vault}
    Approved Folder: {args.vault}/Approved
    Check Interval: {args.interval} seconds
    ============================================
    Move approved files to /Approved/ to execute
    ============================================
    """)

    watcher = ApprovalWatcher(vault_path=args.vault, check_interval=args.interval)

    try:
        watcher.run()
    except KeyboardInterrupt:
        print("\nApproval Watcher stopped by user")
        watcher.log_activity('Approval Watcher stopped by user')


if __name__ == '__main__':
    main()
