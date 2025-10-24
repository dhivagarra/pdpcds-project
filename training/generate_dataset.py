"""
Synthetic Medical Dataset Generator for Clinical Decision Support System
Generates realistic training data based on medical knowledge and clinical patterns
"""

import os
import sys
import pandas as pd
import numpy as np
import json
import random
from typing import Dict, List, Tuple, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models import ICD10Code, MedicalTest, Medication
from app.config import settings


class MedicalDatasetGenerator:
    """
    Generates synthetic medical training data for ML model training
    """
    
    def __init__(self, num_samples: int = 5000):
        self.num_samples = num_samples
        
        # Initialize database connection
        engine = create_engine(settings.database_url)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        self.db_session = SessionLocal()
        
        # Load reference data from database
        self.icd10_codes = self._load_icd10_codes()
        self.medical_tests = self._load_medical_tests()
        self.medications = self._load_medications()
        
        # Define clinical patterns and correlations
        self._setup_clinical_patterns()
    
    def _load_icd10_codes(self) -> List[Dict]:
        """Load ICD-10 codes from database"""
        codes = self.db_session.query(ICD10Code).filter(ICD10Code.is_active == True).all()
        return [
            {
                "code": code.code,
                "description": code.description,
                "category": code.category,
                "id": idx
            }
            for idx, code in enumerate(codes)
        ]
    
    def _load_medical_tests(self) -> List[Dict]:
        """Load medical tests from database"""
        tests = self.db_session.query(MedicalTest).filter(MedicalTest.is_active == True).all()
        return [
            {
                "test_name": test.test_name,
                "test_code": test.test_code,
                "category": test.category,
                "id": idx
            }
            for idx, test in enumerate(tests)
        ]
    
    def _load_medications(self) -> List[Dict]:
        """Load medications from database"""
        meds = self.db_session.query(Medication).filter(Medication.is_active == True).all()
        return [
            {
                "medication_name": med.medication_name,
                "drug_class": med.drug_class,
                "id": idx
            }
            for idx, med in enumerate(meds)
        ]
    
    def _setup_clinical_patterns(self):
        """Define clinical patterns and correlations for realistic data generation"""
        
        # Symptom-disease correlations (higher probability)
        self.symptom_disease_patterns = {
            "pneumonia": {
                "symptoms": ["fever", "productive cough", "shortness of breath", "chest pain", "fatigue"],
                "vital_ranges": {
                    "temperature": (38.0, 40.0),
                    "heart_rate": (90, 130),
                    "bp_systolic": (100, 160),
                    "bp_diastolic": (60, 100)
                },
                "age_preference": (40, 80),
                "icd10_codes": ["J18.9", "J15.9", "J44.0"]
            },
            "hypertension": {
                "symptoms": ["headache", "dizziness", "nausea"],
                "vital_ranges": {
                    "temperature": (36.0, 37.5),
                    "heart_rate": (60, 100),
                    "bp_systolic": (140, 200),
                    "bp_diastolic": (90, 120)
                },
                "age_preference": (50, 80),
                "icd10_codes": ["I10"]
            },
            "diabetes": {
                "symptoms": ["fatigue", "increased urination", "increased thirst", "blurred vision"],
                "vital_ranges": {
                    "temperature": (36.0, 37.5),
                    "heart_rate": (70, 110),
                    "bp_systolic": (120, 180),
                    "bp_diastolic": (70, 100)
                },
                "age_preference": (40, 70),
                "icd10_codes": ["E11.9", "E10.9", "E11.65"]
            },
            "migraine": {
                "symptoms": ["headache", "nausea", "sensitivity to light", "vomiting"],
                "vital_ranges": {
                    "temperature": (36.0, 37.2),
                    "heart_rate": (60, 90),
                    "bp_systolic": (110, 140),
                    "bp_diastolic": (70, 90)
                },
                "age_preference": (20, 50),
                "icd10_codes": ["G43.9"]
            },
            "asthma": {
                "symptoms": ["shortness of breath", "wheezing", "cough", "chest tightness"],
                "vital_ranges": {
                    "temperature": (36.0, 37.5),
                    "heart_rate": (80, 120),
                    "bp_systolic": (100, 140),
                    "bp_diastolic": (60, 90)
                },
                "age_preference": (10, 60),
                "icd10_codes": ["J45.9", "J45.1"]
            },
            "gastritis": {
                "symptoms": ["nausea", "vomiting", "abdominal pain", "loss of appetite"],
                "vital_ranges": {
                    "temperature": (36.0, 38.0),
                    "heart_rate": (70, 100),
                    "bp_systolic": (100, 140),
                    "bp_diastolic": (60, 90)
                },
                "age_preference": (25, 65),
                "icd10_codes": ["K29.20", "K25.9"]
            },
            "heart_failure": {
                "symptoms": ["shortness of breath", "fatigue", "swelling", "rapid heartbeat"],
                "vital_ranges": {
                    "temperature": (36.0, 37.5),
                    "heart_rate": (90, 130),
                    "bp_systolic": (90, 160),
                    "bp_diastolic": (50, 90)
                },
                "age_preference": (60, 85),
                "icd10_codes": ["I50.9"]
            }
        }
        
        # Common symptoms pool
        self.all_symptoms = [
            "fever", "cough", "headache", "fatigue", "nausea", "vomiting",
            "shortness of breath", "chest pain", "abdominal pain", "dizziness",
            "back pain", "muscle aches", "sore throat", "runny nose",
            "diarrhea", "constipation", "loss of appetite", "weight loss",
            "swelling", "palpitations", "anxiety", "depression", "insomnia",
            "joint pain", "rash", "itching", "blurred vision", "ear pain"
        ]
        
        # Common medical history conditions
        self.common_pmh = [
            "hypertension", "diabetes type 2", "hyperlipidemia", "asthma",
            "depression", "anxiety", "GERD", "arthritis", "obesity",
            "sleep apnea", "thyroid disease", "kidney disease", "heart disease"
        ]
        
        # Common medications
        self.common_medications = [
            "lisinopril", "metformin", "simvastatin", "omeprazole",
            "albuterol", "sertraline", "ibuprofen", "acetaminophen",
            "amlodipine", "metoprolol", "prednisone", "azithromycin"
        ]
        
        # Common allergies
        self.common_allergies = [
            "penicillin", "sulfa", "latex", "peanuts", "shellfish",
            "NSAIDs", "codeine", "iodine", "eggs", "milk"
        ]
    
    def _generate_patient_demographics(self) -> Dict[str, Any]:
        """Generate realistic patient demographics"""
        age = np.random.normal(50, 20)
        age = max(18, min(95, int(age)))  # Clamp between 18-95
        
        sex = random.choice(["male", "female"])
        
        return {"age": age, "sex": sex}
    
    def _select_primary_condition(self) -> Tuple[str, Dict]:
        """Select primary medical condition for the case"""
        condition_name = random.choice(list(self.symptom_disease_patterns.keys()))
        condition_data = self.symptom_disease_patterns[condition_name]
        return condition_name, condition_data
    
    def _generate_vital_signs(self, condition_data: Dict, age: int) -> Dict[str, float]:
        """Generate realistic vital signs based on condition"""
        vital_ranges = condition_data["vital_ranges"]
        
        # Add age-based adjustments
        age_factor = 1 + (age - 50) * 0.005  # Slight increase with age
        
        temperature = np.random.uniform(*vital_ranges["temperature"])
        heart_rate = int(np.random.uniform(*vital_ranges["heart_rate"]) * age_factor)
        bp_systolic = int(np.random.uniform(*vital_ranges["bp_systolic"]) * age_factor)
        bp_diastolic = int(np.random.uniform(*vital_ranges["bp_diastolic"]))
        
        return {
            "vital_temperature_c": round(temperature, 1),
            "vital_heart_rate": heart_rate,
            "vital_blood_pressure_systolic": bp_systolic,
            "vital_blood_pressure_diastolic": bp_diastolic
        }
    
    def _generate_symptoms(self, condition_data: Dict) -> List[str]:
        """Generate symptoms based on condition with some noise"""
        primary_symptoms = condition_data["symptoms"]
        
        # Select 2-4 primary symptoms (80% chance each)
        selected_symptoms = []
        for symptom in primary_symptoms:
            if random.random() < 0.8:
                selected_symptoms.append(symptom)
        
        # Add 0-2 random symptoms (noise) (20% chance each)
        other_symptoms = [s for s in self.all_symptoms if s not in primary_symptoms]
        for _ in range(random.randint(0, 2)):
            if random.random() < 0.2 and other_symptoms:
                selected_symptoms.append(random.choice(other_symptoms))
        
        return list(set(selected_symptoms))  # Remove duplicates
    
    def _generate_medical_history(self, age: int, primary_condition: str) -> List[str]:
        """Generate medical history based on age and correlation patterns"""
        pmh = []
        
        # Age-based probability for conditions
        if age > 50:
            if random.random() < 0.4:
                pmh.append("hypertension")
            if random.random() < 0.3:
                pmh.append("diabetes type 2")
            if random.random() < 0.25:
                pmh.append("hyperlipidemia")
        
        if age > 60:
            if random.random() < 0.2:
                pmh.append("heart disease")
            if random.random() < 0.15:
                pmh.append("arthritis")
        
        # Add some random conditions
        available_conditions = [c for c in self.common_pmh if c not in pmh]
        num_additional = random.randint(0, 2)
        for _ in range(num_additional):
            if available_conditions and random.random() < 0.15:
                pmh.append(random.choice(available_conditions))
        
        return pmh
    
    def _generate_medications_and_allergies(self, pmh: List[str]) -> Tuple[List[str], List[str]]:
        """Generate medications based on medical history and random allergies"""
        medications = []
        
        # Condition-based medications
        medication_map = {
            "hypertension": ["lisinopril", "amlodipine", "metoprolol"],
            "diabetes type 2": ["metformin", "insulin"],
            "hyperlipidemia": ["simvastatin", "atorvastatin"],
            "asthma": ["albuterol", "prednisone"],
            "GERD": ["omeprazole", "ranitidine"],
            "depression": ["sertraline", "escitalopram"]
        }
        
        for condition in pmh:
            if condition in medication_map:
                med_options = medication_map[condition]
                if random.random() < 0.7:  # 70% chance of being on medication
                    medications.append(random.choice(med_options))
        
        # Random allergies (0-2)
        allergies = []
        num_allergies = random.randint(0, 2)
        for _ in range(num_allergies):
            if random.random() < 0.3:
                allergies.append(random.choice(self.common_allergies))
        
        return medications, allergies
    
    def _generate_clinical_text(self, symptoms: List[str], condition_name: str, age: int, sex: str) -> Tuple[str, str]:
        """Generate chief complaint and clinical notes"""
        
        # Ensure we have at least one symptom
        if not symptoms:
            symptoms = ["fatigue", "general discomfort"]
        
        # Chief complaint templates
        chief_complaints = [
            f"{', '.join(symptoms[:2])} for {random.randint(1, 7)} days",
            f"Experiencing {symptoms[0]} and {symptoms[1] if len(symptoms) > 1 else 'fatigue'}",
            f"{symptoms[0].title()} and associated symptoms",
            f"Worsening {symptoms[0]} over the past {random.randint(2, 5)} days"
        ]
        
        chief_complaint = random.choice(chief_complaints)
        
        # Clinical notes template
        duration = random.randint(1, 14)
        notes_templates = [
            f"{age}-year-old {sex} presenting with {duration} days of {', '.join(symptoms[:3])}. ",
            f"Patient reports gradual onset of symptoms over {duration} days. ",
            f"Previously healthy {age}-year-old {sex} with acute onset {', '.join(symptoms[:2])}. "
        ]
        
        notes = random.choice(notes_templates)
        
        # Add condition-specific details
        if condition_name == "pneumonia":
            notes += "Productive cough with purulent sputum. No recent travel or sick contacts."
        elif condition_name == "hypertension":
            notes += "Elevated blood pressure on multiple readings. Family history of hypertension."
        elif condition_name == "diabetes":
            notes += "Polyuria, polydipsia, and recent weight loss noted."
        elif condition_name == "migraine":
            notes += "Unilateral throbbing headache with photophobia. Previous similar episodes."
        else:
            notes += "Symptoms are gradually worsening. No obvious precipitating factors identified."
        
        return chief_complaint, notes
    
    def _select_target_labels(self, condition_data: Dict) -> Tuple[int, List[int], List[int]]:
        """Select target labels for disease, tests, and medications"""
        
        # Primary disease (select from ICD-10 codes for this condition)
        target_icd10_codes = condition_data["icd10_codes"]
        primary_icd10 = random.choice(target_icd10_codes)
        
        # Find disease index in our database
        disease_idx = 0
        for idx, icd10 in enumerate(self.icd10_codes):
            if icd10["code"].strip() == primary_icd10.strip():
                disease_idx = idx
                break
        
        # Recommended tests (select 2-4 relevant tests)
        relevant_test_categories = ["Laboratory", "Imaging", "Cardiac"]
        test_indices = []
        for test in self.medical_tests:
            if test["category"] in relevant_test_categories and len(test_indices) < 4:
                if random.random() < 0.6:  # 60% chance of being relevant
                    test_indices.append(test["id"])
        
        # Recommended medications (select 1-3 relevant medications)
        medication_indices = []
        for med in self.medications:
            if len(medication_indices) < 3:
                if random.random() < 0.4:  # 40% chance of being relevant
                    medication_indices.append(med["id"])
        
        return disease_idx, test_indices, medication_indices
    
    def generate_sample(self) -> Dict[str, Any]:
        """Generate a single training sample"""
        
        # Generate patient demographics
        demographics = self._generate_patient_demographics()
        age = demographics["age"]
        sex = demographics["sex"]
        
        # Select primary condition
        condition_name, condition_data = self._select_primary_condition()
        
        # Generate clinical data
        vitals = self._generate_vital_signs(condition_data, age)
        symptoms = self._generate_symptoms(condition_data)
        pmh = self._generate_medical_history(age, condition_name)
        medications, allergies = self._generate_medications_and_allergies(pmh)
        chief_complaint, notes = self._generate_clinical_text(symptoms, condition_name, age, sex)
        
        # Generate target labels
        disease_idx, test_indices, med_indices = self._select_target_labels(condition_data)
        
        # Combine all data
        sample = {
            "age": age,
            "sex": sex,
            **vitals,
            "symptom_list": symptoms,
            "pmh_list": pmh,
            "current_medications": medications,
            "allergies": allergies,
            "chief_complaint": chief_complaint,
            "free_text_notes": notes,
            
            # Target labels
            "target_disease": disease_idx,
            "target_tests": test_indices,
            "target_medications": med_indices,
            "condition_name": condition_name  # For analysis
        }
        
        return sample
    
    def generate_dataset(self, train_ratio: float = 0.8) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Generate complete training and validation datasets"""
        
        print(f"🔄 Generating {self.num_samples} synthetic medical samples...")
        
        samples = []
        for i in range(self.num_samples):
            if i % 500 == 0:
                print(f"   Generated {i}/{self.num_samples} samples...")
            
            sample = self.generate_sample()
            samples.append(sample)
        
        # Convert to DataFrame
        df = pd.DataFrame(samples)
        
        # Split into training and validation
        split_idx = int(len(df) * train_ratio)
        train_df = df[:split_idx].copy()
        val_df = df[split_idx:].copy()
        
        print(f"✅ Dataset generated successfully!")
        print(f"   Training samples: {len(train_df)}")
        print(f"   Validation samples: {len(val_df)}")
        print(f"   Unique conditions: {df['condition_name'].nunique()}")
        print(f"   Condition distribution:")
        for condition, count in df['condition_name'].value_counts().head(10).items():
            print(f"      {condition}: {count}")
        
        return train_df, val_df
    
    def save_datasets(self, train_df: pd.DataFrame, val_df: pd.DataFrame, output_dir: str = "./training/data"):
        """Save datasets to files"""
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        train_path = os.path.join(output_dir, "train_dataset.csv")
        val_path = os.path.join(output_dir, "val_dataset.csv")
        
        train_df.to_csv(train_path, index=False)
        val_df.to_csv(val_path, index=False)
        
        print(f"💾 Datasets saved:")
        print(f"   Training: {train_path}")
        print(f"   Validation: {val_path}")
        
        return train_path, val_path
    
    def __del__(self):
        """Clean up database session"""
        try:
            if hasattr(self, 'db_session'):
                self.db_session.close()
        except:
            pass


def main():
    """Generate synthetic medical dataset for training"""
    
    print("🚀 Starting Medical Dataset Generation...")
    print("=" * 50)
    
    # Generate dataset
    generator = MedicalDatasetGenerator(num_samples=2000)  # Start with 2000 samples
    train_df, val_df = generator.generate_dataset()
    
    # Save datasets
    train_path, val_path = generator.save_datasets(train_df, val_df)
    
    print("=" * 50)
    print("✅ Medical dataset generation completed!")


if __name__ == "__main__":
    main()