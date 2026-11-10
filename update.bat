@echo off
chcp 65001 >nul
cd /d "%~dp0"

if not "%1"=="" (
    python update_skills.py %*
    goto :end
)

echo ====================================================================
echo             Agent Skills 上游 GitHub 自动更新管理终端
echo ====================================================================
echo  [1] 快速检查更新（仅查询远端，不修改任何本地技能）
echo  [2] 一键更新全部技能（自动快照备份 + 拉取上游 + 保护本地定制技能）
echo  [3] 更新指定单个技能（按名称更新）
echo  [4] 退出
echo ====================================================================
set /p choice="请输入选项编号 (1-4，默认 1): "

if "%choice%"=="" set choice=1
if "%choice%"=="1" (
    python update_skills.py --check
    goto :end
)
if "%choice%"=="2" (
    python update_skills.py --update --all --sync
    goto :end
)
if "%choice%"=="3" (
    set /p skill_name="请输入要更新的技能名称 (如 brainstorming / code-review): "
    python update_skills.py --update --skill %skill_name% --sync
    goto :end
)
if "%choice%"=="4" (
    exit /b 0
)

:end
echo.
pause
