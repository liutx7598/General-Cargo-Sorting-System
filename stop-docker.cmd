@echo off
setlocal

set "ROOT=%~dp0"

where docker >nul 2>nul
if errorlevel 1 (
  echo [ERROR] Docker command not found. Please install Docker Desktop first.
  exit /b 1
)

if not exist "%ROOT%.env" (
  copy /Y "%ROOT%.env.example" "%ROOT%.env" >nul
)

docker compose --env-file "%ROOT%.env" -f "%ROOT%docker\docker-compose.yml" down
if errorlevel 1 (
  echo [ERROR] Docker Compose failed to stop.
  exit /b 1
)

echo [OK] Stowage system is stopped

endlocal
