@echo off
setlocal

set "ROOT=%~dp0"

if not exist "%ROOT%.env" (
  copy /Y "%ROOT%.env.example" "%ROOT%.env" >nul
  echo [INFO] Generated .env from .env.example
)

where docker >nul 2>nul
if errorlevel 1 (
  echo [ERROR] Docker command not found. Please install Docker Desktop first.
  exit /b 1
)

docker info >nul 2>nul
if errorlevel 1 (
  echo [ERROR] Docker Desktop is not running. Please start it and retry.
  exit /b 1
)

docker compose --env-file "%ROOT%.env" -f "%ROOT%docker\docker-compose.yml" up -d --build
if errorlevel 1 (
  echo [ERROR] Docker Compose failed to start.
  exit /b 1
)

echo.
echo [OK] Stowage system is up
echo App entry: http://localhost:8088
echo Backend Swagger: http://localhost:8080/swagger-ui.html
echo Algorithm Swagger: http://localhost:8000/docs
echo.
echo If you changed ports in .env, use those ports instead.

endlocal
