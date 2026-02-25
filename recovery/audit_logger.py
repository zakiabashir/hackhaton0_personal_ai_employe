"""
Comprehensive Audit Logging System
Tracks all AI Employee actions for transparency and accountability
Part of Gold Tier AI Employee
"""
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum
from contextlib import contextmanager


class ActionType(Enum):
    """Types of actions that can be audited"""
    FILE_READ = "file_read"
    FILE_WRITE = "file_write"
    FILE_DELETE = "file_delete"
    EMAIL_SEND = "email_send"
    EMAIL_DRAFT = "email_draft"
    SOCIAL_POST = "social_post"
    SOCIAL_DRAFT = "social_draft"
    WATCHER_START = "watcher_start"
    WATCHER_STOP = "watcher_stop"
    WATCHER_ERROR = "watcher_error"
    APPROVAL_REQUEST = "approval_request"
    APPROVAL_GRANTED = "approval_granted"
    APPROVAL_DENIED = "approval_denied"
    PLAN_CREATE = "plan_create"
    PLAN_EXECUTE = "plan_execute"
    ERROR = "error"
    RECOVERY = "recovery"
    CUSTOM = "custom"


class AuditLevel(Enum):
    """Audit logging levels"""
    ESSENTIAL = "essential"  # Always log
    STANDARD = "standard"    # Normal operations
    VERBOSE = "verbose"      # Detailed debugging
    SENSITIVE = "sensitive"  # Requires special handling


class AuditRecord:
    """A single audit record"""

    def __init__(
        self,
        action_type: ActionType,
        level: AuditLevel = AuditLevel.STANDARD,
        component: str = "Unknown",
        details: Dict = None,
        user: str = "AI_Employee",
        status: str = "started",
        related_files: List[str] = None
    ):
        self.record_id = f"AUD-{datetime.now().strftime('%Y%m%d%H%M%S')}-{datetime.now().microsecond // 1000:04d}"
        self.action_type = action_type
        self.level = level
        self.component = component
        self.details = details or {}
        self.user = user
        self.status = status
        self.related_files = related_files or []
        self.timestamp = datetime.now()
        self.duration_ms = None
        self.error_message = None
        self.metadata = {}

    def complete(self, status: str = "completed", error: str = None):
        """Mark the audit record as complete"""
        self.status = status
        self.error_message = error
        self.duration_ms = int((datetime.now() - self.timestamp).total_seconds() * 1000)

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            'record_id': self.record_id,
            'action_type': self.action_type.value,
            'level': self.level.value,
            'component': self.component,
            'details': self.details,
            'user': self.user,
            'status': self.status,
            'related_files': self.related_files,
            'timestamp': self.timestamp.isoformat(),
            'duration_ms': self.duration_ms,
            'error_message': self.error_message,
            'metadata': self.metadata
        }


