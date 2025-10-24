# 📚 Clinical Decision Support System - Complete API Documentation & Testing Guide

## 🎯 API Overview

The Clinical Decision Support System provides a comprehensive REST API for disease prediction, clinical feedback, and continuous learning. This documentation covers all endpoints with detailed testing examples.

**Base URL**: `http://127.0.0.1:8000` (Development)  
**API Version**: v1  
**Content-Type**: `application/json` for all POST requests

---

## 📋 Quick Reference

### Endpoint Categories

| Category | Endpoints | Purpose |
|----------|-----------|---------|
| **Health & Status** | 3 | System health monitoring |
| **Disease Prediction** | 1 | AI-powered medical predictions |
| **Clinical Feedback** | 6 | Doctor feedback & continuous learning |
| **Documentation** | 2 | Interactive API docs |

### Response Codes

| Code | Meaning | Usage |
|------|---------|-------|
| `200` | Success | Request processed successfully |
| `400` | Bad Request | Invalid input data or missing fields |
| `404` | Not Found | Resource or endpoint not found |
| `422` | Validation Error | Pydantic schema validation failed |
| `500` | Server Error | Internal server error |

---

## 🏥 1. Health & Monitoring Endpoints

### 1.1 Basic Health Check

**Endpoint**: `GET /health`  
**Purpose**: Quick system health verification

**Request:**
```bash
curl -X GET "http://127.0.0.1:8000/health"
```

**PowerShell:**
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/health" -Method GET
```

**Expected Response:**
```json
{
  "status": "healthy",
  "service": "Preliminary Disease Prediction and Clinical Decision Support",
  "version": "1.0.0"
}
```

**Testing Notes:**
- ✅ Should return 200 status
- ✅ Verifies basic API connectivity
- ✅ No authentication required

### 1.2 Detailed Health Check

**Endpoint**: `GET /api/v1/health/`  
**Purpose**: Comprehensive system status

**Request:**
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/health/"
```

**Expected Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-20T10:30:00Z",
  "version": "1.0.0",
  "database": "connected",
  "ml_model": "loaded",
  "uptime_seconds": 3600
}
```

### 1.3 Database Health Check

**Endpoint**: `GET /api/v1/health/database`  
**Purpose**: Database connectivity verification

**Request:**
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/health/database"
```

**Expected Response:**
```json
{
  "status": "healthy",
  "database": "connected",
  "database_type": "sqlite",
  "test_query": "successful",
  "timestamp": "2025-10-20T21:10:47.032239"
}
```

---

## 🧠 2. Disease Prediction API

### 2.1 Submit Prediction Request

**Endpoint**: `POST /api/v1/predict/`  
**Purpose**: Generate disease predictions with AI/ML model

#### Request Schema
```json
{
  "age": "integer (required) - Patient age",
  "sex": "string (required) - 'male', 'female', or 'other'", 
  "vital_temperature_c": "float (optional) - Body temperature in Celsius",
  "vital_heart_rate": "integer (optional) - Heart rate in BPM",
  "vital_blood_pressure_systolic": "integer (optional) - Systolic BP",
  "vital_blood_pressure_diastolic": "integer (optional) - Diastolic BP",
  "symptom_list": "array[string] (required) - List of symptoms",
  "pmh_list": "array[string] (optional) - Past medical history",
  "current_medications": "array[string] (optional) - Current medications",
  "allergies": "array[string] (optional) - Known allergies",
  "chief_complaint": "string (optional) - Primary complaint",
  "free_text_notes": "string (optional) - Additional clinical notes"
}
```

#### Test Case 1: Complete Clinical Scenario

**Request:**
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/predict/" \
  -H "Content-Type: application/json" \
  -d '{
    "age": 45,
    "sex": "female",
    "vital_temperature_c": 38.5,
    "vital_heart_rate": 95,
    "vital_blood_pressure_systolic": 140,
    "vital_blood_pressure_diastolic": 90,
    "symptom_list": ["fever", "cough", "shortness of breath", "fatigue"],
    "pmh_list": ["hypertension", "diabetes type 2"],
    "current_medications": ["lisinopril", "metformin"],
    "allergies": ["penicillin"],
    "chief_complaint": "Cough and fever for 4 days",
    "free_text_notes": "Patient reports productive cough with yellow sputum, worsening over past 4 days. No recent travel."
  }'
