@echo off
echo === Jay Uninstaller ===

net session >nul 2>&1
if %errorLevel% neq 0 (
    echo Error: Run as Administrator.
    pause
    exit /b 1
)

echo Removing Files...
if exist "C:\Jay" rmdir /S /Q "C:\Jay"

echo Removing Registry Keys...
reg delete "HKCR\.jay" /f 2>nul
reg delete "HKCR\JayFile" /f 2>nul

echo Removing VS Code Extension...
if exist "%USERPROFILE%\.vscode\extensions\jay-language-support" rmdir /S /Q "%USERPROFILE%\.vscode\extensions\jay-language-support"

echo Removing PATH entry...
powershell -Command "[Environment]::SetEnvironmentVariable('PATH', ($env:PATH -replace ';C:\\Jay',''), 'Machine')"

echo ✅ Jay uninstalled.
pause
