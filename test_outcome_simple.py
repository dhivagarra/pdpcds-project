#!/usr/bin/env python3

"""
Simple test for clinical outcome API endpoint
"""

import requests
import json

def test_clinical_outcome():
    """Test the clinical outcome endpoint with the exact data from the error"""
    
    # Your exact test data that caused the error
    test_data = {
        "prediction_id": 3094,
        "patient_outcome": "improved",
        "final_diagnosis_id": 1,
        "final_condition_name": "Confirmed diagnosis",
        "treatment_effective": True,
        "side_effects": [],
        "diagnosis_confirmation_days": 1,
        "treatment_duration_days": 7,
        "readmission_required": False,
        "complications": [],
        "reported_by": "DR001",
        "outcome_date": "2025-10-21T05:28:57Z"
    }
    
    try:
        response = requests.post(
            "http://127.0.0.1:8000/api/v1/feedback/clinical-outcome",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS! Clinical outcome submitted successfully!")
            print(f"Response: {json.dumps(result, indent=2)}")
            return True
        else:
            print(f"❌ ERROR: Status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Could not connect to server. Make sure it's running on port 8000")
        return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Clinical Outcome API with exact error data")
    print("=" * 60)
    success = test_clinical_outcome()
    print("=" * 60)
    if success:
        print("✅ Test passed! The clinical outcome endpoint is now working.")
    else:
        print("❌ Test failed! Check the server and try again.")