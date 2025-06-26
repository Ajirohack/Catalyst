#!/bin/bash
cd "/Volumes/Project Disk/Catalyst/backend"
source venv/bin/activate
echo "Installing backend requirements..."
pip install -r requirements.txt
echo "Starting backend server..."
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
