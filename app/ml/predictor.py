"""
Clinical Predictor - Main interface for disease prediction and recommendations
Updated to use database integration instead of hardcoded mappings
"""

import os
import json
from typing import Dict, List, Any
import torch
import numpy as np
from datetime import datetime
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from app.ml.model import ClinicalDecisionModel
from app.ml.preprocessor import DataPreprocessor
from app.schemas import DiseasePrediction, TestRecommendation, MedicationRecommendation
from app.models import ICD10Code, MedicalTest, Medication
from app.config import settings


class ClinicalPredictor:
    """
    Main predictor class that orchestrates the ML pipeline
    Now with database integration for reference data
    """
    
    def __init__(self, model_path: str = "./models/", model_version: str = "v1.0"):
        self.model_path = model_path
        self.model_version = model_version
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # Initialize database session
        engine = create_engine(settings.database_url)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        self.db_session = SessionLocal()
        
        # Initialize components
        self.preprocessor = DataPreprocessor()
        self.model = None
        
        # Load reference data from database
        self.icd10_mapping = self._load_icd10_mapping_from_db()
        self.test_mapping = self._load_test_mapping_from_db()
        self.medication_mapping = self._load_medication_mapping_from_db()
        
        # Load model if available, otherwise use dummy predictions
        self._load_model()
    
    def _load_model(self):
        """
        Load the trained PyTorch model with correct dimensions
        """
        model_file = os.path.join(self.model_path, f"clinical_model_{self.model_version}.pth")
        
        if os.path.exists(model_file):
            try:
                # Initialize model with correct dimensions based on loaded reference data
                num_diseases = len(self.icd10_mapping)
                num_tests = len(self.test_mapping) 
                num_medications = len(self.medication_mapping)
                
                # Load preprocessor to get input dimensions
                preprocessor_file = os.path.join(self.model_path, "preprocessor.pkl")
                if os.path.exists(preprocessor_file):
                    import pickle
                    with open(preprocessor_file, 'rb') as f:
                        saved_preprocessor = pickle.load(f)
                        input_size = saved_preprocessor.get_feature_dim()
                else:
                    input_size = 150  # default fallback
                
                print(f"Initializing model with: input_size={input_size}, diseases={num_diseases}, tests={num_tests}, meds={num_medications}")
                
                # Load model with correct dimensions
                self.model = ClinicalDecisionModel(
                    input_size=input_size,
                    num_diseases=num_diseases,
                    num_tests=num_tests,
                    num_medications=num_medications
                )
                self.model.load_state_dict(torch.load(model_file, map_location=self.device))
                self.model.to(self.device)
                self.model.eval()
                print(f"✅ Loaded trained model from {model_file}")
                
                # Load the saved preprocessor 
                if os.path.exists(preprocessor_file):
                    with open(preprocessor_file, 'rb') as f:
                        self.preprocessor = pickle.load(f)
                    print("✅ Loaded trained preprocessor")
                    # Ensure preprocessor is in the correct mode
                    if hasattr(self.preprocessor, 'set_feature_dim'):
                        self.preprocessor.set_feature_dim(input_size)
                else:
                    # Keep the default preprocessor if saved one not found
                    print("⚠️  Using default preprocessor - saved preprocessor not found")
                    
            except Exception as e:
                print(f"Error loading model: {e}")
                self.model = None
        else:
            print(f"Model file not found: {model_file}")
            print("Using dummy predictions for demonstration")
            self.model = None
    
    def _load_icd10_mapping_from_db(self) -> Dict[int, Dict[str, str]]:
        """
        Load ICD-10 code mapping from database
        """
        try:
            icd10_codes = self.db_session.query(ICD10Code).filter(ICD10Code.is_active == True).all()
            mapping = {}
            for idx, icd10 in enumerate(icd10_codes):
                mapping[idx] = {
                    "code": icd10.code,
                    "description": icd10.description,
                    "category": icd10.category
                }
            print(f"Loaded {len(mapping)} ICD-10 codes from database")
            return mapping
        except Exception as e:
            print(f"Error loading ICD-10 codes from database: {e}")
            # Fallback to minimal hardcoded mapping
            return {
                0: {"code": "J18.9", "description": "Pneumonia, unspecified organism", "category": "Respiratory"},
                1: {"code": "R50.9", "description": "Fever, unspecified", "category": "Symptoms"},
                2: {"code": "R51", "description": "Headache", "category": "Symptoms"},
                3: {"code": "R69", "description": "Illness, unspecified", "category": "Symptoms"}
            }
    
    def _load_test_mapping_from_db(self) -> Dict[int, Dict[str, str]]:
        """
        Load diagnostic test mapping from database
        """
        try:
            medical_tests = self.db_session.query(MedicalTest).filter(MedicalTest.is_active == True).all()
            mapping = {}
            for idx, test in enumerate(medical_tests):
                mapping[idx] = {
                    "test": test.test_name,
                    "code": test.test_code,
                    "description": test.description,
                    "category": test.category
                }
            print(f"Loaded {len(mapping)} medical tests from database")
            return mapping
        except Exception as e:
            print(f"Error loading medical tests from database: {e}")
            # Fallback to minimal hardcoded mapping
            return {
                0: {"test": "Complete Blood Count (CBC)", "code": "85025", "description": "Complete blood count", "category": "Laboratory"},
                1: {"test": "Chest X-ray (PA/AP)", "code": "71020", "description": "Chest X-ray", "category": "Imaging"},
                2: {"test": "Basic Metabolic Panel", "code": "80048", "description": "Basic metabolic panel", "category": "Laboratory"}
            }
    
    def _load_medication_mapping_from_db(self) -> Dict[int, Dict[str, str]]:
        """
        Load medication mapping from database
        """
        try:
            medications = self.db_session.query(Medication).filter(Medication.is_active == True).all()
            mapping = {}
            for idx, med in enumerate(medications):
                mapping[idx] = {
                    "medication": med.medication_name,
                    "generic": med.generic_name,
                    "dose": med.typical_dosage,
                    "drug_class": med.drug_class
                }
            print(f"Loaded {len(mapping)} medications from database")
            return mapping
        except Exception as e:
            print(f"Error loading medications from database: {e}")
            # Fallback to minimal hardcoded mapping
            return {
                0: {"medication": "Acetaminophen", "generic": "Acetaminophen", "dose": "650 mg PO q6h PRN", "drug_class": "Analgesic"},
                1: {"medication": "Ibuprofen", "generic": "Ibuprofen", "dose": "400 mg PO q6h PRN", "drug_class": "NSAID"},
                2: {"medication": "Amoxicillin", "generic": "Amoxicillin", "dose": "500 mg PO TID", "drug_class": "Antibiotic"}
            }
    
    def _generate_dummy_predictions(self, input_data: Dict[str, Any]) -> List[DiseasePrediction]:
        """
        Generate dummy predictions when model is not available
        This simulates real model behavior for demonstration
        """
        # Simple rule-based logic for demonstration
        predictions = []
        
        symptoms = input_data.get("symptom_list", [])
        temp = input_data.get("vital_temperature_c")
        
        # Rule 1: Fever + cough = likely respiratory infection
        if temp and temp > 38.0 and any("cough" in s.lower() for s in symptoms):
            predictions.append(DiseasePrediction(
                icd10_code="J18.9",
                diagnosis="Pneumonia, unspecified organism",
                confidence=0.82,
                recommended_tests=[
                    TestRecommendation(test="Chest X-ray (PA/AP)", confidence=0.9, urgency="routine"),
                    TestRecommendation(test="Complete Blood Count (CBC)", confidence=0.8, urgency="routine")
                ],
                recommended_medications=[
                    MedicationRecommendation(
                        medication="Amoxicillin-clavulanate",
                        confidence=0.78,
                        dose_suggestion="500 mg PO TID",
                        duration="7-10 days"
                    )
                ],
                assessment_plan="Likely community-acquired pneumonia. Obtain chest x-ray and CBC; start empiric oral antibiotics considering allergy history. Re-evaluate in 48 hours.",
                rationale=[
                    f"Fever ({temp}°C)",
                    "Productive cough reported",
                    "Clinical presentation consistent with respiratory infection"
                ]
            ))
        
        # Rule 2: Fever alone
        elif temp and temp > 37.5:
            predictions.append(DiseasePrediction(
                icd10_code="R50.9",
                diagnosis="Fever, unspecified",
                confidence=0.65,
                recommended_tests=[
                    TestRecommendation(test="Complete Blood Count (CBC)", confidence=0.8, urgency="routine"),
                    TestRecommendation(test="Urinalysis", confidence=0.6, urgency="routine")
                ],
                recommended_medications=[
                    MedicationRecommendation(
                        medication="Acetaminophen",
                        confidence=0.9,
                        dose_suggestion="650 mg PO q6h PRN",
                        duration="As needed"
                    )
                ],
                assessment_plan="Fever of unknown origin. Supportive care and symptomatic treatment. Monitor for additional symptoms.",
                rationale=[
                    f"Elevated temperature ({temp}°C)",
                    "No clear source identified"
                ]
            ))
        
        # Rule 3: Headache
        if any("headache" in s.lower() for s in symptoms):
            predictions.append(DiseasePrediction(
                icd10_code="R51",
                diagnosis="Headache",
                confidence=0.70,
                recommended_tests=[
                    TestRecommendation(test="Basic Metabolic Panel", confidence=0.5, urgency="routine")
                ],
                recommended_medications=[
                    MedicationRecommendation(
                        medication="Ibuprofen",
                        confidence=0.85,
                        dose_suggestion="400 mg PO q6h PRN",
                        duration="As needed"
                    )
                ],
                assessment_plan="Primary headache. Symptomatic treatment with NSAIDs. Consider neurological evaluation if persistent or severe.",
                rationale=["Patient reports headache"]
            ))
        
        # Rule 4: Cough only
        elif any("cough" in s.lower() for s in symptoms):
            predictions.append(DiseasePrediction(
                icd10_code="J40",
                diagnosis="Bronchitis, not specified as acute or chronic",
                confidence=0.68,
                recommended_tests=[
                    TestRecommendation(test="Chest X-ray (PA/AP)", confidence=0.7, urgency="routine")
                ],
                recommended_medications=[
                    MedicationRecommendation(
                        medication="Dextromethorphan",
                        confidence=0.75,
                        dose_suggestion="15 mg PO q4h PRN",
                        duration="As needed for cough"
                    )
                ],
                assessment_plan="Bronchitis, likely viral etiology. Supportive care with cough suppressants. Monitor for bacterial superinfection.",
                rationale=["Cough without fever suggests viral bronchitis"]
            ))
        
        # Default prediction if no specific rules match
        if not predictions:
            predictions.append(DiseasePrediction(
                icd10_code="Z00.00",
                diagnosis="Encounter for general adult medical examination without abnormal findings",
                confidence=0.40,
                recommended_tests=[
                    TestRecommendation(test="Complete Blood Count (CBC)", confidence=0.6, urgency="routine")
                ],
                recommended_medications=[],
                assessment_plan="Non-specific symptoms. Recommend follow-up if symptoms persist or worsen. Consider routine health maintenance.",
                rationale=["Non-specific clinical presentation"]
            ))
        
        # Ensure we have up to 3 predictions by adding from database mapping if needed
        while len(predictions) < 3 and len(predictions) < len(self.icd10_mapping):
            next_idx = len(predictions)
            if next_idx in self.icd10_mapping:
                icd_data = self.icd10_mapping[next_idx]
                predictions.append(DiseasePrediction(
                    icd10_code=icd_data["code"],
                    diagnosis=icd_data["description"],
                    confidence=max(0.3 - next_idx * 0.1, 0.1),
                    recommended_tests=[],
                    recommended_medications=[],
                    assessment_plan="Consider as differential diagnosis. Additional evaluation may be needed.",
                    rationale=["Differential diagnosis consideration"],
                    risk_factors=[],
                    differential_diagnoses=[]
                ))
        
        return predictions[:3]  # Return top 3
    
    def predict(self, input_data: Dict[str, Any]) -> List[DiseasePrediction]:
        """
        Main prediction method
        """
        try:
            if self.model is not None:
                # Use trained model
                processed_input = self.preprocessor.preprocess_input(input_data)
                
                # Ensure input dimensions match trained model (temporary fix)
                expected_dim = 106  # Model was trained with 106 features
                if processed_input.shape[1] != expected_dim:
                    print(f"⚠️  Adjusting input dims from {processed_input.shape[1]} to {expected_dim}")
                    if processed_input.shape[1] > expected_dim:
                        processed_input = processed_input[:, :expected_dim]  # Crop
                    else:
                        # Pad with zeros if needed
                        padding = torch.zeros(processed_input.shape[0], expected_dim - processed_input.shape[1])
                        processed_input = torch.cat([processed_input, padding], dim=1)
                
                processed_input = processed_input.to(self.device)
                
                # Get model predictions
                with torch.no_grad():
                    outputs = self.model(processed_input)
                    disease_probs = outputs['disease_probabilities']
                    test_probs = outputs['test_probabilities']
                    med_probs = outputs['medication_probabilities']
                    
                    # Get top 3 disease predictions
                    top_values, top_indices = torch.topk(disease_probs, k=min(3, disease_probs.size(1)), dim=1)
                    top_values = top_values.squeeze().cpu().numpy()
                    top_indices = top_indices.squeeze().cpu().numpy()
                    
                    # Get top tests and medications
                    test_values, test_indices = torch.topk(test_probs, k=min(3, test_probs.size(1)), dim=1)
                    med_values, med_indices = torch.topk(med_probs, k=min(2, med_probs.size(1)), dim=1)
                
                # Convert to response format
                predictions = []
                
                # Handle both single sample and batch cases
                if len(top_indices.shape) == 0:  # Single sample
                    top_indices = [top_indices.item()]
                    top_values = [top_values.item()]
                elif len(top_indices.shape) == 1:  # Batch of 1
                    top_indices = top_indices.tolist()
                    top_values = top_values.tolist()
                
                for i, (disease_idx, confidence) in enumerate(zip(top_indices, top_values)):
                    if disease_idx in self.icd10_mapping:
                        icd_data = self.icd10_mapping[disease_idx]
                        
                        # Get relevant tests and medications
                        relevant_tests = []
                        if len(test_indices.shape) > 0:
                            test_idx_list = test_indices.squeeze().cpu().numpy() if len(test_indices.shape) > 1 else [test_indices.item()]
                            test_val_list = test_values.squeeze().cpu().numpy() if len(test_values.shape) > 1 else [test_values.item()]
                            
                            for test_idx, test_conf in zip(test_idx_list[:3], test_val_list[:3]):
                                if test_idx in self.test_mapping:
                                    relevant_tests.append(TestRecommendation(
                                        test=self.test_mapping[test_idx]["test"],
                                        confidence=float(test_conf),
                                        urgency="routine"
                                    ))
                        
                        relevant_meds = []
                        if len(med_indices.shape) > 0:
                            med_idx_list = med_indices.squeeze().cpu().numpy() if len(med_indices.shape) > 1 else [med_indices.item()]
                            med_val_list = med_values.squeeze().cpu().numpy() if len(med_values.shape) > 1 else [med_values.item()]
                            
                            for med_idx, med_conf in zip(med_idx_list[:2], med_val_list[:2]):
                                if med_idx in self.medication_mapping:
                                    relevant_meds.append(MedicationRecommendation(
                                        medication=self.medication_mapping[med_idx]["medication"],
                                        confidence=float(med_conf),
                                        dose_suggestion=self.medication_mapping[med_idx]["dose"]
                                    ))
                        
                        predictions.append(DiseasePrediction(
                            icd10_code=icd_data["code"],
                            diagnosis=icd_data["description"],
                            confidence=float(confidence),
                            recommended_tests=relevant_tests,
                            recommended_medications=relevant_meds,
                            assessment_plan=f"ML model suggests {icd_data['description'].lower()}. Confidence: {confidence:.2f}. Recommend appropriate diagnostic workup and treatment based on clinical context.",
                            rationale=["ML model prediction based on clinical features", f"Model confidence: {confidence:.3f}"]
                        ))
                
                return predictions
            
            else:
                # Use dummy predictions
                return self._generate_dummy_predictions(input_data)
                
        except Exception as e:
            print(f"Prediction error: {e}")
            # Return fallback prediction
            return [DiseasePrediction(
                icd10_code="R69",
                diagnosis="Illness, unspecified",
                confidence=0.30,
                recommended_tests=[],
                recommended_medications=[],
                assessment_plan="Unable to generate specific prediction. Recommend clinical evaluation.",
                rationale=[f"Prediction error: {str(e)}"]
            )]
    
    def get_icd10_by_code(self, code: str) -> Dict[str, str]:
        """
        Get ICD-10 information by code from database
        """
        try:
            icd10 = self.db_session.query(ICD10Code).filter(ICD10Code.code == code).first()
            if icd10:
                return {
                    "code": icd10.code,
                    "description": icd10.description,
                    "category": icd10.category
                }
        except Exception as e:
            print(f"Error retrieving ICD-10 code {code}: {e}")
        
        return None
    
    def search_icd10_by_description(self, search_term: str) -> List[Dict[str, str]]:
        """
        Search ICD-10 codes by description
        """
        try:
            icd10_codes = self.db_session.query(ICD10Code).filter(
                ICD10Code.description.ilike(f"%{search_term}%"),
                ICD10Code.is_active == True
            ).limit(10).all()
            
            return [
                {
                    "code": icd10.code,
                    "description": icd10.description,
                    "category": icd10.category
                }
                for icd10 in icd10_codes
            ]
        except Exception as e:
            print(f"Error searching ICD-10 codes: {e}")
            return []
    
    def __del__(self):
        """
        Clean up database session
        """
        try:
            if hasattr(self, 'db_session'):
                self.db_session.close()
        except:
            pass