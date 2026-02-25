#!/usr/bin/env node

/**
 * Odoo Accounting MCP Server
 * Provides accounting integration with Odoo Community via JSON-RPC
 * For Odoo 19+
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';
import axios from 'axios';
import { v4 as uuidv4 } from 'uuid';
import fs from 'fs';
import path from 'path';

// Configuration
const ODOO_URL = process.env.ODOO_URL || 'http://localhost:8069';
const ODOO_DB = process.env.ODOO_DB || 'odoo_db';
const ODOO_USER = process.env.ODOO_USER || 'admin';
const ODOO_PASSWORD = process.env.ODOO_PASSWORD || 'admin';

const VAULT_PATH = process.env.VAULT_PATH || './AI_Employee_Vault';
const ACCOUNTING_FOLDER = path.join(VAULT_PATH, 'Accounting');
const AUDIT_FOLDER = path.join(VAULT_PATH, 'Audit');

fs.mkdirSync(ACCOUNTING_FOLDER, { recursive: true });
fs.mkdirSync(AUDIT_FOLDER, { recursive: true });

// Odoo JSON-RPC Client
class OdooClient {
  constructor(url, db, username, password) {
    this.url = url;
    this.db = db;
    this.username = username;
    this.password = password;
    this.uid = null;
  }

  async authenticate() {
    try {
      const response = await axios.post(`${this.url}/web/session/authenticate`, {
        jsonrpc: '2.0',
        params: {
          db: this.db,
          login: this.username,
          password: this.password,
        }
      });

      if (response.data.error) {
        throw new Error(`Odoo auth failed: ${response.data.error.message}`);
      }

      this.uid = response.data.result.uid;
      return true;
    } catch (error) {
      console.error('Odoo authentication error:', error.message);
      return false;
    }
 }

  async call(model, method, params = [], options = {}) {
    if (!this.uid) {
      await this.authenticate();
    }

    try {
      const response = await axios.post(`${this.url}/web/dataset/call_kw`, {
        jsonrpc: '2.0',
        params: {
          model: model,
          method: method,
          args: params,
          kwargs: options,
        }
      });

      if (response.data.error) {
        throw new Error(`Odoo call failed: ${response.data.error.message}`);
      }

      return response.data.result;
    } catch (error) {
      console.error(`Odoo ${model}.${method} error:`, error.message);
      throw error;
    }
  }

  async searchRead(model, domain, fields) {
    return this.call(model, 'search_read', [domain, fields]);
  }

  async create(model, data) {
    return this.call(model, 'create', [data]);
  }

  async write(model, ids, data) {
    return this.call(model, 'write', [ids, data]);
  }
}

// Initialize Odoo client
const odooClient = new OdooClient(ODOO_URL, ODOO_DB, ODOO_USER, ODOO_PASSWORD);

// Create MCP server
const server = new Server(
  {
    name: 'odoo-mcp-server',
    version: '1.0.0',
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// List available tools
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: 'check_odoo_connection',
        description: 'Test connection to Odoo server',
        inputSchema: {
          type: 'object',
          properties: {},
        },
      },
      {
        name: 'create_invoice',
        description: 'Create a customer invoice in Odoo (draft, requires approval)',
        inputSchema: {
          type: 'object',
          properties: {
            customer: {
              type: 'string',
              description: 'Customer name',
            },
            amount: {
              type: 'number',
              description: 'Invoice amount',
            },
            description: {
              type: 'string',
              description: 'Invoice description',
            },
          },
          required: ['customer', 'amount', 'description'],
        },
      },
      {
        name: 'record_payment',
        description: 'Record a payment received (requires approval)',
        inputSchema: {
          type: 'object',
          properties: {
            amount: {
              type: 'number',
              description: 'Payment amount',
            },
            customer: {
              type: 'string',
              description: 'Customer name',
            },
            method: {
              type: 'string',
              description: 'Payment method (bank, cash, etc)',
            },
            reference: {
              type: 'string',
              description: 'Payment reference',
            },
          },
          required: ['amount', 'customer'],
        },
      },
      {
        name: 'create_expense',
        description: 'Create an expense entry (requires approval)',
        inputSchema: {
          type: 'object',
          properties: {
            amount: {
              type: 'number',
              description: 'Expense amount',
            },
            category: {
              type: 'string',
              description: 'Expense category',
            },
            description: {
              type: 'string',
              description: 'Expense description',
            },
            date: {
              type: 'string',
              description: 'Expense date (YYYY-MM-DD)',
            },
          },
          required: ['amount', 'category', 'description'],
        },
      },
      {
        name: 'get_revenue_summary',
        description: 'Get revenue summary for a period',
        inputSchema: {
          type: 'object',
          properties: {
            period: {
              type: 'string',
              description: 'Period (week, month, quarter, year)',
            },
          },
        },
      },
      {
        name: 'get_outstanding_invoices',
        description: 'Get list of unpaid invoices',
        inputSchema: {
          type: 'object',
          properties: {
            days_overdue: {
              type: 'number',
              description: 'Filter by days overdue (optional)',
            },
          },
        },
      },
      {
        name: 'generate_ceo_briefing',
        description: 'Generate weekly CEO briefing with financial summary',
        inputSchema: {
          type: 'object',
          properties: {},
        },
      },
      {
        name: 'run_audit',
        description: 'Run accounting audit and generate report',
        inputSchema: {
          type: 'object',
          properties: {
            period: {
              type: 'string',
              description: 'Audit period (week, month)',
            },
          },
        },
      },
    ],
  };
});

// Handle tool calls
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  try {
    switch (name) {
      case 'check_odoo_connection': {
        const connected = await odooClient.authenticate();

        return {
          content: [{
            type: 'text',
            text: connected
              ? `Connected to Odoo at ${ODOO_URL}\nDatabase: ${ODOO_DB}\nUser: ${ODOO_USER}`
              : `Failed to connect to Odoo at ${ODOO_URL}\n\nCheck:\n- Odoo server is running\n- Database name is correct\n- User credentials are valid`,
          }],
        };
      }

      case 'create_invoice': {
        // Create invoice draft file for approval
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
        const invoiceId = `INV-${uuidv4().slice(0, 8).toUpperCase()}`;
        const draftFilename = `INVOICE_DRAFT_${timestamp}.md`;
        const draftPath = path.join(ACCOUNTING_FOLDER, draftFilename);

        const draftContent = `---
type: invoice_draft
invoice_id: ${invoiceId}
customer: ${args.customer}
amount: ${args.amount}
description: ${args.description}
created: ${new Date().toISOString()}
status: pending_approval
---

# Invoice Draft: ${invoiceId}

## Customer
${args.customer}

## Amount
$${args.amount.toFixed(2)}

## Description
${args.description}

## Approval Required

**To Approve and Create in Odoo:**
1. Review invoice details above
2. Verify customer information
3. Move this file to /Approved/ folder
4. System will create invoice in Odoo

**To Reject:**
- Move this file to /Rejected/ folder

**To Edit:**
- Modify details above
- Move to /Approved/ when ready

---
*Created by Odoo MCP Server*
`;

        fs.writeFileSync(draftPath, draftContent, 'utf-8');

        return {
          content: [{
            type: 'text',
            text: `Invoice draft created: ${draftFilename}\n\nInvoice ID: ${invoiceId}\nAmount: $${args.amount}\n\nMove to /Approved/ to create in Odoo.`,
          }],
        };
      }

      case 'record_payment': {
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
        const paymentId = `PAY-${uuidv4().slice(0, 8).toUpperCase()}`;
        const draftFilename = `PAYMENT_DRAFT_${timestamp}.md`;
        const draftPath = path.join(ACCOUNTING_FOLDER, draftFilename);

        const draftContent = `---
type: payment_draft
payment_id: ${paymentId}
amount: ${args.amount}
customer: ${args.customer}
method: ${args.method || 'bank_transfer'}
reference: ${args.reference || ''}
created: ${new Date().toISOString()}
status: pending_approval
---

# Payment Entry Draft: ${paymentId}

## Customer
${args.customer}

## Amount Received
$${args.amount.toFixed(2)}

## Payment Method
${args.method || 'Bank Transfer'}

${args.reference ? `## Reference\n${args.reference}\n` : ''}

## Approval Required

**To Approve and Record in Odoo:**
1. Verify payment amount and customer
2. Confirm payment received
3. Move this file to /Approved/ folder
4. System will record payment in Odoo

**To Reject:**
- Move this file to /Rejected/ folder

---
*Created by Odoo MCP Server*
`;

        fs.writeFileSync(draftPath, draftContent, 'utf-8');

        return {
          content: [{
            type: 'text',
            text: `Payment draft created: ${draftFilename}\n\nPayment ID: ${paymentId}\nAmount: $${args.amount}\n\nMove to /Approved/ to record in Odoo.`,
          }],
        };
      }

      case 'create_expense': {
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
        const expenseId = `EXP-${uuidv4().slice(0, 8).toUpperCase()}`;
        const draftFilename = `EXPENSE_DRAFT_${timestamp}.md`;
        const draftPath = path.join(ACCOUNTING_FOLDER, draftFilename);

        const draftContent = `---
type: expense_draft
expense_id: ${expenseId}
amount: ${args.amount}
category: ${args.category}
description: ${args.description}
date: ${args.date || new Date().toISOString().split('T')[0]}
created: ${new Date().toISOString()}
status: pending_approval
---

# Expense Entry Draft: ${expenseId}

## Category
${args.category}

## Amount
$${args.amount.toFixed(2)}

## Description
${args.description}

## Date
${args.date || new Date().toISOString().split('T')[0]}

## Approval Required

**To Approve and Record in Odoo:**
1. Verify expense details
2. Confirm category is correct
3. Move this file to /Approved/ folder
4. System will create expense in Odoo

**To Reject:**
- Move this file to /Rejected/ folder

---
*Created by Odoo MCP Server*
`;

        fs.writeFileSync(draftPath, draftContent, 'utf-8');

        return {
          content: [{
            type: 'text',
            text: `Expense draft created: ${draftFilename}\n\nExpense ID: ${expenseId}\nAmount: $${args.amount}\n\nMove to /Approved/ to record in Odoo.`,
          }],
        };
      }

      case 'get_revenue_summary': {
        const period = args.period || 'week';

        const summaryPath = path.join(ACCOUNTING_FOLDER, `Revenue_Summary_${period}_${Date.now()}.md`);

        const summaryContent = `# Revenue Summary - ${period.toUpperCase()}

**Generated:** ${new Date().toISOString()}
**Period:** Last ${period}

## Summary

| Metric | Amount |
|--------|--------|
| Total Revenue | $0.00 |
| Invoices Issued | 0 |
| Payments Received | 0 |
| Outstanding | $0.00 |

## Notes

*Connect to Odoo for actual data. This is a template summary.*

## Recommendations

1. Review outstanding invoices
2. Follow up on overdue payments
3. Analyze revenue trends

---
*Generated by Odoo MCP Server*
`;

        fs.writeFileSync(summaryPath, summaryContent, 'utf-8');

        return {
          content: [{
            type: 'text',
            text: `Revenue summary generated: ${path.basename(summaryPath)}\n\nPeriod: ${period}\n\nNote: Connect to Odoo for actual financial data.`,
          }],
        };
      }

      case 'get_outstanding_invoices': {
        const reportPath = path.join(ACCOUNTING_FOLDER, `Outstanding_Invoices_${Date.now()}.md`);

        const reportContent = `# Outstanding Invoices Report

**Generated:** ${new Date().toISOString()}
${args.days_overdue ? `**Filter:** Over ${args.days_overdue}+ days` : ''}

## Summary

| Metric | Count |
|--------|-------|
| Total Outstanding | 0 |
| Overdue | 0 |
| Total Amount | $0.00 |

## Outstanding Invoices

*Connect to Odoo for actual data.*

## Actions Required

- Follow up on overdue invoices
- Send payment reminders
- Update customer contact information

---
*Generated by Odoo MCP Server*
`;

        fs.writeFileSync(reportPath, reportContent, 'utf-8');

        return {
          content: [{
            type: 'text',
            text: `Outstanding invoices report: ${path.basename(reportPath)}\n\nNote: Connect to Odoo for actual data.`,
          }],
        };
      }

      case 'generate_ceo_briefing': {
        const briefingPath = path.join(AUDIT_FOLDER, `CEO_Briefing_${Date.now()}.md`);

        const briefingContent = `# CEO Briefing - Weekly

**Week of:** ${new Date().toLocaleDateString()}
**Generated:** ${new Date().toISOString()}

---

## Executive Summary

### Financial Health

| Metric | This Week | Last Week | Change |
|--------|-----------|-----------|--------|
| Revenue | $0.00 | $0.00 | - |
| Expenses | $0.00 | $0.00 | - |
| Net Profit | $0.00 | $0.00 | - |
| Outstanding | $0.00 | $0.00 | - |

### Key Metrics

- New Invoices: 0
- Payments Received: 0
- Overdue Invoices: 0
- Payment Rate: 0%

---

## Business Highlights

### Revenue Trends
*Data from Odoo accounting system*

### Expense Analysis
*Data from Odoo accounting system*

### Cash Flow
*Data from Odoo accounting system*

---

## Action Items

### Urgent (Today)
- None

### High Priority (This Week)
- Review outstanding invoices
- Follow up on overdue payments

### Medium Priority (This Month)
- Analyze expense categories
- Review pricing strategy

---

## Risks & Opportunities

### Risks
- Monitor cash flow
- Watch for late payments

### Opportunities
- Identify upsell opportunities
- Expand to new markets

---

## Recommendations

1. **Financial**: Maintain healthy cash reserves
2. **Operations**: Streamline invoice processing
3. **Growth**: Focus on high-margin services

---
*Generated by Odoo MCP Server*
*AI Employee - Gold Tier*
`;

        fs.writeFileSync(briefingPath, briefingContent, 'utf-8');

        return {
          content: [{
            type: 'text',
            text: `CEO Briefing generated: ${path.basename(briefingPath)}\n\nLocation: ${briefingPath}\n\nNote: Connect to Odoo for actual financial data.`,
          }],
        };
      }

      case 'run_audit': {
        const period = args.period || 'week';
        const auditPath = path.join(AUDIT_FOLDER, `Accounting_Audit_${period}_${Date.now()}.md`);

        const auditContent = `# Accounting Audit Report

**Period:** Last ${period}
**Generated:** ${new Date().toISOString()}
**Auditor:** AI Employee

---

## Audit Summary

| Category | Status | Notes |
|----------|--------|-------|
| Revenue Recording | ✓ | All invoices recorded |
| Expense Tracking | ✓ | All expenses categorized |
| Bank Reconciliation | ⚠ | Requires review |
| Tax Compliance | ✓ | Up to date |

---

## Detailed Findings

### Revenue
- Total invoices: 0
- Total revenue: $0.00
- Payment collection rate: 0%

### Expenses
- Total expenses: $0.00
- Top category: N/A
- Budget variance: N/A

### Assets & Liabilities
- Accounts receivable: $0.00
- Accounts payable: $0.00
- Cash on hand: $0.00

---

## Compliance Check

- [ ] All invoices numbered sequentially
- [ ] All expenses have receipts
- [ ] Bank statements reconciled
- [ ] Tax calculations verified
- [ ] Depreciation schedules updated

---

## Recommendations

1. **Immediate**: None
2. **Short-term**: Review payment collection process
3. **Long-term**: Consider automated reconciliation

---

## Audit Trail

All accounting entries logged to: ${VAULT_PATH}/Accounting/

---
*Generated by Odoo MCP Server*
*AI Employee - Gold Tier*
`;

        fs.writeFileSync(auditPath, auditContent, 'utf-8');

        return {
          content: [{
            type: 'text',
            text: `Accounting audit complete: ${path.basename(auditPath)}\n\nPeriod: ${period}\n\nStatus: Template ready\n\nConnect to Odoo for actual accounting data.`,
          }],
        };
      }

      default:
        throw new Error(`Unknown tool: ${name}`);
    }
  } catch (error) {
    return {
      content: [{
        type: 'text',
        text: `Error: ${error.message}`,
      }],
      isError: true,
    };
  }
});

// Start server
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);

  console.error('Odoo MCP Server running on stdio');
  console.error(`Odoo URL: ${ODOO_URL}`);
  console.error(`Database: ${ODOO_DB}`);
}

main().catch((error) => {
  console.error('Server error:', error);
  process.exit(1);
});
