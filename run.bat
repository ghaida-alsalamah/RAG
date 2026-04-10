@echo off
echo.
echo  ============================================================
echo   GoRiyadh -- AI Tourist Guide
echo   Starting server at http://localhost:8000
echo  ============================================================
echo.
cd /d "%~dp0"
pip install fastapi uvicorn[standard] python-multipart -q
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
