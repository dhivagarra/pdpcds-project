-- Database initialization script
-- Creates basic tables and inserts reference data

-- Create ICD-10 codes table and insert sample data
INSERT INTO icd10_codes (code, description, category) VALUES
('J18.9', 'Pneumonia, unspecified organism', 'Respiratory'),
('R50.9', 'Fever, unspecified', 'Symptoms'),
('M79.3', 'Panniculitis, unspecified', 'Musculoskeletal'),
('K59.00', 'Constipation, unspecified', 'Digestive'),
('R06.02', 'Shortness of breath', 'Respiratory'),
('R51', 'Headache', 'Neurological'),
('J06.9', 'Acute upper respiratory infection, unspecified', 'Respiratory'),
('K21.9', 'Gastro-esophageal reflux disease without esophagitis', 'Digestive'),
('M25.50', 'Pain in unspecified joint', 'Musculoskeletal'),
('R11.10', 'Vomiting, unspecified', 'Digestive');

-- Create medical tests table and insert sample data
INSERT INTO medical_tests (test_name, test_code, description, category) VALUES
('Chest X-ray (PA/AP)', '71020', 'Posteroanterior and lateral chest X-ray', 'Imaging'),
('Complete Blood Count (CBC)', '85025', 'Complete blood count with differential', 'Laboratory'),
('Basic Metabolic Panel', '80048', 'Basic metabolic panel (8 tests)', 'Laboratory'),
('Urinalysis', '81001', 'Urinalysis with microscopy', 'Laboratory'),
('ECG (12-lead)', '93000', 'Electrocardiogram, 12-lead', 'Cardiac'),
('Blood Culture', '87040', 'Blood culture for bacteria', 'Laboratory'),
('CT Chest without contrast', '71250', 'CT scan of chest without contrast', 'Imaging'),
('Lipid Panel', '80061', 'Lipid panel with total cholesterol', 'Laboratory'),
('Thyroid Function Tests', '84439', 'Thyroid stimulating hormone (TSH)', 'Laboratory'),
('Liver Function Tests', '80076', 'Hepatic function panel', 'Laboratory');

-- Create medications table and insert sample data
INSERT INTO medications (medication_name, generic_name, drug_class, typical_dosage) VALUES
('Amoxicillin-clavulanate', 'Amoxicillin-clavulanate', 'Antibiotic', '500 mg PO TID'),
('Acetaminophen', 'Acetaminophen', 'Analgesic/Antipyretic', '650 mg PO q6h PRN'),
('Ibuprofen', 'Ibuprofen', 'NSAID', '400 mg PO q6h PRN'),
('Azithromycin', 'Azithromycin', 'Antibiotic', '250 mg PO daily'),
('Omeprazole', 'Omeprazole', 'PPI', '20 mg PO daily'),
('Lisinopril', 'Lisinopril', 'ACE Inhibitor', '10 mg PO daily'),
('Metformin', 'Metformin', 'Antidiabetic', '500 mg PO BID'),
('Albuterol inhaler', 'Albuterol', 'Bronchodilator', '2 puffs q4-6h PRN'),
('Loratadine', 'Loratadine', 'Antihistamine', '10 mg PO daily'),
('Simvastatin', 'Simvastatin', 'Statin', '20 mg PO daily');