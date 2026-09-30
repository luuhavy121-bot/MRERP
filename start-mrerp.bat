@echo off
setlocal EnableExtensions
cd /d "%~dp0"

title MRERP Local Launcher

where docker >nul 2>&1
if errorlevel 1 (
  echo [MRERP] Docker CLI was not found. Install or repair Docker Desktop first.
  pause
  exit /b 1
)

if not exist ".env" (
  copy /Y ".env.example" ".env" >nul
  echo [MRERP] A local .env file was created from .env.example.
  echo Replace the placeholder values, save the file, then run this launcher again.
  start "" notepad.exe "%~dp0.env"
  pause
  exit /b 1
)

docker info >nul 2>&1
if errorlevel 1 call :start_docker
if errorlevel 1 goto :docker_failed

echo [MRERP] Starting containers...
docker compose --env-file ".env" up -d
if errorlevel 1 goto :compose_failed

echo [MRERP] Waiting for http://localhost:4173/ ...
for /L %%I in (1,1,60) do (
  curl.exe -fsS "http://localhost:4173/" >nul 2>&1
  if not errorlevel 1 goto :ready
  ping -n 3 127.0.0.1 >nul
)

echo [MRERP] Frontend did not become ready within 120 seconds.
echo Run: docker compose --env-file .env ps
pause
exit /b 1

:ready
echo [MRERP] Ready. Opening the application...
start "" "http://localhost:4173/"
ping -n 3 127.0.0.1 >nul
exit /b 0

:start_docker
set "DOCKER_DESKTOP=%LOCALAPPDATA%\Programs\DockerDesktop\Docker Desktop.exe"
if not exist "%DOCKER_DESKTOP%" set "DOCKER_DESKTOP=C:\Program Files\Docker\Docker\Docker Desktop.exe"

if not exist "%DOCKER_DESKTOP%" exit /b 1

echo [MRERP] Starting Docker Desktop...
start "" "%DOCKER_DESKTOP%"

for /L %%I in (1,1,60) do (
  docker info >nul 2>&1
  if not errorlevel 1 exit /b 0
  ping -n 3 127.0.0.1 >nul
)

exit /b 1

:docker_failed
echo [MRERP] Docker Desktop could not be started or did not become ready.
pause
exit /b 1

:compose_failed
echo [MRERP] Docker Compose could not start the project.
echo Review the output above, then run this launcher again.
pause
exit /b 1
