"""
Simple database test to verify the save_prediction_to_db function works
"""
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.abspath('.'))

from app.models import Prediction
from app.database import engine
from app.config import settings
from sqlalchemy.orm import sessionmaker
import uuid

def test_db_insertion():
    """Test database insertion directly"""
    print("🧪 Testing direct database insertion...")
    
    try:
        # Create a new database session
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        # Sample data
        request_data = {
            "age": 35,
            "sex": "male",
            "vital_temperature_c": 38.5,
            "vital_heart_rate": 95,
            "vital_blood_pressure_systolic": 140,
            "vital_blood_pressure_diastolic": 85,
            "symptom_list": ["fever", "headache"],
            "pmh_list": ["hypertension"],
            "free_text_notes": "Test insertion"
        }
        
        predictions = {
            "diseases": [
                {"name": "Influenza", "icd10": "J11", "confidence": 0.85}
            ]
        }
        
        print(f"💾 Creating prediction record...")
        print(f"📋 Request data keys: {list(request_data.keys())}")
        print(f"🔮 Predictions: {predictions}")
        
        prediction_record = Prediction(
            patient_id=str(uuid.uuid4()),
            age=request_data.get("age"),
            sex=request_data.get("sex"),
            vital_temperature_c=request_data.get("vital_temperature_c"),
            vital_heart_rate=request_data.get("vital_heart_rate"),
            vital_blood_pressure_systolic=request_data.get("vital_blood_pressure_systolic"),
            vital_blood_pressure_diastolic=request_data.get("vital_blood_pressure_diastolic"),
            symptom_list=request_data.get("symptom_list", []),
            pmh_list=request_data.get("pmh_list", []),
            free_text_notes=request_data.get("free_text_notes"),
            predictions=predictions,
            model_version=settings.model_version,
            confidence_threshold=settings.confidence_threshold,
            processing_time_ms=100.0
        )
        
        print("📝 Adding to session...")
        db.add(prediction_record)
        
        print("💾 Committing...")
        db.commit()
        
        print("✅ Insertion successful!")
        
        # Verify the insertion
        result = db.query(Prediction).filter(
            Prediction.patient_id == prediction_record.patient_id
        ).first()
        
        if result:
            print(f"✅ Verification successful! Record ID: {result.id}")
            print(f"📊 Patient ID: {result.patient_id}")
            print(f"🌡️ Temperature: {result.vital_temperature_c}")
        else:
            print("❌ Verification failed - record not found")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Error during insertion: {e}")
        print(f"🐛 Error type: {type(e).__name__}")
        import traceback
        print(f"📚 Traceback:")
        traceback.print_exc()
        db.rollback()
        db.close()
        return False

if __name__ == "__main__":
    test_db_insertion()