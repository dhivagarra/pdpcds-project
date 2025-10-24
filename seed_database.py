"""
Database seeding script for Clinical Decision Support System
Populates reference tables with comprehensive medical data
"""

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from app.database import Base, get_db
from app.models import ICD10Code, MedicalTest, Medication
from app.config import settings
import json
from datetime import datetime

# ICD-10 codes for common medical conditions
ICD10_SEED_DATA = [
    # Infectious diseases (A00-B99)
    {"code": "A09", "description": "Infectious gastroenteritis and colitis, unspecified", "category": "Infectious Diseases"},
    {"code": "A15.0", "description": "Tuberculosis of lung", "category": "Infectious Diseases"},
    {"code": "A15.9", "description": "Respiratory tuberculosis unspecified", "category": "Infectious Diseases"},
    {"code": "B34.9", "description": "Viral infection, unspecified", "category": "Infectious Diseases"},
    {"code": "B37.9", "description": "Candidiasis, unspecified", "category": "Infectious Diseases"},
    
    # Neoplasms (C00-D49)
    {"code": "C78.9", "description": "Secondary malignant neoplasm, unspecified", "category": "Neoplasms"},
    {"code": "C80.1", "description": "Malignant neoplasm, unspecified", "category": "Neoplasms"},
    {"code": "D12.6", "description": "Benign neoplasm of colon, unspecified", "category": "Neoplasms"},
    
    # Endocrine diseases (E00-E89)
    {"code": "E10.9", "description": "Type 1 diabetes mellitus without complications", "category": "Endocrine"},
    {"code": "E11.9", "description": "Type 2 diabetes mellitus without complications", "category": "Endocrine"},
    {"code": "E11.65", "description": "Type 2 diabetes mellitus with hyperglycemia", "category": "Endocrine"},
    {"code": "E03.9", "description": "Hypothyroidism, unspecified", "category": "Endocrine"},
    {"code": "E05.9", "description": "Thyrotoxicosis, unspecified", "category": "Endocrine"},
    {"code": "E78.5", "description": "Hyperlipidemia, unspecified", "category": "Endocrine"},
    {"code": "E66.9", "description": "Obesity, unspecified", "category": "Endocrine"},
    
    # Mental health (F00-F99)
    {"code": "F32.9", "description": "Major depressive disorder, single episode, unspecified", "category": "Mental Health"},
    {"code": "F33.9", "description": "Major depressive disorder, recurrent, unspecified", "category": "Mental Health"},
    {"code": "F41.1", "description": "Generalized anxiety disorder", "category": "Mental Health"},
    {"code": "F41.9", "description": "Anxiety disorder, unspecified", "category": "Mental Health"},
    {"code": "F43.10", "description": "Post-traumatic stress disorder, unspecified", "category": "Mental Health"},
    
    # Nervous system (G00-G99)
    {"code": "G43.9", "description": "Migraine, unspecified", "category": "Neurological"},
    {"code": "G44.1", "description": "Vascular headache, not elsewhere classified", "category": "Neurological"},
    {"code": "G89.3", "description": "Neoplasm related pain (acute) (chronic)", "category": "Neurological"},
    {"code": "G93.1", "description": "Anoxic brain damage, not elsewhere classified", "category": "Neurological"},
    
    # Circulatory system (I00-I99)
    {"code": "I10", "description": "Essential (primary) hypertension", "category": "Cardiovascular"},
    {"code": "I25.10", "description": "Atherosclerotic heart disease of native coronary artery without angina pectoris", "category": "Cardiovascular"},
    {"code": "I48.91", "description": "Unspecified atrial fibrillation", "category": "Cardiovascular"},
    {"code": "I50.9", "description": "Heart failure, unspecified", "category": "Cardiovascular"},
    {"code": "I73.9", "description": "Peripheral vascular disease, unspecified", "category": "Cardiovascular"},
    
    # Respiratory system (J00-J99)
    {"code": "J00", "description": "Acute nasopharyngitis [common cold]", "category": "Respiratory"},
    {"code": "J06.9", "description": "Acute upper respiratory infection, unspecified", "category": "Respiratory"},
    {"code": "J18.9", "description": "Pneumonia, unspecified organism", "category": "Respiratory"},
    {"code": "J20.9", "description": "Acute bronchitis, unspecified", "category": "Respiratory"},
    {"code": "J40", "description": "Bronchitis, not specified as acute or chronic", "category": "Respiratory"},
    {"code": "J44.0", "description": "Chronic obstructive pulmonary disease with acute lower respiratory infection", "category": "Respiratory"},
    {"code": "J44.1", "description": "Chronic obstructive pulmonary disease with acute exacerbation", "category": "Respiratory"},
    {"code": "J45.9", "description": "Asthma, unspecified", "category": "Respiratory"},
    
    # Digestive system (K00-K95)
    {"code": "K21.9", "description": "Gastro-esophageal reflux disease without esophagitis", "category": "Digestive"},
    {"code": "K25.9", "description": "Gastric ulcer, unspecified as acute or chronic, without hemorrhage or perforation", "category": "Digestive"},
    {"code": "K29.20", "description": "Alcoholic gastritis without bleeding", "category": "Digestive"},
    {"code": "K59.00", "description": "Constipation, unspecified", "category": "Digestive"},
    {"code": "K92.2", "description": "Gastrointestinal hemorrhage, unspecified", "category": "Digestive"},
    
    # Genitourinary system (N00-N99)
    {"code": "N18.6", "description": "End stage renal disease", "category": "Genitourinary"},
    {"code": "N39.0", "description": "Urinary tract infection, site not specified", "category": "Genitourinary"},
    {"code": "N40.1", "description": "Enlarged prostate with lower urinary tract symptoms", "category": "Genitourinary"},
    
    # Musculoskeletal system (M00-M99)
    {"code": "M25.50", "description": "Pain in unspecified joint", "category": "Musculoskeletal"},
    {"code": "M54.5", "description": "Low back pain", "category": "Musculoskeletal"},
    {"code": "M79.3", "description": "Panniculitis, unspecified", "category": "Musculoskeletal"},
    {"code": "M62.838", "description": "Other muscle spasm", "category": "Musculoskeletal"},
    
    # Symptoms and signs (R00-R99)
    {"code": "R06.02", "description": "Shortness of breath", "category": "Symptoms"},
    {"code": "R11.10", "description": "Vomiting, unspecified", "category": "Symptoms"},
    {"code": "R50.9", "description": "Fever, unspecified", "category": "Symptoms"},
    {"code": "R51", "description": "Headache", "category": "Symptoms"},
    {"code": "R53", "description": "Malaise and fatigue", "category": "Symptoms"},
    {"code": "R69", "description": "Illness, unspecified", "category": "Symptoms"},
    
    # Injury and external causes (S00-T98)
    {"code": "S72.001A", "description": "Fracture of unspecified part of neck of right femur, initial encounter for closed fracture", "category": "Injury"},
    {"code": "T78.40XA", "description": "Allergy, unspecified, initial encounter", "category": "Injury"},
    
    # External causes (V00-Y99)
    {"code": "Z00.00", "description": "Encounter for general adult medical examination without abnormal findings", "category": "Health Status"},
    {"code": "Z51.11", "description": "Encounter for antineoplastic chemotherapy", "category": "Health Status"},
]

