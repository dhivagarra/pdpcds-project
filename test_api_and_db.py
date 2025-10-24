"""
Test script for the Clinical Decision Support System API
This will test the prediction endpoint and verify database insertion
"""

import requests
import json
import time

# API Configuration
BASE_URL = "http://127.0.0.1:8000"
PREDICT_URL = f"{BASE_URL}/api/v1/predict/"

# Test data for prediction
test_request = {
    "age": 35,
    "sex": "male",
    "vital_temperature_c": 38.5,
    "vital_heart_rate": 95,
    "vital_blood_pressure_systolic": 140,
    "vital_blood_pressure_diastolic": 85,
    "symptom_list": ["fever", "headache", "nausea"],
    "pmh_list": ["hypertension"],
    "free_text_notes": "Patient reports flu-like symptoms for 2 days"
}

def test_api_prediction():
    """Test the prediction API endpoint"""
    print("🧪 Testing Disease Prediction API")
    print("=" * 50)
    
    try:
        print("📤 Sending request to API...")
        response = requests.post(PREDICT_URL, json=test_request, timeout=30)
        
        print(f"📨 Response Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ API call successful!")
            print(f"🔮 Predictions count: {len(result.get('predictions', []))}")
            print(f"⚡ Processing time: {result.get('processing_time_ms', 0):.2f} ms")
            print(f"🏷️ Model version: {result.get('model_version', 'N/A')}")
            
            # Pretty print first prediction
            if result.get('predictions'):
                first_prediction = result['predictions'][0]
                print("\n📋 First Prediction:")
                print(f"   Disease: {first_prediction.get('disease_name', 'N/A')}")
                print(f"   ICD-10: {first_prediction.get('icd10_code', 'N/A')}")
                print(f"   Confidence: {first_prediction.get('confidence', 0):.3f}")
            
            return True
        else:
            print(f"❌ API call failed with status {response.status_code}")
            print(f"📄 Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def check_database_after_api_call():
    """Check if data was inserted into the database after API call"""
    print("\n🔍 Checking Database After API Call")
    print("=" * 50)
    
    import sqlite3
    
    try:
        conn = sqlite3.connect('pdpcds_dev.db')
        cursor = conn.cursor()
        
        # Count total records
        cursor.execute("SELECT COUNT(*) FROM predictions")
        count = cursor.fetchone()[0]
        print(f"📊 Total predictions in database: {count}")
        
        if count > 0:
            print("✅ Database insertion successful!")
            
            # Get the most recent record
            cursor.execute("""
                SELECT patient_id, age, sex, vital_temperature_c, model_version, 
                       processing_time_ms, created_at 
                FROM predictions 
                ORDER BY created_at DESC 
                LIMIT 1
            """)
            
            record = cursor.fetchone()
            if record:
                print("\n📄 Most Recent Record:")
                print(f"   Patient ID: {record[0]}")
                print(f"   Age: {record[1]}")
                print(f"   Sex: {record[2]}")
                print(f"   Temperature: {record[3]}°C")
                print(f"   Model Version: {record[4]}")
                print(f"   Processing Time: {record[5]} ms")
                print(f"   Created At: {record[6]}")
        else:
            print("❌ No records found in database!")
            print("🐛 Database insertion may have failed")
        
        conn.close()
        return count > 0
        
    except Exception as e:
        print(f"❌ Database check error: {e}")
        return False

def main():
    """Run the complete test suite"""
    print("🏥 Clinical Decision Support System - API Test")
    print("=" * 60)
    
    # Test 1: Check if server is running
    try:
        health_response = requests.get(f"{BASE_URL}/health", timeout=5)
        if health_response.status_code == 200:
            print("✅ Server is running and healthy")
        else:
            print("❌ Server health check failed")
            return
    except:
        print("❌ Server is not accessible")
        return
    
    # Wait a moment for any previous operations to complete
    time.sleep(1)
    
    # Test 2: Make API call
    api_success = test_api_prediction()
    
    if api_success:
        # Wait for background task to complete
        print("\n⏳ Waiting 3 seconds for background database task...")
        time.sleep(3)
        
        # Test 3: Check database
        db_success = check_database_after_api_call()
        
        if db_success:
            print("\n🎉 All tests passed! Database insertion is working correctly.")
        else:
            print("\n⚠️ API works but database insertion failed!")
    else:
        print("\n❌ API test failed - cannot proceed with database check")

if __name__ == "__main__":
    main()