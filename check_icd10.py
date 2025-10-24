"""
Simple ICD-10 table checker
"""
import sqlite3

def check_icd10_table():
    try:
        conn = sqlite3.connect('pdpcds_dev.db')
        cursor = conn.cursor()
        
        # Check ICD-10 codes table
        cursor.execute("SELECT COUNT(*) FROM icd10_codes")
        count = cursor.fetchone()[0]
        print(f"📊 ICD-10 codes in database: {count}")
        
        if count > 0:
            cursor.execute("SELECT * FROM icd10_codes LIMIT 10")
            rows = cursor.fetchall()
            print("\n📋 Sample ICD-10 codes:")
            for row in rows:
                print(f"   ID: {row[0]}, Code: {row[1]}, Description: {row[2]}")
        else:
            print("❌ No ICD-10 codes found in database")
            
        # Check medical tests table
        cursor.execute("SELECT COUNT(*) FROM medical_tests")
        test_count = cursor.fetchone()[0]
        print(f"\n🧪 Medical tests in database: {test_count}")
        
        # Check medications table  
        cursor.execute("SELECT COUNT(*) FROM medications")
        med_count = cursor.fetchone()[0]
        print(f"💊 Medications in database: {med_count}")
        
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_icd10_table()