# Medical tests seed data
MEDICAL_TESTS_SEED_DATA = [
    # Laboratory tests
    {"test_name": "Complete Blood Count (CBC)", "test_code": "85025", "description": "Complete blood count with differential", "category": "Laboratory", "typical_range": "WBC: 4.5-11.0 K/uL, RBC: 4.5-5.9 M/uL"},
    {"test_name": "Basic Metabolic Panel", "test_code": "80048", "description": "Basic metabolic panel (8 tests)", "category": "Laboratory", "typical_range": "Glucose: 70-99 mg/dL, BUN: 7-20 mg/dL"},
    {"test_name": "Comprehensive Metabolic Panel", "test_code": "80053", "description": "Comprehensive metabolic panel (14 tests)", "category": "Laboratory", "typical_range": "Multiple analytes"},
    {"test_name": "Lipid Panel", "test_code": "80061", "description": "Cholesterol, HDL, LDL, Triglycerides", "category": "Laboratory", "typical_range": "Total Chol <200 mg/dL, HDL >40 mg/dL"},
    {"test_name": "Thyroid Stimulating Hormone", "test_code": "84443", "description": "TSH level", "category": "Laboratory", "typical_range": "0.4-4.0 mIU/L"},
    {"test_name": "Hemoglobin A1c", "test_code": "83036", "description": "Glycated hemoglobin", "category": "Laboratory", "typical_range": "<5.7% (normal), 5.7-6.4% (prediabetes)"},
    {"test_name": "Urinalysis", "test_code": "81001", "description": "Complete urinalysis with microscopy", "category": "Laboratory", "typical_range": "Specific gravity: 1.005-1.030"},
    {"test_name": "Blood Urea Nitrogen", "test_code": "84520", "description": "BUN level", "category": "Laboratory", "typical_range": "7-20 mg/dL"},
    {"test_name": "Serum Creatinine", "test_code": "82565", "description": "Creatinine level", "category": "Laboratory", "typical_range": "0.7-1.3 mg/dL (male), 0.6-1.1 mg/dL (female)"},
    {"test_name": "Liver Function Tests", "test_code": "80076", "description": "ALT, AST, Bilirubin, Alkaline Phosphatase", "category": "Laboratory", "typical_range": "ALT: 7-40 U/L, AST: 8-40 U/L"},
    
    # Imaging tests
    {"test_name": "Chest X-ray (PA/AP)", "test_code": "71020", "description": "Chest X-ray, frontal view", "category": "Imaging", "typical_range": "Normal lung fields, normal heart size"},
    {"test_name": "CT Chest without contrast", "test_code": "71250", "description": "CT scan of chest without contrast", "category": "Imaging", "typical_range": "No acute abnormalities"},
    {"test_name": "CT Abdomen/Pelvis with contrast", "test_code": "74177", "description": "CT of abdomen and pelvis with contrast", "category": "Imaging", "typical_range": "Normal organ enhancement"},
    {"test_name": "MRI Brain without contrast", "test_code": "70551", "description": "MRI of brain without contrast", "category": "Imaging", "typical_range": "No acute intracranial abnormality"},
    {"test_name": "Echocardiogram", "test_code": "93306", "description": "Transthoracic echocardiogram", "category": "Imaging", "typical_range": "EF >55%, normal wall motion"},
    {"test_name": "Ultrasound Abdomen", "test_code": "76700", "description": "Abdominal ultrasound", "category": "Imaging", "typical_range": "Normal organ echogenicity"},
    
    # Cardiac tests
    {"test_name": "Electrocardiogram (ECG)", "test_code": "93000", "description": "12-lead ECG", "category": "Cardiac", "typical_range": "Normal sinus rhythm, rate 60-100 bpm"},
    {"test_name": "Troponin I", "test_code": "84484", "description": "Cardiac troponin I", "category": "Laboratory", "typical_range": "<0.04 ng/mL"},
    {"test_name": "Brain Natriuretic Peptide", "test_code": "83880", "description": "BNP level", "category": "Laboratory", "typical_range": "<100 pg/mL"},
    
    # Infectious disease tests
    {"test_name": "Blood Culture", "test_code": "87040", "description": "Blood culture for bacteria", "category": "Microbiology", "typical_range": "No growth"},
    {"test_name": "Urine Culture", "test_code": "87086", "description": "Urine culture for bacteria", "category": "Microbiology", "typical_range": "<10,000 CFU/mL"},
    {"test_name": "Rapid Strep Test", "test_code": "87081", "description": "Rapid antigen test for Strep A", "category": "Microbiology", "typical_range": "Negative"},
    {"test_name": "Influenza A/B PCR", "test_code": "87502", "description": "PCR test for influenza A and B", "category": "Microbiology", "typical_range": "Not detected"},
    
    # Pulmonary function
    {"test_name": "Pulmonary Function Tests", "test_code": "94010", "description": "Complete pulmonary function testing", "category": "Pulmonary", "typical_range": "FEV1 >80% predicted, FVC >80% predicted"},
    {"test_name": "Arterial Blood Gas", "test_code": "82803", "description": "Arterial blood gas analysis", "category": "Laboratory", "typical_range": "pH: 7.35-7.45, pCO2: 35-45 mmHg"}
]

