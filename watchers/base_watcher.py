"""
Base Watcher - Template for all AI Employee watchers
"""
import time
import logging
from pathlib import Path
from abc import ABC, abstractmethod
from datetime import datetime


class BaseWatcher(ABC):
    """Base class for all watcher scripts"""

    def __init__(self, vault_path: str, check_interval: int = 60):
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.inbox = self.vault_path / 'Inbox'
        self.logs = self.vault_path / 'Logs'
        self.check_interval = check_interval
        self.logger = self._setup_logger()
        self.processed_items = set()

        # Ensure directories exist
        self.needs_action.mkdir(parents=True, exist_ok=True)
        self.inbox.mkdir(parents=True, exist_ok=True)
        self.logs.mkdir(parents=True, exist_ok=True)

    def _setup_logger(self):
        """Configure logging for the watcher"""
        logger = logging.getLogger(self.__class__.__name__)
        logger.setLevel(logging.INFO)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # File handler
        file_handler = logging.FileHandler(
            self.vault_path / 'Logs' / f'{self.__class__.__name__}.log'
        )
        file_handler.setLevel(logging.DEBUG)

        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)

        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

        return logger

    @abstractmethod
    def check_for_updates(self) -> list:
        """Return list of new items to process"""
        pass

    @abstractmethod
    def create_action_file(self, item) -> Path:
        """Create .md file in Needs_Action folder"""
        pass

    def log_activity(self, message: str):
        """Write activity to daily log file"""
        today = datetime.now().strftime('%Y-%m-%d')
        log_file = self.logs / f'Activity_{today}.md'

        timestamp = datetime.now().isoformat()
        entry = f'\n## {timestamp}\n{message}\n'

        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(entry)

    def run(self):
        """Main watcher loop"""
        self.logger.info(f'Starting {self.__class__.__name__}')
        self.log_activity(f'{self.__class__.__name__} started')

        while True:
            try:
                items = self.check_for_updates()
                for item in items:
                    action_file = self.create_action_file(item)
                    self.logger.info(f'Created action file: {action_file}')
                    self.log_activity(
                        f'Created action file: {action_file.name}'
                    )
            except Exception as e:
                self.logger.error(f'Error: {e}')
                self.log_activity(f'Error: {str(e)}')

            time.sleep(self.check_interval)


if __name__ == '__main__':
    # Example usage
    class ExampleWatcher(BaseWatcher):
        def check_for_updates(self):
            return []

        def create_action_file(self, item):
            return Path('example.md')

    watcher = ExampleWatcher(
        vault_path='E:/hackhaton0_personal_ai_employe/AI_Employee_Vault',
        check_interval=60
    )
    watcher.run()
