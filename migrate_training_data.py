#!/usr/bin/env python3
"""
Migrate training data from CSV files to database tables
This script transfers train_dataset.csv and val_dataset.csv to TrainingData and ValidationData tables
"""

import pandas as pd
import json
import ast
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import TrainingData, ValidationData
from app.database import Base
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = "sqlite:///./pdpcds_dev.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def safe_eval_list(value):
    """Safely convert string representation of list to actual list"""
    if pd.isna(value) or value == '' or value == '[]':
        return []
    
    try:
        # Handle string representation of lists
        if isinstance(value, str):
            # Remove extra quotes and clean up
            cleaned_value = value.strip()
            if cleaned_value.startswith('[') and cleaned_value.endswith(']'):
                return ast.literal_eval(cleaned_value)
            elif cleaned_value.startswith("'[") and cleaned_value.endswith("]'"):
                return ast.literal_eval(cleaned_value[1:-1])
        
        return value if isinstance(value, list) else []
    except (ValueError, SyntaxError) as e:
        logger.warning(f"Could not parse list value '{value}': {e}")
        return []

def migrate_csv_to_database():
    """Migrate CSV training data to database tables"""
    
    # File paths
    train_csv_path = Path("training/data/train_dataset.csv")
    val_csv_path = Path("training/data/val_dataset.csv")
    
    if not train_csv_path.exists():
        logger.error(f"Training CSV file not found: {train_csv_path}")
        return False
    
    if not val_csv_path.exists():
        logger.error(f"Validation CSV file not found: {val_csv_path}")
        return False
    
    try:
        # Create database session
        db = SessionLocal()
        
        # Clear existing data
        logger.info("Clearing existing training and validation data...")
        db.query(TrainingData).delete()
        db.query(ValidationData).delete()
        db.commit()
        
        # Load and migrate training data
        logger.info(f"Loading training data from {train_csv_path}")
        train_df = pd.read_csv(train_csv_path)
        logger.info(f"Found {len(train_df)} training samples")
        
        training_records = []
        for _, row in train_df.iterrows():
            try:
                record = TrainingData(
                    age=int(row['age']),
                    sex=row['sex'],
                    vital_temperature_c=float(row['vital_temperature_c']),
                    vital_heart_rate=int(row['vital_heart_rate']),
                    vital_blood_pressure_systolic=int(row['vital_blood_pressure_systolic']) if pd.notna(row['vital_blood_pressure_systolic']) else None,
                    vital_blood_pressure_diastolic=int(row['vital_blood_pressure_diastolic']) if pd.notna(row['vital_blood_pressure_diastolic']) else None,
                    symptom_list=safe_eval_list(row['symptom_list']),
                    pmh_list=safe_eval_list(row['pmh_list']),
                    current_medications=safe_eval_list(row['current_medications']),
                    allergies=safe_eval_list(row['allergies']),
                    chief_complaint=row['chief_complaint'] if pd.notna(row['chief_complaint']) else None,
                    free_text_notes=row['free_text_notes'] if pd.notna(row['free_text_notes']) else None,
                    target_disease=int(row['target_disease']),
                    target_tests=safe_eval_list(row['target_tests']),
                    target_medications=safe_eval_list(row['target_medications']),
                    condition_name=row['condition_name'],
                    data_source="csv_migration",
                    quality_score=1.0,
                    is_validated=True,
                    created_by="migration_script"
                )
                training_records.append(record)
            except Exception as e:
                logger.error(f"Error processing training row {len(training_records)}: {e}")
                logger.error(f"Row data: {row.to_dict()}")
                continue
        
        # Bulk insert training data
        logger.info(f"Inserting {len(training_records)} training records...")
        db.add_all(training_records)
        db.commit()
        
        # Load and migrate validation data
        logger.info(f"Loading validation data from {val_csv_path}")
        val_df = pd.read_csv(val_csv_path)
        logger.info(f"Found {len(val_df)} validation samples")
        
        validation_records = []
        for _, row in val_df.iterrows():
            try:
                record = ValidationData(
                    age=int(row['age']),
                    sex=row['sex'],
                    vital_temperature_c=float(row['vital_temperature_c']),
                    vital_heart_rate=int(row['vital_heart_rate']),
                    vital_blood_pressure_systolic=int(row['vital_blood_pressure_systolic']) if pd.notna(row['vital_blood_pressure_systolic']) else None,
                    vital_blood_pressure_diastolic=int(row['vital_blood_pressure_diastolic']) if pd.notna(row['vital_blood_pressure_diastolic']) else None,
                    symptom_list=safe_eval_list(row['symptom_list']),
                    pmh_list=safe_eval_list(row['pmh_list']),
                    current_medications=safe_eval_list(row['current_medications']),
                    allergies=safe_eval_list(row['allergies']),
                    chief_complaint=row['chief_complaint'] if pd.notna(row['chief_complaint']) else None,
                    free_text_notes=row['free_text_notes'] if pd.notna(row['free_text_notes']) else None,
                    target_disease=int(row['target_disease']),
                    target_tests=safe_eval_list(row['target_tests']),
                    target_medications=safe_eval_list(row['target_medications']),
                    condition_name=row['condition_name'],
                    data_source="csv_migration",
                    quality_score=1.0,
                    is_validated=True,
                    created_by="migration_script"
                )
                validation_records.append(record)
            except Exception as e:
                logger.error(f"Error processing validation row {len(validation_records)}: {e}")
                logger.error(f"Row data: {row.to_dict()}")
                continue
        
        # Bulk insert validation data
        logger.info(f"Inserting {len(validation_records)} validation records...")
        db.add_all(validation_records)
        db.commit()
        
        # Verify migration
        train_count = db.query(TrainingData).count()
        val_count = db.query(ValidationData).count()
        
        logger.info(f"Migration completed successfully!")
        logger.info(f"Training records in database: {train_count}")
        logger.info(f"Validation records in database: {val_count}")
        
        # Show sample by condition
        logger.info("\nSample counts by condition:")
        for condition in db.query(TrainingData.condition_name).distinct():
            condition_name = condition[0]
            train_condition_count = db.query(TrainingData).filter(TrainingData.condition_name == condition_name).count()
            val_condition_count = db.query(ValidationData).filter(ValidationData.condition_name == condition_name).count()
            logger.info(f"  {condition_name}: {train_condition_count} training, {val_condition_count} validation")
        
        db.close()
        return True
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        if 'db' in locals():
            db.rollback()
            db.close()
        return False

