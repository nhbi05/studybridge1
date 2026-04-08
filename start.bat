@echo off
REM StudyBridge - Full Stack Startup Script (Windows)

echo.
echo ===================================
echo StudyBridge Full Stack Startup
echo ===================================
echo.

REM Check if running from correct directory
if not exist "backend" (
    echo Error: backend folder not found
    echo Please run this from studybridge1 root directory
    pause
    exit /b 1
)

if not exist "frontend" (
    echo Error: frontend folder not found
    echo Please run this from studybridge1 root directory
    pause
    exit /b 1
)

echo Starting Backend (FastAPI)...
echo.

REM Check if backend .env exists
if not exist "backend\.env" (
    echo ERROR: backend\.env not found!
    echo.
    echo Please create backend\.env with:
    echo   SUPABASE_URL=your-url
    echo   SUPABASE_KEY=your-key
    echo   ANTHROPIC_API_KEY=your-key
    echo.
    pause
    exit /b 1
)

REM Start backend in new window
start "StudyBridge Backend" cmd /k "cd backend && python main.py"
timeout /t 2

echo Backend starting at http://localhost:8000
echo API Docs at http://localhost:8000/docs
echo.

echo Starting Frontend (Next.js)...
echo.

REM Check if frontend .env.local exists
if not exist "frontend\.env.local" (
    echo Creating frontend\.env.local...
    echo NEXT_PUBLIC_API_URL=http://localhost:8000 > "frontend\.env.local"
)

REM Start frontend in new window
start "StudyBridge Frontend" cmd /k "cd frontend && npm run dev"
timeout /t 2

echo Frontend starting at http://localhost:3000
echo.

echo ===================================
echo Setup Complete!
echo ===================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:3000
echo Docs:     http://localhost:8000/docs
echo.
echo Both servers are running in separate windows.
echo Close the windows to stop the servers.
echo.

pause