```

**PowerShell:**
```powershell
$body = @{
    age = 45
    sex = "female"
    vital_temperature_c = 38.5
    vital_heart_rate = 95
    vital_blood_pressure_systolic = 140
    vital_blood_pressure_diastolic = 90
    symptom_list = @("fever", "cough", "shortness of breath", "fatigue")
    pmh_list = @("hypertension", "diabetes type 2")
    current_medications = @("lisinopril", "metformin")
    allergies = @("penicillin")
    chief_complaint = "Cough and fever for 4 days"
    free_text_notes = "Patient reports productive cough with yellow sputum"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/predict/" -Method POST -ContentType "application/json" -Body $body
```

#### Test Case 2: Minimal Required Data

**Request:**
```json
{
  "age": 35,
  "sex": "male",
  "symptom_list": ["headache"]
}
```

#### Test Case 3: Pediatric Case

**Request:**
```json
{
  "age": 8,
  "sex": "female", 
  "vital_temperature_c": 39.2,
  "vital_heart_rate": 120,
  "symptom_list": ["fever", "sore throat", "difficulty swallowing"],
  "pmh_list": [],
  "chief_complaint": "High fever and sore throat"
}
```

#### Expected Response Format
```json
{
  "predictions": [
    {
      "icd10_code": "J18.9",
      "diagnosis": "Pneumonia, unspecified organism",
      "confidence": 0.82,
      "recommended_tests": [
        {
          "test": "Chest X-ray (PA/AP)",
          "confidence": 0.9,
          "urgency": "routine",
          "rationale": "Evaluate for pneumonia"
        },
        {
          "test": "Complete Blood Count (CBC)",
          "confidence": 0.8,
          "urgency": "routine"
        }
      ],
      "recommended_medications": [
        {
          "medication": "Amoxicillin-clavulanate",
          "confidence": 0.78,
          "dose_suggestion": "500 mg PO TID",
          "duration": "7-10 days",
          "contraindication_check": true
        }
      ],
      "assessment_plan": "Likely community-acquired pneumonia. Obtain chest x-ray and CBC; start empiric oral antibiotics considering allergy history.",
      "rationale": [
        "Fever (38.5°C) with respiratory symptoms",
        "Productive cough with purulent sputum",
        "Clinical presentation consistent with pneumonia"
      ],
      "risk_factors": [
        "Age > 40",
        "Diabetes mellitus",
        "Hypertension"
      ],
      "differential_diagnoses": [
        "Acute bronchitis",
        "Upper respiratory infection",
        "COVID-19"
      ]
    }
  ],
  "model_version": "v1.0",
  "processing_time_ms": 34.5,
  "confidence_threshold": 0.5,
  "generated_at": "2025-10-20T10:45:30Z",
  "clinical_warnings": [
    "This is a preliminary assessment tool only",
    "Always consider patient history and clinical context",
    "Confirm diagnoses with appropriate diagnostic tests"
  ],
  "disclaimer": "This system provides preliminary predictions for educational and clinical decision support purposes. Always consult with healthcare professionals for final clinical decisions."
}
```

---

## 👩‍⚕️ 3. Clinical Feedback API

### 3.1 Submit Doctor Feedback on Prediction

**Endpoint**: `POST /api/v1/feedback/prediction-feedback`  
**Purpose**: Record doctor feedback on AI predictions for continuous learning

#### Request Schema
```json
{
  "prediction_id": "integer (required) - ID of the prediction being reviewed",
  "doctor_id": "string (required) - Doctor's unique identifier",
  "doctor_name": "string (optional) - Doctor's full name",
  "hospital_unit": "string (optional) - Department/unit name",
  "prediction_accurate": "boolean (required) - Was the prediction correct?",
  "confidence_in_feedback": "float (required) - Doctor's confidence (0.0-1.0)",
  "actual_disease_id": "integer (optional) - Correct disease ID if prediction wrong",
  "actual_condition_name": "string (optional) - Correct condition name",
  "ordered_tests": "array[string] (optional) - Tests actually ordered",
  "prescribed_medications": "array[string] (optional) - Medications prescribed",
  "clinical_notes": "string (optional) - Clinical documentation",
  "outcome_notes": "string (optional) - Patient outcome notes"
}
```

#### Test Case 1: Positive Feedback (Accurate Prediction)

**Request:**
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/feedback/prediction-feedback" \
  -H "Content-Type: application/json" \
  -d '{
    "prediction_id": 123,
    "doctor_id": "DR001",
    "doctor_name": "Dr. Sarah Johnson",
    "hospital_unit": "Emergency Department",
    "prediction_accurate": true,
    "confidence_in_feedback": 0.95,
    "ordered_tests": ["chest_xray", "cbc", "blood_culture"],
    "prescribed_medications": ["amoxicillin_clavulanate", "acetaminophen"],
    "clinical_notes": "Prediction was accurate. Patient responded well to suggested antibiotic therapy. Chest X-ray confirmed pneumonia.",
    "outcome_notes": "Patient improved significantly after 48 hours of treatment. Discharged home on day 3."
  }'
```

#### Test Case 2: Corrective Feedback (Inaccurate Prediction)

**Request:**
```json
{
  "prediction_id": 124,
  "doctor_id": "DR002",
  "doctor_name": "Dr. Michael Chen",
  "hospital_unit": "Internal Medicine",
  "prediction_accurate": false,
  "confidence_in_feedback": 0.90,
  "actual_disease_id": 15,
  "actual_condition_name": "Acute Bronchitis",
  "ordered_tests": ["chest_xray", "sputum_culture"],
  "prescribed_medications": ["azithromycin", "dextromethorphan"],
  "clinical_notes": "Initial prediction of pneumonia was incorrect. Chest X-ray was clear. Clinical presentation more consistent with acute bronchitis.",
  "outcome_notes": "Patient responded well to bronchodilator and antibiotic. Symptoms resolved within 5 days."
}
```

#### Test Case 3: Low Confidence Feedback

**Request:**
```json
{
  "prediction_id": 125,
  "doctor_id": "DR003",
  "prediction_accurate": true,
  "confidence_in_feedback": 0.60,
  "clinical_notes": "Uncertain about diagnosis. Need additional testing to confirm.",
  "outcome_notes": "Awaiting further test results."
}
```

**Expected Response:**
```json
{
  "message": "Feedback submitted successfully",
  "feedback_id": 456,
  "training_data_added": true,
  "training_record_id": 789,
  "total_feedback_for_prediction": 3,
  "prediction_accuracy_rate": 0.87
}
```

### 3.2 Submit Clinical Outcome

**Endpoint**: `POST /api/v1/feedback/clinical-outcome`  
**Purpose**: Record final patient outcomes for treatment effectiveness

#### Request Schema
```json
{
  "prediction_id": "integer (required) - ID of the original prediction",
  "patient_outcome": "string (required) - Final patient outcome",
  "final_diagnosis_id": "integer (required) - Final confirmed diagnosis ID",
  "final_condition_name": "string (required) - Final confirmed condition name",
  "treatment_effective": "boolean (required) - Was the treatment effective?",
  "side_effects": "array[string] (optional) - Any side effects observed",
  "diagnosis_confirmation_days": "integer (optional) - Days to confirm diagnosis",
  "treatment_duration_days": "integer (optional) - Duration of treatment in days",
  "readmission_required": "boolean (optional) - Was readmission required?",
  "complications": "array[string] (optional) - Any complications that occurred",
  "reported_by": "string (required) - Who reported the outcome",
  "outcome_date": "string (required) - Date of outcome assessment (ISO format)"
}
```

#### Test Case 1: Successful Treatment Outcome

**Request:**
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/feedback/clinical-outcome" \
  -H "Content-Type: application/json" \
  -d '{
    "prediction_id": 1,
    "patient_outcome": "fully_recovered",
    "final_diagnosis_id": 5,
    "final_condition_name": "Community-acquired pneumonia",
    "treatment_effective": true,
    "side_effects": ["mild nausea"],
    "diagnosis_confirmation_days": 2,
    "treatment_duration_days": 7,
    "readmission_required": false,
    "complications": [],
    "reported_by": "DR001",
    "outcome_date": "2025-10-21T10:00:00.000Z"
  }'
