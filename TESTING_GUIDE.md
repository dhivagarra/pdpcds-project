"""
Testing the Clinical Decision Support System - Working Commands
===============================================================
"""

# Test 1: Start Server (Run this first)
# -------------------------------------
C:\Users\Babu\Documents\WORKAREA\pdpcds-project\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000

# Test 2: Direct API Documentation (Open in Browser)
# -------------------------------------------------
# http://127.0.0.1:8000/docs

# Test 3: PowerShell Test Commands
# --------------------------------

# Test Health Check
Invoke-WebRequest -Uri "http://127.0.0.1:8000/health" -Method GET

# Test Feedback API (This will create a mock prediction if needed)
$feedbackData = @'
{
  "prediction_id": 1,
  "doctor_id": "DR001", 
  "prediction_accurate": true,
  "confidence_in_feedback": 0.95
}
'@

Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/v1/feedback/prediction-feedback" -Method POST -ContentType "application/json" -Body $feedbackData

# Test 4: CURL Commands (Alternative)
# -----------------------------------

curl -X POST "http://127.0.0.1:8000/api/v1/feedback/prediction-feedback" \
  -H "Content-Type: application/json" \
  -d '{
    "prediction_id": 1,
    "doctor_id": "DR001",
    "prediction_accurate": true, 
    "confidence_in_feedback": 0.95
  }'

# Expected Response:
# {
#   "message": "Feedback submitted successfully",
#   "feedback_id": 1,
#   "training_data_added": true,
#   "total_feedback_for_prediction": 1,
#   "prediction_accuracy_rate": 1.0
# }