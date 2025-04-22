@echo off
setlocal

:: Set the target folder to the current folder
set "TargetFolder=%~dp0"

echo ==========================================================================
echo    Installation of necessary dependencies
echo ==========================================================================
echo.

:: Check if Python is installed
where python >nul 2>&1
if %errorlevel% neq 0 goto pythonNotInstalled

:pythonInstalled
echo Python is installed.
echo.

:: Check if Winget is installed
where winget >nul 2>&1
if %errorlevel% neq 0 goto wingetNotInstalled
goto dependenciesChecked

:wingetNotInstalled
echo ==========================================================================
echo    WARNING: Winget is NOT installed.
echo    The dependency scripts might use Winget to install additional components.
echo    If you encounter errors during script execution, it might be due to missing dependencies
echo    that Winget would have installed.
echo    Winget can be obtained from the Microsoft Store or GitHub (https://github.com/microsoft/winget-cli).
echo ==========================================================================
echo.
pause
goto dependenciesChecked

:pythonNotInstalled
echo Python is not installed on your system. This script requires Python to run.
echo.
echo Please select an option:
echo 1. I will install Python myself and then press Enter to continue.
echo 2. Try to install Python automatically using Winget (requires internet connection).
echo.
:pythonInstallChoice
set "pythonChoice="
set /p "pythonChoice=Enter your choice (1 or 2): "
if not defined pythonChoice (
    echo Error: Please enter a value.
    echo.
    goto pythonInstallChoice
)
if not "%pythonChoice%"=="1" if not "%pythonChoice%"=="2" (
    echo Error: Invalid choice. Please enter 1 or 2.
    echo.
    goto pythonInstallChoice
)
echo.

if "%pythonChoice%"=="1" goto waitForManualPythonInstall
if "%pythonChoice%"=="2" goto tryInstallPython

:waitForManualPythonInstall
echo Please install Python. Once the installation is complete, press Enter to continue.
pause
goto pythonInstalled

:tryInstallPython
echo Checking if Winget is installed...
where winget >nul 2>&1
if %errorlevel% neq 0 goto wingetMissingForPythonInstall

echo Attempting to install Python using Winget...
winget install Python.Python.3 -s msstore --accept-source-agreements --force
if %errorlevel% == 0 goto pythonInstalled
echo.
echo Automatic Python installation failed. Please try installing manually.
echo You can find Python at: https://www.python.org/downloads/
echo Press Enter to continue after manual installation.
pause
goto pythonInstalled

:wingetMissingForPythonInstall
echo Winget is not installed on your system. Automatic Python installation cannot proceed.
echo Winget can be obtained from the Microsoft Store or GitHub (https://github.com/microsoft/winget-cli).
echo.
echo Please install Python and Winget manually. Once both are installed, press Enter to continue.
echo Python: https://www.python.org/downloads/
echo Winget: https://github.com/microsoft/winget-cli
pause
goto dependenciesChecked

:dependenciesChecked
echo.
echo Python is installed.
echo Winget check complete.
echo Continuing with the script...
echo Target folder set to current directory: "%TargetFolder%"
echo.

set "logFileName=script_log_%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%.log"
set "logFilePath=%TargetFolder%%logFileName%"

pause
goto mainMenu

:mainMenu
echo ==========================================================================
echo    Let's get your books ready for conversion!
echo    But first, we need to make sure the necessary components can run.
echo ==========================================================================
echo.
echo Please select an action:
echo.
echo    1. Run BOTH dependency scripts (install_dependencies_p1.py and install_dependencies_p2.py)
echo    2. Run ONLY the first dependency script (install_dependencies_p1.py)
echo    3. Run ONLY the second dependency script (install_dependencies_p2.py)
echo    4. Exit the script
echo.
:getMainChoice
set "choice="
set /p "choice=Enter your choice (1-4): "
if not defined choice (
    echo Error: Please enter a value.
    echo.
    goto getMainChoice
)
if not "%choice%"=="1" if not "%choice%"=="2" if not "%choice%"=="3" if not "%choice%"=="4" (
    echo Error: Invalid choice. Please enter 1, 2, 3, or 4.
    echo.
    goto getMainChoice
)
echo.
if "%choice%"=="1" goto runBoth
if "%choice%"=="2" goto runPart1
if "%choice%"=="3" goto runPart2
if "%choice%"=="4" goto exitScript

:runBoth
echo ------------------------------------------------------
echo Starting install_dependencies_p1.py ...
echo ------------------------------------------------------
set "PowerShellCommand1=powershell -NoProfile -ExecutionPolicy Bypass -Command python.exe '%TargetFolder%install_dependencies_p1.py' '%TargetFolder%'"
%PowerShellCommand1%
if errorlevel 1 goto script1Error

:continueOrRetry
echo.
echo ------------------------------------------------------
echo install_dependencies_p1.py completed successfully.
echo ------------------------------------------------------
echo.
echo What would you like to do next?
echo.
echo    1. Continue to the next script (install_dependencies_p2.py)
echo    2. Save log to file
echo    3. Retry the previous script (install_dependencies_p1.py)
echo    4. Return to the main menu
echo.
:getContinueChoice
set "continueChoice="
set /p "continueChoice=Enter your choice (1-4): "
if not defined continueChoice (
    echo Error: Please enter a value.
    echo.
    goto getContinueChoice
)
if not "%continueChoice%"=="1" if not "%continueChoice%"=="2" if not "%continueChoice%"=="3" if not "%continueChoice%"=="4" (
    echo Error: Invalid choice. Please enter 1, 2, 3, or 4.
    echo.
    goto getContinueChoice
)
echo.
if "%continueChoice%"=="1" goto runPart2Both
if "%continueChoice%"=="2" goto printLogToFile
if "%continueChoice%"=="3" goto runBoth
if "%continueChoice%"=="4" goto mainMenu

:runPart2Both
echo ------------------------------------------------------
echo Starting install_dependencies_p2.py ...
echo ------------------------------------------------------
set "PowerShellCommand2=powershell -NoProfile -ExecutionPolicy Bypass -Command python.exe '%TargetFolder%install_dependencies_p2.py' '%TargetFolder%'"
%PowerShellCommand2%
goto finished

:runPart1
echo ------------------------------------------------------
echo Starting install_dependencies_p1.py ...
echo ------------------------------------------------------
set "PowerShellCommandPart1=powershell -NoProfile -ExecutionPolicy Bypass -Command python.exe '%TargetFolder%install_dependencies_p1.py' '%TargetFolder%'"
%PowerShellCommandPart1%
goto finished

:runPart2
echo ------------------------------------------------------
echo Starting install_dependencies_p2.py ...
echo ------------------------------------------------------
set "PowerShellCommandPart2=powershell -NoProfile -ExecutionPolicy Bypass -Command python.exe '%TargetFolder%install_dependencies_p2.py' '%TargetFolder%'"
%PowerShellCommandPart2%
goto finished

:script1Error
echo.
echo ==========================================================================
echo    ERROR: An error occurred during the execution of install_dependencies_p1.py!
echo    Please check the log file for detailed information.
echo ==========================================================================
goto finishedOptions

:finished
echo.
echo ==========================================================================
echo    Success! All selected dependency scripts have completed successfully.
echo ==========================================================================
goto finishedOptions

:finishedOptions
echo.
echo What would you like to do now?
echo.
echo    1. Exit the script
echo    2. Save the log to a file
echo    3. Retry the previous action
echo    4. Return to the main menu
echo.
:getEndChoice
set "endChoice="
set /p "endChoice=Enter your choice (1-4): "
if not defined endChoice (
    echo Error: Please enter a value.
    echo.
    goto getEndChoice
)
if not "%endChoice%"=="1" if not "%endChoice%"=="2" if not "%endChoice%"=="3" if not "%endChoice%"=="4" (
    echo Error: Invalid choice. Please enter 1, 2, 3, or 4.
    echo.
    goto getEndChoice
)
echo.
if "%endChoice%"=="1" goto exitScript
if "%endChoice%"=="2" goto printLogToFile
if "%endChoice%"=="3" goto retryPrevious
if "%endChoice%"=="4" goto mainMenu

:printLogToFile
echo.
echo Log saved to: "%logFilePath%"
echo.
pause
goto finishedOptions

:retryPrevious
if "%choice%"=="1" goto runBoth
if "%choice%"=="2" goto runPart1
if "%choice%"=="3" goto runPart2
goto mainMenu

:exitScript
echo.
echo Exiting...
timeout /t 2 >nul
exit

endlocal
