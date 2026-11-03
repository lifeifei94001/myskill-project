@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo [1/3] 正在同步本地技能...
python sync.py
if errorlevel 1 (
    echo 同步失败，请检查 Python 环境！
    pause
    exit /b 1
)

echo [2/3] 提交 Git 变更...
git add -A
git commit -m "backup: update skills catalog (%date% %time%)"

echo [3/3] 推送到 GitHub...
git push origin main

echo.
echo ==============================================
echo 备份完成！已成功推送到 lifeifei94001/myskill-project
echo ==============================================
pause
