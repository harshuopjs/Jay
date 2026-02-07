@echo off
setlocal
echo === Jay Installer v7.0 ===

:: Check Admin
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo Error: Run as Administrator.
    pause
    exit /b 1
)

echo Installing C:\Jay...
if exist "C:\Jay" rmdir /S /Q "C:\Jay"
mkdir "C:\Jay"
if %errorlevel% neq 0 goto :fail
xcopy /E /I /Y "jay" "C:\Jay\"
if %errorlevel% neq 0 goto :fail

echo Creating Launcher...
(
@echo off
echo python "C:\Jay\cli.py" %%*
) > "C:\Jay\jay.bat"
if %errorlevel% neq 0 goto :fail

echo Updating PATH...
setx PATH "%PATH%;C:\Jay" /M
if %errorlevel% neq 0 goto :fail

echo Registering File Associations...
reg add "HKCR\.jay" /ve /d "JayFile" /f
if %errorlevel% neq 0 goto :fail
reg add "HKCR\JayFile" /ve /d "Jay Source Code" /f
if %errorlevel% neq 0 goto :fail
if exist "C:\Jay\icons\jay.ico" (
    reg add "HKCR\JayFile\DefaultIcon" /ve /d "C:\Jay\icons\jay.ico" /f
    if %errorlevel% neq 0 goto :fail
)

echo Checking for VS Code...
if exist "%USERPROFILE%\.vscode\extensions" (
    echo Installing VS Code Extension...
    if exist "%USERPROFILE%\.vscode\extensions\jay-language-support" rmdir /S /Q "%USERPROFILE%\.vscode\extensions\jay-language-support"
    mkdir "%USERPROFILE%\.vscode\extensions\jay-language-support"
    xcopy /E /I /Y "jay-vscode-extension" "%USERPROFILE%\.vscode\extensions\jay-language-support\"
    if %errorlevel% neq 0 echo Warning: VS Code extension install failed.
) else (
    echo VS Code extensions folder not found. Skipping extension install.
)

echo ----------------------------------------
echo Jay has been installed successfully.
echo Please restart your computer to complete the setup.
echo After restart, open Command Prompt and run:
echo     jay --version
echo ----------------------------------------
echo.
set /P RESTART="Do you want to restart now? (Y/N) "
if /I "%RESTART%"=="Y" (
    shutdown /r /t 5
)
goto :eof

:fail
echo.
echo Installation FAILED.
pause
exit /b 1
