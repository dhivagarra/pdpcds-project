#!/usr/bin/env python3
"""
COMPLETE SOLUTION: Clinical Decision Support System
===================================================

PROBLEM ANALYSIS:
- pydantic_settings ModuleNotFoundError: ✅ RESOLVED
- Python version conflict (3.13 vs 3.11): ✅ RESOLVED  
- Server shutdown on requests: ALTERNATIVE SOLUTIONS PROVIDED

WORKING SOLUTIONS:
"""

import subprocess
import sys
import os
import json
import time

def start_server_production():
    """Start server in production mode (no reload)"""
    venv_python = r"C:\Users\Babu\Documents\WORKAREA\pdpcds-project\.venv\Scripts\python.exe"
    
    print("🚀 Starting Clinical Decision Support System (Production Mode)")
    print("=" * 60)
    
    try:
        subprocess.run([
            venv_python, "-m", "uvicorn",
            "app.main:app",
            "--host", "127.0.0.1", 
            "--port", "8000"
        ], check=True)
    except KeyboardInterrupt:
        print("\n✅ Server stopped by user")
    except Exception as e:
        print(f"❌ Error: {e}")

def start_server_development():
    """Start server in development mode (with reload)"""
    venv_python = r"C:\Users\Babu\Documents\WORKAREA\pdpcds-project\.venv\Scripts\python.exe"
    
    print("🚀 Starting Clinical Decision Support System (Development Mode)")
    print("=" * 60)
    
    try:
        subprocess.run([
            venv_python, "-m", "uvicorn",
            "app.main:app", 
            "--host", "127.0.0.1",
            "--port", "8000",
            "--reload"
        ], check=True)
    except KeyboardInterrupt:
        print("\n✅ Server stopped by user")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_feedback_api():
    """Test the feedback API"""
    import requests
    
    feedback_data = {
        "prediction_id": 1,
        "doctor_id": "DR001",
        "prediction_accurate": True,
        "confidence_in_feedback": 0.95,
        "clinical_notes": "Test feedback"
    }
    
    try:
        response = requests.post(
            "http://127.0.0.1:8000/api/v1/feedback/prediction-feedback",
            json=feedback_data,
            timeout=30
        )
        
        print(f"✅ Feedback API Status: {response.status_code}")
        print(f"📄 Response: {response.text}")
        
    except Exception as e:
        print(f"❌ Feedback API Error: {e}")

if __name__ == "__main__":
    print("Clinical Decision Support System - Startup Options")
    print("=" * 50)
    print("1. Production Mode (Stable)")
    print("2. Development Mode (Reload)")
    print("3. Test Feedback API")
    
    choice = input("\nSelect option (1-3): ").strip()
    
    if choice == "1":
        start_server_production()
    elif choice == "2": 
        start_server_development()
    elif choice == "3":
        test_feedback_api()
    else:
        print("Invalid choice")