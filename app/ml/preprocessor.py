"""
Data preprocessor for clinical data
Enhanced for training pipeline with comprehensive feature extraction
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Tuple, Optional
import re
import json
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.feature_extraction.text import TfidfVectorizer
import torch


class DataPreprocessor:
    """
    Preprocessor for clinical data before ML model inference
    """
    
    def __init__(self, training_mode: bool = False):
        self.training_mode = training_mode
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.symptom_vocab = self._load_symptom_vocabulary()
        self.pmh_vocab = self._load_pmh_vocabulary()
        self.text_vectorizer = TfidfVectorizer(max_features=50, stop_words='english', ngram_range=(1, 2))
        self.is_fitted = False
        
    def _load_symptom_vocabulary(self) -> Dict[str, int]:
        """
        Load symptom vocabulary mapping
        In production, this would be loaded from a file or database
        """
        common_symptoms = [
            "fever", "cough", "fatigue", "headache", "nausea", "vomiting",
            "diarrhea", "constipation", "chest pain", "abdominal pain",
            "shortness of breath", "dizziness", "weakness", "joint pain",
            "muscle pain", "sore throat", "runny nose", "congestion",
            "rash", "itching", "swelling", "difficulty swallowing",
            "productive cough", "dry cough", "night sweats", "chills",
            "loss of appetite", "weight loss", "weight gain", "insomnia"
        ]
        return {symptom: idx for idx, symptom in enumerate(common_symptoms)}
    
    def _load_pmh_vocabulary(self) -> Dict[str, int]:
        """
        Load past medical history vocabulary mapping
        """
        common_conditions = [
            "hypertension", "diabetes", "heart disease", "asthma", "copd",
            "cancer", "stroke", "kidney disease", "liver disease",
            "arthritis", "depression", "anxiety", "thyroid disorder",
            "high cholesterol", "obesity", "osteoporosis", "allergies",
            "migraines", "sleep apnea", "gastroesophageal reflux"
        ]
        return {condition: idx for idx, condition in enumerate(common_conditions)}
    
    def preprocess_vitals(self, data: Dict[str, Any]) -> np.ndarray:
        """
        Preprocess vital signs data
        """
        vitals = []
        
        # Age normalization (0-100 range)
        age = data.get("age", 0) / 100.0
        vitals.append(age)
        
        # Sex encoding (male=0, female=1, other=0.5)
        sex = data.get("sex", "other")
        sex_encoded = 0.0 if sex == "male" else 1.0 if sex == "female" else 0.5
        vitals.append(sex_encoded)
        
        # Temperature (normalize around normal 37°C)
        temp = data.get("vital_temperature_c")
        if temp is not None:
            vitals.append((temp - 37.0) / 5.0)  # Normalize around normal
        else:
            vitals.append(0.0)  # Missing value
            
        # Heart rate (normalize around normal 70 bpm)
        hr = data.get("vital_heart_rate")
        if hr is not None:
            vitals.append((hr - 70.0) / 50.0)  # Normalize around normal
        else:
            vitals.append(0.0)
            
        # Blood pressure
        sys_bp = data.get("vital_blood_pressure_systolic")
        dia_bp = data.get("vital_blood_pressure_diastolic")
        
        if sys_bp is not None:
            vitals.append((sys_bp - 120.0) / 40.0)  # Normalize around normal
        else:
            vitals.append(0.0)
            
        if dia_bp is not None:
            vitals.append((dia_bp - 80.0) / 20.0)  # Normalize around normal
        else:
            vitals.append(0.0)
        
        return np.array(vitals, dtype=np.float32)
    
    def preprocess_symptoms(self, symptom_list: List[str]) -> np.ndarray:
        """
        Convert symptom list to binary vector
        """
        symptom_vector = np.zeros(len(self.symptom_vocab), dtype=np.float32)
        
        for symptom in symptom_list:
            # Clean and normalize symptom text
            cleaned_symptom = symptom.lower().strip()
            
            # Direct match
            if cleaned_symptom in self.symptom_vocab:
                idx = self.symptom_vocab[cleaned_symptom]
                symptom_vector[idx] = 1.0
            else:
                # Fuzzy matching for partial matches
                for vocab_symptom, idx in self.symptom_vocab.items():
                    if cleaned_symptom in vocab_symptom or vocab_symptom in cleaned_symptom:
                        symptom_vector[idx] = 0.7  # Partial match confidence
                        break
        
        return symptom_vector
    
    def preprocess_pmh(self, pmh_list: List[str]) -> np.ndarray:
        """
        Convert past medical history to binary vector
        """
        pmh_vector = np.zeros(len(self.pmh_vocab), dtype=np.float32)
        
        for condition in pmh_list:
            # Clean and normalize condition text
            cleaned_condition = condition.lower().strip()
            
            # Direct match
            if cleaned_condition in self.pmh_vocab:
                idx = self.pmh_vocab[cleaned_condition]
                pmh_vector[idx] = 1.0
            else:
                # Fuzzy matching
                for vocab_condition, idx in self.pmh_vocab.items():
                    if cleaned_condition in vocab_condition or vocab_condition in cleaned_condition:
                        pmh_vector[idx] = 0.8
                        break
        
        return pmh_vector
    
    def preprocess_text(self, text: str) -> np.ndarray:
        """
        Simple text preprocessing for clinical notes
        Basic bag-of-words approach with medical keywords
        """
        if not text:
            return np.zeros(50, dtype=np.float32)  # Fixed size vector
        
        # Medical keywords to look for
        medical_keywords = [
            "pain", "severe", "mild", "moderate", "chronic", "acute",
            "onset", "duration", "frequency", "radiation", "quality",
            "associated", "relieved", "worsened", "improved", "progressive",
            "intermittent", "constant", "burning", "sharp", "dull",
            "throbbing", "cramping", "pressure", "tightness", "aching",
            "stabbing", "shooting", "tingling", "numbness", "weakness",
            "swelling", "inflammation", "infection", "bleeding", "discharge",
            "lesion", "mass", "nodule", "growth", "ulcer", "wound",
            "trauma", "injury", "fracture", "sprain", "strain", "tear",
            "dysfunction", "failure", "obstruction", "stenosis", "dilation"
        ]
        
        text_lower = text.lower()
        text_vector = np.zeros(len(medical_keywords), dtype=np.float32)
        
        for i, keyword in enumerate(medical_keywords):
            if keyword in text_lower:
                # Count occurrences and normalize
                count = text_lower.count(keyword)
                text_vector[i] = min(count / 3.0, 1.0)  # Cap at 1.0
        
        return text_vector
    
    def preprocess_input(self, data: Dict[str, Any]) -> torch.Tensor:
        """
        Complete preprocessing pipeline for model input
        """
        # Process different data types
        vitals = self.preprocess_vitals(data)
        symptoms = self.preprocess_symptoms(data.get("symptom_list", []))
        pmh = self.preprocess_pmh(data.get("pmh_list", []))
        
        # Process clinical notes
        text_features = self.preprocess_text(
            data.get("free_text_notes", "") + " " + 
            data.get("chief_complaint", "")
        )
        
        # Concatenate all features
        all_features = np.concatenate([vitals, symptoms, pmh, text_features])
        
        # Convert to torch tensor
        return torch.tensor(all_features, dtype=torch.float32).unsqueeze(0)  # Add batch dimension
    
    def fit_training_data(self, df: pd.DataFrame) -> 'DataPreprocessor':
        """
        Fit preprocessor on training data
        """
        print("🔄 Fitting preprocessor on training data...")
        
        # Prepare features for fitting
        features = self._extract_features_batch(df)
        
        # Fit scalers
        vital_features = features[:, :6]  # First 6 features are vitals
        self.scaler.fit(vital_features)
        
        # Fit text vectorizer
        all_text = []
        for idx, row in df.iterrows():
            text = f"{row.get('chief_complaint', '')} {row.get('free_text_notes', '')}"
            all_text.append(text)
        
        if all_text:
            self.text_vectorizer.fit(all_text)
        
        self.is_fitted = True
        print("✅ Preprocessor fitted successfully!")
        return self
    
    def _extract_features_batch(self, df: pd.DataFrame) -> np.ndarray:
        """
        Extract features from batch of samples (for training)
        """
        batch_features = []
        
        for idx, row in df.iterrows():
            # Convert row to dictionary format
            sample_dict = {
                'age': row.get('age', 50),
                'sex': row.get('sex', 'unknown'),
                'vital_temperature_c': row.get('vital_temperature_c', 36.5),
                'vital_heart_rate': row.get('vital_heart_rate', 70),
                'vital_blood_pressure_systolic': row.get('vital_blood_pressure_systolic', 120),
                'vital_blood_pressure_diastolic': row.get('vital_blood_pressure_diastolic', 80),
                'symptom_list': row.get('symptom_list', []),
                'pmh_list': row.get('pmh_list', []),
                'chief_complaint': row.get('chief_complaint', ''),
                'free_text_notes': row.get('free_text_notes', '')
            }
            
            # Process single sample
            features = self._process_single_sample(sample_dict, normalize=False)
            batch_features.append(features)
        
        return np.array(batch_features)
    
    def _process_single_sample(self, input_data: Dict[str, Any], normalize: bool = True) -> np.ndarray:
        """
        Process single sample (used by both batch and single prediction)
        """
        # Extract demographic and vital features
        age = input_data.get('age', 50)
        sex = input_data.get('sex', 'unknown')
        temp = input_data.get('vital_temperature_c', 36.5)
        hr = input_data.get('vital_heart_rate', 70)
        bp_sys = input_data.get('vital_blood_pressure_systolic', 120)
        bp_dia = input_data.get('vital_blood_pressure_diastolic', 80)
        
        # Normalize age to 0-1 range (assuming 18-100 years)
        age_norm = (age - 18) / (100 - 18)
        sex_encoded = 1.0 if sex.lower() == 'male' else 0.0
        
        # Vital signs (will be normalized later if normalize=True)
        vital_features = np.array([age_norm, sex_encoded, temp, hr, bp_sys, bp_dia])
        
        # Symptom features (one-hot encoding)
        symptoms = input_data.get('symptom_list', [])
        symptom_features = np.zeros(len(self.symptom_vocab))
        for symptom in symptoms:
            if isinstance(symptom, str):
                symptom_clean = symptom.lower().strip()
                if symptom_clean in self.symptom_vocab:
                    symptom_features[self.symptom_vocab[symptom_clean]] = 1.0
        
        # PMH features (one-hot encoding)
        pmh_list = input_data.get('pmh_list', [])
        pmh_features = np.zeros(len(self.pmh_vocab))
        for condition in pmh_list:
            if isinstance(condition, str):
                condition_clean = condition.lower().strip()
                # Handle common variations
                if 'diabetes' in condition_clean:
                    condition_clean = 'diabetes'
                elif 'hypertension' in condition_clean or 'high blood pressure' in condition_clean:
                    condition_clean = 'hypertension'
                
                if condition_clean in self.pmh_vocab:
                    pmh_features[self.pmh_vocab[condition_clean]] = 1.0
        
        # Text features
        text_content = f"{input_data.get('chief_complaint', '')} {input_data.get('free_text_notes', '')}"
        if hasattr(self, 'text_vectorizer') and hasattr(self.text_vectorizer, 'vocabulary_'):
            text_features = self.text_vectorizer.transform([text_content]).toarray().flatten()
        else:
            text_features = np.zeros(50)  # Default size
        
        # Combine all features
        all_features = np.concatenate([
            vital_features,
            symptom_features,
            pmh_features,
            text_features
        ])
        
        # Normalize vital signs if requested and scaler is fitted
        if normalize and self.is_fitted:
            vital_normalized = self.scaler.transform(vital_features.reshape(1, -1)).flatten()
            all_features[:6] = vital_normalized
        
        return all_features
    
    def transform_training_batch(self, df: pd.DataFrame) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        Transform training batch to model inputs and targets
        """
        if not self.is_fitted:
            raise ValueError("Preprocessor must be fitted before transforming training data")
        
        # Extract features
        features = self._extract_features_batch(df)
        
        # Normalize vital signs
        features_normalized = features.copy()
        features_normalized[:, :6] = self.scaler.transform(features[:, :6])
        
        # Extract targets
        disease_targets = df['target_disease'].values
        test_targets = self._encode_multi_label_targets(df['target_tests'].values, max_classes=25)
        med_targets = self._encode_multi_label_targets(df['target_medications'].values, max_classes=18)
        
        # Convert to tensors
        x = torch.tensor(features_normalized, dtype=torch.float32)
        y_disease = torch.tensor(disease_targets, dtype=torch.long)
        y_tests = torch.tensor(test_targets, dtype=torch.float32)
        y_meds = torch.tensor(med_targets, dtype=torch.float32)
        
        return x, y_disease, y_tests, y_meds
    
    def _encode_multi_label_targets(self, targets: np.ndarray, max_classes: int) -> np.ndarray:
        """
        Encode multi-label targets for tests and medications
        """
        encoded = np.zeros((len(targets), max_classes))
        
        for i, target_list in enumerate(targets):
            if isinstance(target_list, str):
                try:
                    target_list = eval(target_list)  # Convert string representation to list
                except:
                    target_list = []
            
            if isinstance(target_list, (list, np.ndarray)):
                for idx in target_list:
                    if isinstance(idx, (int, np.integer)) and 0 <= idx < max_classes:
                        encoded[i, idx] = 1.0
        
        return encoded
    
    def get_feature_names(self) -> List[str]:
        """
        Get feature names for model interpretation
        """
        feature_names = []
        
        # Vital signs
        feature_names.extend([
            "age_normalized", "sex_encoded", "temperature_normalized",
            "heart_rate_normalized", "systolic_bp_normalized", "diastolic_bp_normalized"
        ])
        
        # Symptoms
        feature_names.extend([f"symptom_{symptom}" for symptom in self.symptom_vocab.keys()])
        
        # Past medical history
        feature_names.extend([f"pmh_{condition}" for condition in self.pmh_vocab.keys()])
        
        # Text features (medical keywords)
        medical_keywords = [
            "pain", "severe", "mild", "moderate", "chronic", "acute",
            "onset", "duration", "frequency", "radiation", "quality",
            "associated", "relieved", "worsened", "improved", "progressive",
            "intermittent", "constant", "burning", "sharp", "dull",
            "throbbing", "cramping", "pressure", "tightness", "aching",
            "stabbing", "shooting", "tingling", "numbness", "weakness",
            "swelling", "inflammation", "infection", "bleeding", "discharge",
            "lesion", "mass", "nodule", "growth", "ulcer", "wound",
            "trauma", "injury", "fracture", "sprain", "strain", "tear",
            "dysfunction", "failure", "obstruction", "stenosis", "dilation"
        ]
        feature_names.extend([f"text_{keyword}" for keyword in medical_keywords])
        
        return feature_names
    
    def get_feature_dim(self) -> int:
        """
        Get the total number of features produced by this preprocessor
        """
        if not self.is_fitted:
            # Return estimated dimension for unfitted preprocessor
            base_features = 3  # age, vital signs basic
            vital_features = 4  # temp, hr, bp_sys, bp_dia
            symptom_features = len(self.symptom_vocab)
            pmh_features = len(self.pmh_vocab)
            text_features = 50  # TF-IDF max_features
            estimated_dim = base_features + vital_features + symptom_features + pmh_features + text_features
            return estimated_dim
        else:
            # For fitted preprocessor, we need to calculate actual dimension
            # This would be set during fitting process
            return getattr(self, '_feature_dim', 106)  # Default from training
    
    def set_feature_dim(self, dim: int):
        """Set the feature dimension (used during training)"""
        self._feature_dim = dim