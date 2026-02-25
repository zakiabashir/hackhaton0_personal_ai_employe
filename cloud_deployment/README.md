# Cloud Deployment - Platinum Tier
## Deploy AI Employee to Oracle Cloud Free Tier

This directory contains scripts and configuration for deploying the AI Employee to run 24/7 on a cloud VM.

---

## Oracle Cloud Free Tier Setup

### Prerequisites

- Oracle Cloud Account (Free)
- SSH key pair
- Domain (optional, for HTTPS)

### VM Specifications (Free Tier)

- **Shape:** VM.Standard.E2.1.Micro
- **vCPUs:** 1 (always free)
- **Memory:** 1 GB RAM
- **Storage:** 2 x 50 GB boot volumes
- **Bandwidth:** 10 TB/month

---

## Quick Start

### 1. Create Oracle Cloud VM

```bash
# Via Oracle Cloud Console
# Compute -> Instances -> Create Instance
# Name: ai-employee-cloud
# Shape: VM.Standard.E2.1.Micro (Always Free)
# Image: Ubuntu 22.04 or Canonical Ubuntu 22.04
# SSH Key: Upload your public key
```

### 2. Connect to VM

```bash
ssh -i ~/.ssh/your_key ubuntu@<your-vm-public-ip>
```

### 3. Run Setup Script

```bash
# Copy setup script to VM
scp -i ~/.ssh/your_key setup_cloud.sh ubuntu@<vm-ip>:~

# Execute setup
ssh -i ~/.ssh/your_key ubuntu@<vm-ip> "bash setup_cloud.sh"
```

---

## Cloud Agent Responsibilities

### What Cloud Agent DOES:
- Monitor emails (Gmail API)
- Draft email replies
- Draft social media posts
- Generate content calendars
- Create plans and suggestions
- Write updates to /Updates/ folder
- Health monitoring

### What Cloud Agent DOES NOT DO:
- Send emails (requires approval)
- Post to social media (requires approval)
- Access WhatsApp sessions
- Process payments/banking
- Final send/post actions

---

## Local Agent Responsibilities

### What Local Agent DOES:
- Approve/reject drafts from Cloud
- Send approved emails
- Post approved social media
- WhatsApp monitoring
- Payment/banking operations
- Merge Cloud updates to Dashboard
- Final execution actions

### What Local Agent DOES NOT DO:
- Monitor emails continuously
- Generate content drafts
- Health monitoring (Cloud handles this)

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     CLOUD VM (24/7)                          │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Cloud Agent                                           │  │
│  │  - Email Monitoring                                    │  │
│  │  - Content Generation                                  │  │
│  │  - Draft Creation                                      │  │
│  │  - Health Monitoring                                   │  │
│  │  - Writes to /Updates/, /Signals/                      │  │
│  └───────────────────────────────────────────────────────┘  │
│                           │                                  │
│                           ▼                                  │
│                    Git Vault Sync                            │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ Git Pull/Push
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   LOCAL MACHINE                              │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Local Agent                                           │  │
│  │  - Review Cloud drafts                                │  │
│  │  - Approve/Reject actions                              │  │
│  │  - Execute sends/posts                                 │  │
│  │  - WhatsApp monitoring                                 │  │
│  │  - Payment operations                                  │  │
│  │  - Update Dashboard                                    │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                               │
│  Obsidian Vault (Synced via Git)                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Security Rules

### What IS synced (Git):
- Markdown files (*.md)
- State files (*.json)
- Folders: /Updates/, /Signals/, /Plans/, /Needs_Action/

### What is NOT synced:
- .env files (credentials)
- WhatsApp sessions
- Banking credentials
- Payment tokens
- SSH keys
- Local secrets

---

## Health Monitoring

Cloud agent runs health checks every 5 minutes:

```python
# Checks:
- Vault sync status
- Git connectivity
- Pending items in /Needs_Action/
- Drafts awaiting approval
- System resources (CPU, RAM, Disk)
```

Health status written to `/Signals/health.json`

---

## Deployment Steps

### Phase 1: Initial Setup

1. **Create VM** (see above)
2. **Install Dependencies** (run `setup_cloud.sh`)
3. **Configure Git** (run `setup_git_sync.sh`)
4. **Deploy Cloud Agent** (run `deploy_cloud_agent.sh`)
5. **Start Services** (run `start_services.sh`)

### Phase 2: Configure Work Zones

1. Edit `cloud_agent_config.yaml`
2. Edit `local_agent_config.yaml`
3. Test claim-by-move system
4. Test approval workflow

### Phase 3: Deploy Odoo (Optional)

1. Run `setup_odoo_cloud.sh`
2. Configure HTTPS
3. Set up backups
4. Test MCP connection

---

## Troubleshooting

### Cloud VM not accessible
- Check security list (firewall rules)
- Verify SSH key
- Check VM status in console

### Git sync not working
- Check SSH keys for GitHub/GitLab
- Verify repo permissions
- Check network connectivity

### Agent not running
- Check logs: `journalctl -u ai-employee-cloud`
- Restart: `systemctl restart ai-employee-cloud`

---

## Cost Estimate

**Oracle Cloud Free Tier:**
- VM: $0/month (Always Free)
- Storage: $0/month (2 x 50 GB)
- Bandwidth: $0/month (10 TB)
- **Total: $0/month**

**Optional Add-ons:**
- Domain: ~$10-15/year
- SSL Certificate: Free (Let's Encrypt)

---

## Next Steps

1. Create Oracle Cloud account
2. Set up VM following this guide
3. Run deployment scripts
4. Configure Git sync
5. Test Cloud/Local coordination

---

*Platinum Tier - Cloud + Local Executive*
*AI Employee - Production-ish*
