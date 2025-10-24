# Clinical Decision Support System - Complete API Testing Guide
# ============================================================

# Step 1: Start the server
# ------------------------
# Run this command in PowerShell:
# C:\Users\Babu\Documents\WORKAREA\pdpcds-project\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

# Step 2: Test Prediction API (Get a prediction ID first)
# -------------------------------------------------------
$predictionData = Get-Content "test_data_default.json" -Raw
$predictionResponse = Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/v1/predict/" -Method POST -ContentType "application/json" -Body $predictionData
Write-Host "Prediction Response Status:" $predictionResponse.StatusCode
Write-Host "Prediction Response:" $predictionResponse.Content

# Step 3: Test Positive Feedback (Prediction was correct)
# -------------------------------------------------------
$feedbackPositive = Get-Content "test_feedback_positive.json" -Raw
$feedbackResponse1 = Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/v1/feedback/prediction-feedback" -Method POST -ContentType "application/json" -Body $feedbackPositive
Write-Host "Positive Feedback Status:" $feedbackResponse1.StatusCode
Write-Host "Positive Feedback Response:" $feedbackResponse1.Content

# Step 4: Test Negative Feedback (Prediction was wrong)
# -----------------------------------------------------
$feedbackNegative = Get-Content "test_feedback_negative.json" -Raw
$feedbackResponse2 = Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/v1/feedback/prediction-feedback" -Method POST -ContentType "application/json" -Body $feedbackNegative
Write-Host "Negative Feedback Status:" $feedbackResponse2.StatusCode
Write-Host "Negative Feedback Response:" $feedbackResponse2.Content

# Step 5: Test Minimal Feedback (Required fields only)
# ----------------------------------------------------
$feedbackMinimal = Get-Content "test_feedback_minimal.json" -Raw
$feedbackResponse3 = Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/v1/feedback/prediction-feedback" -Method POST -ContentType "application/json" -Body $feedbackMinimal
Write-Host "Minimal Feedback Status:" $feedbackResponse3.StatusCode
Write-Host "Minimal Feedback Response:" $feedbackResponse3.Content

# Step 6: Get Feedback Statistics
# -------------------------------
$statsResponse = Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/v1/feedback/feedback-stats" -Method GET
Write-Host "Stats Response Status:" $statsResponse.StatusCode
Write-Host "Stats Response:" $statsResponse.Content

# Step 7: Test Health Check
# -------------------------
$healthResponse = Invoke-WebRequest -Uri "http://127.0.0.1:8000/health" -Method GET
Write-Host "Health Check Status:" $healthResponse.StatusCode
Write-Host "Health Check Response:" $healthResponse.Content

# Step 8: View API Documentation
# ------------------------------
# Open browser to: http://127.0.0.1:8000/docs