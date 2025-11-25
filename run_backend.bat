@echo off
REM Batch file to set up and run the backend server

echo ==================================================
echo  Setting up and starting the backend server...
echo ==================================================

REM Change to the backend directory
cd backend

REM Check if virtual environment exists, if not create it
IF NOT EXIST venv (
    echo --- Creating virtual environment...
    python -m venv venv
    IF %ERRORLEVEL% NEQ 0 (
        echo.
        echo ERROR: Failed to create virtual environment.
        echo Please ensure Python and venv are installed and in your PATH.
        pause
        exit /b
    )
)

REM Activate the virtual environment
echo --- Activating virtual environment...
call .\venv\Scripts\activate.bat

REM Install dependencies
echo --- Installing dependencies from requirements.txt...
pip install -r requirements.txt
IF %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Failed to install dependencies.
    echo Please check your internet connection and requirements.txt file.
    pause
    exit /b
)

REM Run the FastAPI server
echo --- Starting FastAPI server at http://localhost:8000 ---
echo --- Press CTRL+C to stop the server. ---
uvicorn main:app --reload

REM Deactivate virtual environment (will run when server is stopped)
echo --- Server stopped. ---

pause
