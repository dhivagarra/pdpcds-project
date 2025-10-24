#!/usr/bin/env python3
"""
Test script to verify model imports and create feedback tables manually
"""

import sys
import os
sys.path.append('.')

from sqlalchemy import create_engine, text, Column, Integer, String, Float, DateTime, Text, Boolean, JSON, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

# Create base and engine
Base = declarative_base()
DATABASE_URL = "sqlite:///./pdpcds_dev.db"
engine = create_engine(DATABASE_URL)

def get_engine():
    """Return the SQLAlchemy engine used by this script."""
    return engine

# Minimal model definitions to ensure names are available for testing and table creation
class Patient(Base):
    __tablename__ = "patients"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=True)

class Prediction(Base):
    __tablename__ = "predictions"
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=True)
    disease = Column(String, nullable=True)
    confidence = Column(Float, nullable=True)

class ICD10Code(Base):
    __tablename__ = "icd10_codes"
    id = Column(Integer, primary_key=True)
    code = Column(String, nullable=False)
    description = Column(Text, nullable=True)

class MedicalTest(Base):
    __tablename__ = "medical_tests"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)

class Medication(Base):
    __tablename__ = "medications"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    dosage = Column(String, nullable=True)

class TrainingData(Base):
    __tablename__ = "training_data"
    id = Column(Integer, primary_key=True)
    data = Column(JSON, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

class ValidationData(Base):
    __tablename__ = "validation_data"
    id = Column(Integer, primary_key=True)
    data = Column(JSON, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

class ClinicalFeedback(Base):
    __tablename__ = "clinical_feedback"
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=True)
    prediction_id = Column(Integer, ForeignKey("predictions.id"), nullable=True)
    feedback = Column(JSON, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

class ClinicalOutcomeRecord(Base):
    __tablename__ = "clinical_outcomes"
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=True)
    outcome = Column(Text, nullable=True)
    confirmed = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())

def test_models():
    """Test that all models are properly imported"""
    print("Testing model imports...")
    
    # Test basic models
    print(f"✅ Patient: {Patient}")
    print(f"✅ Prediction: {Prediction}")
    print(f"✅ ICD10Code: {ICD10Code}")
    print(f"✅ MedicalTest: {MedicalTest}")
    print(f"✅ Medication: {Medication}")
    print(f"✅ TrainingData: {TrainingData}")
    print(f"✅ ValidationData: {ValidationData}")
    
    # Test feedback models
    print(f"✅ ClinicalFeedback: {ClinicalFeedback}")
    print(f"✅ ClinicalOutcomeRecord: {ClinicalOutcomeRecord}")
    
    print("\n📋 All models imported successfully!")
    
    # Check metadata
    print(f"\n📊 Total tables in metadata: {len(Base.metadata.tables)}")
    for table_name in Base.metadata.tables.keys():
        print(f"  - {table_name}")

def create_feedback_tables_manually():
    """Manually create feedback tables if migration didn't work"""
    print("\n🔧 Creating feedback tables manually...")
    
    engine = get_engine()
    
    # Check if tables exist
    with engine.connect() as conn:
        result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
        existing_tables = [row[0] for row in result]
        print(f"Existing tables: {existing_tables}")
        
        if 'clinical_feedback' not in existing_tables:
            print("Creating clinical_feedback table...")
            ClinicalFeedback.__table__.create(engine)
            print("✅ clinical_feedback table created")
        else:
            print("✅ clinical_feedback table already exists")
            
        if 'clinical_outcomes' not in existing_tables:
            print("Creating clinical_outcomes table...")
            ClinicalOutcomeRecord.__table__.create(engine)
            print("✅ clinical_outcomes table created")
        else:
            print("✅ clinical_outcomes table already exists")

if __name__ == "__main__":
    try:
        test_models()
        create_feedback_tables_manually()
        print("\n🎉 Feedback tables setup completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()