# Personal AI Employee - Platinum Tier

**Status:** Platinum Tier Complete
**Last Updated:** 2026-02-25
**Built for:** Personal AI Employee Hackathon 0

## Overview

A complete Digital FTE (Full-Time Equivalent) AI Employee deployed across Cloud VM (24/7) and Local Machine with Work-Zone specialization. Built with Claude Code, featuring cross-domain integration, multi-platform social media, WhatsApp monitoring, Odoo accounting, comprehensive audit logging, error recovery, and autonomous execution.

**Cost:** $0/month (Oracle Cloud Free Tier)

## Tier Status: Platinum - Complete

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

### Platinum Deliverables
- [x] **Cloud VM 24/7 deployment** (Oracle Free Tier)
- [x] **Work-Zone specialization** (Cloud drafts, Local approves)
- [x] **Vault sync via Git** (security rules enforced)
- [x] **Claim-by-move system** (prevents double-work)
- [x] **Single-writer rule** for Dashboard.md (Local only)
- [x] **Cloud writes to /Updates/** and /Signals/health.json
- [x] **Odoo on Cloud VM** deployment scripts

## Architecture

```
hackhaton0_personal_ai_employe/
├── AI_Employee_Vault/          # Obsidian vault
│   ├── Dashboard.md            # Main dashboard (Platinum)
│   ├── Company_Handbook.md     # Operating procedures
│   ├── Inbox/                  # New items
│   ├── Needs_Action/           # Pending tasks
│   ├── In_Progress/            # Claimed tasks
│   │   ├── cloud_agent/        # Cloud claimed
│   │   └── local_agent/        # Local claimed
│   ├── Drafts/                 # Awaiting approval
│   ├── Pending_Approval/       # Approval requests
│   ├── Approved/               # Approved actions
│   ├── Rejected/               # Rejected actions
│   ├── Done/                   # Completed
│   ├── Plans/                  # Execution plans
│   ├── Updates/                # Cloud → Local updates
│   ├── Signals/                # Health signals
│   ├── Personal/               # Personal domain
│   ├── Business/               # Business domain
│   ├── Accounting/             # Financial records
│   └── Audit/                  # Audit reports
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
├── cloud_deployment/           # Cloud VM setup
│   ├── README.md               # Deployment guide
│   ├── setup_cloud.sh          # VM initialization
│   ├── setup_git_sync.sh       # Git repository setup
│   └── setup_odoo_cloud.sh     # Odoo deployment
├── orchestrator/                # Cloud + Local agents
│   ├── cloud_agent.py          # Runs on Cloud VM
│   └── local_agent.py          # Runs on Local machine
├── vault_sync/                 # Git-based synchronization
│   ├── sync.py                 # Vault sync implementation
│   └── claim_by_move.py        # Task ownership system
├── .claude/
│   └── skills/
│       └── ai-employee/        # AI Employee skill
│           └── SKILL.md
├── README.md                   # This file
├── HACKATHON_COMPLETE_SUMMARY.md  # Hackathon summary
└── skills-lock.json            # Skill registry
```

## Cloud + Local Architecture

```
┌─────────────────────────────────────────────────────────────┐
│              CLOUD VM (24/7 Oracle Free Tier)                │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Cloud Agent: Email triage, drafts, content, health  │  │
│  │  Odoo: Accounting (24/7)                               │  │
│  └───────────────────────────────────────────────────────┘  │
│                           │                                  │
│                    Git Vault Sync                            │
│              (Security: No credentials synced)               │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   LOCAL MACHINE                              │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Local Agent: Approvals, sends, WhatsApp, payments   │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                               │
│  Obsidian Vault (Synced via Git)                             │
└─────────────────────────────────────────────────────────────┘
```

## Work-Zone Specialization

### Cloud Agent (Cloud VM)
**DOES:**
- Monitor Gmail 24/7
- Draft email replies
- Draft social media posts
- Generate content calendars
- Create execution plans
- Health monitoring
- Write to /Updates/, /Signals/

**NEVER DOES:**
- Send emails
- Post to social media
- Access WhatsApp sessions
- Process payments

### Local Agent (Local Machine)
**DOES:**
- Review Cloud drafts
- Approve/Reject actions
- Send approved emails
- Post approved social media
- WhatsApp monitoring
- Payment/banking operations
- Update Dashboard (single-writer rule)

**NEVER DOES:**
- Continuous email monitoring
- Generate content drafts
- Health monitoring

## Quick Start

### Local Deployment (No Cloud Required)

```bash
# Install dependencies
pip install -r watchers/requirements.txt
playwright install chromium

# Install MCP servers
cd mcp_servers/email-mcp && npm install
cd mcp_servers/social-mcp && npm install
cd mcp_servers/odoo-mcp && npm install

# Start watchers
schedulers\start_all_watchers.bat

# Generate plan
cd watchers
python reasoning_loop.py --action plan
```

### Cloud Deployment (Optional - For 24/7 Operation)

```bash
# 1. Create Oracle Cloud Free Tier VM
# 2. Setup VM
cd cloud_deployment
scp setup_cloud.sh ubuntu@<vm-ip>:~
ssh ubuntu@<vm-ip> "bash setup_cloud.sh"

# 3. Setup Git sync
ssh ubuntu@<vm-ip> "bash setup_git_sync.sh <repo_url>"

# 4. Start Cloud Agent
ssh ubuntu@<vm-ip> "bash start_cloud_agent.sh"

# 5. Start Local Agent (on local machine)
cd orchestrator
python local_agent.py
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

## Platinum Tier Features

| Feature | Status |
|---------|--------|
| Bronze Tier | Complete |
| Silver Tier | Complete |
| Gold Tier | Complete |
| Platinum Tier | Complete |
| Cloud Deployment | Scripts ready |
| Work-Zone Specialization | Implemented |
| Vault Sync (Git) | Implemented |
| Claim-by-Move | Implemented |
| Security Rules | Enforced |

## Documentation

- `README.md` - Project overview (this file)
- `HACKATHON_COMPLETE_SUMMARY.md` - Complete hackathon summary
- `.claude/skills/ai-employee/SKILL.md` - Complete skill documentation
- `mcp_servers/*/README.md` - MCP server documentation
- `schedulers/README.md` - Scheduling guide
- `cloud_deployment/README.md` - Cloud deployment guide
- `recovery/` - Error recovery and audit systems
- `ralph_loop/` - Ralph Wiggum autonomous execution

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Watchers not starting | `pip install -r watchers/requirements.txt` |
| WhatsApp login | Run visible, scan QR code |
| Odoo connection | Check URL, DB, credentials |
| Social posting | Configure API or use browser |
| Errors pile up | Check `/Audit/Error_Report_*.md` |
| Cloud sync failing | Check SSH keys, repo permissions |
| Git conflicts | Run `python vault_sync/sync.py --action check` |

## License

MIT License - Built for Personal AI Employee Hackathon 0

## Credits

Built with Claude Code and Obsidian for the Personal AI Employee Hackathon 0.

**Your Production-Grade Digital FTE - Working 24/7 for $0/month**

*"I'm failing! And I'll keep failing until I don't fail anymore!" - Ralph Wiggum Loop*
