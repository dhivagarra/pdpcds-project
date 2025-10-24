"""
Pydantic schemas for feedback endpoints
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class DoctorFeedback(BaseModel):
    """
    Schema for doctor feedback on predictions
    """
    prediction_id: int = Field(..., description="ID of the original prediction")
    doctor_id: str = Field(..., description="Doctor's identifier (username, employee_id, etc.)")
    doctor_name: Optional[str] = Field(None, description="Doctor's full name")
    
    # Feedback assessment
    prediction_accurate: bool = Field(..., description="Was the original prediction correct?")
    confidence_in_feedback: float = Field(..., ge=0.0, le=1.0, description="Doctor's confidence in their feedback (0-1)")
    
    # Actual diagnosis (if prediction was wrong)
    actual_disease_id: Optional[int] = Field(None, description="Correct ICD-10 disease ID if prediction was wrong")
    actual_condition_name: Optional[str] = Field(None, description="Correct condition name if prediction was wrong")
    
    # Clinical actions taken
    ordered_tests: List[str] = Field(default_factory=list, description="List of medical tests that were actually ordered")
    prescribed_medications: List[str] = Field(default_factory=list, description="List of medications that were prescribed")
    
    # Additional clinical notes
    clinical_notes: Optional[str] = Field(None, description="Additional clinical observations or notes")
    outcome_notes: Optional[str] = Field(None, description="Patient outcome or follow-up information")
    
    # Metadata
    feedback_timestamp: Optional[datetime] = Field(default_factory=datetime.now, description="When feedback was provided")
    hospital_unit: Optional[str] = Field(None, description="Hospital unit or department")


class ClinicalOutcome(BaseModel):
    """
    Schema for final clinical outcomes (follow-up data)
    """
    prediction_id: int = Field(..., description="ID of the original prediction")
    patient_outcome: str = Field(..., description="Final patient outcome (recovered, improved, stable, etc.)")
    
    # Final diagnosis
    final_diagnosis_id: int = Field(..., description="Final confirmed diagnosis ID")
    final_condition_name: str = Field(..., description="Final confirmed condition name")
    
    # Treatment effectiveness
    treatment_effective: bool = Field(..., description="Was the treatment effective?")
    side_effects: List[str] = Field(default_factory=list, description="Any side effects observed")
    
    # Timeline
    diagnosis_confirmation_days: Optional[int] = Field(None, description="Days to confirm diagnosis")
    treatment_duration_days: Optional[int] = Field(None, description="Duration of treatment in days")
    
    # Quality metrics
    readmission_required: bool = Field(default=False, description="Was readmission required?")
    complications: List[str] = Field(default_factory=list, description="Any complications that occurred")
    
    # Reporting
    reported_by: str = Field(..., description="Who reported the outcome")
    outcome_date: datetime = Field(..., description="Date of outcome assessment")


class FeedbackSummary(BaseModel):
    """
    Summary of feedback for a prediction
    """
    prediction_id: int
    total_feedback_count: int
    accuracy_rate: float  # Percentage of doctors who agreed with prediction
    consensus_reached: bool  # Whether doctors agree on the diagnosis
    
    most_common_actual_diagnosis: Optional[str]
    most_common_tests_ordered: List[str]
    most_common_medications: List[str]
    
    feedback_quality_score: float  # Based on doctor confidence and consensus


class TrainingDataRequest(BaseModel):
    """
    Request to add validated clinical data to training set
    """
    # Patient data
    age: int = Field(..., ge=0, le=120)
    sex: str = Field(..., description="Patient sex (male/female/other)")
    
    # Vital signs
    vital_temperature_c: float = Field(..., ge=30.0, le=45.0)
    vital_heart_rate: int = Field(..., ge=30, le=200)
    vital_blood_pressure_systolic: Optional[int] = Field(None, ge=60, le=250)
    vital_blood_pressure_diastolic: Optional[int] = Field(None, ge=30, le=150)
    
    # Clinical presentation
    symptom_list: List[str] = Field(..., min_items=1)
    pmh_list: List[str] = Field(default_factory=list)
    current_medications: List[str] = Field(default_factory=list)
    allergies: List[str] = Field(default_factory=list)
    chief_complaint: Optional[str] = None
    free_text_notes: Optional[str] = None
    
    # Ground truth labels
    confirmed_disease_id: int = Field(..., description="Confirmed ICD-10 disease ID")
    confirmed_condition_name: str = Field(..., description="Confirmed condition name")
    ordered_tests: List[int] = Field(..., description="Tests that were ordered")
    prescribed_medications: List[int] = Field(..., description="Medications that were prescribed")
    
    # Metadata
    data_source: str = Field(default="clinical_feedback")
    quality_score: float = Field(default=0.95, ge=0.0, le=1.0)
    is_validated: bool = Field(default=True)
    created_by: str = Field(..., description="Who added this data")
    add_to_validation_set: bool = Field(default=False, description="Add to validation set instead of training")


class FeedbackResponse(BaseModel):
    """
    Response after submitting feedback
    """
    message: str
    feedback_id: int
    training_data_added: bool
    training_record_id: Optional[int] = None
    
    # Summary stats
    total_feedback_for_prediction: int
    prediction_accuracy_rate: float