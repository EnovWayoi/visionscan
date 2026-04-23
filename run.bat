@echo off
echo Starting VisionScan...

IF NOT EXIST ".venv\Scripts\python.exe" (
    echo Virtual environment not found. Initializing...
    python -m venv .venv
    IF ERRORLEVEL 1 (
        echo Fallback to py launcher...
        py -3 -m venv .venv
        IF ERRORLEVEL 1 (
            echo Python is required but not found. Please install Python 3.12+ and add it to your PATH.
            pause
            exit /b 1
        )
    )
    echo Installing uv package manager...
    .venv\Scripts\python.exe -m pip install uv
    echo Syncing dependencies...
    .venv\Scripts\python.exe -m uv sync
)

.venv\Scripts\python.exe main.py
pause
