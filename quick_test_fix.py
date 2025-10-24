#!/usr/bin/env python3
"""
Quick Fix Verification - Test the exact curl command that was failing
"""

import requests
import json

# The exact payload from the user's curl command
test_payload = {
    "prediction_id": 123,
    "doctor_id": "DR001", 
    "prediction_accurate": True,
    "confidence_in_feedback": 0.85,
    "clinical_notes": "Patient responded well to treatment"
}

print("🔧 Testing the exact curl command that was failing...")
print("=" * 50)

try:
    # Make the request
    response = requests.post(
        "http://127.0.0.1:8000/api/v1/feedback/prediction-feedback",
        json=test_payload,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    
    if response.status_code == 200:
        print("✅ SUCCESS! The KeyError has been fixed!")
        print(f"Response Body: {json.dumps(response.json(), indent=2)}")
    else:
        print(f"❌ Error Status: {response.status_code}")
        print(f"Response Body: {response.text}")
        
except requests.exceptions.ConnectionError:
    print("❌ Connection Error: API server is not running")
    print("Please start the server with: python -m uvicorn app.main:app --reload")
except Exception as e:
    print(f"❌ Unexpected Error: {str(e)}")

print("\n" + "=" * 50)
print("Fix Summary:")
print("- Fixed KeyError: 0 by adding proper array validation")
print("- Added safe access to prediction.predictions[0]")
print("- Added error handling for empty prediction arrays")
print("- Used .get() method for safe dictionary access")