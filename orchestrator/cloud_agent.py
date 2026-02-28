#!/usr/bin/env python3
"""
Cloud Agent - Runs on Cloud VM 24/7
Handles: Email triage, draft generation, content creation, health monitoring

Cloud Agent Responsibilities:
- Monitor emails continuously
- Draft email replies (NEVER SEND)
- Draft social media posts (NEVER POST)
- Generate content calendars
- Create execution plans
- Write updates to /Updates/ folder
- Health monitoring
- Sync vault via Git

Cloud Agent NEVER:
- Sends emails (requires Local approval)
- Posts to social media (requires Local approval)
- Accesses WhatsApp sessions
- Processes payments/banking
"""
import os
import sys
import json
import time
import logging
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'watchers'))

# Cloud zone configuration
CLOUD_VAULT_PATH = os.getenv('CLOUD_VAULT_PATH', os.path.expanduser('~/ai-employee/vault/AI_Employee_Vault'))
UPDATES_FOLDER = Path(CLOUD_VAULT_PATH) / 'Updates'
SIGNALS_FOLDER = Path(CLOUD_VAULT_PATH) / 'Signals'
DRAFTS_FOLDER = Path(CLOUD_VAULT_PATH) / 'Drafts'
PLANS_FOLDER = Path(CLOUD_VAULT_PATH) / 'Plans'
NEEDS_ACTION_FOLDER = Path(CLOUD_VAULT_PATH) / 'Needs_Action'

# Cloud agent identification
AGENT_ID = "cloud_agent"
AGENT_NAME = "Cloud Agent"

# Sync interval (seconds)
VAULT_SYNC_INTERVAL = 60
HEALTH_CHECK_INTERVAL = 300


