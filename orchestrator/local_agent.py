#!/usr/bin/env python3
"""
Local Agent - Runs on Local Machine
Handles: Approvals, sending emails, posting social media, WhatsApp, payments

Local Agent Responsibilities:
- Review Cloud drafts
- Approve/Reject actions
- Send approved emails
- Post approved social media
- WhatsApp monitoring
- Payment/banking operations
- Update Dashboard (single-writer rule)
- Merge Cloud updates

Local Agent NEVER:
- Monitor emails continuously (Cloud handles)
- Generate content drafts (Cloud handles)
- Health monitoring (Cloud handles)
"""
import os
import sys
import json
import time
import logging
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List

# Local zone configuration
LOCAL_VAULT_PATH = os.getenv('LOCAL_VAULT_PATH', 'E:/hackhaton0_personal_ai_employe/AI_Employee_Vault')
APPROVED_FOLDER = Path(LOCAL_VAULT_PATH) / 'Approved'
REJECTED_FOLDER = Path(LOCAL_VAULT_PATH) / 'Rejected'
DRAFTS_FOLDER = Path(LOCAL_VAULT_PATH) / 'Drafts'
UPDATES_FOLDER = Path(LOCAL_VAULT_PATH) / 'Updates'
SIGNALS_FOLDER = Path(LOCAL_VAULT_PATH) / 'Signals'

# Local agent identification
AGENT_ID = "local_agent"
AGENT_NAME = "Local Agent"


