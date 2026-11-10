[CmdletBinding()]
param (
    [switch]$Check,
    [switch]$All,
    [string]$Skill,
    [switch]$NoSync
)

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

$argsList = @()
if ($Check) {
    $argsList += "--check"
} elseif ($All) {
    $argsList += "--update"
    $argsList += "--all"
} elseif ($Skill) {
    $argsList += "--update"
    $argsList += "--skill"
    $argsList += $Skill
} else {
    Write-Host "====================================================================" -ForegroundColor Cyan
    Write-Host "            Agent Skills 上游 GitHub 自动更新管理终端" -ForegroundColor Cyan
    Write-Host "====================================================================" -ForegroundColor Cyan
    Write-Host " [1] 快速检查更新（仅查询远端，不修改任何本地技能）"
    Write-Host " [2] 一键更新全部技能（自动快照备份 + 拉取上游 + 保护本地定制技能）"
    Write-Host " [3] 更新指定单个技能（按名称更新）"
    Write-Host " [4] 退出"
    Write-Host "====================================================================" -ForegroundColor Cyan
    $choice = Read-Host "请输入选项编号 (1-4，默认 1)"
    if ([string]::IsNullOrWhiteSpace($choice)) { $choice = "1" }

    switch ($choice) {
        "1" { $argsList += "--check" }
        "2" { $argsList += @("--update", "--all") }
        "3" {
            $s = Read-Host "请输入要更新的技能名称 (如 brainstorming / code-review)"
            $argsList += @("--update", "--skill", $s)
        }
        "4" { exit 0 }
        default { $argsList += "--check" }
    }
}

if (-not $NoSync -and ($argsList -contains "--update")) {
    $argsList += "--sync"
}

python update_skills.py @argsList
