@echo off
echo Starting Browser Tools MCP Server...

:: Check if npx is installed
where npx >nul 2>nul
if %errorlevel% neq 0 (
    echo Error: npx not found. Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)

:: Check if browser-tools-server is installed
npx @agentdeskai/browser-tools-server --version >nul 2>nul
if %errorlevel% neq 0 (
    echo Installing browser-tools-server...
    npm install -g @agentdeskai/browser-tools-server@latest
    if %errorlevel% neq 0 (
        echo Error: Failed to install browser-tools-server
        pause
        exit /b 1
    )
)

:: Kill any existing processes on port 3026
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :3026') do (
    taskkill /F /PID %%a 2>nul
)

:: Check if port 3026 is still in use
netstat -ano | findstr :3026 >nul
if %errorlevel% equ 0 (
    echo Warning: Port 3026 is still in use. Please close any applications using this port.
    pause
    exit /b 1
)

:: Start the browser tools server
echo Starting browser tools server on port 3026...
echo.
echo Important:
echo 1. Make sure you have installed the Browser Tools Chrome Extension
echo 2. Configure the cursor to use port 3026
echo.

npx @agentdeskai/browser-tools-server --port 3026

pause