#!/usr/bin/env python3
"""
Test Script for Feedback API KeyError Fix
Tests various prediction data scenarios to ensure robust error handling
"""

import requests
import json
import sys
from datetime import datetime

# API Configuration
BASE_URL = "http://127.0.0.1:8000"
FEEDBACK_ENDPOINT = f"{BASE_URL}/api/v1/feedback/prediction-feedback"

def test_feedback_api():
    """Test feedback API with different scenarios"""
    
    print("🧪 Testing Feedback API - KeyError Fix Verification")
    print("=" * 60)
    
    # Test Case 1: Valid feedback for existing prediction (should work)
    test_case_1 = {
        "prediction_id": 999,  # This will create mock prediction
        "doctor_id": "DR001",
        "prediction_accurate": True,
        "confidence_in_feedback": 0.85,
        "clinical_notes": "Patient shows clear signs of muscle strain",
        "outcome_notes": "Recommended rest and physiotherapy"
    }
    
    print("✅ Test Case 1: Valid feedback with accurate prediction")
    print(f"Payload: {json.dumps(test_case_1, indent=2)}")
    
    try:
        response = requests.post(FEEDBACK_ENDPOINT, json=test_case_1)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✅ SUCCESS: Feedback submitted successfully!")
        else:
            print(f"❌ FAILED: Status {response.status_code}")
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
    
    print("\n" + "-" * 40 + "\n")
    
    # Test Case 2: Feedback with correction (prediction_accurate = False)
    test_case_2 = {
        "prediction_id": 998,
        "doctor_id": "DR002", 
        "prediction_accurate": False,
        "actual_disease_id": 2,
        "actual_condition_name": "Lower Back Strain",
        "confidence_in_feedback": 0.90,
        "clinical_notes": "Initial prediction was incorrect, this is actually lower back strain",
        "outcome_notes": "Prescribed anti-inflammatory medication",
        "ordered_tests": ["X-ray lumbar spine"],
        "prescribed_medications": ["Ibuprofen 400mg"]
    }
    
    print("✅ Test Case 2: Feedback with prediction correction")
    print(f"Payload: {json.dumps(test_case_2, indent=2)}")
    
    try:
        response = requests.post(FEEDBACK_ENDPOINT, json=test_case_2)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✅ SUCCESS: Correction feedback submitted successfully!")
        else:
            print(f"❌ FAILED: Status {response.status_code}")
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
    
    print("\n" + "-" * 40 + "\n")
    
    # Test Case 3: Low confidence feedback (should not add to training data)
    test_case_3 = {
        "prediction_id": 997,
        "doctor_id": "DR003",
        "prediction_accurate": True,
        "confidence_in_feedback": 0.60,  # Low confidence
        "clinical_notes": "Uncertain about diagnosis",
        "outcome_notes": "Need more tests to confirm"
    }
    
    print("✅ Test Case 3: Low confidence feedback")
    print(f"Payload: {json.dumps(test_case_3, indent=2)}")
    
    try:
        response = requests.post(FEEDBACK_ENDPOINT, json=test_case_3)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS: Low confidence feedback handled correctly!")
            if not result.get('training_data_added', True):
                print("✅ CORRECT: Low confidence feedback not added to training data")
        else:
            print(f"❌ FAILED: Status {response.status_code}")
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")

def test_health_check():
    """Test if API is running"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ API Health Check: PASSED")
            return True
        else:
            print(f"❌ API Health Check: FAILED - Status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API Health Check: FAILED - {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Feedback API Test Suite")
    print(f"Target API: {BASE_URL}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Check if API is running
    if not test_health_check():
        print("\n❌ API is not running! Please start the FastAPI server first:")
        print("   cd c:\\Users\\Babu\\Documents\\WORKAREA\\pdpcds-project")
        print("   python -m uvicorn app.main:app --reload")
        sys.exit(1)
    
    print("\n")
    test_feedback_api()
    
    print("\n" + "=" * 60)
    print("🎯 Test Suite Completed!")
    print("Expected Results:")
    print("- All test cases should return 200 status")
    print("- No KeyError: 0 should occur")
    print("- High confidence feedback should add training data")
    print("- Low confidence feedback should not add training data")