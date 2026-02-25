# Personal AI Employee - Gold Tier

**Status:** Gold Tier Complete
**Last Updated:** 2026-02-25
**Built for:** Personal AI Employee Hackathon 0

## Overview

A complete Digital FTE (Full-Time Equivalent) AI Employee that manages your entire digital life through an Obsidian vault. Built with Claude Code, featuring cross-domain integration, multi-platform social media, WhatsApp monitoring, Odoo accounting, comprehensive audit logging, error recovery, and autonomous execution.

## Tier Status: Gold - Complete

### Bronze Deliverables
- [x] Obsidian vault with Dashboard.md and Company_Handbook.md
- [x] File System Watcher monitoring
- [x] Claude Code vault integration
- [x] Basic folder structure

### Silver Deliverables
- [x] Multiple Watchers (File System + Gmail + Approval)
- [x] LinkedIn posting capability
- [x] Reasoning Loop with Plan.md
- [x] Email MCP Server
- [x] Approval workflow
- [x] Scheduling scripts

### Gold Deliverables
- [x] WhatsApp Watcher
- [x] Facebook/Instagram/Twitter integration
- [x] Odoo accounting MCP server
- [x] Cross-domain integration (Personal + Business)
- [x] Error recovery system
- [x] Comprehensive audit logging
- [x] Ralph Wiggum autonomous loop
- [x] CEO Briefing generation
- [x] Weekly accounting audits

## Architecture

```
hackhaton0_personal_ai_employe/
├── AI_Employee_Vault/          # Obsidian vault
│   ├── Dashboard.md            # Main dashboard
│   ├── Company_Handbook.md     # Operating procedures
│   ├── Inbox/                  # New items
│   ├── Needs_Action/           # Pending tasks
│   ├── In_Progress/            # Active work
│   ├── Done/                   # Completed
│   ├── Plans/                  # Execution plans
│   ├── Drafts/                 # Awaiting approval
│   ├── Pending_Approval/       # Approval requests
│   ├── Approved/               # Approved actions
│   ├── Rejected/               # Rejected
│   ├── Personal/               # Personal domain
│   ├── Business/               # Business domain
│   ├── Accounting/             # Financial records
│   ├── Audit/                  # Audit reports
│   └── Logs/                   # System logs
├── watchers/                   # Python watcher scripts
│   ├── base_watcher.py         # Base class
│   ├── filesystem_watcher.py   # File monitoring
│   ├── gmail_watcher.py        # Gmail monitoring
│   ├── whatsapp_watcher.py     # WhatsApp monitoring
│   ├── linkedin_poster.py      # LinkedIn posting
│   ├── approval_watcher.py     # Approval executor
│   ├── reasoning_loop.py       # Plan generator
│   └── requirements.txt        # Python deps
├── mcp_servers/                # MCP servers
│   ├── email-mcp/              # Email actions
│   ├── social-mcp/             # Social media actions
│   └── odoo-mcp/               # Accounting actions
├── schedulers/                 # Scheduling scripts
│   ├── start_all_watchers.bat
│   ├── stop_all_watchers.bat
│   ├── daily_tasks.sh
│   └── weekly_tasks.sh
├── recovery/                   # Error handling
│   ├── error_recovery.py       # Recovery system
│   └── audit_logger.py         # Audit logging
├── ralph_loop/                 # Autonomous execution
│   └── ralph_wiggum.py         # Ralph Wiggum loop
├── .claude/
│   └── skills/
│       └── ai-employee/        # AI Employee skill
│           └── SKILL.md
├── README.md                   # This file
└── skills-lock.json            # Skill registry
```

## Quick Start

### 1. Install Dependencies

```bash
# Python dependencies
pip install -r watchers/requirements.txt

# Playwright browsers
playwright install chromium

# MCP servers (Node.js)
cd mcp_servers/email-mcp && npm install
cd mcp_servers/social-mcp && npm install
cd mcp_servers/odoo-mcp && npm install
```

### 2. Start the Watchers

**Windows:**
```bash
schedulers\start_all_watchers.bat
```

**Linux/Mac:**
```bash
cd watchers
python3 filesystem_watcher.py &
python3 gmail_watcher.py &
python3 whatsapp_watcher.py &
python3 approval_watcher.py &
```

### 3. Generate a Plan

```bash
cd watchers
python reasoning_loop.py --action plan
```

### 4. Create Social Media Content

```bash
python linkedin_poster.py --action calendar
```

### 5. Use Autonomous Execution

```bash
cd ralph_loop
python ralph_wiggum.py
```

## Features

### Watchers (5 total)

| Watcher | Domain | Function |
|---------|--------|----------|
| FileSystem | General | Monitors /Inbox for files |
| Gmail | Business | Monitors important emails |
| WhatsApp | Personal/Business | Monitors WhatsApp Web |
| Approval | General | Executes approved actions |
| Social | Business | Generates social content |

### MCP Servers (3 total)

