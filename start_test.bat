@echo off
chcp 65001 > nul
title 八字配對系統本地測試工具

echo 🚀 啟動八字配對系統本地測試工具
echo ==================================================

REM 檢查Python腳本是否存在
if not exist "local_admin_test.py" (
    echo ❌ 找不到 local_admin_test.py
    echo 正在創建測試腳本...
    
    REM 這裡可以添加創建腳本的代碼，或者提示用戶手動創建
    echo 請確保 local_admin_test.py 文件存在
    pause
    exit /b 1
)

echo ✅ 找到測試腳本
echo.

REM 直接運行批處理文件
if exist "run_admin_tests.bat" (
    call run_admin_tests.bat
) else (
    echo ⚠️ 找不到 run_admin_tests.bat
    echo 正在直接運行測試...
    echo.
    python local_admin_test.py
)

pause