```

**PowerShell:**
```powershell
$outcomeBody = @{
    prediction_id = 1
    patient_outcome = "fully_recovered"
    final_diagnosis_id = 5
    final_condition_name = "Community-acquired pneumonia"
    treatment_effective = $true
    side_effects = @("mild nausea")
    diagnosis_confirmation_days = 2
    treatment_duration_days = 7
    readmission_required = $false
    complications = @()
    reported_by = "DR001"
    outcome_date = "2025-10-21T10:00:00.000Z"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/feedback/clinical-outcome" -Method POST -ContentType "application/json" -Body $outcomeBody
```

#### Test Case 2: Treatment with Complications

**Request:**
```json
{
  "prediction_id": 2,
  "patient_outcome": "improved_with_complications",
  "final_diagnosis_id": 12,
  "final_condition_name": "Pneumonia with pleural effusion",
  "treatment_effective": true,
  "side_effects": ["antibiotic-associated diarrhea"],
  "diagnosis_confirmation_days": 3,
  "treatment_duration_days": 14,
  "readmission_required": true,
  "complications": ["pleural effusion", "secondary infection"],
  "reported_by": "DR002",
  "outcome_date": "2025-10-21T15:30:00.000Z"
}
```

#### Test Case 3: Unsuccessful Treatment

**Request:**
```json
{
  "prediction_id": 3,
  "patient_outcome": "no_improvement",
  "final_diagnosis_id": 8,
  "final_condition_name": "Drug-resistant pneumonia",
  "treatment_effective": false,
  "side_effects": ["severe nausea", "allergic reaction"],
  "diagnosis_confirmation_days": 5,
  "treatment_duration_days": 10,
  "readmission_required": true,
  "complications": ["treatment resistance", "adverse drug reaction"],
  "reported_by": "DR003",
  "outcome_date": "2025-10-21T20:45:00.000Z"
}
```

**Expected Response:**
```json
{
  "message": "Clinical outcome submitted successfully",
  "outcome_id": 123,
  "prediction_id": 1
}
```

#### Error Responses:

**404 - Prediction Not Found:**
```json
{
  "detail": "Prediction with ID 999 not found"
}
```

**422 - Validation Error (Missing Required Field):**
```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "reported_by"],
      "msg": "Field required",
      "input": { "prediction_id": 7485, "patient_outcome": "improved", ... },
      "url": "https://errors.pydantic.dev/2.5/v/missing"
    }
  ]
}
```

**Solution**: Add the missing `reported_by` field to your request:
```json
{
  "prediction_id": 7485,
  "patient_outcome": "improved",
  "final_diagnosis_id": 1,
  "final_condition_name": "Confirmed diagnosis",
  "treatment_effective": true,
  "side_effects": [],
  "diagnosis_confirmation_days": 1,
  "treatment_duration_days": 7,
  "readmission_required": false,
  "complications": [],
  "reported_by": "DR001",
  "outcome_date": "2025-10-21T05:18:07Z"
}
```

### 3.3 Add Expert Training Data

**Endpoint**: `POST /api/v1/feedback/add-training-data`  
**Purpose**: Manually add high-quality training cases

**Request:**
```json
{
  "age": 55,
  "sex": "male",
  "vital_temperature_c": 37.8,
  "vital_heart_rate": 88,
  "symptom_list": ["chest pain", "shortness of breath"],
  "target_disease": 8,
  "target_tests": [2, 5, 7],
  "target_medications": [3, 9],
  "condition_name": "Myocardial Infarction",
  "chief_complaint": "Acute chest pain",
  "quality_score": 0.95,
  "created_by": "DR001"
}
```

### 3.4 Get Feedback for Prediction

**Endpoint**: `GET /api/v1/feedback/prediction/{prediction_id}/feedback`  
**Purpose**: Retrieve all feedback for a specific prediction

**Request:**
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/feedback/prediction/123/feedback"
```

