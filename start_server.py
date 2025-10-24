#!/usr/bin/env python3
"""
Start the Clinical Decision Support System server
This script ensures we use the correct Python environment
"""

import subprocess
import sys
import os

# Get the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
venv_python = os.path.join(script_dir, ".venv", "Scripts", "python.exe")

# Check if virtual environment Python exists
if not os.path.exists(venv_python):
    print(f"Error: Virtual environment Python not found at {venv_python}")
    print("Please ensure the virtual environment is set up correctly.")
    sys.exit(1)

print(f"Starting server using: {venv_python}")
print("Clinical Decision Support System")
print("================================")

try:
    # Start the server using the virtual environment Python
    subprocess.run([
        venv_python, "-m", "uvicorn", 
        "app.main:app", 
        "--host", "127.0.0.1",
        "--port", "8000",
        "--reload"
    ], cwd=script_dir)
except KeyboardInterrupt:
    print("\nServer stopped by user")
except Exception as e:
    print(f"Error starting server: {e}")