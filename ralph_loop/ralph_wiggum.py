"""
The Ralph Wiggum Loop - Autonomous Multi-Step Task Completion
Keeps Claude Code iterating until tasks are complete
Part of Gold Tier AI Employee

"I'm failing! And I'll keep failing until I don't fail anymore!"
Based on the Stop Hook pattern for continuous iteration
"""
import json
import time
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Callable
from enum import Enum


class LoopStatus(Enum):
    """Status of the Ralph Wiggum loop"""
    STARTING = "starting"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    MAX_ITERATIONS = "max_iterations"


class CompletionStrategy(Enum):
    """Strategies for determining completion"""
    PROMISE = "promise"           # Claude outputs <promise>TASK_COMPLETE</promise>
    FILE_MOVEMENT = "file_movement"  # Task file moved to /Done
    EXPLICIT = "explicit"          # Claude explicitly confirms completion
    CHECKPOINT = "checkpoint"      # All checkpoints in plan checked


class LoopConfig:
    """Configuration for Ralph Wiggum loop"""

    def __init__(
        self,
        max_iterations: int = 20,
        iteration_timeout: int = 300,  # 5 minutes per iteration
        checkpoint_file: str = None,
        completion_strategy: CompletionStrategy = CompletionStrategy.PROMISE,
        pause_on_error: bool = True,
        save_state: bool = True
    ):
        self.max_iterations = max_iterations
        self.iteration_timeout = iteration_timeout
        self.checkpoint_file = checkpoint_file
        self.completion_strategy = completion_strategy
        self.pause_on_error = pause_on_error
        self.save_state = save_state


