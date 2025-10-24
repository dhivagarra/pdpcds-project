#!/usr/bin/env python3
"""
Script to check database table population
"""
from app.database import engine
from sqlalchemy import text

def check_table_counts():
    """Check how many records are in each reference table"""
    with engine.connect() as conn:
        # Check ICD10 codes
        icd10_result = conn.execute(text('SELECT COUNT(*) FROM icd10_codes'))
        icd10_count = icd10_result.scalar()
        
        # Check medical tests
        tests_result = conn.execute(text('SELECT COUNT(*) FROM medical_tests'))
        tests_count = tests_result.scalar()
        
        # Check medications
        meds_result = conn.execute(text('SELECT COUNT(*) FROM medications'))
        meds_count = meds_result.scalar()
        
        # Check predictions 
        pred_result = conn.execute(text('SELECT COUNT(*) FROM predictions'))
        pred_count = pred_result.scalar()
        
        print("=== DATABASE TABLE COUNTS ===")
        print(f"ICD-10 codes: {icd10_count}")
        print(f"Medical tests: {tests_count}")
        print(f"Medications: {meds_count}")
        print(f"Predictions: {pred_count}")
        
        if icd10_count == 0 and tests_count == 0 and meds_count == 0:
            print("\n❌ ISSUE: All reference tables are empty!")
        else:
            print("\n✅ Some reference data exists")

if __name__ == "__main__":
    check_table_counts()