# Medications seed data
MEDICATIONS_SEED_DATA = [
    # Antibiotics
    {"medication_name": "Amoxicillin", "generic_name": "Amoxicillin", "brand_names": ["Amoxil", "Trimox"], 
     "drug_class": "Penicillin Antibiotic", "typical_dosage": "500 mg PO TID", 
     "contraindications": ["Penicillin allergy"], "side_effects": ["Nausea", "Diarrhea", "Rash"]},
    
    {"medication_name": "Amoxicillin-clavulanate", "generic_name": "Amoxicillin-clavulanate", "brand_names": ["Augmentin"], 
     "drug_class": "Penicillin Antibiotic", "typical_dosage": "875 mg PO BID", 
     "contraindications": ["Penicillin allergy"], "side_effects": ["Nausea", "Diarrhea", "Hepatotoxicity"]},
    
    {"medication_name": "Azithromycin", "generic_name": "Azithromycin", "brand_names": ["Z-Pak", "Zithromax"], 
     "drug_class": "Macrolide Antibiotic", "typical_dosage": "500 mg day 1, then 250 mg daily x 4 days", 
     "contraindications": ["Macrolide allergy"], "side_effects": ["GI upset", "QT prolongation"]},
    
    {"medication_name": "Ciprofloxacin", "generic_name": "Ciprofloxacin", "brand_names": ["Cipro"], 
     "drug_class": "Fluoroquinolone", "typical_dosage": "500 mg PO BID", 
     "contraindications": ["Fluoroquinolone allergy", "Pregnancy"], "side_effects": ["Tendon rupture", "CNS effects"]},
    
    # Pain medications
    {"medication_name": "Acetaminophen", "generic_name": "Acetaminophen", "brand_names": ["Tylenol"], 
     "drug_class": "Analgesic/Antipyretic", "typical_dosage": "650 mg PO q6h PRN", 
     "contraindications": ["Severe hepatic impairment"], "side_effects": ["Hepatotoxicity (overdose)"]},
    
    {"medication_name": "Ibuprofen", "generic_name": "Ibuprofen", "brand_names": ["Advil", "Motrin"], 
     "drug_class": "NSAID", "typical_dosage": "400-600 mg PO q6h PRN", 
     "contraindications": ["NSAID allergy", "Renal impairment"], "side_effects": ["GI bleeding", "Renal toxicity"]},
    
    {"medication_name": "Naproxen", "generic_name": "Naproxen", "brand_names": ["Aleve", "Naprosyn"], 
     "drug_class": "NSAID", "typical_dosage": "220-440 mg PO q12h", 
     "contraindications": ["NSAID allergy"], "side_effects": ["GI bleeding", "Cardiovascular risk"]},
    
    # Cardiovascular medications
    {"medication_name": "Lisinopril", "generic_name": "Lisinopril", "brand_names": ["Prinivil", "Zestril"], 
     "drug_class": "ACE Inhibitor", "typical_dosage": "10-20 mg PO daily", 
     "contraindications": ["ACE inhibitor allergy", "Pregnancy"], "side_effects": ["Dry cough", "Hyperkalemia"]},
    
    {"medication_name": "Amlodipine", "generic_name": "Amlodipine", "brand_names": ["Norvasc"], 
     "drug_class": "Calcium Channel Blocker", "typical_dosage": "5-10 mg PO daily", 
     "contraindications": ["Severe aortic stenosis"], "side_effects": ["Peripheral edema", "Dizziness"]},
    
    {"medication_name": "Metoprolol", "generic_name": "Metoprolol", "brand_names": ["Lopressor", "Toprol"], 
     "drug_class": "Beta Blocker", "typical_dosage": "25-100 mg PO BID", 
     "contraindications": ["Severe bradycardia", "Asthma"], "side_effects": ["Bradycardia", "Fatigue"]},
    
    # Diabetes medications
    {"medication_name": "Metformin", "generic_name": "Metformin", "brand_names": ["Glucophage"], 
     "drug_class": "Biguanide", "typical_dosage": "500-1000 mg PO BID", 
     "contraindications": ["Severe renal impairment"], "side_effects": ["GI upset", "Lactic acidosis (rare)"]},
    
    {"medication_name": "Insulin glargine", "generic_name": "Insulin glargine", "brand_names": ["Lantus"], 
     "drug_class": "Long-acting insulin", "typical_dosage": "Variable, typically 0.2-0.4 units/kg daily", 
     "contraindications": ["Hypoglycemia"], "side_effects": ["Hypoglycemia", "Weight gain"]},
    
    # Respiratory medications
    {"medication_name": "Albuterol", "generic_name": "Albuterol", "brand_names": ["ProAir", "Ventolin"], 
     "drug_class": "Beta2 agonist", "typical_dosage": "2 puffs q4-6h PRN", 
     "contraindications": ["Beta agonist allergy"], "side_effects": ["Tachycardia", "Tremor"]},
    
    {"medication_name": "Prednisone", "generic_name": "Prednisone", "brand_names": ["Deltasone"], 
     "drug_class": "Corticosteroid", "typical_dosage": "20-60 mg PO daily", 
     "contraindications": ["Systemic fungal infection"], "side_effects": ["Hyperglycemia", "Osteoporosis"]},
    
    # Gastrointestinal medications
    {"medication_name": "Omeprazole", "generic_name": "Omeprazole", "brand_names": ["Prilosec"], 
     "drug_class": "Proton Pump Inhibitor", "typical_dosage": "20-40 mg PO daily", 
     "contraindications": ["PPI hypersensitivity"], "side_effects": ["Headache", "C. diff risk"]},
    
    {"medication_name": "Ondansetron", "generic_name": "Ondansetron", "brand_names": ["Zofran"], 
     "drug_class": "Antiemetic", "typical_dosage": "4-8 mg PO q8h PRN", 
     "contraindications": ["5-HT3 antagonist allergy"], "side_effects": ["Headache", "Constipation"]},
    
    # Psychiatric medications
    {"medication_name": "Sertraline", "generic_name": "Sertraline", "brand_names": ["Zoloft"], 
     "drug_class": "SSRI", "typical_dosage": "50-200 mg PO daily", 
     "contraindications": ["MAOI use"], "side_effects": ["Sexual dysfunction", "GI upset"]},
    
    {"medication_name": "Lorazepam", "generic_name": "Lorazepam", "brand_names": ["Ativan"], 
     "drug_class": "Benzodiazepine", "typical_dosage": "0.5-2 mg PO q6-8h PRN", 
     "contraindications": ["Benzodiazepine allergy"], "side_effects": ["Sedation", "Dependence risk"]},
]


