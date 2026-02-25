"""
Reasoning Loop - Generates Plan.md files for multi-step tasks
Implements autonomous task planning and execution
"""
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict


class ReasoningLoop:
    """
    Generates and manages Plan.md files for complex tasks.
    Implements autonomous reasoning for task breakdown and execution.
    """

    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.plans = self.vault_path / 'Plans'
        self.needs_action = self.vault_path / 'Needs_Action'
        self.in_progress = self.vault_path / 'In_Progress'
        self.done = self.vault_path / 'Done'
        self.logs = self.vault_path / 'Logs'

        # Ensure folders exist
        self.plans.mkdir(exist_ok=True)
        self.in_progress.mkdir(exist_ok=True)

        self.logger = self._setup_logger()

    def _setup_logger(self):
        """Setup logging"""
        logger = logging.getLogger('ReasoningLoop')
        logger.setLevel(logging.INFO)

        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        logger.addHandler(handler)

        return logger

    def analyze_tasks(self) -> List[Dict]:
        """Analyze all pending tasks in Needs_Action"""
        tasks = []

        if not self.needs_action.exists():
            return tasks

        for filepath in self.needs_action.glob('*.md'):
            task = self._parse_task_file(filepath)
            if task:
                tasks.append(task)

        return tasks

    def _parse_task_file(self, filepath: Path) -> Dict:
        """Parse a task file and extract relevant information"""
        try:
            content = filepath.read_text(encoding='utf-8')
            frontmatter = self._parse_frontmatter(content)

            return {
                'filename': filepath.name,
                'path': str(filepath),
                'type': frontmatter.get('type', 'unknown'),
                'priority': frontmatter.get('priority', 'medium'),
                'status': frontmatter.get('status', 'pending'),
                'created': frontmatter.get('created', datetime.now().isoformat()),
                'content': content
            }
        except Exception as e:
            self.logger.error(f"Error parsing {filepath}: {e}")
            return None

    def _parse_frontmatter(self, content: str) -> Dict:
        """Parse YAML frontmatter"""
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

    def create_plan(self, tasks: List[Dict] = None, plan_name: str = None) -> Path:
        """Create a Plan.md file for executing tasks"""

        if tasks is None:
            tasks = self.analyze_tasks()

        if not tasks:
            self.logger.info("No tasks to plan")
            return None

        # Sort by priority
        priority_order = {'high': 0, 'medium': 1, 'low': 2}
        tasks.sort(key=lambda t: priority_order.get(t['priority'], 2))

        # Generate plan name
        if not plan_name:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            plan_name = f'Plan_{timestamp}.md'

        plan_path = self.plans / plan_name

        # Generate plan content
        plan_content = self._generate_plan_content(tasks)

        plan_path.write_text(plan_content, encoding='utf-8')

        self.logger.info(f"Created plan: {plan_name}")
        self._log_plan_creation(plan_name, len(tasks))

        return plan_path

    def _generate_plan_content(self, tasks: List[Dict]) -> str:
        """Generate the content for a Plan.md file"""

        content = f'''# Execution Plan
**Created:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Tasks:** {len(tasks)}
**Status:** Ready to Execute

---

## Overview

This plan outlines the steps to complete {len(tasks)} pending task(s).
Tasks are ordered by priority: High → Medium → Low

---

## Task Summary

| Priority | Count |
|----------|-------|
| High     | {sum(1 for t in tasks if t['priority'] == 'high')} |
| Medium   | {sum(1 for t in tasks if t['priority'] == 'medium')} |
| Low      | {sum(1 for t in tasks if t['priority'] == 'low')} |

---

## Execution Steps

'''

        step_number = 1
        for task in tasks:
            content += f'''
### Step {step_number}: {task['filename']}

**Type:** {task['type']}
**Priority:** {task['priority'].upper()}
**File:** `{task['filename']}`

**Actions:**
- [ ] Read and analyze task
- [ ] Execute required actions
- [ ] Create approval request if needed
- [ ] Move to /Done when complete

**Notes:**
{self._get_task_summary(task)}

---

'''
            step_number += 1

        content += '''
## Execution Checklist

### Pre-Execution
- [ ] Review all tasks
- [ ] Confirm resources available
- [ ] Check for dependencies

### During Execution
- [ ] Follow steps in order
- [ ] Update checkboxes as you go
- [ ] Log any issues

### Post-Execution
- [ ] Verify all tasks complete
- [ ] Move processed files to /Done
- [ ] Update Dashboard
- [ ] Create completion summary

---

## Ralph Wiggum Loop Instructions

To execute autonomously until complete:

```bash
# Start continuous execution
/ralph-loop "Execute all steps in the current plan until complete" \\
  --completion-promise "PLAN_COMPLETE" \\
  --max-iterations 20
```

The loop will:
1. Read current step
2. Execute actions
3. Update checkboxes
4. Move to next step
5. Repeat until all steps complete

---

## Stop Conditions

The plan is complete when:
- All checkboxes are checked
- All task files are moved to /Done
- `<promise>PLAN_COMPLETE</promise>` is output

---

*Generated by ReasoningLoop*
*Part of Silver Tier AI Employee*
'''

        return content

    def _get_task_summary(self, task: Dict) -> str:
        """Generate a brief summary of the task"""

        content = task.get('content', '')

        # Extract first few lines of content
        lines = content.split('\n')
        summary_lines = []

        for line in lines[5:15]:  # Skip frontmatter
            line = line.strip()
            if line and not line.startswith('#') and not line.startswith('---'):
                summary_lines.append(line)
                if len(summary_lines) >= 3:
                    break

        return '\n'.join(summary_lines) if summary_lines else 'See task file for details'

    def _log_plan_creation(self, plan_name: str, task_count: int):
        """Log plan creation"""
        log_file = self.logs / f'reasoning_{datetime.now().strftime("%Y%m%d")}.md'

        entry = f'''
## Plan Created: {plan_name}
**Time:** {datetime.now().isoformat()}
**Tasks:** {task_count}

---

'''

        with open(log_file, 'a') as f:
            f.write(entry)

    def update_plan(self, plan_path: Path, updates: Dict) -> Path:
        """Update an existing plan with progress"""

        content = plan_path.read_text(encoding='utf-8')

        # Add update section
        update_section = f'''

## Progress Update
**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

{updates.get('message', 'Progress made on execution plan')}

**Completed Steps:** {updates.get('completed', 0)}
**Remaining Steps:** {updates.get('remaining', 0)}

---

'''

        # Insert before the final "---"
        content = content.rstrip()
        if not content.endswith('---'):
            content += '\n\n---'

        updated_content = content.replace('\n---\n*Generated by', update_section + '\n---\n*Generated by')

        plan_path.write_text(updated_content, encoding='utf-8')

        return plan_path

    def claim_task(self, task_file: Path) -> Path:
        """Claim a task by moving it to In_Progress"""

        if not isinstance(task_file, Path):
            task_file = Path(task_file)

        # Create agent folder in In_Progress
        agent_folder = self.in_progress / 'claude'
        agent_folder.mkdir(exist_ok=True)

        # Move task file
        destination = agent_folder / task_file.name

        # Move using copy + delete (for cross-platform compatibility)
        import shutil
        shutil.copy2(task_file, destination)
        task_file.unlink()

        self.logger.info(f"Claimed task: {task_file.name}")

        return destination

    def complete_task(self, task_file: Path) -> Path:
        """Complete a task by moving it to Done"""

        if not isinstance(task_file, Path):
            task_file = Path(task_file)

        destination = self.done / task_file.name

        import shutil
        shutil.copy2(task_file, destination)
        task_file.unlink()

        self.logger.info(f"Completed task: {task_file.name}")

        return destination


def main():
    """Main function for reasoning loop"""
    import argparse

    parser = argparse.ArgumentParser(description='Reasoning Loop for AI Employee')
    parser.add_argument('--vault', default='E:/hackhaton0_personal_ai_employe/AI_Employee_Vault',
                        help='Path to Obsidian vault')
    parser.add_argument('--action', choices=['plan', 'analyze', 'claim', 'complete'],
                        default='plan', help='Action to perform')
    parser.add_argument('--task', help='Task file to claim/complete')
    parser.add_argument('--plan-name', help='Name for the plan file')

    args = parser.parse_args()

    reasoning = ReasoningLoop(vault_path=args.vault)

    if args.action == 'plan':
        plan = reasoning.create_plan(plan_name=args.plan_name)
        if plan:
            print(f"Created plan: {plan}")

    elif args.action == 'analyze':
        tasks = reasoning.analyze_tasks()
        print(f"Found {len(tasks)} tasks:")
        for task in tasks:
            print(f"  - {task['filename']} ({task['priority']})")

    elif args.action == 'claim' and args.task:
        destination = reasoning.claim_task(args.task)
        print(f"Claimed task: {destination}")


if __name__ == '__main__':
    main()