**Expected Response:**
```json
[
  {
    "prediction_id": 123,
    "doctor_id": "DR001",
    "doctor_name": "Dr. Sarah Johnson",
    "prediction_accurate": true,
    "confidence_in_feedback": 0.95,
    "clinical_notes": "Accurate prediction",
    "feedback_timestamp": "2025-10-20T10:30:00Z"
  }
]
```

### 3.5 Get Feedback Summary

**Endpoint**: `GET /api/v1/feedback/prediction/{prediction_id}/summary`  
**Purpose**: Get consensus summary for a prediction

**Request:**
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/feedback/prediction/123/summary"
```

**Expected Response:**
```json
{
  "prediction_id": 123,
  "total_feedback_count": 3,
  "accuracy_rate": 0.67,
  "consensus_reached": true,
  "average_confidence": 0.85,
  "most_common_actual_diagnosis": "Pneumonia"
}
```

### 3.6 Get Feedback Statistics

**Endpoint**: `GET /api/v1/feedback/feedback-stats`  
**Purpose**: System-wide feedback statistics

**Request:**
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/feedback/feedback-stats"
```

**Expected Response:**
```json
{
  "total_feedback_submissions": 1250,
  "overall_accuracy_rate": 0.78,
  "high_confidence_feedback_count": 980,
  "training_data_generated": 850,
  "average_doctor_confidence": 0.82,
  "most_accurate_predictions": [
    {"condition": "Pneumonia", "accuracy": 0.91},
    {"condition": "Hypertension", "accuracy": 0.88}
  ]
}
```

