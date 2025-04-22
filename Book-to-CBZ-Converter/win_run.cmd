@echo off
setlocal enabledelayedexpansion

:: Set the target folder location
set "TargetFolder=%~dp0"

:: Create a safe timestamp (YYYYMMDD_HHMM)
for /f "tokens=1-4 delims=/ " %%a in ("%date%") do (
    set year=%%d
    set month=%%b
    set day=%%c
)
for /f "tokens=1-2 delims=: " %%a in ("%time%") do (
    set hour=%%a
    set minute=%%b
)
:: Zero-pad single-digit hour
if "!hour!" lss "10" set hour=0!hour!
set "logFileName=error_log_!year!!month!!day!_!hour!!minute!.txt"
set "logFilePath=%TargetFolder%!logFileName!"

:: Try running convert_books.py
echo Running convert_books.py...
python "%~dp0convert_books.py" "%TargetFolder%"
set "pythonErrorLevel=%errorlevel%"

if %pythonErrorLevel% neq 0 (
    echo Error occurred during convert_books.py (exit code: %pythonErrorLevel%). Check error log: "%logFilePath%"
    call :logError "Error during convert_books.py with exit code: %pythonErrorLevel%"
) else (
    echo convert_books.py completed successfully.
)

echo All tasks completed!
timeout /t 3 >nul
exit /b

:: Function to log errors
:logError
echo [%date% %time%] %~1 >> "%logFilePath%"
exit /b 1
