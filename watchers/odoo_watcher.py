#!/usr/bin/env python3
"""
odoo_watcher.py - Monitor Odoo accounting events and create invoices
Integrates with Odoo Community 17+ for accounting automation
"""
import os
import sys
import json
import logging
import requests
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Add parent directory
sys.path.insert(0, str(Path(__file__).parent.parent))
from base_watcher import BaseWatcher


class OdooWatcher(BaseWatcher):
    """
    Odoo Accounting Watcher
    Monitors Odoo for:
    - New invoices to create
    - Payment reminders
    - Weekly CEO briefings
    - Expense tracking
    """

    def __init__(self, vault_path: str = None, check_interval: int = 300):
        super().__init__(vault_path, check_interval)

        # Odoo configuration
        self.odoo_url = os.getenv('ODOO_URL', 'http://localhost:8069')
        self.odoo_db = os.getenv('ODOO_DB_NAME', 'odoo_db')
        self.odoo_user = os.getenv('ODOO_USERNAME', 'admin')
        self.odoo_password = os.getenv('ODOO_PASSWORD', 'admin')
        self.odoo_company_id = os.getenv('ODOO_COMPANY_ID', '1')

        # Session cookie (set after login)
        self.session_id = None

        # Accounting folder
        self.accounting_folder = self.vault_path / 'Accounting'
        self.invoices_folder = self.accounting_folder / 'Invoices'
        self.expenses_folder = self.accounting_folder / 'Expenses'
        self.reports_folder = self.accounting_folder / 'Reports'

        for folder in [self.accounting_folder, self.invoices_folder,
                       self.expenses_folder, self.reports_folder]:
            folder.mkdir(parents=True, exist_ok=True)

        self.logger.info("Odoo Watcher initialized")
        self.logger.info(f"Odoo URL: {self.odoo_url}")

    def login(self) -> bool:
        """Login to Odoo and get session"""
        try:
            url = f"{self.odoo_url}/web/session/authenticate"
            data = {
                "jsonrpc": "2.0",
                "params": {
                    "db": self.odoo_db,
                    "login": self.odoo_user,
                    "password": self.odoo_password,
                }
            }

            response = requests.post(url, json=data, timeout=30)

            if response.status_code == 200:
                result = response.json()
                if result.get('result'):
                    self.session_id = response.cookies.get('session_id')
                    self.logger.info("Odoo login successful")
                    return True

            self.logger.error(f"Odoo login failed: {response.text}")
            return False

        except Exception as e:
            self.logger.error(f"Odoo login error: {e}")
            return False

    def call_odoo(self, model: str, method: str, args: List = None,
                  kwargs: Dict = None) -> Optional[dict]:
        """Call Odoo RPC method"""
        try:
            url = f"{self.odoo_url}/jsonrpc"

            payload = {
                "jsonrpc": "2.0",
                "method": "call",
                "params": {
                    "service": "object",
                    "method": "execute_kw",
                    "args": [
                        self.odoo_db,
                        self.session_id or 1,  # uid
                        self.odoo_password,  # password
                        model,
                        method,
                        args or [],
                        kwargs or {}
                    ]
                },
                "id": 1
            }

            response = requests.post(url, json=payload, timeout=30)

            if response.status_code == 200:
                result = response.json()
                if 'error' in result.get('result', {}):
                    self.logger.error(f"Odoo RPC error: {result['result']['error']}")
                    return None
                return result.get('result')
            else:
                self.logger.error(f"Odoo RPC failed: {response.status_code}")
                return None

        except Exception as e:
            self.logger.error(f"Odoo RPC error: {e}")
            return None

    def check_accounting_tasks(self):
        """Check for accounting tasks in Needs_Action"""
        needs_action = self.vault_path / 'Needs_Action'

        if not needs_action.exists():
            return

        for task_file in needs_action.glob('*.md'):
            content = task_file.read_text().lower()

            if 'invoice' in content:
                self.create_invoice_from_task(task_file)
            elif 'expense' in content:
                self.record_expense_from_task(task_file)
            elif 'payment' in content:
                self.check_payment_status(task_file)

    def create_invoice_from_task(self, task_file: Path):
        """Create an invoice in Odoo from task file"""
        try:
            content = task_file.read_text()
            self.logger.info(f"Creating invoice from: {task_file.name}")

            # Parse invoice details
            # This is simplified - real implementation would parse properly
            invoice_data = {
                'partner_id': 1,  # Customer ID
                'move_type': 'out_invoice',
                'invoice_date': datetime.now().strftime('%Y-%m-%d'),
                'invoice_line_ids': [
                    (0, 0, {
                        'name': 'Service/Product',
                        'quantity': 1,
                        'price_unit': 100.0,
                    })
                ]
            }

            # Call Odoo to create invoice
            result = self.call_odoo('account.move', 'create', [invoice_data])

            if result:
                self.logger.info(f"Invoice created in Odoo: ID={result}")

                # Save invoice record
                invoice_file = self.invoices_folder / f"INV_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
                invoice_file.write_text(f"""---
type: invoice
odoo_id: {result}
created_at: {datetime.now().isoformat()}
source_task: {task_file.name}
---

# Invoice Created

Odoo Invoice ID: {result}
Date: {datetime.now().strftime('%Y-%m-%d')}

Original Task: {task_file.name}
""")

                # Move task to Done
                done_folder = self.vault_path / 'Done'
                done_folder.mkdir(exist_ok=True)
                task_file.rename(done_folder / task_file.name)

        except Exception as e:
            self.logger.error(f"Error creating invoice: {e}")

    def record_expense_from_task(self, task_file: Path):
        """Record an expense in Odoo"""
        try:
            content = task_file.read_text()
            self.logger.info(f"Recording expense from: {task_file.name}")

            expense_data = {
                'name': 'Expense',
                'date': datetime.now().strftime('%Y-%m-%d'),
                'amount': 50.0,
                'payment_mode': 'own_account',
            }

            result = self.call_odoo('hr.expense', 'create', [expense_data])

            if result:
                self.logger.info(f"Expense recorded in Odoo: ID={result}")

                # Save expense record
                expense_file = self.expenses_folder / f"EXP_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
                expense_file.write_text(f"""---
type: expense
odoo_id: {result}
created_at: {datetime.now().isoformat()}
source_task: {task_file.name}
---

# Expense Recorded

Odoo Expense ID: {result}
Date: {datetime.now().strftime('%Y-%m-%d')}

Original Task: {task_file.name}
""")

                # Move task to Done
                done_folder = self.vault_path / 'Done'
                done_folder.mkdir(exist_ok=True)
                task_file.rename(done_folder / task_file.name)

        except Exception as e:
            self.logger.error(f"Error recording expense: {e}")

    def check_payment_status(self, task_file: Path):
        """Check payment status in Odoo"""
        try:
            # Search for unpaid invoices
            result = self.call_odoo(
                'account.move',
                'search_read',
                [[['state', '=', 'draft'], ['move_type', '=', 'out_invoice']]],
                {'fields': ['id', 'partner_id', 'amount_total', 'invoice_date']}
            )

            if result:
                self.logger.info(f"Found {len(result)} unpaid invoices")

                # Create payment reminder
                report_file = self.reports_folder / f"PAYMENT_STATUS_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
                report_file.write_text(f"""---
type: payment_status_report
generated_at: {datetime.now().isoformat()}
---

# Payment Status Report

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}

## Unpaid Invoices: {len(result)}

| Invoice ID | Customer | Amount | Date |
|------------|----------|--------|------|
""")

                for invoice in result[:10]:  # Last 10
                    report_file.write_text(
                        f"| {invoice.get('id')} | {invoice.get('partner_id', [{}])[0].get('name', 'N/A')} | "
                        f"${invoice.get('amount_total', 0):.2f} | {invoice.get('invoice_date', 'N/A')} |\n",
                        append=True
                    )

        except Exception as e:
            self.logger.error(f"Error checking payment status: {e}")

    def generate_weekly_briefing(self):
        """Generate weekly CEO briefing from Odoo data"""
        try:
            # Get this week's data
            today = datetime.now()
            week_start = today - timedelta(days=today.weekday())

            # Search for invoices created this week
            result = self.call_odoo(
                'account.move',
                'search_read',
                [[['create_date', '>=', week_start.strftime('%Y-%m-%d')]]],
                {'fields': ['id', 'amount_total', 'state', 'invoice_date']}
            )

            total_revenue = 0
            paid_count = 0
            pending_count = 0

            if result:
                for invoice in result:
                    if invoice.get('move_type') == 'out_invoice':
                        total_revenue += invoice.get('amount_total', 0)
                        if invoice.get('state') == 'posted':
                            paid_count += 1
                        else:
                            pending_count += 1

            # Create briefing
            briefing_file = self.accounting_folder / f"BRIEFING_{today.strftime('%Y%m%d')}.md"
            briefing_file.write_text(f"""---
type: ceo_briefing
period: weekly
week_starting: {week_start.strftime('%Y-%m-%d')}
generated_at: {datetime.now().isoformat()}
---

# CEO Briefing - Weekly

**Week of:** {week_start.strftime('%B %d, %Y')}

## Financial Summary

| Metric | This Week |
|--------|-----------|
| Revenue | ${total_revenue:.2f} |
| Invoices Paid | {paid_count} |
| Invoices Pending | {pending_count} |
| Total Invoices | {paid_count + pending_count} |

## Actions Required

"""
            )

            if pending_count > 0:
                briefing_file.write_text(
                    f"- ⚠️ Follow up on {pending_count} unpaid invoice(s)\n",
                    append=True
                )

            briefing_file.write_text("""

## Notes
- Full details in Odoo Accounting module
- Review expenses in Accounting/Expenses/

---
*Generated by AI Employee - Odoo Integration*
""")

            self.logger.info(f"Weekly briefing generated: {briefing_file.name}")

        except Exception as e:
            self.logger.error(f"Error generating briefing: {e}")

    def run(self):
        """Main loop"""
        self.logger.info("Odoo Watcher starting...")

        # Login to Odoo
        if not self.login():
            self.logger.error("Failed to login to Odoo. Check credentials in .env")
            return

        last_briefing = None

        while self.running:
            try:
                current_time = datetime.now()

                # Check for accounting tasks
                self.check_accounting_tasks()

                # Generate weekly briefing (every Monday)
                if current_time.weekday() == 0 and last_briefing != current_time.date():
                    self.generate_weekly_briefing()
                    last_briefing = current_time.date()

                time.sleep(self.check_interval)

            except KeyboardInterrupt:
                self.logger.info("Odoo Watcher stopping...")
                self.running = False
            except Exception as e:
                self.logger.error(f"Error in main loop: {e}")
                time.sleep(60)

        self.logger.info("Odoo Watcher stopped")


def main():
    """Main entry point"""
    vault_path = os.getenv('VAULT_PATH',
        Path(__file__).parent.parent / 'AI_Employee_Vault')

    watcher = OdooWatcher(str(vault_path))
    watcher.run()


if __name__ == '__main__':
    main()
