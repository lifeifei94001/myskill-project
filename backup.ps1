# PowerShell backup script
$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $scriptDir

Write-Host "==> 正在同步本地技能与元数据..." -ForegroundColor Cyan
python sync.py

Write-Host "==> 检查 Git 状态..." -ForegroundColor Cyan
git add -A

$status = git status --porcelain
if (-not $status) {
    Write-Host "==> 没有检测到技能变动，已是最新状态！" -ForegroundColor Green
    exit 0
}

$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
$commitMsg = "backup: update skills catalog ($timestamp)"

Write-Host "==> 提交更新: $commitMsg" -ForegroundColor Cyan
git commit -m $commitMsg

Write-Host "==> 推送到 GitHub (lifeifei94001/myskill-project)..." -ForegroundColor Cyan
git push origin main

Write-Host "==> 备份完成！已成功推送到 GitHub。" -ForegroundColor Green
