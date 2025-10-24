"""
Simple API test to verify background task execution
"""
import requests
import json
import time

# Test data
test_data = {
    "age": 35,
    "sex": "male",
    "vital_temperature_c": 38.5,
    "vital_heart_rate": 95,
    "vital_blood_pressure_systolic": 140,
    "vital_blood_pressure_diastolic": 85,
    "symptom_list": ["fever", "headache", "nausea"],
    "pmh_list": ["hypertension"],
    "free_text_notes": "API test - checking background task"
}

def test_api():
    print("🧪 Testing API with background task logging...")
    
    try:
        response = requests.post(
            "http://127.0.0.1:8000/api/v1/predict/",
            json=test_data,
            timeout=10
        )
        
        print(f"📨 Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ API call successful!")
            print(f"⚡ Processing time: {result.get('processing_time_ms', 0):.2f} ms")
            
            # Wait a bit for background task
            print("⏳ Waiting 2 seconds for background task...")
            time.sleep(2)
            
            return True
        else:
            print(f"❌ API failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_api()