class RalphWiggumLoop:
    """
    The Ralph Wiggum Loop - Autonomous execution until completion

    Monitors task progress and re-invokes Claude Code until:
    1. Task is complete
    2. Max iterations reached
    3. Explicit stop requested

    Uses checkpoint files and promise detection for completion.
    """

    PROMISE_START = "<promise>"
    PROMISE_END = "</promise>"

    def __init__(
        self,
        vault_path: str,
        config: LoopConfig = None
    ):
        self.vault_path = Path(vault_path)
        self.state_folder = self.vault_path / '.ralph_state'
        self.state_folder.mkdir(parents=True, exist_ok=True)

        self.config = config or LoopConfig()
        self.logger = self._setup_logger()

        # Loop state
        self.current_loop_id = None
        self.iteration = 0
        self.status = LoopStatus.STARTING

    def _setup_logger(self):
        """Setup logging for Ralph Wiggum loop"""
        logger = logging.getLogger('RalphWiggumLoop')
        logger.setLevel(logging.DEBUG)

        # File handler
        log_file = self.vault_path / 'Logs' / 'ralph_wiggum.log'
        log_file.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)

        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)

        logger.addHandler(file_handler)

        return logger

    def start_loop(
        self,
        task_prompt: str,
        task_file: Path = None,
        checkpoints: List[str] = None
    ) -> Dict:
        """
        Start a Ralph Wiggum loop for a task

        Args:
            task_prompt: The prompt to give Claude Code
            task_file: Optional task file to monitor
            checkpoints: Optional list of checkpoints to verify

        Returns:
            Loop state dictionary
        """

        # Generate loop ID
        loop_id = f"RALPH-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        self.current_loop_id = loop_id

        # Initialize state
        state = {
            'loop_id': loop_id,
            'task_prompt': task_prompt,
            'task_file': str(task_file) if task_file else None,
            'checkpoints': checkpoints or [],
            'iteration': 0,
            'max_iterations': self.config.max_iterations,
            'status': LoopStatus.STARTING.value,
            'started_at': datetime.now().isoformat(),
            'completed_at': None,
            'completion_reason': None,
            'history': []
        }

        # Save initial state
        self._save_state(state)

        self.logger.info(f"Starting Ralph Wiggum loop: {loop_id}")
        self.logger.info(f"Task: {task_prompt[:100]}...")

        # Update status
        self.status = LoopStatus.RUNNING
        state['status'] = LoopStatus.RUNNING.value

        return state

    def next_iteration(self, state: Dict, previous_output: str = None) -> bool:
        """
        Determine if loop should continue to next iteration

        Args:
            state: Current loop state
            previous_output: Previous Claude Code output

        Returns:
            True if should continue, False otherwise
        """

        # Check max iterations
        if state['iteration'] >= state['max_iterations']:
            state['status'] = LoopStatus.MAX_ITERATIONS.value
            state['completion_reason'] = 'max_iterations_reached'
            self._save_state(state)
            self.logger.warning(f"Loop {state['loop_id']} reached max iterations")
            return False

        # Check for completion promise in output
        if previous_output and self._check_promise_completion(previous_output):
            state['status'] = LoopStatus.COMPLETED.value
            state['completion_reason'] = 'promise_detected'
            state['completed_at'] = datetime.now().isoformat()
            self._save_state(state)
            self.logger.info(f"Loop {state['loop_id']} completed via promise")
            return False

        # Check file movement completion
        if self.config.completion_strategy == CompletionStrategy.FILE_MOVEMENT:
            if self._check_file_completion(state):
                state['status'] = LoopStatus.COMPLETED.value
                state['completion_reason'] = 'file_moved_to_done'
                state['completed_at'] = datetime.now().isoformat()
                self._save_state(state)
                self.logger.info(f"Loop {state['loop_id']} completed via file movement")
                return False

        # Check checkpoint completion
        if state.get('checkpoints'):
            completed = self._check_checkpoint_completion(state)
            if completed:
                state['status'] = LoopStatus.COMPLETED.value
                state['completion_reason'] = 'all_checkpoints_complete'
                state['completed_at'] = datetime.now().isoformat()
                self._save_state(state)
                self.logger.info(f"Loop {state['loop_id']} completed via checkpoints")
                return False

        # Continue loop
        state['iteration'] += 1
        state['history'].append({
            'iteration': state['iteration'],
            'timestamp': datetime.now().isoformat(),
            'has_output': previous_output is not None
        })

        self._save_state(state)

        return True

    def _check_promise_completion(self, output: str) -> bool:
        """Check if output contains completion promise"""

        if not output:
            return False

        # Look for promise markers
        start_idx = output.find(self.PROMISE_START)
        if start_idx == -1:
            return False

        end_idx = output.find(self.PROMISE_END, start_idx)
        if end_idx == -1:
            return False

        # Extract promise content
        promise_content = output[start_idx + len(self.PROMISE_START):end_idx].strip()

        # Check for completion promises
        completion_promises = [
            'TASK_COMPLETE',
            'PLAN_COMPLETE',
            'ALL_COMPLETE',
            'DONE',
            'FINISHED',
            'COMPLETE'
        ]

        for promise in completion_promises:
            if promise in promise_content.upper():
                self.logger.info(f"Completion promise found: {promise}")
                return True

        return False

    def _check_file_completion(self, state: Dict) -> bool:
        """Check if task file has been moved to Done"""

        task_file = state.get('task_file')
        if not task_file:
            return False

        task_path = Path(task_file)
        if not task_path.exists():
            # File no longer exists - check if in Done
            done_path = self.vault_path / 'Done' / task_path.name
            return done_path.exists()

        return False

    def _check_checkpoint_completion(self, state: Dict) -> bool:
        """Check if all checkpoints are complete"""

        checkpoints = state.get('checkpoints', [])
        if not checkpoints:
            return False

        # For plan-based checkpoints, check Plan.md file
        if self.config.checkpoint_file:
            plan_file = self.vault_path / self.config.checkpoint_file
            if plan_file.exists():
                content = plan_file.read_text()
                # Check if all checkboxes are checked
                lines = content.split('\n')
                total_checks = sum(1 for line in lines if '- [ ]' in line or '- [x]' in line)
                checked = sum(1 for line in lines if '- [x]' in line)

                if total_checks > 0 and checked == total_checks:
                    return True

        return False

    def _save_state(self, state: Dict):
        """Save loop state to file"""

        if not self.config.save_state:
            return

        state_file = self.state_folder / f"{state['loop_id']}.json"

        with open(state_file, 'w') as f:
            json.dump(state, f, indent=2, default=str)

    def load_state(self, loop_id: str) -> Optional[Dict]:
        """Load existing loop state"""

        state_file = self.state_folder / f"{loop_id}.json"

        if state_file.exists():
            with open(state_file, 'r') as f:
                return json.load(f)

        return None

    def stop_loop(self, loop_id: str, reason: str = "manual_stop"):
        """Manually stop a running loop"""

        state = self.load_state(loop_id)
        if state:
            state['status'] = LoopStatus.COMPLETED.value
            state['completion_reason'] = reason
            state['completed_at'] = datetime.now().isoformat()
            self._save_state(state)
            self.logger.info(f"Loop {loop_id} stopped: {reason}")

    def get_prompt_for_iteration(self, state: Dict) -> str:
        """Get the prompt for the current iteration"""

        base_prompt = state['task_prompt']

        # Add iteration context
        iteration_context = f"""

---

**Ralph Wiggum Loop - Iteration {state['iteration'] + 1}/{state['max_iterations']}**

You are in an autonomous execution loop. Continue working on the task until complete.

**Completion Strategy:** {self.config.completion_strategy.value}

**To signal completion:**
"""

        if self.config.completion_strategy == CompletionStrategy.PROMISE:
            iteration_context += f'- Output: `{self.PROMISE_START}TASK_COMPLETE{self.PROMISE_END}`\n'
        elif self.config.completion_strategy == CompletionStrategy.FILE_MOVEMENT:
            iteration_context += '- Move the task file to /Done folder\n'
        elif self.config.completion_strategy == CompletionStrategy.CHECKPOINT:
            iteration_context += '- Check all boxes in the plan\n'

        iteration_context += f'''
**Previous iterations:** {state['iteration']}

**Note:** If you encounter an error, describe it and continue. The loop will help you persist until completion.
'''

        return base_prompt + iteration_context

    def generate_loop_report(self, loop_id: str = None) -> Path:
        """Generate report for a loop"""

        if loop_id:
            state = self.load_state(loop_id)
        elif self.current_loop_id:
            state = self.load_state(self.current_loop_id)
        else:
            # Generate report for all loops
            return self._generate_all_loops_report()

        if not state:
            raise ValueError(f"Loop {loop_id} not found")

        report_path = self.vault_path / 'Audit' / f'Ralph_Loop_Report_{state["loop_id"]}.md'

        duration = None
        if state.get('completed_at'):
            start = datetime.fromisoformat(state['started_at'])
            end = datetime.fromisoformat(state['completed_at'])
            duration = (end - start).total_seconds()

        report_content = f'''# Ralph Wiggum Loop Report

**Loop ID:** {state['loop_id']}
**Status:** {state['status'].upper()}
**Iterations:** {state['iteration']}/{state['max_iterations']}

---

## Summary

| Metric | Value |
|--------|-------|
| Started | {state['started_at']} |
| Completed | {state.get('completed_at', 'N/A')} |
| Duration | {f'{duration:.0f} seconds' if duration else 'N/A'} |
| Completion Reason | {state.get('completion_reason', 'N/A')} |

---

## Task

{state['task_prompt']}

'''

        if state.get('task_file'):
            report_content += f"**Task File:** `{state['task_file']}`\n\n"

        if state.get('checkpoints'):
            report_content += f"**Checkpoints:** {len(state['checkpoints'])} defined\n\n"

        report_content += '''
---

## Iteration History

'''

        for entry in state.get('history', []):
            report_content += f"- **Iteration {entry['iteration']}**: {entry['timestamp']}\n"

        if state['status'] == LoopStatus.MAX_ITERATIONS.value:
            report_content += '''

## ⚠️ Max Iterations Reached

The loop reached maximum iterations without completion.

**Recommendations:**
- Review task complexity
- Consider breaking into smaller sub-tasks
- Increase max_iterations for complex tasks
- Check for blocking issues

---

'''

        report_content += '''
---
*Generated by Ralph Wiggum Loop*
*AI Employee - Gold Tier*
'''

        report_path.write_text(report_content)

        return report_path

    def _generate_all_loops_report(self) -> Path:
        """Generate report for all loops"""

        loops = []
        for state_file in self.state_folder.glob('RALPH-*.json'):
            with open(state_file, 'r') as f:
                loops.append(json.load(f))

        report_path = self.vault_path / 'Audit' / f'Ralph_Loops_Summary_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md'

        report_content = f'''# Ralph Wiggum Loops Summary

**Generated:** {datetime.now().isoformat()}
**Total Loops:** {len(loops)}

---

## Recent Loops

'''

        for loop in sorted(loops, key=lambda x: x['started_at'], reverse=True)[:20]:
            status_icon = {
                'completed': '✓',
                'failed': '✗',
                'max_iterations': '⚠',
                'starting': '▶',
                'running': '◉'
            }.get(loop['status'], '?')

            report_content += f'''
### {status_icon} {loop['loop_id']}

- **Status:** {loop['status']}
- **Iterations:** {loop['iteration']}/{loop['max_iterations']}
- **Started:** {loop['started_at']}
- **Reason:** {loop.get('completion_reason', 'N/A')}

'''

        report_content += '''
---
*Generated by Ralph Wiggum Loop*
*AI Employee - Gold Tier*
'''

        report_path.write_text(report_content)

        return report_path