---

## 📖 4. Documentation Endpoints

### 4.1 Interactive API Documentation (Swagger UI)

**Endpoint**: `GET /docs`  
**Purpose**: Interactive API explorer

**Usage:**
```
Open in browser: http://127.0.0.1:8000/docs
```

**Features:**
- ✅ Interactive API testing
- ✅ Request/response examples
- ✅ Schema validation
- ✅ Authentication testing (when implemented)

### 4.2 Alternative Documentation (ReDoc)

**Endpoint**: `GET /redoc`  
**Purpose**: Clean, readable API documentation

**Usage:**
```
Open in browser: http://127.0.0.1:8000/redoc
```

**Features:**
- ✅ Clean, professional layout
- ✅ Downloadable OpenAPI spec
- ✅ Code examples in multiple languages

---

## 🧪 5. Complete Testing Workflows

### Workflow 1: Basic System Verification

```bash
# 1. Check system health
curl -X GET "http://127.0.0.1:8000/health"

# 2. Test prediction API
curl -X POST "http://127.0.0.1:8000/api/v1/predict/" \
  -H "Content-Type: application/json" \
  -d '{"age": 40, "sex": "male", "symptom_list": ["headache"]}'

# 3. Submit feedback (use prediction_id from step 2)
curl -X POST "http://127.0.0.1:8000/api/v1/feedback/prediction-feedback" \
  -H "Content-Type: application/json" \
  -d '{"prediction_id": 1, "doctor_id": "DR001", "prediction_accurate": true, "confidence_in_feedback": 0.8}'
```

### Workflow 2: Complete Clinical Scenario

