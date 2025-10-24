#!/usr/bin/env python3
"""
Database Management Utilities for Training Data
Provides tools for managing training and validation datasets directly in the database
"""

import json
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy import create_engine, func, text
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import logging
import random
from pathlib import Path

# Setup
import sys
sys.path.append(str(Path(__file__).parent.parent))

from app.models import TrainingData, ValidationData, ICD10Code, MedicalTest, Medication
from app.database import Base

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TrainingDataManager:
    """
    Manager class for training and validation data in the database
    """
    
    def __init__(self, database_url: str = "sqlite:///./pdpcds_dev.db"):
        self.database_url = database_url
        self.engine = create_engine(database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    
    def get_session(self):
        """Get a new database session"""
        return self.SessionLocal()
    
    def add_training_sample(self, 
                          age: int,
                          sex: str,
                          vital_temperature_c: float,
                          vital_heart_rate: int,
                          symptom_list: List[str],
                          target_disease: int,
                          target_tests: List[int],
                          target_medications: List[int],
                          condition_name: str,
                          vital_blood_pressure_systolic: Optional[int] = None,
                          vital_blood_pressure_diastolic: Optional[int] = None,
                          pmh_list: Optional[List[str]] = None,
                          current_medications: Optional[List[str]] = None,
                          allergies: Optional[List[str]] = None,
                          chief_complaint: Optional[str] = None,
                          free_text_notes: Optional[str] = None,
                          data_source: str = "manual",
                          quality_score: float = 1.0,
                          is_validated: bool = False,
                          created_by: Optional[str] = None) -> TrainingData:
        """
        Add a new training sample to the database
        
        Returns:
            TrainingData: The created training record
        """
        
        db = self.get_session()
        try:
            record = TrainingData(
                age=age,
                sex=sex,
                vital_temperature_c=vital_temperature_c,
                vital_heart_rate=vital_heart_rate,
                vital_blood_pressure_systolic=vital_blood_pressure_systolic,
                vital_blood_pressure_diastolic=vital_blood_pressure_diastolic,
                symptom_list=symptom_list,
                pmh_list=pmh_list or [],
                current_medications=current_medications or [],
                allergies=allergies or [],
                chief_complaint=chief_complaint,
                free_text_notes=free_text_notes,
                target_disease=target_disease,
                target_tests=target_tests,
                target_medications=target_medications,
                condition_name=condition_name,
                data_source=data_source,
                quality_score=quality_score,
                is_validated=is_validated,
                created_by=created_by
            )
            
            db.add(record)
            db.commit()
            db.refresh(record)
            
            logger.info(f"✅ Added training sample ID {record.id} for condition: {condition_name}")
            return record
            
        except Exception as e:
            db.rollback()
            logger.error(f"❌ Error adding training sample: {e}")
            raise
        finally:
            db.close()
    
    def add_validation_sample(self, 
                            age: int,
                            sex: str,
                            vital_temperature_c: float,
                            vital_heart_rate: int,
                            symptom_list: List[str],
                            target_disease: int,
                            target_tests: List[int],
                            target_medications: List[int],
                            condition_name: str,
                            vital_blood_pressure_systolic: Optional[int] = None,
                            vital_blood_pressure_diastolic: Optional[int] = None,
                            pmh_list: Optional[List[str]] = None,
                            current_medications: Optional[List[str]] = None,
                            allergies: Optional[List[str]] = None,
                            chief_complaint: Optional[str] = None,
                            free_text_notes: Optional[str] = None,
                            data_source: str = "manual",
                            quality_score: float = 1.0,
                            is_validated: bool = False,
                            created_by: Optional[str] = None) -> ValidationData:
        """
        Add a new validation sample to the database
        
        Returns:
            ValidationData: The created validation record
        """
        
        db = self.get_session()
        try:
            record = ValidationData(
                age=age,
                sex=sex,
                vital_temperature_c=vital_temperature_c,
                vital_heart_rate=vital_heart_rate,
                vital_blood_pressure_systolic=vital_blood_pressure_systolic,
                vital_blood_pressure_diastolic=vital_blood_pressure_diastolic,
                symptom_list=symptom_list,
                pmh_list=pmh_list or [],
                current_medications=current_medications or [],
                allergies=allergies or [],
                chief_complaint=chief_complaint,
                free_text_notes=free_text_notes,
                target_disease=target_disease,
                target_tests=target_tests,
                target_medications=target_medications,
                condition_name=condition_name,
                data_source=data_source,
                quality_score=quality_score,
                is_validated=is_validated,
                created_by=created_by
            )
            
            db.add(record)
            db.commit()
            db.refresh(record)
            
            logger.info(f"✅ Added validation sample ID {record.id} for condition: {condition_name}")
            return record
            
        except Exception as e:
            db.rollback()
            logger.error(f"❌ Error adding validation sample: {e}")
            raise
        finally:
            db.close()
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive statistics about the training and validation datasets
        """
        db = self.get_session()
        try:
            stats = {}
            
            # Basic counts
            train_count = db.query(TrainingData).count()
            val_count = db.query(ValidationData).count()
            
            stats['total_samples'] = {
                'training': train_count,
                'validation': val_count,
                'total': train_count + val_count
            }
            
            # Condition distribution
            train_conditions = db.query(
                TrainingData.condition_name,
                func.count(TrainingData.id).label('count')
            ).group_by(TrainingData.condition_name).all()
            
            val_conditions = db.query(
                ValidationData.condition_name,
                func.count(ValidationData.id).label('count')
            ).group_by(ValidationData.condition_name).all()
            
            condition_stats = {}
            for condition, count in train_conditions:
                condition_stats[condition] = {'training': count, 'validation': 0}
            
            for condition, count in val_conditions:
                if condition in condition_stats:
                    condition_stats[condition]['validation'] = count
                else:
                    condition_stats[condition] = {'training': 0, 'validation': count}
            
            stats['condition_distribution'] = condition_stats
            
            # Data quality statistics
            train_quality_stats = db.query(
                func.avg(TrainingData.quality_score).label('avg_quality'),
                func.min(TrainingData.quality_score).label('min_quality'),
                func.max(TrainingData.quality_score).label('max_quality'),
                func.count(TrainingData.id).filter(TrainingData.is_validated == True).label('validated_count')
            ).first()
            
            val_quality_stats = db.query(
                func.avg(ValidationData.quality_score).label('avg_quality'),
                func.min(ValidationData.quality_score).label('min_quality'),
                func.max(ValidationData.quality_score).label('max_quality'),
                func.count(ValidationData.id).filter(ValidationData.is_validated == True).label('validated_count')
            ).first()
            
            stats['quality_metrics'] = {
                'training': {
                    'average_quality': float(train_quality_stats.avg_quality) if train_quality_stats.avg_quality else 0,
                    'min_quality': float(train_quality_stats.min_quality) if train_quality_stats.min_quality else 0,
                    'max_quality': float(train_quality_stats.max_quality) if train_quality_stats.max_quality else 0,
                    'validated_samples': train_quality_stats.validated_count or 0
                },
                'validation': {
                    'average_quality': float(val_quality_stats.avg_quality) if val_quality_stats.avg_quality else 0,
                    'min_quality': float(val_quality_stats.min_quality) if val_quality_stats.min_quality else 0,
                    'max_quality': float(val_quality_stats.max_quality) if val_quality_stats.max_quality else 0,
                    'validated_samples': val_quality_stats.validated_count or 0
                }
            }
            
            # Data source distribution
            train_sources = db.query(
                TrainingData.data_source,
                func.count(TrainingData.id).label('count')
            ).group_by(TrainingData.data_source).all()
            
            val_sources = db.query(
                ValidationData.data_source,
                func.count(ValidationData.id).label('count')
            ).group_by(ValidationData.data_source).all()
            
            stats['data_sources'] = {
                'training': {source: count for source, count in train_sources},
                'validation': {source: count for source, count in val_sources}
            }
            
            return stats
            
        finally:
            db.close()
    
    def rebalance_datasets(self, train_ratio: float = 0.8, 
                          random_seed: Optional[int] = None) -> Tuple[int, int]:
        """
        Rebalance the train/validation split while maintaining condition distribution
        
        Args:
            train_ratio: Proportion of data to use for training (0.0 to 1.0)
            random_seed: Random seed for reproducibility
            
        Returns:
            Tuple of (new_train_count, new_val_count)
        """
        if random_seed is not None:
            random.seed(random_seed)
        
        db = self.get_session()
        try:
            # Get all samples grouped by condition
            all_conditions = db.query(TrainingData.condition_name).distinct().all()
            all_conditions.extend(db.query(ValidationData.condition_name).distinct().all())
            unique_conditions = list(set([c[0] for c in all_conditions]))
            
            new_train_samples = []
            new_val_samples = []
            
            for condition in unique_conditions:
                # Get all samples for this condition
                train_samples = db.query(TrainingData).filter(
                    TrainingData.condition_name == condition
                ).all()
                
                val_samples = db.query(ValidationData).filter(
                    ValidationData.condition_name == condition
                ).all()
                
                # Combine all samples
                all_samples = []
                
                # Convert training samples
                for sample in train_samples:
                    sample_dict = {
                        'id': sample.id,
                        'type': 'training',
                        'data': sample
                    }
                    all_samples.append(sample_dict)
                
                # Convert validation samples
                for sample in val_samples:
                    sample_dict = {
                        'id': sample.id,
                        'type': 'validation',
                        'data': sample
                    }
                    all_samples.append(sample_dict)
                
                # Randomly shuffle
                random.shuffle(all_samples)
                
                # Split based on train_ratio
                condition_count = len(all_samples)
                train_count = int(condition_count * train_ratio)
                
                condition_train = all_samples[:train_count]
                condition_val = all_samples[train_count:]
                
                new_train_samples.extend(condition_train)
                new_val_samples.extend(condition_val)
            
            # Clear existing data
            db.query(TrainingData).delete()
            db.query(ValidationData).delete()
            
            # Add rebalanced training data
            for sample_info in new_train_samples:
                original_data = sample_info['data']
                
                if sample_info['type'] == 'training':
                    # Already training data, just re-add
                    new_record = TrainingData(**{
                        attr: getattr(original_data, attr) 
                        for attr in TrainingData.__table__.columns.keys() 
                        if attr != 'id'
                    })
                else:
                    # Convert from validation to training
                    new_record = TrainingData(**{
                        attr: getattr(original_data, attr)
                        for attr in ValidationData.__table__.columns.keys()
                        if attr != 'id' and hasattr(TrainingData, attr)
                    })
                
                db.add(new_record)
            
            # Add rebalanced validation data
            for sample_info in new_val_samples:
                original_data = sample_info['data']
                
                if sample_info['type'] == 'validation':
                    # Already validation data, just re-add
                    new_record = ValidationData(**{
                        attr: getattr(original_data, attr)
                        for attr in ValidationData.__table__.columns.keys()
                        if attr != 'id'
                    })
                else:
                    # Convert from training to validation
                    new_record = ValidationData(**{
                        attr: getattr(original_data, attr)
                        for attr in TrainingData.__table__.columns.keys()
                        if attr != 'id' and hasattr(ValidationData, attr)
                    })
                
                db.add(new_record)
            
            db.commit()
            
            # Get final counts
            final_train_count = db.query(TrainingData).count()
            final_val_count = db.query(ValidationData).count()
            
            logger.info(f"✅ Rebalanced datasets: {final_train_count} training, {final_val_count} validation")
            
            return final_train_count, final_val_count
            
        except Exception as e:
            db.rollback()
            logger.error(f"❌ Error rebalancing datasets: {e}")
            raise
        finally:
            db.close()
    
    def validate_data_integrity(self) -> Dict[str, Any]:
        """
        Validate data integrity and identify potential issues
        """
        db = self.get_session()
        try:
            issues = {
                'critical': [],
                'warnings': [],
                'info': []
            }
            
            # Check for missing vital signs
            train_missing_vitals = db.query(TrainingData).filter(
                (TrainingData.vital_temperature_c == None) |
                (TrainingData.vital_heart_rate == None)
            ).count()
            
            val_missing_vitals = db.query(ValidationData).filter(
                (ValidationData.vital_temperature_c == None) |
                (ValidationData.vital_heart_rate == None)
            ).count()
            
            if train_missing_vitals + val_missing_vitals > 0:
                issues['critical'].append(
                    f"Missing vital signs: {train_missing_vitals} training, {val_missing_vitals} validation"
                )
            
            # Check for empty symptom lists
            train_empty_symptoms = db.query(TrainingData).filter(
                func.json_array_length(TrainingData.symptom_list) == 0
            ).count()
            
            val_empty_symptoms = db.query(ValidationData).filter(
                func.json_array_length(ValidationData.symptom_list) == 0
            ).count()
            
            if train_empty_symptoms + val_empty_symptoms > 0:
                issues['warnings'].append(
                    f"Empty symptom lists: {train_empty_symptoms} training, {val_empty_symptoms} validation"
                )
            
            # Check for invalid target diseases
            max_disease_id = db.query(func.max(ICD10Code.id)).scalar() or 0
            
            invalid_train_diseases = db.query(TrainingData).filter(
                (TrainingData.target_disease < 0) | 
                (TrainingData.target_disease > max_disease_id)
            ).count()
            
            invalid_val_diseases = db.query(ValidationData).filter(
                (ValidationData.target_disease < 0) | 
                (ValidationData.target_disease > max_disease_id)
            ).count()
            
            if invalid_train_diseases + invalid_val_diseases > 0:
                issues['critical'].append(
                    f"Invalid disease IDs: {invalid_train_diseases} training, {invalid_val_diseases} validation"
                )
            
            # Check age ranges
            train_age_issues = db.query(TrainingData).filter(
                (TrainingData.age < 0) | (TrainingData.age > 120)
            ).count()
            
            val_age_issues = db.query(ValidationData).filter(
                (ValidationData.age < 0) | (ValidationData.age > 120)
            ).count()
            
            if train_age_issues + val_age_issues > 0:
                issues['warnings'].append(
                    f"Unusual ages (< 0 or > 120): {train_age_issues} training, {val_age_issues} validation"
                )
            
            # Check for low quality scores
            train_low_quality = db.query(TrainingData).filter(
                TrainingData.quality_score < 0.7
            ).count()
            
            val_low_quality = db.query(ValidationData).filter(
                ValidationData.quality_score < 0.7
            ).count()
            
            if train_low_quality + val_low_quality > 0:
                issues['info'].append(
                    f"Low quality samples (< 0.7): {train_low_quality} training, {val_low_quality} validation"
                )
            
            return issues
            
        finally:
            db.close()
    
    def export_to_csv(self, output_dir: str = "exported_data") -> Tuple[str, str]:
        """
        Export current training and validation data to CSV files
        
        Returns:
            Tuple of (train_csv_path, val_csv_path)
        """
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        db = self.get_session()
        try:
            # Export training data
            train_query = """
            SELECT 
                age, sex, vital_temperature_c, vital_heart_rate,
                vital_blood_pressure_systolic, vital_blood_pressure_diastolic,
                symptom_list, pmh_list, current_medications, allergies,
                chief_complaint, free_text_notes, target_disease,
                target_tests, target_medications, condition_name
            FROM training_data
            ORDER BY condition_name, id
            """
            
            train_df = pd.read_sql(train_query, db.connection())
            train_csv_path = output_path / f"train_dataset_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            train_df.to_csv(train_csv_path, index=False)
            
            # Export validation data
            val_query = """
            SELECT 
                age, sex, vital_temperature_c, vital_heart_rate,
                vital_blood_pressure_systolic, vital_blood_pressure_diastolic,
                symptom_list, pmh_list, current_medications, allergies,
                chief_complaint, free_text_notes, target_disease,
                target_tests, target_medications, condition_name
            FROM validation_data
            ORDER BY condition_name, id
            """
            
            val_df = pd.read_sql(val_query, db.connection())
            val_csv_path = output_path / f"val_dataset_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            val_df.to_csv(val_csv_path, index=False)
            
            logger.info(f"✅ Exported {len(train_df)} training samples to {train_csv_path}")
            logger.info(f"✅ Exported {len(val_df)} validation samples to {val_csv_path}")
            
            return str(train_csv_path), str(val_csv_path)
            
        finally:
            db.close()


def main():
    """Demo function showing usage of TrainingDataManager"""
    
    print("🗄️  Training Data Management Utilities")
    print("=" * 50)
    
    manager = TrainingDataManager()
    
    # Get current statistics
    print("\n📊 Current Dataset Statistics:")
    stats = manager.get_statistics()
    
    print(f"Total samples: {stats['total_samples']['total']}")
    print(f"  - Training: {stats['total_samples']['training']}")
    print(f"  - Validation: {stats['total_samples']['validation']}")
    
    print("\nCondition Distribution:")
    for condition, counts in stats['condition_distribution'].items():
        total = counts['training'] + counts['validation']
        print(f"  {condition}: {total} total ({counts['training']} train, {counts['validation']} val)")
    
    print("\nData Quality:")
    print(f"  Training - Avg Quality: {stats['quality_metrics']['training']['average_quality']:.3f}")
    print(f"  Validation - Avg Quality: {stats['quality_metrics']['validation']['average_quality']:.3f}")
    
    # Validate data integrity
    print("\n🔍 Data Integrity Check:")
    issues = manager.validate_data_integrity()
    
    if issues['critical']:
        print("❌ Critical Issues:")
        for issue in issues['critical']:
            print(f"  - {issue}")
    
    if issues['warnings']:
        print("⚠️  Warnings:")
        for issue in issues['warnings']:
            print(f"  - {issue}")
    
    if issues['info']:
        print("ℹ️  Information:")
        for issue in issues['info']:
            print(f"  - {issue}")
    
    if not any([issues['critical'], issues['warnings'], issues['info']]):
        print("✅ No data integrity issues found!")
    
    print("\n🎯 Management utilities are ready for use!")


if __name__ == "__main__":
    main()