| Server | Capabilities |
|--------|--------------|
| Email | Send emails, create drafts, test config |
| Social | FB/IG/Twitter posts, content calendars, analytics |
| Odoo | Accounting, invoices, payments, CEO briefings, audits |

### Cross-Domain Integration

**Personal Domain:**
- WhatsApp personal messages
- Personal email tracking
- Personal tasks

**Business Domain:**
- Business communications
- Social media management
- Accounting and invoicing
- CEO Briefings

### Error Recovery

Automatic retry with graceful degradation:
- Network: 5 retries, 10s delay
- Authentication: 2 retries, 30s delay
- File System: 3 retries, 5s delay

### Audit Logging

Complete audit trail of all actions:
- Action type and timestamp
- Component and user
- Related files
- Success/failure status
- Error messages

### Ralph Wiggum Loop

Autonomous execution until completion:
- Promise-based completion
- File movement detection
- Checkpoint verification
- Max iterations limit

## Configuration

### Gmail (Optional)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create project, enable Gmail API
3. Create OAuth credentials
4. Download credentials.json
5. Run: `python gmail_watcher.py --credentials path/to/credentials.json`

### WhatsApp (Optional)

1. Run: `python whatsapp_watcher.py`
2. Scan QR code in browser
3. Session saved for subsequent runs

### Odoo (Optional)

Set environment variables:
```bash
export ODOO_URL="http://localhost:8069"
export ODOO_DB="odoo_db"
export ODOO_USER="admin"
export ODOO_PASSWORD="admin"
```

### Social Media (Optional)

**Twitter API:**
```bash
export TWITTER_API_KEY="your-key"
export TWITTER_API_SECRET="your-secret"
export TWITTER_ACCESS_TOKEN="your-token"
export TWITTER_ACCESS_SECRET="your-secret"
```

## Scheduling

### Windows Task Scheduler

**Startup:** `schedulers\start_all_watchers.bat`
**Daily (9am):** `schedulers\daily_tasks.sh`
**Weekly Monday (9am):** `schedulers\weekly_tasks.sh`

### Linux/Mac Cron

```bash
@reboot cd /path/to/watchers && python3 filesystem_watcher.py &
@reboot cd /path/to/watchers && python3 whatsapp_watcher.py &
@reboot cd /path/to/watchers && python3 approval_watcher.py &
0 9 * * * /path/to/schedulers/daily_tasks.sh
0 9 * * 1 /path/to/schedulers/weekly_tasks.sh
```

## Workflows

### Business Workflow
```
Lead (Gmail/WhatsApp)
→ Action File (/Business/)
→ Plan Generation
→ Response Draft (/Drafts/)
→ Approval (/Approved/)
→ Send (MCP)
→ Invoice (Odoo MCP)
→ Audit Trail
```

### Social Media Workflow
```
Content Generation
→ Draft (/Drafts/)
→ Review/Edit
→ Approval (/Approved/)
→ Post (Social MCP)
→ Performance Report
```

### Accounting Workflow
```
Invoice (Odoo MCP)
→ Draft (/Accounting/)
→ Approval
→ Send
→ Payment Received
→ Record (Odoo)
→ CEO Briefing
```

## Gold Tier Features

| Feature | Status |
|---------|--------|
| Bronze Tier | Complete |
| Silver Tier | Complete |
| WhatsApp Watcher | Complete |
| Social Media Integration | Complete |
| Odoo Accounting | Complete |
| Cross-Domain Integration | Complete |
| Error Recovery | Complete |
| Audit Logging | Complete |
| Ralph Wiggum Loop | Complete |
| CEO Briefing | Complete |

## Documentation

- `.claude/skills/ai-employee/SKILL.md` - Complete skill documentation
- `mcp_servers/*/README.md` - MCP server documentation
- `schedulers/README.md` - Scheduling guide
- `recovery/` - Error recovery and audit systems
- `ralph_loop/` - Ralph Wiggum autonomous execution

## Next Steps (Platinum Tier)

1. **Deploy to Cloud VM 24/7**
   - Oracle Cloud Free Tier
   - Always-on watchers

2. **Work-Zone Specialization**
   - Cloud: Email triage, drafts, social drafts
   - Local: Approvals, WhatsApp, payments, sends

3. **Vault Sync**
   - Git-based sync
   - Or Syncthing
   - Claim-by-move rule

4. **Odoo on Cloud**
   - 24/7 accounting
   - HTTPS, backups

5. **A2A Upgrade** (Optional)
   - Direct agent messaging
   - Vault as audit record

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Watchers not starting | `pip install -r watchers/requirements.txt` |
| WhatsApp login | Run visible, scan QR code |
| Odoo connection | Check URL, DB, credentials |
| Social posting | Configure API or use browser |
| Errors piling up | Check `/Audit/Error_Report_*.md` |

## License

MIT License - Built for Personal AI Employee Hackathon 0

## Credits

Built with Claude Code and Obsidian for the Personal AI Employee Hackathon 0.

**Your Digital FTE - Working 24/7**

"I'm failing! And I'll keep failing until I don't fail anymore!" - Ralph Wiggum Loop
