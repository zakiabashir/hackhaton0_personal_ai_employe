# Email MCP Server

Model Context Protocol server for sending emails via SMTP.

## Setup

1. Install dependencies:
```bash
cd email-mcp
npm install
```

2. Configure email:

Option A: Environment variables
```bash
export EMAIL_USER="your-email@gmail.com"
export EMAIL_PASS="your-app-password"
```

Option B: Configuration file
```json
{
  "host": "smtp.gmail.com",
  "port": 587,
  "secure": false,
  "auth": {
    "user": "your-email@gmail.com",
    "pass": "your-app-password"
  }
}
```

3. Add to Claude Code MCP config:

```json
{
  "mcpServers": {
    "email": {
      "command": "node",
      "args": ["E:/hackhaton0_personal_ai_employe/mcp_servers/email-mcp/index.js"],
      "env": {
        "EMAIL_USER": "your-email@gmail.com",
        "EMAIL_PASS": "your-app-password"
      }
    }
  }
}
```

## Tools

### send_email
Send an email immediately.

### draft_email
Create a draft in the vault for approval.

### check_email_config
Verify email configuration and test connection.

## Gmail Setup

For Gmail, you need an App Password:

1. Go to Google Account Settings
2. Enable 2-Step Verification
3. Generate App Password
4. Use App Password in configuration
