@echo off
REM Start server using virtual environment Python explicitly
cd /d "C:\Users\Babu\Documents\WORKAREA\pdpcds-project"
"C:\Users\Babu\Documents\WORKAREA\pdpcds-project\.venv\Scripts\python.exe" -m uvicorn app.main:app --reload --port 8000