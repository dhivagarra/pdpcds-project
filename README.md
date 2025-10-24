# Preliminary Disease Prediction and Clinical Decision Support (ICD-10)

A web-based clinical decision support system that predicts preliminary diseases and generates ICD-10 codes, recommended tests, medications, and dynamic assessment plans using machine learning.

## Technology Stack

- **Backend**: Python, FastAPI
- **Machine Learning**: PyTorch
- **Database**: PostgreSQL
- **API**: JSON-based schema
- **Deployment**: FastAPI model serving

## Project Structure

```
pdpcds-project/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration settings
│   ├── database.py          # Database connection and setup
│   ├── models/              # Database models
│   ├── schemas/             # Pydantic schemas
│   ├── api/                 # API endpoints
│   ├── ml/                  # Machine learning components
│   └── utils/               # Utility functions
├── data/                    # Training data and datasets
├── models/                  # Trained ML models
├── tests/                   # Test cases
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variables template
├── docker-compose.yml      # Docker setup
└── README.md               # This file
```

## Features

- Multi-task ML model for disease prediction, test recommendation, and medication suggestion
- ICD-10 code mapping and classification
- Confidence scoring and explainable AI rationale
- RESTful API with JSON input/output
- PostgreSQL database for data management
- Real-time prediction serving

## Setup Instructions

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up PostgreSQL database
4. Configure environment variables
5. Run the application: `uvicorn app.main:app --reload`

## API Endpoints

- `POST /predict` - Disease prediction and recommendations
- `GET /health` - Health check endpoint
- `GET /docs` - Interactive API documentation

## Input Format

```json
{
  "age": 54,
  "sex": "female",
  "vital_temperature_c": 38.2,
  "vital_heart_rate": 110,
  "symptom_list": ["fever", "productive cough"],
  "pmh_list": ["hypertension"],
  "free_text_notes": "Patient reports 3 days of worsening cough."
}
```

## Output Format

```json
{
  "predictions": [
    {
      "icd10_code": "J18.9",
      "diagnosis": "Pneumonia, unspecified organism",
      "confidence": 0.82,
      "recommended_tests": [{"test": "Chest X-ray (PA/AP)", "confidence": 0.9}],
      "recommended_medications": [{"medication": "Amoxicillin-clavulanate", "confidence": 0.78, "dose_suggestion": "500 mg PO TID"}],
      "assessment_plan": "Likely community-acquired pneumonia. Obtain chest x-ray and CBC; start empiric oral antibiotics considering allergy history.",
      "rationale": ["Fever (38.2°C)", "Productive cough with purulent sputum", "Elevated heart rate"]
    }
  ],
  "generated_at": "2025-10-14T12:34:56+05:30"
}
```

## Development

- Use `pytest` for testing
- Follow PEP 8 style guidelines
- Document all functions and classes
- Maintain high test coverage

## License

This project is for educational and research purposes only. Not intended for clinical use without proper validation and regulatory approval.