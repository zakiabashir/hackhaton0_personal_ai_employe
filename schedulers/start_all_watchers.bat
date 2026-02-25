@echo off
REM Start All Watchers - Windows Task Scheduler Script
REM Part of Silver Tier AI Employee

set VAULT_PATH=E:\hackhaton0_personal_ai_employe\AI_Employee_Vault
set WATCHER_DIR=E:\hackhaton0_personal_ai_employe\watchers
set LOG_DIR=%VAULT_PATH%\Logs

echo ============================================
echo Starting AI Employee Watchers
echo ============================================
echo Time: %date% %time%
echo Vault: %VAULT_PATH%
echo ============================================

REM Create logs directory if not exists
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

REM Start FileSystem Watcher
echo Starting FileSystem Watcher...
start /min "FileSystemWatcher" python "%WATCHER_DIR%\filesystem_watcher.py" --vault "%VAULT_PATH%"

REM Start Approval Watcher
echo Starting Approval Watcher...
start /min "ApprovalWatcher" python "%WATCHER_DIR%\approval_watcher.py" --vault "%VAULT_PATH%"

echo ============================================
echo All watchers started
echo ============================================
echo.
echo Watchers are running in background windows.
echo Check %LOG_DIR% for activity logs.
echo.
echo To stop all watchers, run stop_all_watchers.bat
echo ============================================

timeout /t 3
