#!/usr/bin/env python3
"""
Test the clinical feedback API endpoints
"""

import requests
import json
from datetime import datetime

# API base URL
BASE_URL = "http://127.0.0.1:8000/api/v1"

def test_feedback_api():
    """Test the feedback API endpoints"""
    
    print("🧪 Testing Clinical Feedback API")
    print("=" * 50)
    
    # First, let's see what predictions exist
    print("\n1. Checking existing predictions...")
    try:
        # This assumes your API is running
        response = requests.get(f"{BASE_URL}/predict/")
        print(f"API Status: {response.status_code}")
        
        if response.status_code != 200:
            print("❌ API not running. Please start the server with: uvicorn app.main:app --reload")
            return
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Please start the server with: uvicorn app.main:app --reload")
        return
    
    # Test submitting feedback
    print("\n2. Testing feedback submission...")
    
    feedback_data = {
        "prediction_id": 1,  # Assuming prediction ID 1 exists
        "doctor_id": "dr_smith_123",
        "doctor_name": "Dr. Sarah Smith",
        "hospital_unit": "Emergency Department",
        "prediction_accurate": True,
        "confidence_in_feedback": 0.95,
        "ordered_tests": [0, 3, 4],  # ECG, chest X-ray, CBC
        "prescribed_medications": [1, 2],  # antibiotics, pain relief
        "clinical_notes": "Patient responded well to treatment. Symptoms improved within 24 hours.",
        "outcome_notes": "Complete recovery. Patient discharged after 3 days."
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/feedback/prediction-feedback",
            json=feedback_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Feedback submission status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Feedback submitted successfully!")
            print(f"   Feedback ID: {result['feedback_id']}")
            print(f"   Training data added: {result['training_data_added']}")
            print(f"   Accuracy rate: {result['prediction_accuracy_rate']:.1%}")
        else:
            print(f"❌ Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error submitting feedback: {e}")
    
    # Test adding training data directly
    print("\n3. Testing direct training data addition...")
    
    training_data = {
        "age": 45,
        "sex": "female",
        "vital_temperature_c": 37.8,
        "vital_heart_rate": 95,
        "vital_blood_pressure_systolic": 140,
        "vital_blood_pressure_diastolic": 85,
        "symptom_list": ["fever", "cough", "fatigue"],
        "pmh_list": ["hypertension"],
        "current_medications": ["lisinopril"],
        "allergies": ["penicillin"],
        "chief_complaint": "Fever and productive cough for 3 days",
        "free_text_notes": "Patient presents with typical symptoms of respiratory infection. Chest clear on auscultation.",
        "confirmed_disease_id": 34,  # pneumonia
        "confirmed_condition_name": "pneumonia",
        "ordered_tests": [3, 4, 6],  # chest X-ray, CBC, sputum culture
        "prescribed_medications": [1, 2, 3],  # antibiotics, bronchodilator, expectorant
        "data_source": "api_test",
        "quality_score": 0.98,
        "is_validated": True,
        "created_by": "test_doctor",
        "add_to_validation_set": False
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/feedback/add-training-data",
            json=training_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Training data addition status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Training data added successfully!")
            print(f"   Record ID: {result['record_id']}")
            print(f"   Condition: {result['condition']}")
            print(f"   Dataset: {result['dataset_type']}")
        else:
            print(f"❌ Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error adding training data: {e}")
    
    # Test getting feedback statistics
    print("\n4. Testing feedback statistics...")
    
    try:
        response = requests.get(f"{BASE_URL}/feedback/feedback-stats?days=30")
        
        print(f"Stats request status: {response.status_code}")
        
        if response.status_code == 200:
            stats = response.json()
            print("✅ Feedback statistics retrieved!")
            print(f"   Total feedback: {stats.get('total_feedback', 0)}")
            print(f"   Unique predictions: {stats.get('unique_predictions_with_feedback', 0)}")
            print(f"   Unique doctors: {stats.get('unique_doctors', 0)}")
            if stats.get('total_feedback', 0) > 0:
                print(f"   Accuracy rate: {stats.get('prediction_accuracy_rate', 0):.1%}")
        else:
            print(f"❌ Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error getting stats: {e}")

def show_api_usage():
    """Show how doctors would use the feedback API"""
    
    print("\n" + "=" * 60)
    print("🏥 DOCTOR FEEDBACK API USAGE EXAMPLES")
    print("=" * 60)
    
    print("""
## 1. Doctor Confirms Correct Prediction

POST /api/v1/feedback/prediction-feedback
{
    "prediction_id": 123,
    "doctor_id": "dr_jones_456", 
    "doctor_name": "Dr. Michael Jones",
    "prediction_accurate": true,
    "confidence_in_feedback": 0.9,
    "ordered_tests": [0, 3, 4],
    "prescribed_medications": [1, 2],
    "clinical_notes": "Prediction was accurate. Patient responded well to suggested treatment."
}

## 2. Doctor Corrects Wrong Prediction  

POST /api/v1/feedback/prediction-feedback
{
    "prediction_id": 124,
    "doctor_id": "dr_patel_789",
    "doctor_name": "Dr. Priya Patel", 
    "prediction_accurate": false,
    "confidence_in_feedback": 0.95,
    "actual_disease_id": 27,
    "actual_condition_name": "heart_failure",
    "ordered_tests": [0, 5, 7, 8],
    "prescribed_medications": [8, 9, 10],
    "clinical_notes": "Initial prediction was pneumonia, but further tests revealed heart failure."
}

## 3. Get Feedback Summary for a Prediction

GET /api/v1/feedback/prediction/123/summary
Returns: {
    "prediction_id": 123,
    "total_feedback_count": 3,
    "accuracy_rate": 0.67,
    "consensus_reached": false,
    "most_common_actual_diagnosis": "heart_failure" 
}

## 4. Add Expert-Validated Training Case

POST /api/v1/feedback/add-training-data
{
    "age": 65,
    "sex": "male", 
    "vital_temperature_c": 37.2,
    "vital_heart_rate": 88,
    "symptom_list": ["chest pain", "shortness of breath"],
    "confirmed_disease_id": 27,
    "confirmed_condition_name": "heart_failure",
    "ordered_tests": [0, 5, 7],
    "prescribed_medications": [8, 9],
    "created_by": "dr_expert_cardiology"
}
    """)

if __name__ == "__main__":
    test_feedback_api()
    show_api_usage()