def verify_migration():
    """Verify the migration was successful by comparing record counts"""
    try:
        # Load CSV files
        train_df = pd.read_csv("training/data/train_dataset.csv")
        val_df = pd.read_csv("training/data/val_dataset.csv")
        
        # Query database
        db = SessionLocal()
        train_db_count = db.query(TrainingData).count()
        val_db_count = db.query(ValidationData).count()
        db.close()
        
        logger.info(f"\nMigration Verification:")
        logger.info(f"CSV Training records: {len(train_df)}")
        logger.info(f"DB Training records: {train_db_count}")
        logger.info(f"CSV Validation records: {len(val_df)}")
        logger.info(f"DB Validation records: {val_db_count}")
        
        if len(train_df) == train_db_count and len(val_df) == val_db_count:
            logger.info("✅ Migration verification PASSED - All records migrated successfully!")
            return True
        else:
            logger.error("❌ Migration verification FAILED - Record counts don't match!")
            return False
            
    except Exception as e:
        logger.error(f"Verification failed: {e}")
        return False

if __name__ == "__main__":
    logger.info("Starting training data migration from CSV to database...")
    
    # Run migration
    if migrate_csv_to_database():
        # Verify migration
        if verify_migration():
            logger.info("\n🎉 Training data migration completed successfully!")
            logger.info("You can now use the database-based training pipeline.")
        else:
            logger.error("Migration completed but verification failed.")
    else:
        logger.error("Migration failed.")