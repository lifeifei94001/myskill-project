@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ==============================================
echo 正在执行技能还原（恢复到当前工作区）...
echo ==============================================

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0restore.ps1"

echo.
pause
