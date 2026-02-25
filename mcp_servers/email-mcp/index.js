#!/usr/bin/env node

/**
 * Email MCP Server
 * Provides email sending capabilities via SMTP
 * Implements Model Context Protocol for Claude Code integration
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';
import nodemailer from 'nodemailer';
import fs from 'fs';
import path from 'path';

// Configuration
const CONFIG_PATH = process.env.EMAIL_CONFIG || './email-config.json';
const APPROVAL_FOLDER = process.env.APPROVAL_FOLDER || '../AI_Employee_Vault/Approved';

// Load email configuration
let emailConfig = {
  host: 'smtp.gmail.com',
  port: 587,
  secure: false,
  auth: {
    user: process.env.EMAIL_USER || '',
    pass: process.env.EMAIL_PASS || ''
  }
};

// Load config from file if exists
if (fs.existsSync(CONFIG_PATH)) {
  try {
    emailConfig = JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf-8'));
  } catch (e) {
    console.error('Failed to load email config:', e.message);
  }
}

// Create email transporter
let transporter = null;

function createTransporter() {
  if (!emailConfig.auth.user || !emailConfig.auth.pass) {
    console.error('Email credentials not configured');
    return null;
  }

  return nodemailer.createTransport({
    host: emailConfig.host,
    port: emailConfig.port,
    secure: emailConfig.secure,
    auth: emailConfig.auth
  });
}

// Create MCP server
const server = new Server(
  {
    name: 'email-mcp-server',
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
        name: 'send_email',
        description: 'Send an email via SMTP',
        inputSchema: {
          type: 'object',
          properties: {
            to: {
              type: 'string',
              description: 'Recipient email address',
            },
            subject: {
              type: 'string',
              description: 'Email subject',
            },
            body: {
              type: 'string',
              description: 'Email body (plain text or HTML)',
            },
            isHtml: {
              type: 'boolean',
              description: 'Whether body is HTML (default: false)',
            },
          },
          required: ['to', 'subject', 'body'],
        },
      },
      {
        name: 'draft_email',
        description: 'Create an email draft for approval (does not send)',
        inputSchema: {
          type: 'object',
          properties: {
            to: {
              type: 'string',
              description: 'Recipient email address',
            },
            subject: {
              type: 'string',
              description: 'Email subject',
            },
            body: {
              type: 'string',
              description: 'Email body',
            },
            vaultPath: {
              type: 'string',
              description: 'Path to vault Drafts folder',
            },
          },
          required: ['to', 'subject', 'body'],
        },
      },
      {
        name: 'check_email_config',
        description: 'Check if email is configured and test connection',
        inputSchema: {
          type: 'object',
          properties: {},
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
      case 'send_email': {
        if (!transporter) {
          transporter = createTransporter();
        }

        if (!transporter) {
          return {
            content: [{
              type: 'text',
              text: 'Error: Email not configured. Set EMAIL_USER and EMAIL_PASS environment variables.',
            }],
          };
        }

        const mailOptions = {
          from: emailConfig.auth.user,
          to: args.to,
          subject: args.subject,
          ...(args.isHtml ? { html: args.body } : { text: args.body }),
        };

        const info = await transporter.sendMail(mailOptions);

        return {
          content: [{
            type: 'text',
            text: `Email sent successfully! Message ID: ${info.messageId}`,
          }],
        };
      }

      case 'draft_email': {
        const vaultPath = args.vaultPath || APPROVAL_FOLDER;
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
        const draftFilename = `EMAIL_DRAFT_${timestamp}.md`;
        const draftPath = path.join(vaultPath, draftFilename);

        const draftContent = `---
type: email_draft
to: ${args.to}
subject: ${args.subject}
created: ${new Date().toISOString()}
status: pending_approval
---

# Email Draft

## To: ${args.to}

## Subject: ${args.subject}

## Body:

${args.body}

---

## Approval Instructions

**To Approve and Send:**
1. Review the email above
2. Edit if needed
3. Move this file to /Approved/ folder
4. Use send_email tool to send

**To Reject:**
- Move this file to /Rejected/ folder

---
*Created by Email MCP Server*
`;

        // Ensure directory exists
        fs.mkdirSync(vaultPath, { recursive: true });

        // Write draft file
        fs.writeFileSync(draftPath, draftContent, 'utf-8');

        return {
          content: [{
            type: 'text',
            text: `Email draft created: ${draftPath}\n\nMove to /Approved/ folder when ready to send.`,
          }],
        };
      }

      case 'check_email_config': {
        const configStatus = {
          configured: !!(emailConfig.auth.user && emailConfig.auth.pass),
          host: emailConfig.host,
          port: emailConfig.port,
          user: emailConfig.auth.user ? emailConfig.auth.user.replace(/(.{2}).*(@.*)/, '$1***$2') : 'Not set',
        };

        if (!transporter && configStatus.configured) {
          transporter = createTransporter();
        }

        if (transporter) {
          try {
            await transporter.verify();
            configStatus.connection = 'OK';
          } catch (e) {
            configStatus.connection = `Failed: ${e.message}`;
          }
        }

        return {
          content: [{
            type: 'text',
            text: `Email Configuration Status:\n\n${JSON.stringify(configStatus, null, 2)}`,
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

  console.error('Email MCP Server running on stdio');
}

main().catch((error) => {
  console.error('Server error:', error);
  process.exit(1);
});
