---
name: ai-employee
description: |
  Production-grade Personal AI Employee deployed to Cloud VM 24/7 with Work-Zone
  specialization. Cloud handles email triage/drafts/social drafts, Local handles approvals/
  WhatsApp/payments/sends. Vault sync via Git with claim-by-move system.
  Platinum Tier - Always-On Cloud + Local Executive.
---

# AI Employee Skill - Platinum Tier

**Production-Grade Digital FTE - Cloud + Local Executive Architecture**

Personal AI Employee deployed across Cloud VM (24/7) and Local Machine with Work-Zone specialization. Cloud handles continuous monitoring and drafting, Local handles approvals and final execution.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│              CLOUD VM (24/7 Oracle Free Tier)                │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Cloud Agent Responsibilities:                         │  │
│  │  - Email triage & monitoring (24/7)                   │  │
│  │  - Draft email replies (NEVER SEND)                   │  │
│  │  - Draft social media posts (NEVER POST)              │  │
│  │  - Generate content calendars                          │  │
│  │  - Create execution plans                              │  │
│  │  - Write updates to /Updates/ folder                   │  │
│  │  - Health monitoring                                   │  │
│  │  - Odoo accounting (Cloud deployment)                  │  │
│  └───────────────────────────────────────────────────────┘  │
│                           │                                  │
│                    Git Vault Sync                            │
│              (Security: No credentials synced)               │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ Git Pull/Push
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   LOCAL MACHINE                              │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Local Agent Responsibilities:                          │  │
│  │  - Review Cloud drafts                                 │  │
│  │  - Approve/Reject actions                               │  │
│  │  - Send approved emails                                 │  │
│  │  - Post approved social media                           │  │
│  │  - WhatsApp monitoring                                  │  │
│  │  - Payment/banking operations                           │  │
│  │  - Update Dashboard (single-writer rule)               │  │
│  │  - Merge Cloud updates                                  │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                               │
│  Obsidian Vault (Synced via Git)                             │
└─────────────────────────────────────────────────────────────┘
```

## Work-Zone Specialization

### Cloud Zone (Cloud Agent)
**DOES:**
- Monitor Gmail 24/7
- Draft email replies
- Draft social media posts (FB/IG/Twitter/LinkedIn)
- Generate content calendars
- Create execution plans
- Health monitoring
- Run Odoo for accounting (cloud deployment)
- Write to /Updates/, /Signals/ folders

**NEVER DOES:**
- Send emails (requires Local approval)
- Post to social media (requires Local approval)
- Access WhatsApp sessions (security)
- Process payments/banking (security)

### Local Zone (Local Agent)
**DOES:**
- Approve/reject Cloud drafts
- Send approved emails
- Post approved social media
- WhatsApp monitoring
- Payment/banking operations
- Update Dashboard.md (single-writer rule)
- Final "send/post" actions
- Merge Cloud updates into Dashboard

**NEVER DOES:**
- Continuous email monitoring (Cloud handles)
- Generate content drafts (Cloud handles)
- Health monitoring (Cloud handles)

## Vault Sync via Git

### Setup

```bash
# On Cloud VM
cd cloud_deployment
bash setup_cloud.sh
bash setup_git_sync.sh <repo_url>

# On Local Machine
python vault_sync/sync.py --init --repo <repo_url>
```

### Security Rules

**IS synced (Git):**
- Markdown files (*.md)
- JSON state files
- /Updates/ folder
- /Signals/ folder
- /Plans/ folder
- /Needs_Action/ folder
- /Drafts/ folder (drafts only, no credentials)

**NEVER synced:**
- .env files (credentials)
- WhatsApp sessions
- Banking credentials
- Payment tokens
- SSH keys
- Local secrets

### Sync Commands

```bash
# Pull updates
python vault_sync/sync.py --action pull

# Push updates
python vault_sync/sync.py --action push

# Check status
python vault_sync/sync.py --action status
```

## Claim-by-Move System

Prevents double-work between Cloud and Local agents.

### Rule

First agent to move an item from `/Needs_Action` to `/In_Progress/<agent>/` owns it. Other agents must ignore it.

### Usage

```bash
# Claim a task
python vault_sync/claim_by_move.py --agent cloud_agent --action claim --task example.md

# Check available tasks
python vault_sync/claim_by_move.py --agent cloud_agent --action list

# Check status
python vault_sync/claim_by_move.py --agent local_agent --action status