def create_seeding_session():
    """Create database session for seeding"""
    engine = create_engine(settings.database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()


def seed_icd10_codes(session):
    """Seed ICD-10 codes table"""
    print("🔄 Seeding ICD-10 codes...")
    
    for icd_data in ICD10_SEED_DATA:
        # Check if code already exists
        existing = session.query(ICD10Code).filter(ICD10Code.code == icd_data["code"]).first()
        if not existing:
            icd10_record = ICD10Code(
                code=icd_data["code"],
                description=icd_data["description"],
                category=icd_data["category"],
                is_active=True
            )
            session.add(icd10_record)
    
    session.commit()
    count = session.query(ICD10Code).count()
    print(f"✅ ICD-10 codes seeded: {count} total records")


def seed_medical_tests(session):
    """Seed medical tests table"""
    print("🔄 Seeding medical tests...")
    
    for test_data in MEDICAL_TESTS_SEED_DATA:
        # Check if test already exists
        existing = session.query(MedicalTest).filter(MedicalTest.test_code == test_data["test_code"]).first()
        if not existing:
            test_record = MedicalTest(
                test_name=test_data["test_name"],
                test_code=test_data["test_code"],
                description=test_data["description"],
                category=test_data["category"],
                typical_range=test_data["typical_range"],
                is_active=True
            )
            session.add(test_record)
    
    session.commit()
    count = session.query(MedicalTest).count()
    print(f"✅ Medical tests seeded: {count} total records")


def seed_medications(session):
    """Seed medications table"""
    print("🔄 Seeding medications...")
    
    for med_data in MEDICATIONS_SEED_DATA:
        # Check if medication already exists
        existing = session.query(Medication).filter(Medication.medication_name == med_data["medication_name"]).first()
        if not existing:
            medication_record = Medication(
                medication_name=med_data["medication_name"],
                generic_name=med_data["generic_name"],
                brand_names=med_data["brand_names"],
                drug_class=med_data["drug_class"],
                typical_dosage=med_data["typical_dosage"],
                contraindications=med_data["contraindications"],
                side_effects=med_data["side_effects"],
                is_active=True
            )
            session.add(medication_record)
    
    session.commit()
    count = session.query(Medication).count()
    print(f"✅ Medications seeded: {count} total records")


def main():
    """Main seeding function"""
    print("🚀 Starting database seeding...")
    print("=" * 50)
    
    try:
        session = create_seeding_session()
        
        # Seed all tables
        seed_icd10_codes(session)
        seed_medical_tests(session)
        seed_medications(session)
        
        session.close()
        
        print("=" * 50)
        print("✅ Database seeding completed successfully!")
        print("\n📊 Final counts:")
        
        # Verify final counts
        session = create_seeding_session()
        icd10_count = session.query(ICD10Code).count()
        tests_count = session.query(MedicalTest).count()
        meds_count = session.query(Medication).count()
        
        print(f"   ICD-10 codes: {icd10_count}")
        print(f"   Medical tests: {tests_count}")
        print(f"   Medications: {meds_count}")
        
        session.close()
        
    except Exception as e:
        print(f"❌ Error during seeding: {e}")
        if 'session' in locals():
            session.rollback()
            session.close()
        raise


if __name__ == "__main__":
    main()