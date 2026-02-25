#!/usr/bin/env python3
"""
Claim-by-Move System - Platinum Tier
Prevents double-work by having agents claim tasks via file movement

Rule: First agent to move an item from /Needs_Action to /In_Progress/<agent>/ owns it.
Other agents must ignore items that are already claimed.
"""
import os
import json
import time
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional


class ClaimByMove:
    """
    Claim-by-move task ownership system
    Prevents multiple agents from working on the same task
    """

    def __init__(self, vault_path: str, agent_id: str):
        self.vault_path = Path(vault_path)
        self.agent_id = agent_id
        self.needs_action = self.vault_path / 'Needs_Action'
        self.in_progress = self.vault_path / 'In_Progress'
        self.agent_folder = self.in_progress / agent_id
        self.logger = self._setup_logger()

        # Create agent folder
        self.agent_folder.mkdir(parents=True, exist_ok=True)

    def _setup_logger(self):
        logger = logging.getLogger(f'ClaimByMove-{self.agent_id}')
        logger.setLevel(logging.INFO)

        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        return logger

    def claim_task(self, task_file: Path) -> bool:
        """
        Attempt to claim a task by moving it

        Returns True if claim successful, False if already claimed
        """
        if not task_file.exists():
            self.logger.warning(f"Task file not found: {task_file}")
            return False

        # Check if task matches this agent's responsibilities
        if not self._should_claim(task_file):
            self.logger.debug(f"Task not for this agent: {task_file.name}")
            return False

        try:
            # Attempt to move (atomic operation)
            destination = self.agent_folder / task_file.name

            # Use rename for atomic move
            task_file.rename(destination)

            # Create claim record
            self._record_claim(destination)

            self.logger.info(f"Claimed task: {task_file.name}")
            return True

        except FileNotFoundError:
            # File was moved by another agent (race condition)
            self.logger.debug(f"Task already claimed: {task_file.name}")
            return False

        except Exception as e:
            self.logger.error(f"Error claiming task: {e}")
            return False

    def _should_claim(self, task_file: Path) -> bool:
        """
        Check if this agent should claim the task
        Based on agent responsibilities (Cloud vs Local)
        """
        content = task_file.read_text()

        # Cloud agent responsibilities
        if self.agent_id == 'cloud_agent':
            cloud_keywords = ['email', 'gmail', 'facebook', 'instagram',
                           'twitter', 'social', 'linkedin', 'content', 'calendar']
            return any(kw in content.lower() for kw in cloud_keywords)

        # Local agent responsibilities
        elif self.agent_id == 'local_agent':
            local_keywords = ['approval', 'whatsapp', 'payment', 'bank',
                           'send', 'post', 'execute']
            return any(kw in content.lower() for kw in local_keywords)

        return False

    def _record_claim(self, claimed_file: Path):
        """Record the claim for audit trail"""
        claim_record = {
            'task': claimed_file.name,
            'claimed_by': self.agent_id,
            'claimed_at': datetime.now().isoformat(),
            'original_path': f"/Needs_Action/{claimed_file.name}"
        }

        record_file = claimed_file.with_suffix('.claim.json')
        record_file.write_text(json.dumps(claim_record, indent=2))

    def check_available_tasks(self) -> List[Path]:
        """Get list of available (unclaimed) tasks"""
        if not self.needs_action.exists():
            return []

        return list(self.needs_action.glob('*.md'))

    def check_claimed_tasks(self) -> List[Path]:
        """Get list of tasks claimed by this agent"""
        if not self.agent_folder.exists():
            return []

        return list(self.agent_folder.glob('*.md'))

    def release_task(self, task_file: Path, destination_folder: str = 'Done'):
        """
        Release a claimed task by moving to destination folder
        Call when task is complete or should be reassigned
        """
        if not task_file.exists():
            return

        destination = self.vault_path / destination_folder
        destination.mkdir(parents=True, exist_ok=True)

        try:
            # Move to destination
            final_dest = destination / task_file.name
            task_file.rename(final_dest)

            self.logger.info(f"Released task to {destination_folder}: {task_file.name}")

        except Exception as e:
            self.logger.error(f"Error releasing task: {e}")

    def get_all_claims(self) -> Dict[str, List[str]]:
        """Get all current claims by all agents"""
        claims = {}

        if not self.in_progress.exists():
            return claims

        for agent_folder in self.in_progress.iterdir():
            if agent_folder.is_dir():
                agent_id = agent_folder.name
                claimed = [f.name for f in agent_folder.glob('*.md')]
                claims[agent_id] = claimed

        return claims

    def check_agent_status(self, agent_id: str = None) -> Dict:
        """Check status of an agent's current work"""
        if agent_id:
            agent_folder = self.in_progress / agent_id
        else:
            agent_folder = self.agent_folder

        if not agent_folder.exists():
            return {'agent': agent_id or self.agent_id, 'claimed': 0}

        claimed_files = list(agent_folder.glob('*.md'))

        return {
            'agent': agent_id or self.agent_id,
            'claimed': len(claimed_files),
            'tasks': [f.name for f in claimed_files]
        }


def main():
    """CLI for claim-by-move system"""
    import argparse

    parser = argparse.ArgumentParser(description='Claim-by-Move System')
    parser.add_argument('--vault', default='AI_Employee_Vault', help='Path to vault')
    parser.add_argument('--agent', required=True, help='Agent ID (cloud_agent or local_agent)')
    parser.add_argument('--action', choices=['list', 'claim', 'status', 'release'],
                       default='list', help='Action to perform')
    parser.add_argument('--task', help='Task file name (for claim/release)')

    args = parser.parse_args()

    system = ClaimByMove(args.vault, args.agent)

    if args.action == 'list':
        available = system.check_available_tasks()
        print(f"Available tasks for {args.agent}:")
        for task in available:
            print(f"  - {task.name}")

    elif args.action == 'claim':
        if not args.task:
            print("Error: --task required for claim action")
            return

        task_file = system.needs_action / args.task
        if system.claim_task(task_file):
            print(f"Successfully claimed: {args.task}")
        else:
            print(f"Failed to claim or not eligible: {args.task}")

    elif args.action == 'status':
        status = system.check_agent_status()
        print(json.dumps(status, indent=2))

        # Show all agents
        all_claims = system.get_all_claims()
        print("\nAll agent claims:")
        for agent, tasks in all_claims.items():
            print(f"  {agent}: {len(tasks)} tasks")

    elif args.action == 'release':
        if not args.task:
            print("Error: --task required for release action")
            return

        task_file = system.agent_folder / args.task
        system.release_task(task_file, 'Done')
        print(f"Released task: {args.task}")


if __name__ == '__main__':
    main()
