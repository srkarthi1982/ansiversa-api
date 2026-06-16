@echo off
call .venv\Scripts\activate.bat

cls

echo Starting Ansiversa API...

uvicorn app.main:app --reload
