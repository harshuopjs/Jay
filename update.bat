@echo off
echo === Jay Updater ===

if not exist "C:\Jay\jay.bat" (
    echo Jay is not installed. Run install.bat first.
    pause
    exit /b 1
)

call install.bat
echo ✅ Jay updated.
pause
