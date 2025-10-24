# CURL Commands for Testing Clinical Decision Support System
# =========================================================

# 1. Test Health Check
curl -X GET "http://127.0.0.1:8000/health"

# 2. Test Prediction API
curl -X POST "http://127.0.0.1:8000/api/v1/predict/" \
  -H "Content-Type: application/json" \
  -d @test_data_default.json

# 3. Test Doctor Feedback - Correct Prediction
curl -X POST "http://127.0.0.1:8000/api/v1/feedback/prediction-feedback" \
  -H "Content-Type: application/json" \
  -d @test_feedback_positive.json

# 4. Test Doctor Feedback - Incorrect Prediction
curl -X POST "http://127.0.0.1:8000/api/v1/feedback/prediction-feedback" \
  -H "Content-Type: application/json" \
  -d @test_feedback_negative.json

# 5. Get Feedback Statistics
curl -X GET "http://127.0.0.1:8000/api/v1/feedback/feedback-stats"

# 6. View API Documentation
# Browser: http://127.0.0.1:8000/docs