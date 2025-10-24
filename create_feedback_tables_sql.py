#!/usr/bin/env python3
"""
Create feedback tables directly using SQL
"""

import sqlite3
import os

def create_feedback_tables():
    """Create clinical feedback and outcome tables"""
    
    db_path = "pdpcds_dev.db"
    if not os.path.exists(db_path):
        print(f"❌ Database file not found: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Create clinical_feedback table
        print("Creating clinical_feedback table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS clinical_feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prediction_id INTEGER NOT NULL,
                doctor_id VARCHAR NOT NULL,
                doctor_name VARCHAR,
                hospital_unit VARCHAR,
                prediction_accurate BOOLEAN NOT NULL,
                confidence_in_feedback FLOAT NOT NULL,
                actual_disease_id INTEGER,
                actual_condition_name VARCHAR,
                ordered_tests TEXT,  -- JSON array
                prescribed_medications TEXT,  -- JSON array
                clinical_notes TEXT,
                outcome_notes TEXT,
                feedback_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (prediction_id) REFERENCES predictions (id)
            )
        """)
        
        # Create indexes for clinical_feedback
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_clinical_feedback_prediction_id ON clinical_feedback (prediction_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_clinical_feedback_doctor_id ON clinical_feedback (doctor_id)")
        
        print("✅ clinical_feedback table created")
        
        # Create clinical_outcomes table
        print("Creating clinical_outcomes table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS clinical_outcomes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prediction_id INTEGER NOT NULL,
                patient_outcome VARCHAR NOT NULL,
                final_diagnosis_id INTEGER NOT NULL,
                final_condition_name VARCHAR NOT NULL,
                treatment_effective BOOLEAN NOT NULL,
                side_effects TEXT,  -- JSON array
                diagnosis_confirmation_days INTEGER,
                treatment_duration_days INTEGER,
                readmission_required BOOLEAN DEFAULT FALSE,
                complications TEXT,  -- JSON array
                reported_by VARCHAR NOT NULL,
                outcome_date TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (prediction_id) REFERENCES predictions (id)
            )
        """)
        
        # Create indexes for clinical_outcomes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_clinical_outcomes_prediction_id ON clinical_outcomes (prediction_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_clinical_outcomes_outcome_date ON clinical_outcomes (outcome_date)")
        
        print("✅ clinical_outcomes table created")
        
        # Commit changes
        conn.commit()
        
        # Verify tables were created
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = cursor.fetchall()
        print(f"\n📋 All tables in database:")
        for table in tables:
            print(f"  - {table[0]}")
        
        # Check if our new tables are there
        table_names = [table[0] for table in tables]
        if 'clinical_feedback' in table_names and 'clinical_outcomes' in table_names:
            print("\n🎉 Feedback tables created successfully!")
        else:
            print("\n❌ Some tables were not created")
            
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        conn.rollback()
        
    finally:
        conn.close()

if __name__ == "__main__":
    create_feedback_tables()