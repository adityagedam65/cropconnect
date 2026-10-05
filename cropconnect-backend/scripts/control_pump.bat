@echo off
cd /d "%~dp0.."
if "%1"=="" goto :usage
if "%2"=="" (
    python scripts\control_pump.py %1
) else (
    python scripts\control_pump.py %1 %2
)
goto :eof

:usage
echo ESP32 Pump Control
echo Usage: control_pump.bat [on^|off] [pump_id]
echo Examples:
echo   control_pump.bat on
echo   control_pump.bat off pump2
echo.
echo Make sure Python is installed and available in PATH
pause
