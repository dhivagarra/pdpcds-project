#!/usr/bin/env python3

"""
Test script to verify the clinical outcome endpoint is working correctly
"""

import requests
import json
from datetime import datetime

# Test data
test_outcome = {
    "prediction_id": 1,
    "patient_outcome": "improved", 
    "final_diagnosis_id": 5,
    "final_condition_name": "Community-acquired pneumonia",
    "treatment_effective": True,
    "side_effects": ["mild nausea"],
    "diagnosis_confirmation_days": 2,
    "treatment_duration_days": 7,
    "readmission_required": False,
    "complications": [],
    "reported_by": "DR001",
    "outcome_date": "2025-10-21T10:00:00.000Z"
}

def test_clinical_outcome_endpoint():
    """Test the clinical outcome endpoint"""
    
    base_url = "http://127.0.0.1:8000"
    
    # First test basic health
    try:
        health_response = requests.get(f"{base_url}/health")
        print(f"Health check: {health_response.status_code}")
        print(f"Health response: {health_response.json()}")
    except Exception as e:
        print(f"Health check failed: {e}")
        return False
    
    # Test clinical outcome endpoint
    try:
        response = requests.post(
            f"{base_url}/api/v1/feedback/clinical-outcome",
            json=test_outcome,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Clinical outcome status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Clinical outcome endpoint working!")
            print(f"Response: {json.dumps(result, indent=2)}")
            return True
        else:
            print(f"❌ Clinical outcome endpoint failed: {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Clinical outcome endpoint error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Clinical Outcome API Endpoint")
    print("=" * 50)
    
    success = test_clinical_outcome_endpoint()
    
    if success:
        print("\n✅ Clinical outcome endpoint verification successful!")
    else:
        print("\n❌ Clinical outcome endpoint verification failed!")