"""
Database models for the Clinical Decision Support System
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Patient(Base):
    """
    Patient model for storing patient information
    """
    __tablename__ = "patients"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String, unique=True, index=True)
    age = Column(Integer)
    sex = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Prediction(Base):
    """
    Prediction model for storing ML predictions
    """
    __tablename__ = "predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String, index=True)
    
    # Input data
    age = Column(Integer)
    sex = Column(String)
    vital_temperature_c = Column(Float)
    vital_heart_rate = Column(Integer)
    vital_blood_pressure_systolic = Column(Integer, nullable=True)
    vital_blood_pressure_diastolic = Column(Integer, nullable=True)
    symptom_list = Column(JSON)
    pmh_list = Column(JSON)
    free_text_notes = Column(Text)
    
    # Predictions (top 3)
    predictions = Column(JSON)
    
    # Metadata
    model_version = Column(String)
    confidence_threshold = Column(Float)
    processing_time_ms = Column(Float)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Note: Relationships with feedback models commented out to avoid circular imports
    # feedback = relationship("ClinicalFeedback", back_populates="prediction")
    # outcomes = relationship("ClinicalOutcomeRecord", back_populates="prediction")


class ICD10Code(Base):
    """
    ICD-10 codes reference table
    """
    __tablename__ = "icd10_codes"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True)
    description = Column(Text)
    category = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class MedicalTest(Base):
    """
    Medical tests reference table
    """
    __tablename__ = "medical_tests"
    
    id = Column(Integer, primary_key=True, index=True)
    test_name = Column(String, index=True)
    test_code = Column(String, unique=True, index=True)
    description = Column(Text)
    category = Column(String)
    typical_range = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Medication(Base):
    """
    Medications reference table
    """
    __tablename__ = "medications"
    
    id = Column(Integer, primary_key=True, index=True)
    medication_name = Column(String, index=True)
    generic_name = Column(String)
    brand_names = Column(JSON)
    drug_class = Column(String)
    typical_dosage = Column(String)
    contraindications = Column(JSON)
    side_effects = Column(JSON)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class TrainingData(Base):
    """
    Training data samples for ML model training
    """
    __tablename__ = "training_data"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Patient demographics and vitals
    age = Column(Integer, nullable=False)
    sex = Column(String, nullable=False)
    vital_temperature_c = Column(Float, nullable=False)
    vital_heart_rate = Column(Integer, nullable=False)
    vital_blood_pressure_systolic = Column(Integer, nullable=True)
    vital_blood_pressure_diastolic = Column(Integer, nullable=True)
    
    # Clinical data
    symptom_list = Column(JSON, nullable=False)  # List of symptoms
    pmh_list = Column(JSON, default=lambda: [])  # Past medical history
    current_medications = Column(JSON, default=lambda: [])  # Current medications
    allergies = Column(JSON, default=lambda: [])  # Known allergies
    chief_complaint = Column(Text, nullable=True)
    free_text_notes = Column(Text, nullable=True)
    
    # Target labels (ground truth)
    target_disease = Column(Integer, nullable=False)  # ICD10 ID
    target_tests = Column(JSON, nullable=False)  # List of medical test IDs
    target_medications = Column(JSON, nullable=False)  # List of medication IDs
    condition_name = Column(String, nullable=False, index=True)  # Human-readable condition
    
    # Metadata
    data_source = Column(String, default="synthetic")  # synthetic, manual, imported
    quality_score = Column(Float, default=1.0)  # Quality rating 0-1
    is_validated = Column(Boolean, default=False)  # Medical expert validation
    created_by = Column(String, nullable=True)  # Who created this sample
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Indexes for efficient querying
    __table_args__ = (
        {"sqlite_autoincrement": True}
    )


class ValidationData(Base):
    """
    Validation data samples for ML model evaluation
    """
    __tablename__ = "validation_data"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Patient demographics and vitals
    age = Column(Integer, nullable=False)
    sex = Column(String, nullable=False)
    vital_temperature_c = Column(Float, nullable=False)
    vital_heart_rate = Column(Integer, nullable=False)
    vital_blood_pressure_systolic = Column(Integer, nullable=True)
    vital_blood_pressure_diastolic = Column(Integer, nullable=True)
    
    # Clinical data
    symptom_list = Column(JSON, nullable=False)  # List of symptoms
    pmh_list = Column(JSON, default=lambda: [])  # Past medical history
    current_medications = Column(JSON, default=lambda: [])  # Current medications
    allergies = Column(JSON, default=lambda: [])  # Known allergies
    chief_complaint = Column(Text, nullable=True)
    free_text_notes = Column(Text, nullable=True)
    
    # Target labels (ground truth)
    target_disease = Column(Integer, nullable=False)  # ICD10 ID
    target_tests = Column(JSON, nullable=False)  # List of medical test IDs
    target_medications = Column(JSON, nullable=False)  # List of medication IDs
    condition_name = Column(String, nullable=False, index=True)  # Human-readable condition
    
    # Metadata
    data_source = Column(String, default="synthetic")  # synthetic, manual, imported
    quality_score = Column(Float, default=1.0)  # Quality rating 0-1
    is_validated = Column(Boolean, default=False)  # Medical expert validation
    created_by = Column(String, nullable=True)  # Who created this sample
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Indexes for efficient querying
    __table_args__ = (
        {"sqlite_autoincrement": True}
    )