```bash
# 1. Submit complex clinical case
curl -X POST "http://127.0.0.1:8000/api/v1/predict/" \
  -H "Content-Type: application/json" \
  -d @test_data_complete.json

# 2. Doctor reviews and confirms prediction
curl -X POST "http://127.0.0.1:8000/api/v1/feedback/prediction-feedback" \
  -H "Content-Type: application/json" \
  -d @test_feedback_positive.json

# 3. Record final patient outcome
curl -X POST "http://127.0.0.1:8000/api/v1/feedback/clinical-outcome" \
  -H "Content-Type: application/json" \
  -d '{
    "prediction_id": 1,
    "patient_outcome": "fully_recovered",
    "final_diagnosis_id": 5,
    "final_condition_name": "Community-acquired pneumonia",
    "treatment_effective": true,
    "side_effects": ["mild nausea"],
    "reported_by": "DR001",
    "outcome_date": "2025-10-21T10:00:00.000Z"
  }'

# 4. Check feedback statistics
curl -X GET "http://127.0.0.1:8000/api/v1/feedback/feedback-stats"
```

### Workflow 3: Error Handling Testing

```bash
# Test invalid data
curl -X POST "http://127.0.0.1:8000/api/v1/predict/" \
  -H "Content-Type: application/json" \
  -d '{"age": "invalid", "symptom_list": []}'  # Should return 422

# Test missing required fields
curl -X POST "http://127.0.0.1:8000/api/v1/predict/" \
  -H "Content-Type: application/json" \
  -d '{"sex": "male"}'  # Missing age and symptom_list

# Test non-existent prediction feedback
curl -X POST "http://127.0.0.1:8000/api/v1/feedback/prediction-feedback" \
  -H "Content-Type: application/json" \
  -d '{"prediction_id": 99999, "doctor_id": "DR001", "prediction_accurate": true, "confidence_in_feedback": 0.8}'
```

---

## 📊 6. Performance Testing

### Load Testing with curl

```bash
# Test concurrent requests (run multiple terminals)
for i in {1..10}; do
  curl -X POST "http://127.0.0.1:8000/api/v1/predict/" \
    -H "Content-Type: application/json" \
    -d '{"age": 30, "sex": "female", "symptom_list": ["fever"]}' &
done
wait
```

### PowerShell Performance Test

```powershell
# Test API response times
$stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
$response = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/predict/" -Method POST -ContentType "application/json" -Body '{"age": 35, "sex": "male", "symptom_list": ["headache"]}'
$stopwatch.Stop()
Write-Host "Response time: $($stopwatch.ElapsedMilliseconds)ms"
```

---

## 🔧 7. Test Data Files

### test_data_complete.json
```json
{
  "age": 67,
  "sex": "male",
  "vital_temperature_c": 38.9,
  "vital_heart_rate": 105,
  "vital_blood_pressure_systolic": 160,
  "vital_blood_pressure_diastolic": 95,
  "symptom_list": ["chest pain", "shortness of breath", "diaphoresis", "nausea"],
  "pmh_list": ["coronary artery disease", "hypertension", "hyperlipidemia"],
  "current_medications": ["atorvastatin", "lisinopril", "aspirin"],
  "allergies": ["codeine"],
  "chief_complaint": "Acute chest pain for 2 hours",
  "free_text_notes": "Patient reports crushing substernal chest pain radiating to left arm, associated with diaphoresis and nausea. Pain started at rest."
}
```

### test_feedback_positive.json  
```json
{
  "prediction_id": 1,
  "doctor_id": "DR001",
  "doctor_name": "Dr. Sarah Johnson",
  "hospital_unit": "Emergency Department",
  "prediction_accurate": true,
  "confidence_in_feedback": 0.95,
  "ordered_tests": ["ecg", "troponins", "chest_xray"],
  "prescribed_medications": ["aspirin", "atorvastatin", "metoprolol"],
  "clinical_notes": "Prediction was accurate. ECG showed ST elevation, troponins elevated. Diagnosed with STEMI.",
  "outcome_notes": "Patient underwent successful PCI. Good outcome with full recovery."
}
```

### test_outcome.json
```json
{
  "prediction_id": 1,
  "patient_outcome": "excellent_recovery",
  "final_diagnosis_id": 12,
  "final_condition_name": "ST-elevation myocardial infarction",
  "treatment_effective": true,
  "side_effects": [],
  "diagnosis_confirmation_days": 0,
  "treatment_duration_days": 5,
  "readmission_required": false,
  "complications": [],
  "reported_by": "DR001",
  "outcome_date": "2025-10-21T00:00:00Z"
}
```

