"""
Standalone test that starts server and tests API in the same process
"""
import threading
import time
import requests
import uvicorn
from fastapi import FastAPI
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.abspath('.'))

def run_server():
    """Run the server in a separate thread"""
    from app.main import app
    uvicorn.run(app, host="127.0.0.1", port=8001, log_level="info")

def test_api():
    """Test the API once server is running"""
    print("🧪 Testing API with integrated server...")
    
    # Wait for server to start
    time.sleep(3)
    
    test_data = {
        "age": 35,
        "sex": "male",
        "vital_temperature_c": 38.5,
        "vital_heart_rate": 95,
        "vital_blood_pressure_systolic": 140,
        "vital_blood_pressure_diastolic": 85,
        "symptom_list": ["fever", "headache"],
        "pmh_list": ["hypertension"],
        "free_text_notes": "Integration test"
    }
    
    try:
        response = requests.post(
            "http://127.0.0.1:8001/api/v1/predict/",
            json=test_data,
            timeout=10
        )
        
        print(f"📨 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ API call successful!")
            print(f"⚡ Processing time: {result.get('processing_time_ms', 0):.2f} ms")
            print(f"🔮 Predictions: {len(result.get('predictions', []))}")
            return True
        else:
            print(f"❌ API failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False

def check_database():
    """Check database for inserted records"""
    print("\n🔍 Checking database for inserted records...")
    
    import sqlite3
    try:
        conn = sqlite3.connect('pdpcds_dev.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM predictions")
        count = cursor.fetchone()[0]
        print(f"📊 Total predictions in database: {count}")
        
        if count > 0:
            cursor.execute("""
                SELECT patient_id, age, sex, vital_temperature_c, created_at 
                FROM predictions 
                ORDER BY created_at DESC 
                LIMIT 1
            """)
            
            record = cursor.fetchone()
            if record:
                print("✅ Latest record found:")
                print(f"   Patient ID: {record[0][:8]}...")
                print(f"   Age: {record[1]}")
                print(f"   Sex: {record[2]}")
                print(f"   Temperature: {record[3]}°C")
                print(f"   Created: {record[4]}")
        
        conn.close()
        return count > 0
        
    except Exception as e:
        print(f"❌ Database check error: {e}")
        return False

if __name__ == "__main__":
    print("🏥 Clinical Decision Support System - Integrated Test")
    print("=" * 60)
    
    # Start server in background thread
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    # Test API
    api_success = test_api()
    
    # Check database
    if api_success:
        db_success = check_database()
        
        if db_success:
            print("\n🎉 SUCCESS: API works and database insertion is working!")
        else:
            print("\n⚠️ API works but database insertion failed!")
    else:
        print("\n❌ API test failed!")
    
    # Allow some time to see results before exit
    time.sleep(2)