# Convenience functions for Claude Code integration

def create_task_prompt(
    task_description: str,
    context: str = "",
    completion_hint: str = None
) -> str:
    """Create a properly formatted task prompt for Ralph Wiggum loop"""

    prompt = f"""{task_description}

{context}

"""

    if completion_hint:
        prompt += f"\n**When complete:** {completion_hint}\n"

    return prompt


def start_ralph_loop(
    vault_path: str,
    task_prompt: str,
    max_iterations: int = 20,
    completion_strategy: str = "promise"
) -> str:
    """Start a Ralph Wiggum loop (convenience function)"""

    config = LoopConfig(
        max_iterations=max_iterations,
        completion_strategy=CompletionStrategy(completion_strategy)
    )

    loop = RalphWiggumLoop(vault_path, config)
    state = loop.start_loop(task_prompt)

    return state['loop_id']


def main():
    """Test Ralph Wiggum loop"""
    vault = 'E:/hackhaton0_personal_ai_employe/AI_Employee_Vault'

    # Create a test loop
    loop = RalphWiggumLoop(vault)

    task = create_task_prompt(
        task_description="Process all pending files in Needs_Action folder",
        context="Check each file, take appropriate action, and move to Done when complete.",
        completion_hint="Output <promise>TASK_COMPLETE</promise> when all files processed"
    )

    state = loop.start_loop(task)
    print(f"Started loop: {state['loop_id']}")

    # Generate report
    report = loop.generate_loop_report()
    print(f"Report: {report}")


if __name__ == '__main__':
    main()