class AuditLogger:
    """
    Comprehensive audit logging system
    Tracks all actions for transparency and accountability
    """

    def __init__(self, vault_path: str, min_level: AuditLevel = AuditLevel.STANDARD):
        self.vault_path = Path(vault_path)
        self.audit_folder = self.vault_path / 'Audit'
        self.audit_log = self.audit_folder / 'audit_log.jsonl'
        self.sensitive_log = self.audit_folder / 'sensitive_log.jsonl'
        self.min_level = min_level

        # Ensure folders exist
        self.audit_folder.mkdir(parents=True, exist_ok=True)

        self.logger = self._setup_logger()
        self.active_records: Dict[str, AuditRecord] = {}

    def _setup_logger(self):
        """Setup logging"""
        logger = logging.getLogger('AuditLogger')
        logger.setLevel(logging.DEBUG)

        # File handler
        file_handler = logging.FileHandler(
            self.audit_folder / 'audit_system.log'
        )
        file_handler.setLevel(logging.DEBUG)

        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)

        logger.addHandler(file_handler)

        return logger

    @contextmanager
    def audit_action(
        self,
        action_type: ActionType,
        component: str = "Unknown",
        details: Dict = None,
        level: AuditLevel = AuditLevel.STANDARD,
        related_files: List[str] = None
    ):
        """Context manager for auditing an action"""

        # Check if we should log this level
        level_priority = {
            AuditLevel.ESSENTIAL: 0,
            AuditLevel.STANDARD: 1,
            AuditLevel.VERBOSE: 2,
            AuditLevel.SENSITIVE: 3
        }

        if level_priority.get(level, 1) > level_priority.get(self.min_level, 1):
            # Skip logging
            yield None
            return

        # Create audit record
        record = AuditRecord(
            action_type=action_type,
            level=level,
            component=component,
            details=details,
            related_files=related_files
        )

        self.active_records[record.record_id] = record

        try:
            yield record
            record.complete(status="completed")
        except Exception as e:
            record.complete(status="failed", error=str(e))
            raise
        finally:
            self._write_record(record)
            del self.active_records[record.record_id]

    def log(
        self,
        action_type: ActionType,
        component: str,
        details: Dict = None,
        level: AuditLevel = AuditLevel.STANDARD,
        status: str = "logged",
        related_files: List[str] = None
    ) -> AuditRecord:
        """Log a single action"""

        record = AuditRecord(
            action_type=action_type,
            level=level,
            component=component,
            details=details,
            status=status,
            related_files=related_files
        )

        record.complete()
        self._write_record(record)

        return record

    def _write_record(self, record: AuditRecord):
        """Write audit record to appropriate log"""

        # Sensitive actions go to separate log
        if record.level == AuditLevel.SENSITIVE:
            log_file = self.sensitive_log
            # Sanitize sensitive details for main log
            sanitized_record = record.to_dict()
            if 'details' in sanitized_record:
                sanitized_record['details'] = '[REDACTED - See sensitive log]'
            log_data = sanitized_record
        else:
            log_file = self.audit_log
            log_data = record.to_dict()

        # Write to file
        with open(log_file, 'a') as f:
            f.write(json.dumps(log_data) + '\n')

        # Also log to system logger
        self.logger.info(f"[{record.record_id}] {record.action_type.value} - {record.component}: {record.status}")

    def get_audit_trail(
        self,
        component: str = None,
        action_type: ActionType = None,
        hours: int = 24,
        status: str = None
    ) -> List[Dict]:
        """Query audit trail with filters"""

        from datetime import timedelta

        cutoff = datetime.now() - timedelta(hours=hours)
        results = []

        # Read from main audit log
        if self.audit_log.exists():
            with open(self.audit_log, 'r') as f:
                for line in f:
                    if line.strip():
                        try:
                            record = json.loads(line)
                            timestamp = datetime.fromisoformat(record['timestamp'])

                            # Apply filters
                            if timestamp < cutoff:
                                continue
                            if component and record.get('component') != component:
                                continue
                            if action_type and record.get('action_type') != action_type.value:
                                continue
                            if status and record.get('status') != status:
                                continue

                            results.append(record)
                        except Exception:
                            continue

        return results

    def generate_audit_report(
        self,
        hours: int = 168,  # Week
        include_sensitive: bool = False
    ) -> Path:
        """Generate comprehensive audit report"""

        records = self.get_audit_trail(hours=hours)

        report_path = self.audit_folder / f'Audit_Report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md'

        # Statistics
        total_actions = len(records)
        by_component = {}
        by_action = {}
        by_status = {}

        for record in records:
            # Count by component
            comp = record.get('component', 'Unknown')
            by_component[comp] = by_component.get(comp, 0) + 1

            # Count by action type
            action = record.get('action_type', 'unknown')
            by_action[action] = by_action.get(action, 0) + 1

            # Count by status
            stat = record.get('status', 'unknown')
            by_status[stat] = by_status.get(stat, 0) + 1

        # Generate report
        report_content = f'''# Comprehensive Audit Report

**Generated:** {datetime.now().isoformat()}
**Period:** Last {hours} hours ({hours // 24} days)
**Report ID:** {datetime.now().strftime('%Y%m%d%H%M%S')}

---

## Executive Summary

| Metric | Count |
|--------|-------|
| Total Actions Logged | {total_actions} |
| Unique Components | {len(by_component)} |
| Action Types | {len(by_action)} |

---

## Actions by Component

| Component | Actions |
|-----------|---------|
'''

        for comp, count in sorted(by_component.items(), key=lambda x: x[1], reverse=True):
            report_content += f"| {comp} | {count} |\n"

        report_content += "\n## Actions by Type\n\n"

        for action, count in sorted(by_action.items(), key=lambda x: x[1], reverse=True):
            report_content += f"- **{action}**: {count}\n"

        report_content += "\n## Actions by Status\n\n"

        for stat, count in sorted(by_status.items(), key=lambda x: x[1], reverse=True):
            status_icon = "✓" if stat == "completed" else "⚠️" if stat == "failed" else "•"
            report_content += f"- {status_icon} **{stat}**: {count}\n"

        # Recent activity
        report_content += "\n## Recent Activity (Last 50)\n\n"

        for record in records[-50:]:
            timestamp = record.get('timestamp', '')
            component = record.get('component', 'Unknown')
            action = record.get('action_type', 'unknown')
            status = record.get('status', 'unknown')

            status_icon = {
                'completed': '✓',
                'failed': '✗',
                'started': '▶',
                'logged': '•'
            }.get(status, '?')

            report_content += f"- {status_icon} `{timestamp[:19]}` **{component}**: {action} ({status})\n"

        # Failed actions
        failed_records = [r for r in records if r.get('status') == 'failed']
        if failed_records:
            report_content += f"\n## Failed Actions ({len(failed_records)})\n\n"

            for record in failed_records[:20]:  # Top 20
                report_content += f'''
### {record.get('record_id', 'Unknown')}

- **Component:** {record.get('component')}
- **Action:** {record.get('action_type')}
- **Error:** {record.get('error_message', 'No error message')}
- **Time:** {record.get('timestamp')}

'''

        # Sensitive actions
        if include_sensitive and self.sensitive_log.exists():
            report_content += "\n## Sensitive Actions\n\n"
            report_content += f"*{len(self._read_sensitive_log())} sensitive actions logged separately.*\n"

        report_content += '''
---

## Compliance & Security

### Data Access
- All file accesses logged
- Sensitive data redacted from main log
- Separate sensitive log maintained

### Approval Actions
- All approval requests logged
- Approval decisions recorded
- User attribution maintained

### Error Handling
- All errors logged with context
- Recovery actions tracked
- Failure patterns identifiable

---

## Recommendations

'''

        # Generate recommendations based on audit data
        failed_rate = len(failed_records) / max(total_actions, 1)

        if failed_rate > 0.1:
            report_content += "- ⚠️ **High failure rate detected** - Review error patterns\n"
        elif failed_rate > 0.05:
            report_content += "- ⚠️ **Moderate failure rate** - Monitor closely\n"
        else:
            report_content += "- ✓ **Failure rate within acceptable limits**\n"

        report_content += '''
## Full Audit Trail

See `audit_log.jsonl` for complete JSON log of all actions.

---
*Generated by Comprehensive Audit Logger*
*AI Employee - Gold Tier*
'''

        report_path.write_text(report_content)

        return report_path

    def _read_sensitive_log(self) -> List[Dict]:
        """Read sensitive log file"""
        records = []
        if self.sensitive_log.exists():
            with open(self.sensitive_log, 'r') as f:
                for line in f:
                    if line.strip():
                        try:
                            records.append(json.loads(line))
                        except Exception:
                            continue
        return records

    def get_compliance_summary(self) -> Dict:
        """Get compliance-related summary"""

        records = self.get_audit_trail(hours=720)  # 30 days

        summary = {
            'period_days': 30,
            'total_actions': len(records),
            'sensitive_actions': 0,
            'approval_requests': 0,
            'external_communications': 0,
            'data_accesses': 0,
            'failed_actions': 0
        }

        for record in records:
            action = record.get('action_type', '')

            if action in [ActionType.EMAIL_SEND.value, ActionType.SOCIAL_POST.value]:
                summary['external_communications'] += 1

            if action == ActionType.APPROVAL_REQUEST.value:
                summary['approval_requests'] += 1

            if action in [ActionType.FILE_READ.value, ActionType.FILE_WRITE.value]:
                summary['data_accesses'] += 1

            if record.get('status') == 'failed':
                summary['failed_actions'] += 1

        # Count sensitive actions
        if self.sensitive_log.exists():
            summary['sensitive_actions'] = len(self._read_sensitive_log())

        return summary


def main():
    """Test audit logger"""
    logger = AuditLogger('E:/hackhaton0_personal_ai_employe/AI_Employee_Vault')

    # Test logging
    with logger.audit_action(
        action_type=ActionType.FILE_WRITE,
        component="TestComponent",
        details={"file": "test.txt"},
        level=AuditLevel.STANDARD
    ) as record:
        record.metadata["test"] = "data"

    # Generate report
    report = logger.generate_audit_report(hours=1)
    print(f"Audit report: {report}")


if __name__ == '__main__':
    main()
