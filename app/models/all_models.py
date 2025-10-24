"""
Import all models to ensure they're registered with SQLAlchemy
"""

# Import all models so they're available when the module is imported
from app.models import *
from app.models.feedback import ClinicalFeedback, ClinicalOutcomeRecord

# Make feedback models available in the main models namespace
__all__ = [
    'Patient', 'Prediction', 'ICD10Code', 'MedicalTest', 'Medication',
    'TrainingData', 'ValidationData', 'ClinicalFeedback', 'ClinicalOutcomeRecord'
]