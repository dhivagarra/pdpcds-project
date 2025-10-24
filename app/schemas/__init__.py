"""
Pydantic schemas for request/response validation
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class SexEnum(str, Enum):
    """Sex enumeration"""
    male = "male"
    female = "female"
    other = "other"


class PredictionRequest(BaseModel):
    """
    Request schema for disease prediction
    """
    age: int = Field(..., ge=0, le=150, description="Patient age in years")
    sex: SexEnum = Field(..., description="Patient sex")
    
    # Vital signs
    vital_temperature_c: Optional[float] = Field(None, ge=30.0, le=45.0, description="Temperature in Celsius")
    vital_heart_rate: Optional[int] = Field(None, ge=30, le=250, description="Heart rate in BPM")
    vital_blood_pressure_systolic: Optional[int] = Field(None, ge=50, le=300, description="Systolic BP in mmHg")
    vital_blood_pressure_diastolic: Optional[int] = Field(None, ge=30, le=200, description="Diastolic BP in mmHg")
    
    # Clinical data
    symptom_list: List[str] = Field(default=[], description="List of symptoms")
    pmh_list: List[str] = Field(default=[], description="Past medical history")
    current_medications: List[str] = Field(default=[], description="Current medications")
    allergies: List[str] = Field(default=[], description="Known allergies")
    
    # Free text
    chief_complaint: Optional[str] = Field(None, max_length=500, description="Chief complaint")
    free_text_notes: Optional[str] = Field(None, max_length=2000, description="Additional clinical notes")
    
    @validator('symptom_list', 'pmh_list', 'current_medications', 'allergies')
    def validate_lists(cls, v):
        return [item.strip().lower() for item in v if item.strip()]


class TestRecommendation(BaseModel):
    """
    Test recommendation schema
    """
    test: str = Field(..., description="Test name")
    test_code: Optional[str] = Field(None, description="Test code (CPT/LOINC)")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    urgency: Optional[str] = Field("routine", description="Urgency level")
    rationale: Optional[str] = Field(None, description="Reason for recommendation")


class MedicationRecommendation(BaseModel):
    """
    Medication recommendation schema
    """
    medication: str = Field(..., description="Medication name")
    generic_name: Optional[str] = Field(None, description="Generic name")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    dose_suggestion: Optional[str] = Field(None, description="Suggested dosage")
    duration: Optional[str] = Field(None, description="Treatment duration")
    contraindication_check: bool = Field(True, description="Check for contraindications")
    rationale: Optional[str] = Field(None, description="Reason for recommendation")


class DiseasePrediction(BaseModel):
    """
    Individual disease prediction schema
    """
    icd10_code: str = Field(..., description="ICD-10 diagnosis code")
    diagnosis: str = Field(..., description="Disease/condition name")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Prediction confidence")
    
    recommended_tests: List[TestRecommendation] = Field(default=[], description="Recommended tests")
    recommended_medications: List[MedicationRecommendation] = Field(default=[], description="Recommended medications")
    
    assessment_plan: str = Field(..., description="Clinical assessment and plan")
    rationale: List[str] = Field(default=[], description="Reasoning behind the prediction")
    
    # Risk factors and considerations
    risk_factors: List[str] = Field(default=[], description="Identified risk factors")
    differential_diagnoses: List[str] = Field(default=[], description="Alternative diagnoses to consider")


class PredictionResponse(BaseModel):
    """
    Response schema for disease prediction
    """
    predictions: List[DiseasePrediction] = Field(..., max_items=3, description="Top 3 predictions")
    
    # Metadata
    model_version: str = Field(..., description="ML model version")
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")
    confidence_threshold: float = Field(..., description="Minimum confidence threshold used")
    
    # Timestamps
    generated_at: datetime = Field(..., description="Prediction generation timestamp")
    
    # Warnings and disclaimers
    clinical_warnings: List[str] = Field(default=[], description="Important clinical warnings")
    disclaimer: str = Field(
        default="This is a preliminary prediction tool. Always consult with healthcare professionals for clinical decisions.",
        description="Medical disclaimer"
    )


class HealthResponse(BaseModel):
    """
    Health check response schema
    """
    status: str = Field(..., description="Service status")
    service: str = Field(..., description="Service name")
    version: str = Field(..., description="Service version")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")


class ErrorResponse(BaseModel):
    """
    Error response schema
    """
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    detail: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    timestamp: datetime = Field(default_factory=datetime.now, description="Error timestamp")