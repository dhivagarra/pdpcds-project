"""
Database models for clinical feedback system - Simplified version without foreign keys
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, JSON
from sqlalchemy.sql import func
from app.database import Base


class ClinicalFeedback(Base):
    """
    Store doctor feedback on predictions (simplified without foreign keys)
    """
    __tablename__ = "clinical_feedback"
    
    id = Column(Integer, primary_key=True, index=True)
    prediction_id = Column(Integer, nullable=False, index=True)  # Just a reference, no FK
    
    # Doctor information
    doctor_id = Column(String, nullable=False, index=True)
    doctor_name = Column(String, nullable=True)
    hospital_unit = Column(String, nullable=True)
    
    # Feedback assessment
    prediction_accurate = Column(Boolean, nullable=False)
    confidence_in_feedback = Column(Float, nullable=False)  # 0-1 scale
    
    # Corrected diagnosis (if prediction was wrong)
    actual_disease_id = Column(Integer, nullable=True)
    actual_condition_name = Column(String, nullable=True)
    
    # Clinical actions taken
    ordered_tests = Column(JSON, nullable=False, default=lambda: [])
    prescribed_medications = Column(JSON, nullable=False, default=lambda: [])
    
    # Clinical notes
    clinical_notes = Column(Text, nullable=True)
    outcome_notes = Column(Text, nullable=True)
    
    # Metadata
    feedback_timestamp = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ClinicalOutcomeRecord(Base):
    """
    Record actual patient outcomes for learning purposes (matches actual table structure)
    """
    __tablename__ = "clinical_outcomes"
    
    id = Column(Integer, primary_key=True, index=True)
    prediction_id = Column(Integer, nullable=False, index=True)
    
    # Patient outcome information (matching actual table structure)
    patient_outcome = Column(String, nullable=False)
    final_diagnosis_id = Column(Integer, nullable=False)
    final_condition_name = Column(String, nullable=False)
    treatment_effective = Column(Boolean, nullable=False)
    
    # Clinical details
    side_effects = Column(JSON, nullable=True, default=lambda: [])
    diagnosis_confirmation_days = Column(Integer, nullable=True)
    treatment_duration_days = Column(Integer, nullable=True)
    readmission_required = Column(Boolean, nullable=True, default=False)
    complications = Column(JSON, nullable=True, default=lambda: [])
    
    # Metadata
    reported_by = Column(String, nullable=False)
    outcome_date = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())