---

## ⚠️ 8. Common Issues & Troubleshooting

### Issue 1: API Server Not Running
**Error**: `Connection refused` or `ConnectionError`
**Solution**: 
```bash
cd c:\Users\Babu\Documents\WORKAREA\pdpcds-project
.\.venv\Scripts\uvicorn.exe app.main:app --reload
```

### Issue 2: 422 Validation Error
**Error**: `422 Unprocessable Entity`
**Cause**: Invalid request data format
**Solution**: Check request schema and ensure all required fields are provided

### Issue 3: 500 Internal Server Error
**Error**: `500 Internal Server Error`
**Cause**: Server-side issue (database connection, model loading, etc.)
**Solution**: Check server logs and ensure database is accessible

### Issue 4: Missing Required Field Error (422)
**Error**: `422 Unprocessable Entity` with "Field required" message
**Cause**: Required field missing from request body (e.g., `reported_by` in clinical outcome)
**Solution**: Check the request schema and add all required fields:

```json
{
  "prediction_id": 7485,
  "patient_outcome": "improved",
  "final_diagnosis_id": 1,
  "final_condition_name": "Confirmed diagnosis",
  "treatment_effective": true,
  "reported_by": "DR001",
  "outcome_date": "2025-10-21T05:18:07Z"
}
```

### Issue 5: Database Schema Mismatch Error (500)
**Error**: `500 Internal Server Error` with message about missing columns (e.g., "table clinical_outcomes has no column named feedback_id")
**Cause**: Model definition doesn't match actual database table structure
**Solution**: The model has been updated to match the actual table structure. If you still see this error:

1. Check if the server has been restarted after the model update
2. Ensure all required fields are provided in the request
3. Verify the database tables are properly created

**Fixed Model Structure**: The `ClinicalOutcomeRecord` model now matches the actual database table with fields like `patient_outcome`, `final_diagnosis_id`, etc.

### Issue 6: pydantic_settings ModuleNotFoundError
**Error**: `ModuleNotFoundError: No module named 'pydantic_settings'`
**Solution**: Use virtual environment uvicorn:
```bash
.\.venv\Scripts\uvicorn.exe app.main:app --reload
```

---

## 🎯 9. Success Criteria

### API Health Verification
- ✅ `/health` returns 200 with `"status": "healthy"`
- ✅ All endpoints respond within < 100ms for simple requests
- ✅ Database connections successful

### Prediction API Testing  
- ✅ Valid prediction requests return 200 with proper JSON structure
- ✅ Invalid requests return 422 with validation errors
- ✅ Predictions include ICD-10 codes, confidence scores, and recommendations

### Feedback API Testing
- ✅ Feedback submissions return 200 with confirmation
- ✅ High-confidence feedback creates training data
- ✅ Feedback statistics update correctly

### Performance Benchmarks
- ✅ Prediction API: < 50ms average response time
- ✅ Feedback API: < 100ms average response time  
- ✅ Concurrent requests: Support 10+ simultaneous users
- ✅ Database operations: 100% success rate

---

## 📈 10. Monitoring & Analytics

### Key Metrics to Track
- **API Response Times**: Monitor prediction and feedback endpoint performance
- **Prediction Accuracy**: Track doctor feedback and correction rates
- **Training Data Growth**: Monitor automatic training data generation
- **Database Performance**: Query times and connection health
- **Error Rates**: Track 4xx and 5xx error frequencies

### Recommended Monitoring Tools
- **Development**: Built-in FastAPI metrics and logging
- **Production**: Prometheus + Grafana for comprehensive monitoring
- **Log Analysis**: Structured logging with request tracing

---

**Document Version**: 1.0  
**Created**: October 20, 2025  
**Author**: PDPCDS Development Team  
**Status**: Comprehensive API Testing Documentation Complete

**🚀 Ready for comprehensive API testing and validation!**