# Release task (complete)
python vault_sync/claim_by_move.py --agent local_agent --action release --task example.md
```

### Folders

```
/In_Progress/
├── cloud_agent/      # Tasks claimed by Cloud
└── local_agent/      # Tasks claimed by Local
```

## Cloud Deployment

### Oracle Cloud Free Tier

- **VM:** VM.Standard.E2.1.Micro (Always Free)
- **vCPUs:** 1
- **RAM:** 1 GB
- **Storage:** 2 x 50 GB
- **Cost:** $0/month

### Setup Steps

1. **Create Oracle Cloud account**
2. **Create VM** (Ubuntu 22.04)
3. **Run setup script:**
   ```bash
   scp setup_cloud.sh ubuntu@<vm-ip>:~
   ssh ubuntu@<vm-ip> "bash setup_cloud.sh"
   ```
4. **Setup Git sync:**
   ```bash
   ssh ubuntu@<vm-ip> "bash setup_git_sync.sh <repo_url>"
   ```
5. **Deploy Cloud Agent:**
   ```bash
   ssh ubuntu@<vm-ip> "bash start_cloud_agent.sh"
   ```
6. **Setup Odoo (optional):**
   ```bash
   ssh ubuntu@<vm-ip> "bash setup_odoo_cloud.sh"
   ```

## Odoo Cloud Deployment

### Features

- Odoo Community 19+ on Cloud VM
- 24/7 availability
- HTTPS with Let's Encrypt
- Automated backups
- MCP integration for draft-only accounting

### Setup

```bash
# On Cloud VM
bash setup_odoo_cloud.sh 19.0
```

### Access

- URL: `http://<vm-ip>:8069`
- Admin password: Set during installation
- Database: Auto-created

### Integration

Cloud Agent uses Odoo MCP for:
- Draft invoices (require Local approval)
- Draft payments (require Local approval)
- CEO Briefing generation
- Weekly accounting audits

## Local Agent Configuration

### Start Local Agent

```bash
cd orchestrator
python local_agent.py
```

### What Local Agent Does

1. **Sync vault** (pull Cloud updates)
2. **Check /Approved/** for approved actions
3. **Execute sends/posts** (email, social media)
4. **Monitor WhatsApp**
5. **Process payments**
6. **Update Dashboard** (single-writer rule)
7. **Push updates** for Cloud to see

### Approvals Workflow

```
Cloud creates draft in /Drafts/
    ↓
Local reviews draft
    ↓
Local moves to /Approved/
    ↓
Local Agent executes (send/post)
    ↓
Moves to /Done/
```

## Health Monitoring

Cloud Agent writes health status every 5 minutes:

```json
{
  "timestamp": "2026-02-25T...",
  "agent": "cloud_agent",
  "status": "healthy",
  "uptime_seconds": 3600,
  "system": {
    "cpu_percent": 15,
    "memory_percent": 45,
    "disk_used_gb": 12.3
  },
  "tasks": {
    "drafts_awaiting_approval": 3,
    "in_progress": 2
  },
  "sync": {
    "last_sync": "2026-02-25T...",
    "git_status": "connected"
  }
}
```

Location: `/Signals/health.json`

## Single-Writer Rule for Dashboard

Only **Local Agent** writes to `Dashboard.md`.

Cloud Agent writes to:
- `/Updates/<update_type>_<timestamp>.json`
- `/Signals/health.json`

Local Agent then:
1. Reads /Updates/ folder
2. Merges updates into Dashboard.md
3. Pushes via Git

## Troubleshooting

### Cloud VM not accessible

1. Check Oracle Cloud Console
2. Verify security list (firewall)
3. Check VM is running
4. Verify SSH key

### Git sync not working

1. Check SSH keys for GitHub/GitLab
2. Verify repo permissions
3. Check network connectivity
4. Run `git status` for errors

### Agent not running

```bash
# Cloud
ssh ubuntu@<vm-ip> "systemctl status ai-employee-cloud"

# Local
python local_agent.py  # Check output
```

### Conflicts in vault

```bash
python vault_sync/sync.py --action check
```

## Tier Summary

| Tier | Status | Key Features |
|------|--------|-------------|
| Bronze | ✅ | Vault, watchers, basic automation |
| Silver | ✅ | Multiple watchers, LinkedIn, MCP, approval workflow |
| Gold | ✅ | WhatsApp, social platforms, Odoo, error recovery, audit, Ralph Wiggum |
| Platinum | ✅ | Cloud 24/7, Work-Zone specialization, Git sync, claim-by-move |

## Configuration Files

- `cloud_deployment/cloud_agent_config.yaml` - Cloud Agent settings
- `orchestrator/local_agent_config.yaml` - Local Agent settings
- `vault_sync/.gitignore` - Security rules for sync

## Quick Start

```bash
# 1. Setup Cloud VM
# Create Oracle Cloud VM, then:
cd cloud_deployment
bash setup_cloud.sh
bash setup_git_sync.sh <repo_url>
bash start_cloud_agent.sh

# 2. Setup Local
cd orchestrator
python local_agent.py

# 3. Test sync
cd vault_sync
python sync.py --action pull
python sync.py --action push
```

## Best Practices

1. **Security:** Never sync credentials via Git
2. **Approvals:** Always review Cloud drafts before approving
3. **Sync:** Pull before working, push after changes
4. **Claims:** Use claim-by-move to avoid conflicts
5. **Health:** Monitor Cloud agent health signals
6. **Backups:** Regular vault backups (Git serves as backup)

---

**AI Employee - Platinum Tier**

*Production-Grade Digital FTE - Cloud + Local Executive*
*Built for Personal AI Employee Hackathon 0*
