# PowerShell restore script for new computer or workspace
param(
    [string]$TargetDir = "",
    [switch]$Global = $false
)

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$skillsSource = Join-Path $scriptDir "skills"
$agentsMdSource = Join-Path $scriptDir "AGENTS.md"

if (-not (Test-Path $skillsSource)) {
    Write-Error "未找到 skills 目录！"
    exit 1
}

if ($TargetDir -eq "") {
    if ($Global) {
        $userHome = [System.Environment]::GetFolderPath('UserProfile')
        $TargetDir = Join-Path $userHome ".agents\skills"
    } else {
        # Default: current workspace or parent workspace's .agents/skills
        $parent = Split-Path -Parent $scriptDir
        $TargetDir = Join-Path $parent ".agents\skills"
    }
}

Write-Host "==> 目标技能目录: $TargetDir" -ForegroundColor Cyan

if (-not (Test-Path $TargetDir)) {
    New-Item -ItemType Directory -Path $TargetDir -Force | Out-Null
}

$skillFolders = Get-ChildItem -Path $skillsSource -Directory
Write-Host "==> 准备还原 $($skillFolders.Count) 个技能..." -ForegroundColor Cyan

foreach ($folder in $skillFolders) {
    $dest = Join-Path $TargetDir $folder.Name
    Copy-Item -Path $folder.FullName -Destination $dest -Recurse -Force
    Write-Host "  [+] 已还原: $($folder.Name)" -ForegroundColor Green
}

# Copy AGENTS.md if target is a project workspace
$targetParent = Split-Path -Parent $TargetDir
$targetAgentsMd = Join-Path $targetParent "AGENTS.md"
if (Test-Path $agentsMdSource) {
    Copy-Item -Path $agentsMdSource -Destination $targetAgentsMd -Force
    Write-Host "  [+] 已还原: AGENTS.md -> $targetAgentsMd" -ForegroundColor Green
}

Write-Host "`n==> 全部技能还原完成！Antigravity、Claude Code 等 Agent 即刻可用。" -ForegroundColor Cyan
