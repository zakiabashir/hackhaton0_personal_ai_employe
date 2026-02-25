# Scheduler Scripts

Part of Silver Tier AI Employee - Automated task scheduling.

## Windows Task Scheduler

### Start All Watchers on Startup

1. Open Task Scheduler
2. Create Basic Task
3. Name: "AI Employee - Start Watchers"
4. Trigger: At startup
5. Action: Start a program
   - Program: `E:\hackhaton0_personal_ai_employe\schedulers\start_all_watchers.bat`

### Daily Tasks (9:00 AM)

1. Create Basic Task
2. Name: "AI Employee - Daily Tasks"
3. Trigger: Daily at 9:00 AM
4. Action: Start a program
   - Program: `bash` (or WSL bash)
   - Arguments: `E:\hackhaton0_personal_ai_employe\schedulers\daily_tasks.sh`

### Weekly Tasks (Monday 9:00 AM)

1. Create Basic Task
2. Name: "AI Employee - Weekly Tasks"
3. Trigger: Weekly on Monday at 9:00 AM
4. Action: Start a program
   - Program: `bash`
   - Arguments: `E:\hackhaton0_personal_ai_employe\schedulers\weekly_tasks.sh`

## Linux/Mac Cron Jobs

Add to crontab with `crontab -e`:

```bash
# Start watchers on reboot
@reboot cd /path/to/watchers && python3 filesystem_watcher.py &
@reboot cd /path/to/watchers && python3 approval_watcher.py &

# Daily tasks at 9 AM
0 9 * * * /path/to/schedulers/daily_tasks.sh

# Weekly tasks on Monday at 9 AM
0 9 * * 1 /path/to/schedulers/weekly_tasks.sh
```

## Manual Execution

### Start all watchers:
```bash
# Windows
schedulers\start_all_watchers.bat

# Linux/Mac
cd watchers
python3 filesystem_watcher.py &
python3 approval_watcher.py &
```

### Stop all watchers:
```bash
# Windows
schedulers\stop_all_watchers.bat

# Linux/Mac
pkill -f filesystem_watcher
pkill -f approval_watcher
```

### Run daily tasks manually:
```bash
bash schedulers/daily_tasks.sh
```

### Run weekly tasks manually:
```bash
bash schedulers/weekly_tasks.sh
```
