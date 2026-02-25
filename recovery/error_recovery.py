"""
Error Recovery System - Graceful degradation and automatic recovery
Part of Gold Tier AI Employee
"""
import logging
import json
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable
from enum import Enum


class ErrorSeverity(Enum):
    """Error severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class RecoveryAction(Enum):
    """Recovery action types"""
    RETRY = "retry"
    FALLBACK = "fallback"
    SKIP = "skip"
    ESCALATE = "escalate"
    SHUTDOWN = "shutdown"


class ErrorCategory(Enum):
    """Error categories for handling"""
    NETWORK = "network"
    AUTHENTICATION = "authentication"
    FILE_SYSTEM = "file_system"
    API = "api"
    DEPENDENCY = "dependency"
    UNKNOWN = "unknown"


class ErrorRecord:
    """Record of an error for tracking and analysis"""

    def __init__(
        self,
        error_id: str,
        category: ErrorCategory,
        severity: ErrorSeverity,
        message: str,
        component: str,
        traceback: str = None
    ):
        self.error_id = error_id
        self.category = category
        self.severity = severity
        self.message = message
        self.component = component
        self.traceback = traceback
        self.timestamp = datetime.now()
        self.resolved = False
        self.recovery_attempts = 0
        self.recovery_action = None

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            'error_id': self.error_id,
            'category': self.category.value,
            'severity': self.severity.value,
            'message': self.message,
            'component': self.component,
            'traceback': self.traceback,
            'timestamp': self.timestamp.isoformat(),
            'resolved': self.resolved,
            'recovery_attempts': self.recovery_attempts,
            'recovery_action': self.recovery_action.value if self.recovery_action else None
        }


class RecoveryStrategy:
    """Defines recovery strategy for error types"""

    def __init__(
        self,
        category: ErrorCategory,
        max_retries: int = 3,
        retry_delay: int = 5,
        fallback_action: Optional[Callable] = None,
        escalation_threshold: int = 3
    ):
        self.category = category
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.fallback_action = fallback_action
        self.escalation_threshold = escalation_threshold


class ErrorRecoverySystem:
    """
    Centralized error recovery system for AI Employee
    Provides graceful degradation and automatic recovery
    """

    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.audit_folder = self.vault_path / 'Audit'
        self.error_log = self.audit_folder / 'error_log.jsonl'
        self.recovery_log = self.audit_folder / 'recovery_log.jsonl'

        # Ensure folders exist
        self.audit_folder.mkdir(parents=True, exist_ok=True)

        self.logger = self._setup_logger()
        self.error_records: Dict[str, ErrorRecord] = {}
        self.recovery_strategies: Dict[ErrorCategory, RecoveryStrategy] = {}

        # Load existing error records
        self._load_error_records()

        # Setup default recovery strategies
        self._setup_default_strategies()

    def _setup_logger(self):
        """Setup logging for error recovery"""
        logger = logging.getLogger('ErrorRecoverySystem')
        logger.setLevel(logging.DEBUG)

        # File handler
        file_handler = logging.FileHandler(
            self.audit_folder / 'error_recovery.log'
        )
        file_handler.setLevel(logging.DEBUG)

        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)

        logger.addHandler(file_handler)

        return logger

    def _load_error_records(self):
        """Load existing error records from log"""
        if self.error_log.exists():
            try:
                with open(self.error_log, 'r') as f:
                    for line in f:
                        if line.strip():
                            data = json.loads(line)
                            record = ErrorRecord(
                                error_id=data['error_id'],
                                category=ErrorCategory(data['category']),
                                severity=ErrorSeverity(data['severity']),
                                message=data['message'],
                                component=data['component'],
                                traceback=data.get('traceback')
                            )
                            record.resolved = data.get('resolved', False)
                            record.recovery_attempts = data.get('recovery_attempts', 0)
                            self.error_records[record.error_id] = record
            except Exception as e:
                self.logger.error(f"Error loading records: {e}")

    def _setup_default_strategies(self):
        """Setup default recovery strategies for error categories"""
        self.recovery_strategies = {
            ErrorCategory.NETWORK: RecoveryStrategy(
                ErrorCategory.NETWORK,
                max_retries=5,
                retry_delay=10,
                escalation_threshold=5
            ),
            ErrorCategory.AUTHENTICATION: RecoveryStrategy(
                ErrorCategory.AUTHENTICATION,
                max_retries=2,
                retry_delay=30,
                escalation_threshold=2
            ),
            ErrorCategory.FILE_SYSTEM: RecoveryStrategy(
                ErrorCategory.FILE_SYSTEM,
                max_retries=3,
                retry_delay=5,
                escalation_threshold=3
            ),
            ErrorCategory.API: RecoveryStrategy(
                ErrorCategory.API,
                max_retries=3,
                retry_delay=5,
                escalation_threshold=4
            ),
            ErrorCategory.DEPENDENCY: RecoveryStrategy(
                ErrorCategory.DEPENDENCY,
                max_retries=1,
                retry_delay=60,
                escalation_threshold=1
            ),
            ErrorCategory.UNKNOWN: RecoveryStrategy(
                ErrorCategory.UNKNOWN,
                max_retries=2,
                retry_delay=10,
                escalation_threshold=3
            )
        }

    def register_strategy(self, strategy: RecoveryStrategy):
        """Register a custom recovery strategy"""
        self.recovery_strategies[strategy.category] = strategy

    def report_error(
        self,
        category: ErrorCategory,
        severity: ErrorSeverity,
        message: str,
        component: str,
        traceback: str = None
    ) -> ErrorRecord:
        """Report a new error and create recovery record"""

        import uuid
        error_id = f"ERR-{uuid.uuid4().hex[:8].upper()}"

        record = ErrorRecord(
            error_id=error_id,
            category=category,
            severity=severity,
            message=message,
            component=component,
            traceback=traceback
        )

        self.error_records[error_id] = record

        # Log to file
        with open(self.error_log, 'a') as f:
            f.write(json.dumps(record.to_dict()) + '\n')

        self.logger.error(f"[{error_id}] {component}: {message}")

        # Attempt recovery
        self._attempt_recovery(record)

        return record

    def _attempt_recovery(self, record: ErrorRecord) -> bool:
        """Attempt to recover from an error"""

        strategy = self.recovery_strategies.get(
            record.category,
            self.recovery_strategies[ErrorCategory.UNKNOWN]
        )

        record.recovery_attempts += 1

        # Determine recovery action
        if record.recovery_attempts <= strategy.max_retries:
            # Retry
            action = RecoveryAction.RETRY
            self.logger.info(f"[{record.error_id}] Attempting retry {record.recovery_attempts}/{strategy.max_retries}")

        elif record.recovery_attempts <= strategy.escalation_threshold:
            # Try fallback or escalate
            if strategy.fallback_action:
                action = RecoveryAction.FALLBACK
            else:
                action = RecoveryAction.ESCALATE
            self.logger.warning(f"[{record.error_id}] Recovery action: {action.value}")

        else:
            # Give up and escalate
            action = RecoveryAction.ESCALATE
            self.logger.critical(f"[{record.error_id}] Max retries exceeded, escalating")

        record.recovery_action = action

        # Log recovery action
        self._log_recovery_action(record, action)

        # Execute recovery
        if action == RecoveryAction.RETRY:
            # Return True to indicate retry should happen
            return True
        elif action == RecoveryAction.FALLBACK and strategy.fallback_action:
            try:
                strategy.fallback_action(record)
                record.resolved = True
            except Exception as e:
                self.logger.error(f"Fallback action failed: {e}")

        return False

    def _log_recovery_action(self, record: ErrorRecord, action: RecoveryAction):
        """Log recovery action"""
        log_entry = {
            'error_id': record.error_id,
            'action': action.value,
            'timestamp': datetime.now().isoformat(),
            'attempt': record.recovery_attempts
        }

        with open(self.recovery_log, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')

    def mark_resolved(self, error_id: str):
        """Mark an error as resolved"""
        if error_id in self.error_records:
            self.error_records[error_id].resolved = True
            self.logger.info(f"[{error_id}] Marked as resolved")

    def get_active_errors(self) -> List[ErrorRecord]:
        """Get all unresolved errors"""
        return [
            record for record in self.error_records.values()
            if not record.resolved
        ]

    def get_errors_by_category(self, category: ErrorCategory) -> List[ErrorRecord]:
        """Get all errors in a category"""
        return [
            record for record in self.error_records.values()
            if record.category == category
        ]

    def get_error_summary(self, hours: int = 24) -> dict:
        """Get error summary for time period"""

        cutoff = datetime.now() - timedelta(hours=hours)

        recent_errors = [
            record for record in self.error_records.values()
            if record.timestamp > cutoff
        ]

        summary = {
            'period_hours': hours,
            'total_errors': len(recent_errors),
            'unresolved': len([r for r in recent_errors if not r.resolved]),
            'by_category': {},
            'by_severity': {},
            'by_component': {}
        }

        for record in recent_errors:
            # Count by category
            cat = record.category.value
            summary['by_category'][cat] = summary['by_category'].get(cat, 0) + 1

            # Count by severity
            sev = record.severity.value
            summary['by_severity'][sev] = summary['by_severity'].get(sev, 0) + 1

            # Count by component
            comp = record.component
            summary['by_component'][comp] = summary['by_component'].get(comp, 0) + 1

        return summary

    def generate_error_report(self) -> Path:
        """Generate comprehensive error report"""

        summary = self.get_error_summary(hours=168)  # Week
        active_errors = self.get_active_errors()

        report_path = self.audit_folder / f'Error_Report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md'

        report_content = f'''# Error Recovery Report

**Generated:** {datetime.now().isoformat()}
**Period:** Last 7 days

---

## Summary

| Metric | Count |
|--------|-------|
| Total Errors | {summary['total_errors']} |
| Unresolved | {summary['unresolved']} |
| Resolution Rate | {((summary['total_errors'] - summary['unresolved']) / max(summary['total_errors'], 1) * 100):.1f}% |

---

## Errors by Category

'''

        for category, count in summary['by_category'].items():
            report_content += f'- **{category}**: {count}\n'

        report_content += '\n## Errors by Severity\n\n'

        for severity, count in summary['by_severity'].items():
            report_content += f'- **{severity}**: {count}\n'

        report_content += '\n## Errors by Component\n\n'

        for component, count in summary['by_component'].items():
            report_content += f'- **{component}**: {count}\n'

        if active_errors:
            report_content += '\n## Active Errors\n\n'

            for error in active_errors[:10]:  # Top 10
                report_content += f'''
### {error.error_id} - {error.severity.value.upper()}

- **Category:** {error.category.value}
- **Component:** {error.component}
- **Message:** {error.message}
- **Attempts:** {error.recovery_attempts}
- **Action:** {error.recovery_action.value if error.recovery_action else 'None'}
- **Time:** {error.timestamp.isoformat()}

'''
        else:
            report_content += '\n## Active Errors\n\nNo active errors. All systems nominal.\n'

        report_content += '''
---

## Recommendations

'''

        if summary['unresolved'] > 10:
            report_content += '- ⚠️ High number of unresolved errors - review recommended\n'
        elif summary['unresolved'] > 5:
            report_content += '- ⚠️ Moderate number of unresolved errors - monitor\n'
        else:
            report_content += '- ✓ Error rate within acceptable limits\n'

        report_content += '''
## Recovery Actions Taken

See `recovery_log.jsonl` for detailed recovery action history.

---
*Generated by Error Recovery System*
*AI Employee - Gold Tier*
'''

        report_path.write_text(report_content)

        return report_path


# Decorator for automatic error handling
def handle_errors(component: str, category: ErrorCategory = ErrorCategory.UNKNOWN):
    """Decorator for automatic error handling"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Get error recovery system
                # (In practice, this would be passed in or accessed via singleton)
                import traceback
                raise
        return wrapper
    return decorator


def main():
    """Test error recovery system"""
    system = ErrorRecoverySystem('E:/hackhaton0_personal_ai_employe/AI_Employee_Vault')

    # Test error reporting
    system.report_error(
        category=ErrorCategory.NETWORK,
        severity=ErrorSeverity.WARNING,
        message="Connection timeout to Gmail API",
        component="GmailWatcher",
        traceback="Traceback here..."
    )

    # Generate report
    report = system.generate_error_report()
    print(f"Error report generated: {report}")


if __name__ == '__main__':
    main()
