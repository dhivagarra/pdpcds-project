#!/usr/bin/env python3
"""
Debug script to check preprocessor dimensions
"""
import json
import pickle
from app.ml.preprocessor import DataPreprocessor

# Load test data
with open('test_data_pneumonia.json', 'r') as f:
    test_data = json.load(f)

print("🔍 Testing preprocessor dimensions...")

# Test default preprocessor
print("\n1. Default Preprocessor:")
default_preprocessor = DataPreprocessor()
try:
    result = default_preprocessor.preprocess_input(test_data)
    print(f"   Output shape: {result.shape}")
    print(f"   Feature dim: {default_preprocessor.get_feature_dim()}")
except Exception as e:
    print(f"   Error: {e}")

# Test trained preprocessor
print("\n2. Trained Preprocessor:")
try:
    with open('./models/preprocessor.pkl', 'rb') as f:
        trained_preprocessor = pickle.load(f)
    
    result = trained_preprocessor.preprocess_input(test_data)
    print(f"   Output shape: {result.shape}")
    print(f"   Feature dim: {trained_preprocessor.get_feature_dim()}")
    print(f"   Is fitted: {trained_preprocessor.is_fitted}")
except Exception as e:
    print(f"   Error: {e}")

print("\n✅ Dimension analysis complete!")