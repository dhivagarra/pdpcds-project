"""
Test script to demonstrate the Clinical Decision Support System API
"""

import requests
import json
from datetime import datetime

# API endpoint
BASE_URL = "http://127.0.0.1:8000"

def test_health_endpoint():
    """Test the health check endpoint"""
    print("🔍 Testing Health Endpoint...")
    
    response = requests.get(f"{BASE_URL}/health")
    if response.status_code == 200:
        print("✅ Health check passed!")
        print(f"   Response: {response.json()}")
    else:
        print(f"❌ Health check failed: {response.status_code}")
    
    print()

def test_prediction_endpoint():
    """Test the disease prediction endpoint"""
    print("🔍 Testing Disease Prediction Endpoint...")
    
    # Sample patient data - case of suspected pneumonia
    patient_data = {
        "age": 54,
        "sex": "female",
        "vital_temperature_c": 38.2,
        "vital_heart_rate": 110,
        "symptom_list": ["fever", "productive cough", "fatigue"],
        "pmh_list": ["hypertension"],
        "free_text_notes": "Patient reports 3 days of worsening cough with yellow sputum. Shortness of breath on exertion.",
        "chief_complaint": "Cough and fever"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/predict/",
            json=patient_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print("✅ Prediction successful!")
            result = response.json()
            
            print(f"   Processing time: {result['processing_time_ms']:.2f}ms")
            print(f"   Model version: {result['model_version']}")
            print(f"   Number of predictions: {len(result['predictions'])}")
            print()
            
            # Display predictions
            for i, prediction in enumerate(result['predictions'], 1):
                print(f"   Prediction #{i}:")
                print(f"     🏥 Diagnosis: {prediction['diagnosis']}")
                print(f"     🔢 ICD-10 Code: {prediction['icd10_code']}")
                print(f"     📊 Confidence: {prediction['confidence']:.2%}")
                
                if prediction['recommended_tests']:
                    print(f"     🧪 Recommended Tests:")
                    for test in prediction['recommended_tests']:
                        print(f"       - {test['test']} (confidence: {test['confidence']:.2%})")
                
                if prediction['recommended_medications']:
                    print(f"     💊 Recommended Medications:")
                    for med in prediction['recommended_medications']:
                        print(f"       - {med['medication']} - {med.get('dose_suggestion', 'As directed')}")
                        print(f"         Confidence: {med['confidence']:.2%}")
                
                print(f"     📋 Assessment: {prediction['assessment_plan']}")
                print(f"     💭 Rationale: {', '.join(prediction['rationale'])}")
                print()
                
        else:
            print(f"❌ Prediction failed: {response.status_code}")
            print(f"   Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
    
    print()

def test_api_documentation():
    """Test API documentation endpoint"""
    print("🔍 Testing API Documentation...")
    
    response = requests.get(f"{BASE_URL}/docs")
    if response.status_code == 200:
        print("✅ API documentation is accessible!")
        print(f"   Visit: {BASE_URL}/docs for interactive API docs")
    else:
        print(f"❌ API documentation failed: {response.status_code}")
    
    print()

def main():
    """Run all tests"""
    print("🚀 Clinical Decision Support System - API Test Suite")
    print("=" * 60)
    print()
    
    # Test health endpoint
    test_health_endpoint()
    
    # Test prediction endpoint
    test_prediction_endpoint()
    
    # Test documentation
    test_api_documentation()
    
    print("🎉 Test suite completed!")
    print(f"   API Server: {BASE_URL}")
    print(f"   Interactive Docs: {BASE_URL}/docs")
    print(f"   API Documentation: {BASE_URL}/redoc")

if __name__ == "__main__":
    main()