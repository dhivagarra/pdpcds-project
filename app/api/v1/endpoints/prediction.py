"""
Prediction endpoints for disease prediction and clinical decision support
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime
import time
import uuid

from app.database import get_db
from app.schemas import PredictionRequest, PredictionResponse, ErrorResponse
from app.ml.predictor import ClinicalPredictor
from app.models import Prediction
from app.config import settings

router = APIRouter()

# Initialize the ML predictor (will be loaded when first used)
predictor = None


def get_predictor() -> ClinicalPredictor:
    """
    Get or initialize the ML predictor
    """
    global predictor
    if predictor is None:
        predictor = ClinicalPredictor(
            model_path=settings.model_path,
            model_version=settings.model_version
        )
    return predictor


def save_prediction_to_db(
    request_data: dict,
    predictions: list,
    processing_time: float
):
    """
    Save prediction to database in background
    Note: Creates its own database session to avoid session conflicts
    """
    try:
        print(f"🚀 Background task started - saving prediction to database...")
        print(f"📋 Request data keys: {list(request_data.keys())}")
        print(f"🔮 Predictions type: {type(predictions)} with {len(predictions)} items")
        
        # Import here to avoid circular imports in background tasks
        from app.database import engine
        from sqlalchemy.orm import sessionmaker
        
        # Create a new database session for the background task
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        try:
            # Convert predictions to JSON-serializable format
            predictions_dict = []
            for pred in predictions:
                if hasattr(pred, 'dict'):
                    # It's a Pydantic model, convert to dict
                    predictions_dict.append(pred.dict())
                else:
                    # It's already a dict
                    predictions_dict.append(pred)
            
            print(f"📄 Converted {len(predictions_dict)} predictions to dict format")
            
            prediction_record = Prediction(
                patient_id=str(uuid.uuid4()),  # Generate unique patient ID for this session
                age=request_data.get("age"),
                sex=request_data.get("sex"),
                vital_temperature_c=request_data.get("vital_temperature_c"),
                vital_heart_rate=request_data.get("vital_heart_rate"),
                vital_blood_pressure_systolic=request_data.get("vital_blood_pressure_systolic"),
                vital_blood_pressure_diastolic=request_data.get("vital_blood_pressure_diastolic"),
                symptom_list=request_data.get("symptom_list", []),
                pmh_list=request_data.get("pmh_list", []),
                free_text_notes=request_data.get("free_text_notes"),
                predictions=predictions_dict,  # Use the serializable dict version
                model_version=settings.model_version,
                confidence_threshold=settings.confidence_threshold,
                processing_time_ms=processing_time
            )
            
            db.add(prediction_record)
            db.commit()
            print(f"✅ Prediction saved successfully to database with ID: {prediction_record.id}")
            
        except Exception as db_error:
            print(f"❌ Database error: {db_error}")
            db.rollback()
            raise
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ Error in background task: {e}")
        print(f"🐛 Error type: {type(e).__name__}")
        import traceback
        print(f"📚 Full traceback:")
        traceback.print_exc()


@router.post("/", response_model=PredictionResponse)
async def predict_disease(
    request: PredictionRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Predict diseases and generate clinical recommendations
    
    This endpoint accepts patient data and returns:
    - Top 3 disease predictions with ICD-10 codes
    - Recommended diagnostic tests
    - Medication suggestions  
    - Clinical assessment plans
    - Confidence scores and rationale
    """
    start_time = time.time()
    
    print(f"🚀 API endpoint reached - predict_disease called")
    print(f"📋 Request data: age={request.age}, sex={request.sex}, temp={request.vital_temperature_c}")
    
    try:
        # Get the ML predictor
        ml_predictor = get_predictor()
        print(f"🤖 ML predictor obtained")
        
        # Convert request to dict for processing
        request_dict = request.dict()
        print(f"📄 Request converted to dict with {len(request_dict)} keys")
        
        # Generate predictions using ML model
        predictions = ml_predictor.predict(request_dict)
        
        # Calculate processing time
        processing_time = (time.time() - start_time) * 1000
        
        # Create response
        response = PredictionResponse(
            predictions=predictions,
            model_version=settings.model_version,
            processing_time_ms=processing_time,
            confidence_threshold=settings.confidence_threshold,
            generated_at=datetime.now(),
            clinical_warnings=[
                "This is a preliminary assessment tool only",
                "Always consider patient history and clinical context",
                "Confirm diagnoses with appropriate diagnostic tests",
                "Consider contraindications before prescribing medications"
            ]
        )
        
        # Save to database in background
        print(f"📝 Adding background task to save prediction to database")
        background_tasks.add_task(
            save_prediction_to_db,
            request_dict,
            predictions,  # Pass the actual predictions list
            processing_time
        )
        print(f"✅ Background task added successfully")

        return response
        
    except Exception as e:
        processing_time = (time.time() - start_time) * 1000
        
        raise HTTPException(
            status_code=500,
            detail={
                "error": "PredictionError",
                "message": f"Failed to generate prediction: {str(e)}",
                "processing_time_ms": processing_time,
                "timestamp": datetime.now().isoformat()
            }
        )


@router.get("/history/{patient_id}")
async def get_prediction_history(
    patient_id: str,
    db: Session = Depends(get_db)
):
    """
    Get prediction history for a specific patient
    """
    try:
        predictions = db.query(Prediction).filter(
            Prediction.patient_id == patient_id
        ).order_by(Prediction.created_at.desc()).all()
        
        return {
            "patient_id": patient_id,
            "prediction_count": len(predictions),
            "predictions": [
                {
                    "id": pred.id,
                    "age": pred.age,
                    "sex": pred.sex,
                    "predictions": pred.predictions,
                    "model_version": pred.model_version,
                    "processing_time_ms": pred.processing_time_ms,
                    "created_at": pred.created_at
                }
                for pred in predictions
            ]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "HistoryError",
                "message": f"Failed to retrieve prediction history: {str(e)}"
            }
        )