#!/bin/bash

# install if necessary
if [ ! -d ".venv" ]; then
    python scripts/install.py
fi

# activate .venv
source .venv/bin/activate

# start without blocking the terminal
nohup python3 -m screenrecorder.main >/dev/null 2>&1 &
