@echo off
REM Stop All Watchers - Windows Script
REM Part of Silver Tier AI Employee

echo ============================================
echo Stopping AI Employee Watchers
echo ============================================

REM Kill all watcher processes
taskkill /FI "WINDOWTITLE eq FileSystemWatcher*" /F 2>nul
taskkill /FI "WINDOWTITLE eq ApprovalWatcher*" /F 2>nul
taskkill /FI "WINDOWTITLE eq GmailWatcher*" /F 2>nul

echo ============================================
echo All watchers stopped
echo ============================================

timeout /t 2
