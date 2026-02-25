"""
File System Watcher - Monitors Inbox folder for new files
Creates action files for AI processing
"""
import os
import time
import hashlib
from pathlib import Path
from datetime import datetime
from base_watcher import BaseWatcher


class FileSystemWatcher(BaseWatcher):
    """Watches the /Inbox folder for new files"""

    def __init__(self, vault_path: str, check_interval: int = 30):
        super().__init__(vault_path, check_interval)
        self.known_files = set()
        self.logger.info(f'Monitoring Inbox: {self.inbox}')

    def _get_file_hash(self, filepath: Path) -> str:
        """Calculate file hash for change detection"""
        hasher = hashlib.md5()
        try:
            with open(filepath, 'rb') as f:
                hasher.update(f.read())
            return hasher.hexdigest()
        except Exception:
            return ''

    def _get_file_info(self, filepath: Path) -> dict:
        """Get comprehensive file information"""
        stat = filepath.stat()
        return {
            'name': filepath.name,
            'size': stat.st_size,
            'size_mb': round(stat.st_size / (1024 * 1024), 2),
            'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
            'extension': filepath.suffix.lower(),
            'path': str(filepath)
        }

    def _determine_priority(self, info: dict) -> str:
        """Determine priority based on file characteristics"""
        name_lower = info['name'].lower()

        if any(kw in name_lower for kw in ['urgent', 'asap', 'important']):
            return 'high'
        elif any(kw in name_lower for kw in ['invoice', 'payment', 'contract']):
            return 'high'
        elif info['extension'] in ['.pdf', '.doc', '.docx']:
            return 'medium'
        else:
            return 'low'

    def _suggest_actions(self, info: dict) -> list:
        """Suggest actions based on file type"""
        actions = []
        ext = info['extension']

        # Common actions for all files
        actions.append('- [ ] Review file content')
        actions.append('- [ ] Categorize and tag')

        # Type-specific actions
        if ext in ['.pdf', '.doc', '.docx', '.txt']:
            actions.append('- [ ] Extract and summarize text content')
            actions.append('- [ ] Check for action items')
        elif ext in ['.jpg', '.jpeg', '.png', '.gif']:
            actions.append('- [ ] Review image content')
            actions.append('- [ ] OCR if text is present')
        elif ext in ['.csv', '.xlsx', '.xls']:
            actions.append('- [ ] Analyze data structure')
            actions.append('- [ ] Create summary statistics')
        elif ext in ['.zip', '.rar', '.7z']:
            actions.append('- [ ] Extract and verify contents')
            actions.append('- [ ] Scan for security concerns')

        actions.append('- [ ] Move to /Done after processing')

        return actions

    def check_for_updates(self) -> list:
        """Check for new or modified files in Inbox"""
        new_items = []

        if not self.inbox.exists():
            self.logger.warning(f'Inbox folder not found: {self.inbox}')
            return new_items

        for filepath in self.inbox.iterdir():
            # Skip directories and hidden files
            if filepath.is_dir() or filepath.name.startswith('.'):
                continue

            file_hash = self._get_file_hash(filepath)
            file_id = f"{filepath.name}_{file_hash[:8]}"

            if file_id not in self.known_files:
                info = self._get_file_info(filepath)
                info['hash'] = file_hash
                info['filepath'] = filepath
                new_items.append(info)
                self.known_files.add(file_id)
                self.logger.info(f'New file detected: {filepath.name}')

        return new_items

    def create_action_file(self, item: dict) -> Path:
        """Create action file for detected file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_name = item['name'].replace(' ', '_').replace('/', '_')
        action_filename = f'FILE_{timestamp}_{safe_name}.md'
        action_path = self.needs_action / action_filename

        priority = self._determine_priority(item)
        actions = self._suggest_actions(item)

        # Create markdown content
        content = f'''---
type: file_drop
original_name: {item['name']}
size: {item['size_mb']} MB ({item['size']} bytes)
extension: {item['extension']}
modified: {item['modified']}
priority: {priority}
status: pending
file_path: {item['path']}
created: {datetime.now().isoformat()}
---

# File Processing: {item['name']}

## File Information
- **Location:** `{item['path']}`
- **Size:** {item['size_mb']} MB
- **Type:** {item['extension']}
- **Modified:** {item['modified']}
- **Priority:** {priority.upper()}

## Suggested Actions
{chr(10).join(actions)}

## Notes
- File detected by FileSystemWatcher
- Waiting for AI processing
'''

        action_path.write_text(content, encoding='utf-8')
        return action_path


def main():
    """Run the file system watcher"""
    import argparse

    parser = argparse.ArgumentParser(
        description='File System Watcher for AI Employee'
    )
    parser.add_argument(
        '--vault',
        default='E:/hackhaton0_personal_ai_employe/AI_Employee_Vault',
        help='Path to Obsidian vault'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=30,
        help='Check interval in seconds'
    )

    args = parser.parse_args()

    watcher = FileSystemWatcher(
        vault_path=args.vault,
        check_interval=args.interval
    )

    print(f"""
    ============================================
    File System Watcher Started
    ============================================
    Vault: {args.vault}
    Inbox: {watcher.inbox}
    Needs Action: {watcher.needs_action}
    Check Interval: {args.interval} seconds
    ============================================
    Press Ctrl+C to stop
    ============================================
    """)

    try:
        watcher.run()
    except KeyboardInterrupt:
        print("\nWatcher stopped by user")
        watcher.log_activity('Watcher stopped by user')


if __name__ == '__main__':
    main()
