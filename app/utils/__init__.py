"""
Utility functions for the Clinical Decision Support System
"""

import hashlib
import json
import logging
from typing import Any, Dict, List
from datetime import datetime
import re


def setup_logging(log_level: str = "INFO") -> logging.Logger:
    """
    Set up logging configuration
    """
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("app.log")
        ]
    )
    return logging.getLogger(__name__)


def generate_session_id(data: Dict[str, Any]) -> str:
    """
    Generate a unique session ID based on input data
    """
    # Create a hash of relevant data (excluding timestamps)
    relevant_data = {
        "age": data.get("age"),
        "sex": data.get("sex"),
        "symptoms": sorted(data.get("symptom_list", [])),
        "pmh": sorted(data.get("pmh_list", []))
    }
    
    data_string = json.dumps(relevant_data, sort_keys=True)
    return hashlib.md5(data_string.encode()).hexdigest()[:16]


def validate_vital_signs(data: Dict[str, Any]) -> List[str]:
    """
    Validate vital signs and return warnings for abnormal values
    """
    warnings = []
    
    # Temperature validation
    temp = data.get("vital_temperature_c")
    if temp:
        if temp < 35.0:
            warnings.append("Hypothermia detected (temperature < 35°C)")
        elif temp > 40.0:
            warnings.append("High fever detected (temperature > 40°C)")
    
    # Heart rate validation  
    hr = data.get("vital_heart_rate")
    if hr:
        if hr < 50:
            warnings.append("Bradycardia detected (heart rate < 50 bpm)")
        elif hr > 120:
            warnings.append("Tachycardia detected (heart rate > 120 bpm)")
    
    # Blood pressure validation
    sys_bp = data.get("vital_blood_pressure_systolic")
    dia_bp = data.get("vital_blood_pressure_diastolic")
    
    if sys_bp and dia_bp:
        if sys_bp > 180 or dia_bp > 110:
            warnings.append("Hypertensive crisis detected (BP > 180/110)")
        elif sys_bp < 90 or dia_bp < 60:
            warnings.append("Hypotension detected (BP < 90/60)")
    
    return warnings


def clean_symptom_text(symptom: str) -> str:
    """
    Clean and normalize symptom text
    """
    # Remove extra whitespace and convert to lowercase
    cleaned = re.sub(r'\s+', ' ', symptom.strip().lower())
    
    # Remove special characters except hyphens and parentheses
    cleaned = re.sub(r'[^\w\s\-\(\)]', '', cleaned)
    
    return cleaned


def calculate_age_category(age: int) -> str:
    """
    Categorize age for risk assessment
    """
    if age < 18:
        return "pediatric"
    elif age < 65:
        return "adult"
    else:
        return "geriatric"


def format_timestamp(dt: datetime = None) -> str:
    """
    Format timestamp in ISO format with timezone
    """
    if dt is None:
        dt = datetime.now()
    return dt.isoformat()


def sanitize_input_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitize input data to prevent injection attacks
    """
    sanitized = {}
    
    # Numeric fields
    numeric_fields = ["age", "vital_temperature_c", "vital_heart_rate", 
                     "vital_blood_pressure_systolic", "vital_blood_pressure_diastolic"]
    
    for field in numeric_fields:
        if field in data and data[field] is not None:
            try:
                sanitized[field] = float(data[field])
            except (ValueError, TypeError):
                # Skip invalid numeric values
                pass
    
    # String fields
    string_fields = ["sex", "chief_complaint", "free_text_notes"]
    
    for field in string_fields:
        if field in data and data[field] is not None:
            # Remove potentially dangerous characters
            text = str(data[field])
            text = re.sub(r'[<>"\';]', '', text)  # Remove HTML/SQL injection chars
            text = text.strip()[:2000]  # Limit length
            if text:
                sanitized[field] = text
    
    # List fields
    list_fields = ["symptom_list", "pmh_list", "current_medications", "allergies"]
    
    for field in list_fields:
        if field in data and isinstance(data[field], list):
            sanitized_list = []
            for item in data[field]:
                if isinstance(item, str):
                    cleaned_item = re.sub(r'[<>"\';]', '', str(item))
                    cleaned_item = cleaned_item.strip()[:100]  # Limit item length
                    if cleaned_item:
                        sanitized_list.append(cleaned_item)
            sanitized[field] = sanitized_list
    
    return sanitized


def get_medical_disclaimer() -> str:
    """
    Return standard medical disclaimer
    """
    return (
        "MEDICAL DISCLAIMER: This system provides preliminary predictions for "
        "educational and decision support purposes only. It is not intended to "
        "replace professional medical judgment, diagnosis, or treatment. "
        "Always consult qualified healthcare professionals for medical decisions. "
        "The predictions should be used as supplementary information only."
    )


def format_confidence_level(confidence: float) -> str:
    """
    Convert numeric confidence to descriptive level
    """
    if confidence >= 0.8:
        return "High confidence"
    elif confidence >= 0.6:
        return "Moderate confidence"
    elif confidence >= 0.4:
        return "Low confidence"
    else:
        return "Very low confidence"


def extract_keywords_from_text(text: str) -> List[str]:
    """
    Extract medical keywords from free text
    """
    if not text:
        return []
    
    # Common medical keywords to identify
    medical_terms = [
        "pain", "ache", "burning", "sharp", "dull", "throbbing",
        "nausea", "vomiting", "diarrhea", "constipation",
        "fever", "chills", "sweats", "fatigue", "weakness",
        "shortness", "breath", "cough", "wheeze", "congestion",
        "headache", "dizziness", "confusion", "numbness",
        "swelling", "rash", "itching", "bleeding", "discharge"
    ]
    
    text_lower = text.lower()
    found_keywords = []
    
    for term in medical_terms:
        if term in text_lower:
            found_keywords.append(term)
    
    return list(set(found_keywords))  # Remove duplicates