class CloudAgent:
    """
    Cloud Agent - Runs on Cloud VM 24/7
    Responsible for monitoring, drafting, and coordination
    """

    def __init__(self):
        self.vault_path = Path(CLOUD_VAULT_PATH)
        self.updates_folder = self.vault_path / 'Updates'
        self.signals_folder = self.vault_path / 'Signals'
        self.drafts_folder = self.vault_path / 'Drafts'
        self.plans_folder = self.vault_path / 'Plans'
        self.in_progress_folder = self.vault_path / 'In_Progress' / AGENT_ID

        # Create folders
        for folder in [self.updates_folder, self.signals_folder,
                       self.drafts_folder, self.plans_folder,
                       self.in_progress_folder]:
            folder.mkdir(parents=True, exist_ok=True)

        self.logger = self._setup_logger()
        self.running = True

        self.logger.info(f"Cloud Agent initialized: {AGENT_ID}")
        self.logger.info(f"Vault path: {self.vault_path}")

    def _setup_logger(self):
        """Setup logging for Cloud Agent"""
        logger = logging.getLogger('CloudAgent')
        logger.setLevel(logging.INFO)

        # Console handler
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)

        # File handler
        log_file = self.vault_path / 'Logs' / 'cloud_agent.log'
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
        """Sync vault via Git (pull any Local updates)"""
        try:
            self.logger.debug("Syncing vault via Git...")

            # Git pull to get updates from Local
            result = subprocess.run(
                ['git', 'pull', 'origin', 'main'],
                cwd=self.vault_path,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                self.logger.debug("Vault synced successfully")
                return True
            else:
                self.logger.warning(f"Git sync failed: {result.stderr}")
                return False

        except Exception as e:
            self.logger.error(f"Vault sync error: {e}")
            return False

    def push_updates(self):
        """Push Cloud updates to Git for Local to see"""
        try:
            self.logger.debug("Pushing updates to Git...")

            # Add, commit, and push
            subprocess.run(
                ['git', 'add', '-A'],
                cwd=self.vault_path,
                capture_output=True,
                timeout=30
            )

            commit_msg = f"Cloud Agent update - {datetime.now().isoformat()}"
            subprocess.run(
                ['git', 'commit', '-m', commit_msg],
                cwd=self.vault_path,
                capture_output=True,
                timeout=30
            )

            subprocess.run(
                ['git', 'push', 'origin', 'main'],
                cwd=self.vault_path,
                capture_output=True,
                timeout=60
            )

            self.logger.debug("Updates pushed successfully")
            return True

        except Exception as e:
            self.logger.error(f"Push updates error: {e}")
            return False

    def claim_task(self, task_file: Path) -> bool:
        """
        Claim a task using claim-by-move rule
        Move from /Needs_Action to /In_Progress/cloud_agent/
        """
        try:
            if not task_file.exists():
                return False

            # Move to in_progress
            destination = self.in_progress_folder / task_file.name
            subprocess.run(['mv', str(task_file), str(destination)],
                         check=True)

            self.logger.info(f"Claimed task: {task_file.name}")
            return True

        except subprocess.CalledProcessError:
            # Another agent may have claimed it
            return False

    def check_new_tasks(self) -> List[Path]:
        """Check for new tasks in Needs_Action"""
        tasks = []
        needs_action = self.vault_path / 'Needs_Action'

        if not needs_action.exists():
            return tasks

        # Find tasks (not already in progress)
        for task_file in needs_action.glob('*.md'):
            # Check if email or social (Cloud responsibilities)
            content = task_file.read_text()
            if self._is_cloud_responsibility(content):
                tasks.append(task_file)

        return tasks

    def _is_cloud_responsibility(self, content: str) -> bool:
        """Check if task is Cloud agent's responsibility"""
        content_lower = content.lower()

        # Cloud handles: emails, social media drafts, content generation
        cloud_keywords = ['email', 'gmail', 'facebook', 'instagram', 'twitter',
                         'social', 'linkedin', 'draft', 'content', 'calendar']

        return any(kw in content_lower for kw in cloud_keywords)

    def process_task(self, task_file: Path):
        """Process a claimed task"""
        self.logger.info(f"Processing task: {task_file.name}")

        # Read task content
        content = task_file.read_text()

        # Determine action
        if 'email' in content.lower():
            self._draft_email_reply(task_file)
        elif 'social' in content.lower() or 'content' in content.lower():
            self._create_content_draft(task_file)
        else:
            self.logger.warning(f"Unknown task type: {task_file.name}")

        # Move to Done after processing
        done_folder = self.vault_path / 'Done'
        done_folder.mkdir(exist_ok=True)
        subprocess.run(['mv', str(task_file), str(done_folder / task_file.name)],
                       check=False)

    def _draft_email_reply(self, task_file: Path):
        """Draft an email reply"""
        # Create draft in Drafts folder
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        draft_name = f"EMAIL_DRAFT_CLOUD_{timestamp}.md"
        draft_path = self.drafts_folder / draft_name

        draft_content = f'''---
type: email_draft
created_by: cloud_agent
created_at: {datetime.now().isoformat()}
status: pending_approval
---

# Email Reply Draft (Cloud Generated)

**Original Task:** {task_file.name}

## Draft Reply

[Draft email content would be generated here by Claude]

---

## Cloud Agent Notes
- This is a draft only
- Local agent must review and approve
- Move to /Approved/ to send
- Move to /Rejected/ to cancel

---
*Drafted by Cloud Agent*
*Requires Local approval to send*
'''

        draft_path.write_text(draft_content)
        self.logger.info(f"Email draft created: {draft_name}")

        # Write update
        self._write_update('email_draft_created', {
            'draft_file': draft_name,
            'original_task': task_file.name
        })

    def _create_content_draft(self, task_file: Path):
        """Create social media content draft"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        draft_name = f"CONTENT_DRAFT_CLOUD_{timestamp}.md"
        draft_path = self.drafts_folder / draft_name

        draft_content = f'''---
type: social_content_draft
created_by: cloud_agent
created_at: {datetime.now().isoformat()}
status: pending_approval
---

# Social Media Content Draft (Cloud Generated)

**Original Task:** {task_file.name}

## Platform Options:
- [ ] Facebook
- [ ] Instagram
- [ ] Twitter/X
- [ ] LinkedIn

## Draft Content:

[Content would be generated here by Claude]

## Suggested Hashtags:
#Business #Automation #AI

---

## Cloud Agent Notes
- This is a draft only
- Local agent must review and approve
- Move to /Approved/ to post
- Move to /Rejected/ to cancel

---
*Drafted by Cloud Agent*
*Requires Local approval to post*
'''

        draft_path.write_text(draft_content)
        self.logger.info(f"Content draft created: {draft_name}")

        # Write update
        self._write_update('content_draft_created', {
            'draft_file': draft_name,
            'original_task': task_file.name
        })

    def _write_update(self, update_type: str, data: Dict):
        """Write an update for Local agent to see"""
        update_file = self.updates_folder / f"update_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        update = {
            'timestamp': datetime.now().isoformat(),
            'agent': AGENT_ID,
            'type': update_type,
            'data': data
        }

        with open(update_file, 'w') as f:
            json.dump(update, f, indent=2)

        self.logger.debug(f"Update written: {update_file.name}")

    def write_health_status(self):
        """Write health status to /Signals/ folder"""
        health_file = self.signals_folder / 'health.json'

        # Get system stats
        try:
            import psutil
            cpu_percent = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
        except ImportError:
            cpu_percent = 0
            memory = type('obj', (object,), {'percent': 0})()
            disk = type('obj', (object,), {'used': 0, 'total': 1})()

        # Count pending items
        drafts_count = len(list(self.drafts_folder.glob('*.md'))) if self.drafts_folder.exists() else 0

        health = {
            'timestamp': datetime.now().isoformat(),
            'agent': AGENT_ID,
            'status': 'healthy',
            'uptime_seconds': int(time.time() - self.start_time) if hasattr(self, 'start_time') else 0,
            'system': {
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'disk_used_gb': round(disk.used / (1024**3), 2),
                'disk_total_gb': round(disk.total / (1024**3), 2)
            },
            'tasks': {
                'drafts_awaiting_approval': drafts_count,
                'in_progress': len(list(self.in_progress_folder.glob('*.md'))) if self.in_progress_folder.exists() else 0
            },
            'sync': {
                'last_sync': datetime.now().isoformat(),
                'git_status': 'connected'
            }
        }

        with open(health_file, 'w') as f:
            json.dump(health, f, indent=2)

        self.logger.debug("Health status written")

    def run(self):
        """Main Cloud Agent loop"""
        self.logger.info("Cloud Agent starting...")
        self.start_time = time.time()

        last_sync = 0
        last_health = 0

        while self.running:
            try:
                current_time = time.time()

                # Sync vault periodically
                if current_time - last_sync >= VAULT_SYNC_INTERVAL:
                    self.sync_vault()
                    last_sync = current_time

                # Check for new tasks
                new_tasks = self.check_new_tasks()
                for task in new_tasks:
                    if self.claim_task(task):
                        self.process_task(task)

                # Write health status
                if current_time - last_health >= HEALTH_CHECK_INTERVAL:
                    self.write_health_status()
                    self.push_updates()
                    last_health = current_time

                # Sleep
                time.sleep(10)

            except KeyboardInterrupt:
                self.logger.info("Cloud Agent stopping...")
                self.running = False
            except Exception as e:
                self.logger.error(f"Error in main loop: {e}")
                time.sleep(30)

        self.logger.info("Cloud Agent stopped")


def main():
    """Main entry point"""
    try:
        import psutil
    except ImportError:
        print("Installing psutil...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'psutil'])
        import psutil

    agent = CloudAgent()
    agent.run()


if __name__ == '__main__':
    main()
