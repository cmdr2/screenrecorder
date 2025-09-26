@echo off

@rem install if necessary
if not exist .venv (
    call python scripts\install.py
)

@rem activate .venv
call .venv\Scripts\activate.bat

@rem start without blocking the window, allowing it to close
start /B pythonw -m screenrecorder.main
