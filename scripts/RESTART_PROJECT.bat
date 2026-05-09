@echo off
setlocal

echo ----------------------------------------------------
echo 🚀 AI Business Insights Dashboard - Systems Restart
echo ----------------------------------------------------

cd /d "%~dp0\.."

:: 1. Terminate any existing processes on relevant ports
echo.
echo 🛑 Shutting down existing services...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5000') do taskkill /F /PID %%a 2>nul
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5173') do taskkill /F /PID %%a 2>nul
echo ✅ Cleanup complete.

:: 2. Start Backend (Flask)
echo.
echo 📦 Launching Backend API (Flask)...
cd backend
start /B python app.py > ..\logs\backend.log 2>&1
cd ..
echo ✅ Backend started in background on http://localhost:5000

:: 3. Start Frontend (React/Vite)
echo.
echo 🎨 Launching Frontend UI (React/Vite)...
cd frontend
start /B npm run dev > ..\logs\frontend.log 2>&1
cd ..
echo ✅ Frontend started in background on http://localhost:5173

echo.
echo ----------------------------------------------------
echo ✨ System restart triggered! 
echo.
echo Backend logs: [logs\backend.log]
echo Frontend logs: [logs\frontend.log]
echo.
echo 🌐 Opening dashboard at: http://localhost:5173
timeout /t 5 /nobreak > nul
start http://localhost:5173
echo ----------------------------------------------------

endlocal
