@echo off
chcp 65001 > nul
echo 🔧 八字配對系統 - 本地管理員測試工具
echo ==================================================

REM 檢查Python是否安裝
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未找到Python，請先安裝Python 3.x
    pause
    exit /b 1
)

echo ✅ 找到Python
echo.

REM 檢查必要文件是否存在
if not exist "admin_service.py" (
    echo ❌ 找不到 admin_service.py
    echo 請將此文件放在與 admin_service.py 相同的目錄
    pause
    exit /b 1
)

if not exist "new_calculator.py" (
    echo ❌ 找不到 new_calculator.py
    echo 請將此文件放在與 new_calculator.py 相同的目錄
    pause
    exit /b 1
)

echo ✅ 所有必要文件都存在
echo.

REM 顯示菜單
:menu
echo 請選擇操作：
echo 1. 運行所有測試（20組八字）
echo 2. 列出所有測試案例
echo 3. 運行單個測試案例
echo 4. 查看幫助
echo 5. 退出
echo.

set /p choice="請輸入選擇 (1-5): "

if "%choice%"=="1" (
    echo.
    echo 🧪 開始運行所有測試...
    echo ==================================================
    python local_admin_test.py
    goto end
)

if "%choice%"=="2" (
    echo.
    echo 📋 列出所有測試案例...
    echo ==================================================
    python local_admin_test.py list
    goto end
)

if "%choice%"=="3" (
    echo.
    set /p testnum="請輸入測試編號 (1-20): "
    if "%testnum%"=="" (
        echo ❌ 請輸入有效的測試編號
        goto menu
    )
    echo 🔍 運行測試案例 #%testnum%...
    echo ==================================================
    python local_admin_test.py single %testnum%
    goto end
)

if "%choice%"=="4" (
    echo.
    echo 📖 幫助信息：
    echo ==================================================
    python local_admin_test.py help
    goto end
)

if "%choice%"=="5" (
    exit /b 0
)

echo ❌ 無效選擇，請重新輸入
echo.
goto menu

:end
echo.
echo ==================================================
echo 測試完成！按任意鍵返回菜單...
pause >nul
goto menu