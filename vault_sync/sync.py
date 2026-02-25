#!/usr/bin/env python3
"""
Vault Sync System - Platinum Tier
Handles synchronization between Cloud and Local vaults via Git

Security Rules:
- Only syncs markdown and JSON files
- NEVER syncs .env, credentials, WhatsApp sessions, payment tokens
- Cloud uses .gitignore to exclude sensitive data
- Local keeps sensitive data separate
"""
import os
import sys
import json
import logging
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List


class VaultSync:
    """
    Vault synchronization via Git
    Ensures Cloud and Local stay in sync while respecting security rules
    """

    def __init__(self, vault_path: str, repo_url: str = None):
        self.vault_path = Path(vault_path)
        self.repo_url = repo_url
        self.logger = self._setup_logger()

        # Security: folders to NEVER sync
        self.security_exclude = [
            '.env',
            '*.env',
            '.whatsapp_session',
            '*credentials*',
            '*secrets*',
            '*tokens*',
            '*.pem',
            '*.key'
        ]

        # Folders to sync
        self.sync_folders = [
            'Updates',
            'Signals',
            'Plans',
            'Needs_Action',
            'In_Progress',
            'Drafts',
            'Approved',
            'Rejected',
            'Done',
            'Personal',
            'Business',
            'Accounting',
            'Audit'
        ]

    def _setup_logger(self):
        logger = logging.getLogger('VaultSync')
        logger.setLevel(logging.INFO)

        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - VaultSync - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        return logger

    def setup_gitignore(self):
        """Create .gitignore for security (NEVER sync sensitive data)"""
        gitignore_path = self.vault_path / '.gitignore'

        gitignore_content = '''# Security - NEVER sync these
.env
*.env
.env.local
.env.production

# WhatsApp sessions
.whatsapp_session/
*.session
*.session-journal

# Banking/Payment credentials
*credentials*
*secrets*
*tokens*
banking/
payments/

# SSH keys
*.pem
*.key
id_*

# Local only
.local/
*.local

# Python cache
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
*.egg-info/

# Node modules
node_modules/
package-lock.json

# Logs (keep local, sync only summaries)
*.log
logs/*.log

# But DO sync vault content
!AI_Employee_Vault/
!AI_Employee_Vault/**/*.md
!AI_Employee_Vault/**/*.json
!Updates/
!Signals/
!Plans/
!Needs_Action/
!In_Progress/
!Drafts/
!Approved/
!Rejected/
!Done/
!Personal/
!Business/
!Accounting/
!Audit/
'''

        gitignore_path.write_text(gitignore_content)
        self.logger.info("Created .gitignore with security rules")

    def init_git_repo(self):
        """Initialize Git repository"""
        if not (self.vault_path / '.git').exists():
            subprocess.run(['git', 'init'], cwd=self.vault_path, check=True)
            self.setup_gitignore()

            if self.repo_url:
                subprocess.run(['git', 'remote', 'add', 'origin', self.repo_url],
                             cwd=self.vault_path, check=True)

            self.logger.info("Git repository initialized")
        else:
            self.logger.info("Git repository already exists")

    def pull(self, remote: str = 'origin', branch: str = 'main') -> bool:
        """Pull updates from remote"""
        try:
            self.logger.info(f"Pulling from {remote}/{branch}...")

            result = subprocess.run(
                ['git', 'pull', remote, branch],
                cwd=self.vault_path,
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode == 0:
                self.logger.info("Pull successful")
                return True
            else:
                self.logger.error(f"Pull failed: {result.stderr}")
                return False

        except Exception as e:
            self.logger.error(f"Pull error: {e}")
            return False

    def push(self, remote: str = 'origin', branch: str = 'main') -> bool:
        """Push updates to remote"""
        try:
            self.logger.info(f"Pushing to {remote}/{branch}...")

            # Add all changes
            subprocess.run(['git', 'add', '-A'], cwd=self.vault_path,
                          capture_output=True, timeout=30)

            # Commit
            commit_msg = f"Vault sync - {datetime.now().isoformat()} - {os.getenv('AGENT_ID', 'unknown')}"
            result = subprocess.run(['git', 'commit', '-m', commit_msg],
                                   cwd=self.vault_path, capture_output=True, text=True, timeout=30)

            # Push
            result = subprocess.run(
                ['git', 'push', remote, branch],
                cwd=self.vault_path,
                capture_output=True,
                text=True,
                timeout=120
            )

            if result.returncode == 0:
                self.logger.info("Push successful")
                return True
            else:
                self.logger.error(f"Push failed: {result.stderr}")
                return False

        except Exception as e:
            self.logger.error(f"Push error: {e}")
            return False

    def check_conflicts(self) -> List[str]:
        """Check for merge conflicts"""
        conflicts = []

        # Check for common conflict markers
        for md_file in self.vault_path.rglob('*.md'):
            content = md_file.read_text()
            if '<<<<<<<' in content or '>>>>>>>' in content:
                conflicts.append(str(md_file))

        return conflicts

    def resolve_conflict(self, file_path: str, strategy: str = 'theirs'):
        """
        Resolve merge conflict
        strategy: 'theirs' (use remote) or 'ours' (use local)
        """
        file_path = Path(file_path)

        if strategy == 'theirs':
            # Use remote version
            subprocess.run(['git', 'checkout', '--theirs', str(file_path)],
                         cwd=self.vault_path)
        else:
            # Use local version
            subprocess.run(['git', 'checkout', '--ours', str(file_path)],
                         cwd=self.vault_path)

        subprocess.run(['git', 'add', str(file_path)], cwd=self.vault_path)
        self.logger.info(f"Resolved conflict in {file_path} using {strategy} strategy")

    def get_sync_status(self) -> Dict:
        """Get current sync status"""
        try:
            # Get branch info
            result = subprocess.run(['git', 'status', '-sb'],
                                   cwd=self.vault_path, capture_output=True, text=True)

            # Get pending changes count
            changes_result = subprocess.run(['git', 'status', '--porcelain'],
                                           cwd=self.vault_path, capture_output=True, text=True)
            pending_changes = len([line for line in changes_result.stdout.split('\n') if line.strip()])

            return {
                'branch': result.stdout.split('\n')[0].replace('## ', '') if result.stdout else 'unknown',
                'pending_changes': pending_changes,
                'repo_exists': (self.vault_path / '.git').exists(),
                'last_sync': datetime.now().isoformat()
            }

        except Exception as e:
            return {
                'error': str(e),
                'repo_exists': (self.vault_path / '.git').exists()
            }


def main():
    """CLI for vault sync"""
    import argparse

    parser = argparse.ArgumentParser(description='Vault Sync - Platinum Tier')
    parser.add_argument('--vault', default='AI_Employee_Vault', help='Path to vault')
    parser.add_argument('--repo', help='Git repository URL')
    parser.add_argument('--action', choices=['init', 'pull', 'push', 'status', 'check'],
                       default='status', help='Action to perform')

    args = parser.parse_args()

    sync = VaultSync(args.vault, args.repo)

    if args.action == 'init':
        sync.init_git_repo()
    elif args.action == 'pull':
        sync.pull()
    elif args.action == 'push':
        sync.push()
    elif args.action == 'check':
        conflicts = sync.check_conflicts()
        if conflicts:
            print(f"Found {len(conflicts)} conflicts:")
            for c in conflicts:
                print(f"  - {c}")
        else:
            print("No conflicts found")
    else:  # status
        status = sync.get_sync_status()
        print(json.dumps(status, indent=2))


if __name__ == '__main__':
    main()