class LocalAgent:
    """
    Local Agent - Runs on Local Machine
    Responsible for approvals, execution, and coordination
    """

    def __init__(self):
        self.vault_path = Path(LOCAL_VAULT_PATH)
        self.approved_folder = self.vault_path / 'Approved'
        self.rejected_folder = self.vault_path / 'Rejected'
        self.drafts_folder = self.vault_path / 'Drafts'
        self.updates_folder = self.vault_path / 'Updates'
        self.signals_folder = self.vault_path / 'Signals'
        self.in_progress_folder = self.vault_path / 'In_Progress' / AGENT_ID

        # Create folders
        for folder in [self.approved_folder, self.rejected_folder,
                       self.drafts_folder, self.updates_folder,
                       self.signals_folder, self.in_progress_folder]:
            folder.mkdir(parents=True, exist_ok=True)

        self.logger = self._setup_logger()
        self.running = True

        self.logger.info(f"Local Agent initialized: {AGENT_ID}")
        self.logger.info(f"Vault path: {self.vault_path}")

    def _setup_logger(self):
        """Setup logging for Local Agent"""
        logger = logging.getLogger('LocalAgent')
        logger.setLevel(logging.INFO)

        # Console handler
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)

        # File handler
        log_file = self.vault_path / 'Logs' / 'local_agent.log'
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)

        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console.setFormatter(formatter)
        file_handler.setFormatter(formatter)

        logger.addHandler(console)
        logger.addHandler(file_handler)

        return logger

    def sync_vault(self):
        """Sync vault via Git (pull Cloud updates)"""
        try:
            self.logger.debug("Syncing vault from Git...")

            result = subprocess.run(
                ['git', 'pull', 'origin', 'main'],
                cwd=self.vault_path,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                self.logger.debug("Vault synced from Cloud")
                return True
            else:
                self.logger.warning(f"Git sync failed: {result.stderr}")
                return False

        except Exception as e:
            self.logger.error(f"Vault sync error: {e}")
            return False

    def push_updates(self):
        """Push Local updates to Git for Cloud to see"""
        try:
            self.logger.debug("Pushing Local updates to Git...")

            subprocess.run(['git', 'add', '-A'], cwd=self.vault_path,
                          capture_output=True, timeout=30)

            commit_msg = f"Local Agent update - {datetime.now().isoformat()}"
            subprocess.run(['git', 'commit', '-m', commit_msg],
                          cwd=self.vault_path, capture_output=True, timeout=30)

            subprocess.run(['git', 'push', 'origin', 'main'],
                          cwd=self.vault_path, capture_output=True, timeout=60)

            self.logger.debug("Local updates pushed successfully")
            return True

        except Exception as e:
            self.logger.error(f"Push updates error: {e}")
            return False

    def check_cloud_updates(self) -> List[Dict]:
        """Check for updates from Cloud agent"""
        updates = []
        updates_folder = self.vault_path / 'Updates'

        if not updates_folder.exists():
            return updates

        for update_file in updates_folder.glob('update_*.json'):
            try:
                with open(update_file, 'r') as f:
                    update = json.load(f)
                    updates.append(update)

                # Process and remove
                self._process_cloud_update(update)
                update_file.unlink()

            except Exception as e:
                self.logger.error(f"Error processing update {update_file}: {e}")

        return updates

    def _process_cloud_update(self, update: Dict):
        """Process an update from Cloud agent"""
        update_type = update.get('type')
        data = update.get('data', {})

        self.logger.info(f"Processing Cloud update: {update_type}")

        if update_type == 'email_draft_created':
            self.logger.info(f"  Cloud created email draft: {data.get('draft_file')}")
            # Local will review this draft

        elif update_type == 'content_draft_created':
            self.logger.info(f"  Cloud created content draft: {data.get('draft_file')}")
            # Local will review this draft

        # Merge into Dashboard
        self._merge_to_dashboard(update)

    def _merge_to_dashboard(self, update: Dict):
        """Merge Cloud update into Dashboard (single-writer rule)"""
        dashboard_file = self.vault_path / 'Dashboard.md'

        if not dashboard_file.exists():
            return

        content = dashboard_file.read_text()

        # Add update to Dashboard
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
        update_entry = f"- {timestamp} - {update.get('type', 'unknown')} from Cloud\n"

        if '## Recent Activity' in content:
            # Add after Recent Activity header
            content = content.replace(
                '## Recent Activity\n',
                f'## Recent Activity\n{update_entry}'
            )

        dashboard_file.write_text(content)
        self.logger.debug("Merged update to Dashboard")

    def check_approved_actions(self) -> List[Path]:
        """Check for approved actions in /Approved folder"""
        return list(self.approved_folder.glob('*.md'))

    def execute_approved_action(self, action_file: Path):
        """Execute an approved action"""
        self.logger.info(f"Executing approved action: {action_file.name}")

        content = action_file.read_text()

        # Determine action type
        if 'email_draft' in content or 'EMAIL_DRAFT' in content:
            self._send_email(action_file)
        elif 'social_post_draft' in content or 'SOCIAL_POST' in content:
            self._post_social_media(action_file)
        elif 'content_draft' in content or 'CONTENT_DRAFT' in content:
            self._post_social_media(action_file)
        else:
            self.logger.warning(f"Unknown action type: {action_file.name}")

        # Move to Done after execution
        done_folder = self.vault_path / 'Done'
        done_folder.mkdir(exist_ok=True)
        subprocess.run(['mv', str(action_file), str(done_folder / action_file.name)],
                       check=False)

    def _send_email(self, draft_file: Path):
        """Send approved email draft"""
        self.logger.info(f"Sending email from draft: {draft_file.name}")

        # In production, this would use the Email MCP server
        self.logger.info("Email sent successfully (simulated)")

        # Write to execution log
        self._log_execution('email_sent', {'draft': draft_file.name})

    def _post_social_media(self, draft_file: Path):
        """Post approved social media content"""
        self.logger.info(f"Posting social media from draft: {draft_file.name}")

        # In production, this would use the Social MCP server
        self.logger.info("Social media post successful (simulated)")

        # Write to execution log
        self._log_execution('social_posted', {'draft': draft_file.name})

    def _log_execution(self, action_type: str, data: Dict):
        """Log execution action"""
        log_file = self.vault_path / 'Audit' / f'executed_actions_{datetime.now().strftime("%Y%m%d")}.jsonl'
        log_file.parent.mkdir(parents=True, exist_ok=True)

        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'agent': AGENT_ID,
            'action': action_type,
            'data': data
        }

        with open(log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')

    def check_cloud_health(self) -> Dict:
        """Check Cloud agent health from signals"""
        health_file = self.signals_folder / 'health.json'

        if not health_file.exists():
            return {'status': 'unknown', 'message': 'No health signal from Cloud'}

        try:
            with open(health_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    def claim_task(self, task_file: Path) -> bool:
        """
        Claim a task using claim-by-move rule
        Move from /Needs_Action to /In_Progress/local_agent/
        """
        try:
            if not task_file.exists():
                return False

            destination = self.in_progress_folder / task_file.name
            subprocess.run(['mv', str(task_file), str(destination)],
                         check=True)

            self.logger.info(f"Claimed task: {task_file.name}")
            return True

        except subprocess.CalledProcessError:
            return False

    def run_interactive(self):
        """
        Run Local Agent in interactive mode
        Periodically check for Cloud updates and approved actions
        """
        self.logger.info("Local Agent starting in interactive mode...")

        last_sync = 0
        last_health_check = 0

        while self.running:
            try:
                current_time = time.time()

                # Sync vault periodically (every 60 seconds)
                if current_time - last_sync >= 60:
                    self.sync_vault()
                    last_sync = current_time

                # Check Cloud updates
                updates = self.check_cloud_updates()
                if updates:
                    self.logger.info(f"Processed {len(updates)} updates from Cloud")

                # Check approved actions
                approved = self.check_approved_actions()
                for action in approved:
                    self.execute_approved_action(action)

                # Check Cloud health (every 5 minutes)
                if current_time - last_health_check >= 300:
                    health = self.check_cloud_health()
                    self.logger.info(f"Cloud health: {health.get('status', 'unknown')}")
                    last_health_check = current_time

                # Push updates periodically
                if current_time - last_sync >= 120:
                    self.push_updates()

                # Sleep
                time.sleep(10)

            except KeyboardInterrupt:
                self.logger.info("Local Agent stopping...")
                self.running = False
            except Exception as e:
                self.logger.error(f"Error in main loop: {e}")
                time.sleep(30)

        self.logger.info("Local Agent stopped")


def main():
    """Main entry point"""
    agent = LocalAgent()

    # Run in interactive mode
    agent.run_interactive()


if __name__ == '__main__':
    main()
