"""
Clinical Predictor - Main interface for disease prediction and recommendations
"""

import os
import json
from typing import Dict, List, Any
import torch
import numpy as np
from datetime import datetime
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from app.ml.model import ClinicalDecisionModel
from app.ml.preprocessor import DataPreprocessor
from app.schemas import DiseasePrediction, TestRecommendation, MedicationRecommendation
from app.models import ICD10Code, MedicalTest, Medication
from app.config import settings


class ClinicalPredictor:
    """
    Main predictor class that orchestrates the ML pipeline
    """
    
    def __init__(self, model_path: str = "./models/", model_version: str = "v1.0"):
        self.model_path = model_path
        self.model_version = model_version
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # Initialize database session
        engine = create_engine(settings.database_url)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        self.db_session = SessionLocal()
        
        # Initialize components
        self.preprocessor = DataPreprocessor()
        self.model = None
        
        # Load reference data from database
        self.icd10_mapping = self._load_icd10_mapping_from_db()
        self.test_mapping = self._load_test_mapping_from_db()
        self.medication_mapping = self._load_medication_mapping_from_db()
        
        # Load model if available, otherwise use dummy predictions
        self._load_model()
    
    def _load_model(self):
        """
        Load the trained PyTorch model
        """
        model_file = os.path.join(self.model_path, f"clinical_model_{self.model_version}.pth")
        
        if os.path.exists(model_file):
            try:
                # Load model
                self.model = ClinicalDecisionModel()
                self.model.load_state_dict(torch.load(model_file, map_location=self.device))
                self.model.to(self.device)
                self.model.eval()
                print(f"Loaded model from {model_file}")
            except Exception as e:
                print(f"Error loading model: {e}")
                self.model = None
        else:
            print(f"Model file not found: {model_file}")
            print("Using dummy predictions for demonstration")
            self.model = None
    
    def _load_icd10_mapping_from_db(self) -> Dict[int, Dict[str, str]]:
        """
        Load ICD-10 code mapping from database
        """
        try:
            icd10_codes = self.db_session.query(ICD10Code).filter(ICD10Code.is_active == True).all()
            mapping = {}
            for idx, icd10 in enumerate(icd10_codes):
                mapping[idx] = {
                    "code": icd10.code,
                    "description": icd10.description,
                    "category": icd10.category
                }
            print(f"Loaded {len(mapping)} ICD-10 codes from database")
            return mapping
        except Exception as e:
            print(f"Error loading ICD-10 codes from database: {e}")
            # Fallback to minimal hardcoded mapping
            return {
                0: {"code": "J18.9", "description": "Pneumonia, unspecified organism", "category": "Respiratory"},
                1: {"code": "R50.9", "description": "Fever, unspecified", "category": "Symptoms"},
                2: {"code": "R51", "description": "Headache", "category": "Symptoms"},
                3: {"code": "R69", "description": "Illness, unspecified", "category": "Symptoms"}
            }
11: {"code": "A15.7 ", "description": " Primary respiratory tuberculosis"},
12: {"code": "A15.8 ", "description": " Other respiratory tuberculosis"},
13: {"code": "A15.9 ", "description": " Respiratory tuberculosis unspecified"},
14: {"code": "B38.1 ", "description": " Chronic pulmonary coccidioidomycosis"},
15: {"code": "B39.1 ", "description": " Chronic pulmonary histoplasmosis capsulati"},
16: {"code": "B40.1 ", "description": " Chronic pulmonary blastomycosis"},
17: {"code": "E08.0 ", "description": " Diabetes due to underlying condition with hyperosmolarity without nonketotic hyperglycemic hyperosmolar coma"},
18: {"code": "E08.1 ", "description": " Diabetes due to underlying condition with hyperosmolarity with coma"},
19: {"code": "E08.10 ", "description": " Diabetes due to underlying condition with ketoacidosis without coma"},
20: {"code": "E08.11 ", "description": " Diabetes due to underlying condition with ketoacidosis with coma"},
21: {"code": "E08.21 ", "description": " Diabetes due to underlying condition with diabetic nephropathy"},
22: {"code": "E08.22 ", "description": " Diabetes due to underlying condition with diabetic chronic kidney disease"},
23: {"code": "E08.29 ", "description": " Diabetes due to underlying condition with other diabetic kidney complication"},
24: {"code": "E08.311 ", "description": " Diabetes due to underlying condition with unspecified diabetic retinopathy with macular edema"},
25: {"code": "E08.319 ", "description": " Diabetes due to underlying condition with unspecified diabetic retinopathy without macular edema"},
26: {"code": "E08.321 ", "description": " Diabetes due to underlying condition with mild nonproliferative diabetic retinopathy with macular edema"},
27: {"code": "E08.329 ", "description": " Diabetes due to underlying condition with mild nonproliferative diabetic retinopathy without macular edema"},
28: {"code": "E08.331 ", "description": " Diabetes due to underlying condition with moderate nonproliferative diabetic retinopathy with macular edema"},
29: {"code": "E08.339 ", "description": " Diabetes due to underlying condition with moderate nonproliferative diabetic retinopathy without macular edema"},
30: {"code": "E08.341 ", "description": " Diabetes due to underlying condition with severe nonproliferative diabetic retinopathy with macular edema"},
31: {"code": "E08.349 ", "description": " Diabetes due to underlying condition with severe nonproliferative diabetic retinopathy without macular edema"},
32: {"code": "E08.351 ", "description": " Diabetes due to underlying condition with proliferative diabetic retinopathy with macular edema"},
33: {"code": "E08.359 ", "description": " Diabetes due to underlying condition with proliferative diabetic retinopathy without macular edema"},
34: {"code": "E08.36 ", "description": " Diabetes due to underlying condition with diabetic cataract"},
35: {"code": "E08.39 ", "description": " Diabetes due to underlying condition with other diabetic opthalmic complication"},
36: {"code": "E08.40 ", "description": " Diabetes due to underlying condition with diabetic neuropathy, unspecified"},
37: {"code": "E08.41 ", "description": " Diabetes due to underlying condition with diabetic mononeuropathy"},
38: {"code": "E08.42 ", "description": " Diabetes due to underlying condition with diabetic polyneuropathy"},
39: {"code": "E08.43 ", "description": " Diabetes due to underlying condition with diabetic autonomic (poly)neuropathy"},
40: {"code": "E08.44 ", "description": " Diabetes due to underlying condition with diabetic amyotrophy"},
41: {"code": "E08.49 ", "description": " Diabetes due to underlying condition with other diabetic neuro complications"},
42: {"code": "E08.51 ", "description": " Diabetes due to underlying condition with diabetes peripheral angiopathy without gangrene"},
43: {"code": "E08.52 ", "description": " Diabetes due to underlying condition with diabetic peripheral angiopathy with gangrene"},
44: {"code": "E08.59 ", "description": " Diabetes due to underlying condition with other circulatory complication"},
45: {"code": "E08.610 ", "description": " Diabetes due to underlying condition with diabetic neuropathic arthropathy"},
46: {"code": "E08.618 ", "description": " Diabetes due to underlying condition with other diabetic arthropathy"},
47: {"code": "E08.620 ", "description": " Diabetes due to underlying condition with diabetic dermatitis"},
48: {"code": "E08.621 ", "description": " Diabetes mellitus due to underlying condition with foot ulcer"},
49: {"code": "E08.622 ", "description": " Diabetes due to underlying condition with other skin ulcer"},
50: {"code": "E08.628 ", "description": " Diabetes due to underlying condition with other skin complication"},
51: {"code": "E08.630 ", "description": " Diabetes due to underlying condition with periodontal disease"},
52: {"code": "E08.638 ", "description": " Diabetes due to underlying condition with other oral complication"},
53: {"code": "E08.641 ", "description": " Diabetes due to underlying condition with hypoglycemia with coma"},
54: {"code": "E08.649 ", "description": " Diabetes due to underlying condition with hypoglycemia without coma"},
55: {"code": "E08.65 ", "description": " Diabetes due to underlying condition with hyperglycemia"},
56: {"code": "E08.69 ", "description": " Diabetes due to underlying condition with other complication"},
57: {"code": "E08.8 ", "description": " Diabetes due to underlying condition with unspecified complications"},
58: {"code": "E08.9 ", "description": " Diabetes due to underlying condition without complications"},
59: {"code": "E09.0 ", "description": " Drug/chemical diabetes with hyperosmolarity without nonketotic hyperglycemichyperosmolar coma"},
60: {"code": "E09.1 ", "description": " Drug/chemical diabetes mellitus with hyperosmolarity with coma"},
61: {"code": "E09.10 ", "description": " Drug/chemical diabetes mellitus with ketoacidosis without coma"},
62: {"code": "E09.11 ", "description": " Drug/chemical diabetes mellitus with ketoacidosis with coma"},
63: {"code": "E09.21 ", "description": " Drug/chemical diabetes mellitus with diabetic nephropathy"},
64: {"code": "E09.22 ", "description": " Drug/chemical diabetes with diabetic chronic kidney disease"},
65: {"code": "E09.29 ", "description": " Drug/chemical diabetes with other diabetic kidney complication"},
66: {"code": "E09.311 ", "description": " Drug/chemical diabetes with unspecified diabetic retinopathy with macular edema"},
67: {"code": "E09.319 ", "description": " Drug/chemical diabetes with unspecified diabetic retinopathy without macular edema"},
68: {"code": "E09.321 ", "description": " Drug/chemical diabetes with mild nonproliferative diabetic retinopathy with macular edema"},
69: {"code": "E09.329 ", "description": " Drug/chemical diabetes with mild nonproliferative diabetic retinopathy without macular edema"},
70: {"code": "E09.331 ", "description": " Drug/chemical diabetes with moderate nonproliferative diabetic retinopathy with macular edema"},
71: {"code": "E09.339 ", "description": " Drug/chemical diabetes with moderate nonproliferative diabetic retinopathy without macular edema"},
72: {"code": "E09.341 ", "description": " Drug/chemical diabetes with severe nonproliferative diabetic retinopathy with macular edema"},
73: {"code": "E09.349 ", "description": " Drug/chemical diabetes with severe nonproliferative diabetic retinopathy without macular edema"},
74: {"code": "E09.351 ", "description": " Drug/chemical diabetes with proliferative diabetic retinopathy with macular edema"},
75: {"code": "E09.359 ", "description": " Drug/chemical diabetes with proliferative diabetic retinopathy without macular edema"},
76: {"code": "E09.36 ", "description": " Drug/chemical diabetes mellitus with diabetic cataract"},
77: {"code": "E09.39 ", "description": " Drug/chemical diabetes with other diabetic ophthalmic complication"},
78: {"code": "E09.40 ", "description": " Drug/chemical diabetes with neuro complication with diabetic neuropathy, unspecified"},
79: {"code": "E09.41 ", "description": " Drug/chemical diabetes with neuro complication with diabetic mononeuropathy"},
80: {"code": "E09.42 ", "description": " Drug/chemical diabetes with neurological complication with diabetic polyneuropathy"},
81: {"code": "E09.43 ", "description": " Drug/chemical diabetes with neuro complication with diabetes autonomic (poly)neuropathy"},
82: {"code": "E09.44 ", "description": " Drug/chemical diabetes with neurological complication with diabetic amyotrophy"},
83: {"code": "E09.49 ", "description": " Drug/chemical diabetes with neuro complications with other diabetic neuro complications"},
84: {"code": "E09.51 ", "description": " Drug/chemical diabetes with diabetic peripheral angiopathy without gangrene"},
85: {"code": "E09.52 ", "description": " Drug/chemical diabetes with diabetic peripheral angiopathy with gangrene"},
86: {"code": "E09.59 ", "description": " Drug/chemical diabetes mellitus with other circulatory complications"},
87: {"code": "E09.610 ", "description": " Drug/chemical diabetes with diabetic neuropathic arthropathy"},
88: {"code": "E09.618 ", "description": " Drug/chemical diabetes mellitus with other diabetic arthropathy"},
89: {"code": "E09.620 ", "description": " Drug/chemical diabetes mellitus with diabetic dermatitis"},
90: {"code": "E09.621 ", "description": " Drug or chemical induced diabetes mellitus with foot ulcer"},
91: {"code": "E09.622 ", "description": " Drug or chemical induced diabetes mellitus with other skin ulcer"},
92: {"code": "E09.628 ", "description": " Drug/chemical diabetes mellitus with other skin complications"},
93: {"code": "E09.630 ", "description": " Drug/chemical diabetes mellitus with periodontal disease"},
94: {"code": "E09.638 ", "description": " Drug/chemical diabetes mellitus with other oral complications"},
95: {"code": "E09.641 ", "description": " Drug/chemical diabetes mellitus with hypoglycemia with coma"},
96: {"code": "E09.649 ", "description": " Drug/chemical diabetes mellitus with hypoglycemia without coma"},
97: {"code": "E09.65 ", "description": " Drug or chemical induced diabetes mellitus with hyperglycemia"},
98: {"code": "E09.69 ", "description": " Drug/chemical diabetes mellitus with other complication"},
99: {"code": "E09.8 ", "description": " Drug/chemical diabetes mellitus with unspecified complications"},
100: {"code": "E09.9 ", "description": " Drug or chemical induced diabetes mellitus without complications"},
101: {"code": "E10.0 ", "description": " Type 1 diabetes mellitus with coma "},
102: {"code": "E10.1 ", "description": " Type 1 diabetes mellitus with ketoacidosis "},
103: {"code": "E10.10 ", "description": " Type 1 diabetes mellitus with ketoacidosis without coma"},
104: {"code": "E10.11 ", "description": " Type 1 diabetes mellitus with ketoacidosis with coma"},
105: {"code": "E10.2 ", "description": " Type 1 diabetes mellitus with kidney complications"},
106: {"code": "E10.21 ", "description": " Type 1 diabetes mellitus with diabetic nephropathy"},
107: {"code": "E10.22 ", "description": " Type 1 diabetes mellitus with diabetic chronic kidney disease"},
108: {"code": "E10.29 ", "description": " Type 1 diabetes mellitus with other diabetic kidney complication"},
109: {"code": "E10.3 ", "description": " Type 1 diabetes mellitus with ophthalmic complications"},
110: {"code": "E10.311 ", "description": " Type 1 diabetes with unspecified diabetic retinopathy with macular edema"},
111: {"code": "E10.319 ", "description": " Type 1 diabetes with unspecified diabetic retinopathy without macular edema"},
112: {"code": "E10.321 ", "description": " Type 1 diabetes with mild nonproliferative diabetic retinopathy with macular edema"},
113: {"code": "E10.329 ", "description": " Type 1 diabetes with mild nonproliferative diabetic retinopathy without macular edema"},
114: {"code": "E10.331 ", "description": " Type 1 diabetes with moderate nonproliferative diabetic retinopathy with macular edema"},
115: {"code": "E10.339 ", "description": " Type 1 diabetes with moderate nonproliferative diabetic retinopathy without macular edema"},
116: {"code": "E10.341 ", "description": " Type 1 diabetes with severe nonproliferative diabetic retinopathy with macular edema"},
117: {"code": "E10.349 ", "description": " Type 1 diabetes with severe nonproliferative diabetic retinopathy without macular edema"},
118: {"code": "E10.351 ", "description": " Type 1 diabetes with proliferative diabetic retinopathy with macular edema"},
119: {"code": "E10.359 ", "description": " Type 1 diabetes with proliferative diabetic retinopathy without macular edema"},
120: {"code": "E10.36 ", "description": " Type 1 diabetes mellitus with diabetic cataract"},
121: {"code": "E10.39 ", "description": " Type 1 diabetes with other diabetic ophthalmic complication"},
122: {"code": "E10.4 ", "description": " Type 1 diabetes mellitus with neurological complications"},
123: {"code": "E10.40 ", "description": " Type 1 diabetes mellitus with diabetic neuropathy, unsp"},
124: {"code": "E10.41 ", "description": " Type 1 diabetes mellitus with diabetic mononeuropathy"},
125: {"code": "E10.42 ", "description": " Type 1 diabetes mellitus with diabetic polyneuropathy"},
126: {"code": "E10.43 ", "description": " Type 1 diabetes with diabetic autonomic (poly)neuropathy"},
127: {"code": "E10.44 ", "description": " Type 1 diabetes mellitus with diabetic amyotrophy"},
128: {"code": "E10.49 ", "description": " Type 1 diabetes with other diabetic neurological complication"},
129: {"code": "E10.5 ", "description": " Type 1 diabetes mellitus with peripheral circulatory complications"},
130: {"code": "E10.51 ", "description": " Type 1 diabetes with diabetic peripheral angiopathy without gangrene"},
131: {"code": "E10.52 ", "description": " Type 1 diabetes with diabetic peripheral angiopathy with gangrene"},
132: {"code": "E10.59 ", "description": " Type 1 diabetes mellitus with other circulatory complications"},
133: {"code": "E10.6 ", "description": " Type 1 diabetes mellitus with other specified complications"},
134: {"code": "E10.610 ", "description": " Type 1 diabetes mellitus with diabetic neuropathic arthropathy"},
135: {"code": "E10.618 ", "description": " Type 1 diabetes mellitus with other diabetic arthropathy"},
136: {"code": "E10.620 ", "description": " Type 1 diabetes mellitus with diabetic dermatitis"},
137: {"code": "E10.621 ", "description": " Type 1 diabetes mellitus with foot ulcer"},
138: {"code": "E10.622 ", "description": " Type 1 diabetes mellitus with other skin ulcer"},
139: {"code": "E10.628 ", "description": " Type 1 diabetes mellitus with other skin complications"},
140: {"code": "E10.630 ", "description": " Type 1 diabetes mellitus with periodontal disease"},
141: {"code": "E10.638 ", "description": " Type 1 diabetes mellitus with other oral complications"},
142: {"code": "E10.641 ", "description": " Type 1 diabetes mellitus with hypoglycemia with coma"},
143: {"code": "E10.649 ", "description": " Type 1 diabetes mellitus with hypoglycemia without coma"},
144: {"code": "E10.65 ", "description": " Type 1 diabetes mellitus with hyperglycemia"},
145: {"code": "E10.69 ", "description": " Type 1 diabetes mellitus with hyperosmolarity"},
146: {"code": "E10.8 ", "description": " Type 1 diabetes mellitus with unspecified complications"},
147: {"code": "E10.9 ", "description": " Type 1 diabetes mellitus without complications"},
148: {"code": "E11.0 ", "description": " Type 2 diabetes mellitus with coma "},
149: {"code": "E11.1 ", "description": " Type 2 diabetes mellitus with ketoacidosis"},
150: {"code": "E11.2 ", "description": " Type 2 diabetes mellitus with kidney complications"},
151: {"code": "E11.21 ", "description": " Type 2 diabetes mellitus with diabetic nephropathy"},
152: {"code": "E11.22 ", "description": " Type 2 diabetes mellitus with diabetic chronic kidney disease"},
153: {"code": "E11.29 ", "description": " Type 2 diabetes mellitus with other diabetic kidney complication"},
154: {"code": "E11.3 ", "description": " Type 2 diabetes mellitus with ophthalmic complications"},
155: {"code": "E11.311 ", "description": " Type 2 diabetes with unspecified diabetic retinopathy with macular edema"},
156: {"code": "E11.319 ", "description": " Type 2 diabetes with unspecified diabetic retinopathy without macular edema"},
157: {"code": "E11.351 ", "description": " Type 2 diabetes with proliferative diabetic retinopathy with macular edema"},
158: {"code": "E11.359 ", "description": " Type 2 diabetes with proliferative diabetic retinopathy without macular edema"},
159: {"code": "E11.36 ", "description": " Type 2 diabetes mellitus with diabetic cataract"},
160: {"code": "E11.39 ", "description": " Type 2 diabetes with other diabetic ophthalmic complication"},
161: {"code": "E11.4 ", "description": " Type 2 diabetes mellitus with neurological complications"},
162: {"code": "E11.40 ", "description": " Type 2 diabetes mellitus with diabetic neuropathy, unspecified"},
163: {"code": "E11.41 ", "description": " Type 2 diabetes mellitus with diabetic mononeuropathy"},
164: {"code": "E11.42 ", "description": " Type 2 diabetes mellitus with diabetic polyneuropathy"},
165: {"code": "E11.43 ", "description": " Type 2 diabetes with diabetic autonomic (poly)neuropathy"},
166: {"code": "E11.44 ", "description": " Type 2 diabetes mellitus with diabetic amyotrophy"},
167: {"code": "E11.49 ", "description": " Type 2 diabetes with other diabetic neurological complication"},
168: {"code": "E11.5 ", "description": " Type 2 diabetes mellitus with peripheral circulatory complications "},
169: {"code": "E11.51 ", "description": " Type 2 diabetes with diabetic peripheral angiopathy without gangrene"},
170: {"code": "E11.52 ", "description": " Type 2 diabetes with diabetic peripheral angiopathy with gangrene"},
171: {"code": "E11.59 ", "description": " Type 2 diabetes mellitus with other circulatory complications"},
172: {"code": "E11.6 ", "description": " Type 2 diabetes mellitus with other specified complications"},
173: {"code": "E11.610 ", "description": " Type 2 diabetes mellitus with diabetic neuropathic arthropathy"},
174: {"code": "E11.618 ", "description": " Type 2 diabetes mellitus with other diabetic arthropathy"},
175: {"code": "E11.620 ", "description": " Type 2 diabetes mellitus with diabetic dermatitis"},
176: {"code": "E11.621 ", "description": " Type 2 diabetes mellitus with foot ulcer"},
177: {"code": "E11.622 ", "description": " Type 2 diabetes mellitus with other skin ulcer"},
178: {"code": "E11.628 ", "description": " Type 2 diabetes mellitus with other skin complications"},
179: {"code": "E11.630 ", "description": " Type 2 diabetes mellitus with periodontal disease"},
180: {"code": "E11.638 ", "description": " Type 2 diabetes mellitus with other oral complications"},
181: {"code": "E11.641 ", "description": " Type 2 diabetes mellitus with hypoglycemia with coma"},
182: {"code": "E11.649 ", "description": " Type 2 diabetes mellitus with hypoglycemia without coma"},
183: {"code": "E11.65 ", "description": " Type 2 diabetes mellitus with hyperglycemia"},
184: {"code": "E11.69 ", "description": " Type 2 diabetes mellitus with other specified complication"},
185: {"code": "E11.8 ", "description": " Type 2 diabetes mellitus with unspecified complications"},
186: {"code": "E11.9 ", "description": " Type 2 diabetes mellitus without complications"},
187: {"code": "E13.1 ", "description": " Other diabetes mellitus with hyperosmolarity with coma"},
188: {"code": "E13.10 ", "description": " Other diabetes mellitus with ketoacidosis without coma"},
189: {"code": "E13.11 ", "description": " Other diabetes mellitus with ketoacidosis with coma"},
190: {"code": "E13.21 ", "description": " Other specified diabetes mellitus with diabetic nephropathy"},
191: {"code": "E13.22 ", "description": " Other diabetes mellitus with diabetic chronic kidney disease"},
192: {"code": "E13.29 ", "description": " Other diabetes mellitus with other diabetic kidney complication"},
193: {"code": "E13.311 ", "description": " Other diabetes with unspecified diabetic retinopathy with macular edema"},
194: {"code": "E13.319 ", "description": " Other diabetes with unspecified diabetic retinopathy without macular edema"},
195: {"code": "E13.321 ", "description": " Other diabetes with mild nonproliferative diabetic retinopathy with macular edema"},
196: {"code": "E13.329 ", "description": " Other diabetes with mild nonproliferative diabetic retinopathy without macular edema"},
197: {"code": "E13.341 ", "description": " Other diabetes with severe nonproliferative diabetic retinopathy with macular edema"},
198: {"code": "E13.351 ", "description": " Other diabetes with proliferative diabetic retinopathy with macular edema"},
199: {"code": "E13.359 ", "description": " Other diabetes with proliferative diabetic retinopathy without macular edema"},
200: {"code": "E13.36 ", "description": " Other specified diabetes mellitus with diabetic cataract"},
201: {"code": "E13.39 ", "description": " Other diabetes mellitus with other diabetic ophthalmic complication"},
202: {"code": "E13.40 ", "description": " Other diabetes mellitus with diabetic neuropathy, unspecified"},
203: {"code": "E13.41 ", "description": " Other diabetes mellitus with diabetic mononeuropathy"},
204: {"code": "E13.42 ", "description": " Other diabetes mellitus with diabetic polyneuropathy"},
205: {"code": "E13.43 ", "description": " Other diabetes mellitus with diabetic autonomic (poly)neuropathy"},
206: {"code": "E13.44 ", "description": " Other specified diabetes mellitus with diabetic amyotrophy"},
207: {"code": "E13.49 ", "description": " Other diabetes with other diabetic neurological complication"},
208: {"code": "E13.51 ", "description": " Other diabetes with diabetic peripheral angiopathy without gangrene"},
209: {"code": "E13.52 ", "description": " Other diabetes with diabetic peripheral angiopathy with gangrene"},
210: {"code": "E13.59 ", "description": " Other diabetes mellitus with other circulatory complications"},
211: {"code": "E13.610 ", "description": " Other diabetes mellitus with diabetic neuropathic arthropathy"},
212: {"code": "E13.618 ", "description": " Other diabetes mellitus with other diabetic arthropathy"},
213: {"code": "E13.620 ", "description": " Other specified diabetes mellitus with diabetic dermatitis"},
214: {"code": "E13.621 ", "description": " Other specified diabetes mellitus with foot ulcer"},
215: {"code": "E13.622 ", "description": " Other specified diabetes mellitus with other skin ulcer"},
216: {"code": "E13.628 ", "description": " Other diabetes mellitus with other skin complications"},
217: {"code": "E13.630 ", "description": " Other specified diabetes mellitus with periodontal disease"},
218: {"code": "E13.638 ", "description": " Other diabetes mellitus with other oral complications"},
219: {"code": "E13.641 ", "description": " Other diabetes mellitus with hypoglycemia with coma"},
220: {"code": "E13.649 ", "description": " Other diabetes mellitus with hypoglycemia without coma"},
221: {"code": "E13.65 ", "description": " Other specified diabetes mellitus with hyperglycemia"},
222: {"code": "E13.69 ", "description": " Other diabetes mellitus with other specified complication"},
223: {"code": "E13.8 ", "description": " Other diabetes mellitus with unspecified complications"},
224: {"code": "E13.9 ", "description": " Other specified diabetes mellitus without complications"},
225: {"code": "I10 ", "description": " Essential (primary) hypertension"},
226: {"code": "I11 ", "description": " Hypertensive heart disease"},
227: {"code": "I11.0 ", "description": " Hypertensive heart disease with (congestive) heart failure"},
228: {"code": "I11.9 ", "description": " Hypertensive heart disease without (congestive) heart failure "},
229: {"code": "I12 ", "description": " Hypertensive kidney disease"},
230: {"code": "I12.0 ", "description": " Hypertensive chronic kidney disease with stage 5 chronic kidney disease or end stage renal disease"},
231: {"code": "I12.9 ", "description": " Hypertensive chronic kidney disease with stage 1 through stage 4 chronic kidney disease, or unspecified chronic kidney disease"},
232: {"code": "I13 ", "description": " Hypertensive heart AND chronic kidney disease"},
233: {"code": "I13.0 ", "description": " Hypertensive heart and renal disease with (congestive) heart failure "},
234: {"code": "I13.9 ", "description": " Hypertensive heart and renal disease, unspecified"},
235: {"code": "I15 ", "description": " Secondary hypertension (due to another underlying condition)"},
236: {"code": "I27.0 ", "description": " Primary pulmonary hypertension"},
237: {"code": "I27.2 ", "description": " Other secondary pulmonary hypertension"},
238: {"code": "I28.8 ", "description": " Other diseases of pulmonary vessels"},
239: {"code": "I28.9 ", "description": " Disease of pulmonary vessels, unspecified"},
240: {"code": "I37.0 ", "description": " Nonrheumatic pulmonary valve stenosis"},
241: {"code": "I37.1 ", "description": " Nonrheumatic pulmonary valve insufficiency"},
242: {"code": "I37.2 ", "description": " Nonrheumatic pulmonary valve stenosis with insufficiency"},
243: {"code": "I37.8 ", "description": " Other nonrheumatic pulmonary valve disorders"},
244: {"code": "I37.9 ", "description": " Nonrheumatic pulmonary valve disorder, unspecified"},
245: {"code": "I50.1 ", "description": " Left ventricular failure, unspecified"},
246: {"code": "I50.20 ", "description": " Systolic (congestive) heart failure"},
247: {"code": "I50.21 ", "description": " Acute systolic (congestive) heart failure"},
248: {"code": "I50.22 ", "description": " Chronic systolic (congestive) heart failure"},
249: {"code": "I50.23 ", "description": " Acute on chronic systolic (congestive) heart failure"},
250: {"code": "I50.30 ", "description": " Diastolic (congestive) heart failure"},
251: {"code": "I50.31 ", "description": " Acute diastolic (congestive) heart failure"},
252: {"code": "I50.32 ", "description": " Chronic diastolic (congestive) heart failure"},
253: {"code": "I50.33 ", "description": " Acute on chronic diastolic (congestive) heart failure"},
254: {"code": "I50.40 ", "description": " Combined systolic (congestive) and diastolic (congestive) heart failure"},
255: {"code": "I50.41 ", "description": " Acute combined systolic and diastolic (congestive) heart failure"},
256: {"code": "I50.42 ", "description": " Chronic combined systolic and diastolic heart failure"},
257: {"code": "I50.43 ", "description": " Acute on chronic combined systolic and diastolic heart failure"},
258: {"code": "I50.810 ", "description": " Right heart failure, unspecified"},
259: {"code": "I50.811 ", "description": " Acute right heart failure"},
260: {"code": "I50.812 ", "description": " Chronic right heart failure"},
261: {"code": "I50.813 ", "description": " Acute on chronic right heart failure"},
262: {"code": "I50.814 ", "description": " Right heart failure due to left heart failure"},
263: {"code": "I50.82 ", "description": " Biventricular heart failure"},
264: {"code": "I50.83 ", "description": " High output heart failure"},
265: {"code": "I50.84 ", "description": " End stage heart failure"},
266: {"code": "I50.89 ", "description": " Other heart failure"},
267: {"code": "I50.9 ", "description": " Heart failure, unspecified"},
268: {"code": "J40. ", "description": " Bronchitis, not specified as acute or chronic"},
269: {"code": "J41.0 ", "description": " Simple chronic bronchitis"},
270: {"code": "J41.1 ", "description": " Mucopurulent chronic bronchitis"},
271: {"code": "J41.8 ", "description": " Mixed simple and mucopurulent chronic bronchitis"},
272: {"code": "J42 ", "description": " Unspecified chronic bronchitis"},
273: {"code": "J43.0 ", "description": " Unilateral pulmonary emphysema [MacLeod's syndrome]"},
274: {"code": "J43.1 ", "description": " Panlobular emphysema"},
275: {"code": "J43.2 ", "description": " Centrilobular emphysema"},
276: {"code": "J43.8 ", "description": " Other emphysema"},
277: {"code": "J43.9 ", "description": " Emphysema, unspecified"},
278: {"code": "J44.0 ", "description": " Chronic obstructive pulmonary disease with acute lower respiratory infection"},
279: {"code": "J44.1 ", "description": " Chronic obstructive pulmonary disease with acute exacerbation, unspecified "},
280: {"code": "J44.9 ", "description": " Chronic obstructive pulmonary disease, unspecified"},
281: {"code": "J45.0 ", "description": " Predominantly allergic asthma"},
282: {"code": "J45.1 ", "description": " Nonallergic asthma  "},
283: {"code": "J45.2 ", "description": " Mild intermittent asthma"},
284: {"code": "J45.20 ", "description": " Mild intermittent asthma, uncomplicated"},
285: {"code": "J45.21 ", "description": " Mild intermittent asthma with (acute) exacerbation"},
286: {"code": "J45.22 ", "description": " Mild intermittent asthma with status asthmaticus"},
287: {"code": "J45.3 ", "description": " Mild persistent asthma"},
288: {"code": "J45.30 ", "description": " Mild persistent asthma, uncomplicated"},
289: {"code": "J45.31 ", "description": " Mild persistent asthma with (acute) exacerbation"},
290: {"code": "J45.32 ", "description": " Mild persistent asthma with status asthmaticus"},
291: {"code": "J45.4 ", "description": " Moderate persistent asthma"},
292: {"code": "J45.40 ", "description": " Moderate persistent asthma, uncomplicated"},
293: {"code": "J45.41 ", "description": " Moderate persistent asthma with (acute) exacerbation"},
294: {"code": "J45.42 ", "description": " Moderate persistent asthma with status asthmaticus"},
295: {"code": "J45.50 ", "description": " Severe persistent asthma, uncomplicated"},
296: {"code": "J45.51 ", "description": " Severe persistent asthma with (acute) exacerbation"},
297: {"code": "J45.52 ", "description": " Severe persistent asthma with status asthmaticus"},
298: {"code": "J45.9 ", "description": " Other and unspecified asthma"},
299: {"code": "J45.901 ", "description": " Unspecified asthma with (acute) exacerbation"},
300: {"code": "J45.902 ", "description": " Unspecified asthma with status asthmaticus"},
301: {"code": "J45.909 ", "description": " Unspecified asthma, uncomplicated "},
302: {"code": "J45.990 ", "description": " Exercise induced bronchospasm"},
303: {"code": "J45.991 ", "description": " Cough variant asthma"},
304: {"code": "J45.998 ", "description": " Other asthma"},
305: {"code": "J47.0 ", "description": " Bronchiectasis with acute lower respiratory infection"},
306: {"code": "J47.1 ", "description": " Bronchiectasis with (acute) exacerbation"},
307: {"code": "J47.9 ", "description": " Bronchiectasis, uncomplicated"},
308: {"code": "J68.4 ", "description": " Chronic respiratory condition due to chemicals, gases, fumes and vapors"},
309: {"code": "J70.1 ", "description": " Chronic and other pulmonary manifestations due to radiation"},
310: {"code": "J70.3 ", "description": " Chronic druginduced interstitial lung disorders"},
311: {"code": "J81.1 ", "description": " Chronic pulmonary edema"},
312: {"code": "J82. ", "description": " Pulmonary eosinophilia, not elsewhere classified"},
313: {"code": "J84.10 ", "description": " Pulmonary fibrosis, unspecified"},
314: {"code": "J84.112 ", "description": " Idiopathic pulmonary fibrosis"},
315: {"code": "J84.115 ", "description": " Respiratory bronchiolitis interstitial lung disease"},
316: {"code": "J84.2 ", "description": " Pulmonary alveolar microlithiasis"},
317: {"code": "J84.3 ", "description": " Idiopathic pulmonary hemosiderosis"},
318: {"code": "J84.82 ", "description": " Adult pulmonary Langerhans cell histiocytosis"},
319: {"code": "J84.842 ", "description": " Pulmonary interstitial glycogenosis"},
320: {"code": "J84.89 ", "description": " Other specified interstitial pulmonary diseases"},
321: {"code": "J84.9 ", "description": " Interstitial pulmonary disease, unspecified"},
322: {"code": "J95.3 ", "description": " Chronic pulmonary insufficiency following surgery"},
323: {"code": "J95.822 ", "description": " Acute and chronic postprocedural respiratory failure"},
324: {"code": "J96.10 ", "description": " Chronic respiratory failure, unspecified with hypoxia or hypercapnia"},
325: {"code": "J96.11 ", "description": " Chronic respiratory failure with hypoxia"},
326: {"code": "J96.12 ", "description": " Chronic respiratory failure with hypercapnia"},
327: {"code": "J96.21 ", "description": " Acute and chronic respiratory failure with hypoxia"},
328: {"code": "J96.22 ", "description": " Acute and chronic respiratory failure with hypercapnia"},
329: {"code": "J98.19 ", "description": " Other pulmonary collapse"},
330: {"code": "J98.2 ", "description": " Interstitial emphysema"},
331: {"code": "J98.3 ", "description": " Compensatory emphysema"},
332: {"code": "K62.6 ", "description": " Ulcer of anus and rectum"},
333: {"code": "L89.0 ", "description": " Pressure ulcer of unspecified elbow, unstageable"},
334: {"code": "L89.10 ", "description": " Pressure ulcer of right elbow, unstageable"},
335: {"code": "L89.100 ", "description": " Pressure ulcer of unspecified part of back, unstageable"},
336: {"code": "L89.102 ", "description": " Pressure ulcer of unspecified part of back, stage 2"},
337: {"code": "L89.103 ", "description": " Pressure ulcer of unspecified part of back, stage 3"},
338: {"code": "L89.104 ", "description": " Pressure ulcer of unspecified part of back, stage 4"},
339: {"code": "L89.109 ", "description": " Pressure ulcer of unspecified part of back, unspecified stage"},
340: {"code": "L89.110 ", "description": " Pressure ulcer of right upper back, unstageable"},
341: {"code": "L89.112 ", "description": " Pressure ulcer of right upper back, stage 2"},
342: {"code": "L89.113 ", "description": " Pressure ulcer of right upper back, stage 3"},
343: {"code": "L89.114 ", "description": " Pressure ulcer of right upper back, stage 4"},
344: {"code": "L89.119 ", "description": " Pressure ulcer of right upper back, unspecified stage"},
345: {"code": "L89.12 ", "description": " Pressure ulcer of right elbow, stage 2"},
346: {"code": "L89.120 ", "description": " Pressure ulcer of left upper back, unstageable"},
347: {"code": "L89.122 ", "description": " Pressure ulcer of left upper back, stage 2"},
348: {"code": "L89.123 ", "description": " Pressure ulcer of left upper back, stage 3"},
349: {"code": "L89.124 ", "description": " Pressure ulcer of left upper back, stage 4"},
350: {"code": "L89.129 ", "description": " Pressure ulcer of left upper back, unspecified stage"},
351: {"code": "L89.13 ", "description": " Pressure ulcer of right elbow, stage 3"},
352: {"code": "L89.130 ", "description": " Pressure ulcer of right lower back, unstageable"},
353: {"code": "L89.132 ", "description": " Pressure ulcer of right lower back, stage 2"},
354: {"code": "L89.133 ", "description": " Pressure ulcer of right lower back, stage 3"},
355: {"code": "L89.134 ", "description": " Pressure ulcer of right lower back, stage 4"},
356: {"code": "L89.139 ", "description": " Pressure ulcer of right lower back, unspecified stage"},
357: {"code": "L89.14 ", "description": " Pressure ulcer of right elbow, stage 4"},
358: {"code": "L89.140 ", "description": " Pressure ulcer of left lower back, unstageable"},
359: {"code": "L89.142 ", "description": " Pressure ulcer of left lower back, stage 2"},
360: {"code": "L89.143 ", "description": " Pressure ulcer of left lower back, stage 3"},
361: {"code": "L89.144 ", "description": " Pressure ulcer of left lower back, stage 4"},
362: {"code": "L89.149 ", "description": " Pressure ulcer of left lower back, unspecified stage"},
363: {"code": "L89.150 ", "description": " Pressure ulcer of sacral region, unstageable"},
364: {"code": "L89.152 ", "description": " Pressure ulcer of sacral region, stage 2"},
365: {"code": "L89.153 ", "description": " Pressure ulcer of sacral region, stage 3"},
366: {"code": "L89.154 ", "description": " Pressure ulcer of sacral region, stage 4"},
367: {"code": "L89.159 ", "description": " Pressure ulcer of sacral region, unspecified stage"},
368: {"code": "L89.19 ", "description": " Pressure ulcer of right elbow, unspecified stage"},
369: {"code": "L89.2 ", "description": " Pressure ulcer of unspecified elbow, stage 2"},
370: {"code": "L89.20 ", "description": " Pressure ulcer of left elbow, unstageable"},
371: {"code": "L89.200 ", "description": " Pressure ulcer of unspecified hip, unstageable"},
372: {"code": "L89.202 ", "description": " Pressure ulcer of unspecified hip, stage 2"},
373: {"code": "L89.203 ", "description": " Pressure ulcer of unspecified hip, stage 3"},
374: {"code": "L89.204 ", "description": " Pressure ulcer of unspecified hip, stage 4"},
375: {"code": "L89.209 ", "description": " Pressure ulcer of unspecified hip, unspecified stage"},
376: {"code": "L89.210 ", "description": " Pressure ulcer of right hip, unstageable"},
377: {"code": "L89.212 ", "description": " Pressure ulcer of right hip, stage 2"},
378: {"code": "L89.213 ", "description": " Pressure ulcer of right hip, stage 3"},
379: {"code": "L89.214 ", "description": " Pressure ulcer of right hip, stage 4"},
380: {"code": "L89.219 ", "description": " Pressure ulcer of right hip, unspecified stage"},
381: {"code": "L89.22 ", "description": " Pressure ulcer of left elbow, stage 2"},
382: {"code": "L89.220 ", "description": " Pressure ulcer of left hip, unstageable"},
383: {"code": "L89.222 ", "description": " Pressure ulcer of left hip, stage 2"},
384: {"code": "L89.223 ", "description": " Pressure ulcer of left hip, stage 3"},
385: {"code": "L89.224 ", "description": " Pressure ulcer of left hip, stage 4"},
386: {"code": "L89.229 ", "description": " Pressure ulcer of left hip, unspecified stage"},
387: {"code": "L89.23 ", "description": " Pressure ulcer of left elbow, stage 3"},
388: {"code": "L89.24 ", "description": " Pressure ulcer of left elbow, stage 4"},
389: {"code": "L89.29 ", "description": " Pressure ulcer of left elbow, unspecified stage"},
390: {"code": "L89.3 ", "description": " Pressure ulcer of unspecified elbow, stage 3"},
391: {"code": "L89.300 ", "description": " Pressure ulcer of unspecified buttock, unstageable"},
392: {"code": "L89.302 ", "description": " Pressure ulcer of unspecified buttock, stage 2"},
393: {"code": "L89.303 ", "description": " Pressure ulcer of unspecified buttock, stage 3"},
394: {"code": "L89.304 ", "description": " Pressure ulcer of unspecified buttock, stage 4"},
395: {"code": "L89.309 ", "description": " Pressure ulcer of unspecified buttock, unspecified stage"},
396: {"code": "L89.310 ", "description": " Pressure ulcer of right buttock, unstageable"},
397: {"code": "L89.312 ", "description": " Pressure ulcer of right buttock, stage 2"},
398: {"code": "L89.313 ", "description": " Pressure ulcer of right buttock, stage 3"},
399: {"code": "L89.314 ", "description": " Pressure ulcer of right buttock, stage 4"},
400: {"code": "L89.319 ", "description": " Pressure ulcer of right buttock, unspecified stage"},
401: {"code": "L89.320 ", "description": " Pressure ulcer of left buttock, unstageable"},
402: {"code": "L89.322 ", "description": " Pressure ulcer of left buttock, stage 2"},
403: {"code": "L89.323 ", "description": " Pressure ulcer of left buttock, stage 3"},
404: {"code": "L89.324 ", "description": " Pressure ulcer of left buttock, stage 4"},
405: {"code": "L89.329 ", "description": " Pressure ulcer of left buttock, unspecified stage"},
406: {"code": "L89.4 ", "description": " Pressure ulcer of unspecified elbow, stage 4"},
407: {"code": "L89.40 ", "description": " Pressure ulcer of contiguous site of back, buttock and hip, unspecified stg"},
408: {"code": "L89.42 ", "description": " Pressure ulcer of contiguous site of back, buttock and hip, stage 2"},
409: {"code": "L89.43 ", "description": " Pressure ulcer of contiguous site of back, buttock and hip, stage 3"},
410: {"code": "L89.44 ", "description": " Pressure ulcer of contiguous site of back, buttock and hip, stage 4"},
411: {"code": "L89.45 ", "description": " Pressure ulcer of contiguous site of back,buttock & hip, unstageable"},
412: {"code": "L89.500 ", "description": " Pressure ulcer of unspecified ankle, unstageable"},
413: {"code": "L89.502 ", "description": " Pressure ulcer of unspecified ankle, stage 2"},
414: {"code": "L89.503 ", "description": " Pressure ulcer of unspecified ankle, stage 3"},
415: {"code": "L89.504 ", "description": " Pressure ulcer of unspecified ankle, stage 4"},
416: {"code": "L89.509 ", "description": " Pressure ulcer of unspecified ankle, unspecified stage"},
417: {"code": "L89.510 ", "description": " Pressure ulcer of right ankle, unstageable"},
418: {"code": "L89.512 ", "description": " Pressure ulcer of right ankle, stage 2"},
419: {"code": "L89.513 ", "description": " Pressure ulcer of right ankle, stage 3"},
420: {"code": "L89.514 ", "description": " Pressure ulcer of right ankle, stage 4"},
421: {"code": "L89.519 ", "description": " Pressure ulcer of right ankle, unspecified stage"},
422: {"code": "L89.520 ", "description": " Pressure ulcer of left ankle, unstageable"},
423: {"code": "L89.522 ", "description": " Pressure ulcer of left ankle, stage 2"},
424: {"code": "L89.523 ", "description": " Pressure ulcer of left ankle, stage 3"},
425: {"code": "L89.524 ", "description": " Pressure ulcer of left ankle, stage 4"},
426: {"code": "L89.529 ", "description": " Pressure ulcer of left ankle, unspecified stage"},
427: {"code": "L89.600 ", "description": " Pressure ulcer of unspecified heel, unstageable"},
428: {"code": "L89.602 ", "description": " Pressure ulcer of unspecified heel, stage 2"},
429: {"code": "L89.603 ", "description": " Pressure ulcer of unspecified heel, stage 3"},
430: {"code": "L89.604 ", "description": " Pressure ulcer of unspecified heel, stage 4"},
431: {"code": "L89.609 ", "description": " Pressure ulcer of unspecified heel, unspecified stage"},
432: {"code": "L89.610 ", "description": " Pressure ulcer of right heel, unstageable"},
433: {"code": "L89.612 ", "description": " Pressure ulcer of right heel, stage 2"},
434: {"code": "L89.613 ", "description": " Pressure ulcer of right heel, stage 3"},
435: {"code": "L89.614 ", "description": " Pressure ulcer of right heel, stage 4"},
436: {"code": "L89.619 ", "description": " Pressure ulcer of right heel, unspecified stage"},
437: {"code": "L89.620 ", "description": " Pressure ulcer of left heel, unstageable"},
438: {"code": "L89.622 ", "description": " Pressure ulcer of left heel, stage 2"},
439: {"code": "L89.623 ", "description": " Pressure ulcer of left heel, stage 3"},
440: {"code": "L89.624 ", "description": " Pressure ulcer of left heel, stage 4"},
441: {"code": "L89.629 ", "description": " Pressure ulcer of left heel, unspecified stage"},
442: {"code": "L89.810 ", "description": " Pressure ulcer of head, unstageable"},
443: {"code": "L89.812 ", "description": " Pressure ulcer of head, stage 2"},
444: {"code": "L89.813 ", "description": " Pressure ulcer of head, stage 3"},
445: {"code": "L89.814 ", "description": " Pressure ulcer of head, stage 4"},
446: {"code": "L89.819 ", "description": " Pressure ulcer of head, unspecified stage"},
447: {"code": "L89.890 ", "description": " Pressure ulcer of other site, unstageable"},
448: {"code": "L89.892 ", "description": " Pressure ulcer of other site, stage 2"},
449: {"code": "L89.893 ", "description": " Pressure ulcer of other site, stage 3"},
450: {"code": "L89.894 ", "description": " Pressure ulcer of other site, stage 4"},
451: {"code": "L89.899 ", "description": " Pressure ulcer of other site, unspecified stage"},
452: {"code": "L89.9 ", "description": " Pressure ulcer of unspecified elbow, unspecified stage"},
453: {"code": "L89.90 ", "description": " Pressure ulcer of unspecified site, unspecified stage"},
454: {"code": "L89.92 ", "description": " Pressure ulcer of unspecified site, stage 2"},
455: {"code": "L89.93 ", "description": " Pressure ulcer of unspecified site, stage 3"},
456: {"code": "L89.94 ", "description": " Pressure ulcer of unspecified site, stage 4"},
457: {"code": "L89.95 ", "description": " Pressure ulcer of unspecified site, unstageable"},
458: {"code": "L97.101 ", "description": " Nonpressure chronic ulcer of unspecified thigh limited to breakdown skin"},
459: {"code": "L97.102 ", "description": " Nonpressure chronic ulcer of unspecified thigh with fat layer exposed"},
460: {"code": "L97.103 ", "description": " Nonpressure chronic ulcer of unspecified thigh with necrosis of muscle"},
461: {"code": "L97.104 ", "description": " Nonpressure chronic ulcer of unspecified thigh with necrosis of bone"},
462: {"code": "L97.109 ", "description": " Nonpressure chronic ulcer of unspecified thigh with unspecified severity"},
463: {"code": "L97.111 ", "description": " Nonpressure chronic ulcer of right thigh limited to breakdown skin"},
464: {"code": "L97.112 ", "description": " Nonpressure chronic ulcer of right thigh with fat layer exposed"},
465: {"code": "L97.113 ", "description": " Nonpressure chronic ulcer of right thigh with necrosis of muscle"},
466: {"code": "L97.114 ", "description": " Nonpressure chronic ulcer of right thigh with necrosis of bone"},
467: {"code": "L97.119 ", "description": " Nonpressure chronic ulcer of right thigh with unspecified severity"},
468: {"code": "L97.121 ", "description": " Nonpressure chronic ulcer of left thigh limited to breakdown skin"},
469: {"code": "L97.122 ", "description": " Nonpressure chronic ulcer of left thigh with fat layer exposed"},
470: {"code": "L97.123 ", "description": " Nonpressure chronic ulcer of left thigh with necrosis of muscle"},
471: {"code": "L97.124 ", "description": " Nonpressure chronic ulcer of left thigh with necrosis of bone"},
472: {"code": "L97.129 ", "description": " Nonpressure chronic ulcer of left thigh with unspecified severity"},
473: {"code": "L97.201 ", "description": " Nonpressure chronic ulcer of unspecified calf limited to breakdown skin"},
474: {"code": "L97.202 ", "description": " Nonpressure chronic ulcer of unspecified calf with fat layer exposed"},
475: {"code": "L97.203 ", "description": " Nonpressure chronic ulcer of unspecified calf with necrosis of muscle"},
476: {"code": "L97.204 ", "description": " Nonpressure chronic ulcer of unspecified calf with necrosis of bone"},
477: {"code": "L97.209 ", "description": " Nonpressure chronic ulcer of unspecified calf with unspecified severity"},
478: {"code": "L97.211 ", "description": " Nonpressure chronic ulcer of right calf limited to breakdown skin"},
479: {"code": "L97.212 ", "description": " Nonpressure chronic ulcer of right calf with fat layer exposed"},
480: {"code": "L97.213 ", "description": " Nonpressure chronic ulcer of right calf with necrosis of muscle"},
481: {"code": "L97.214 ", "description": " Nonpressure chronic ulcer of right calf with necrosis of bone"},
482: {"code": "L97.219 ", "description": " Nonpressure chronic ulcer of right calf with unspecified severity"},
483: {"code": "L97.221 ", "description": " Nonpressure chronic ulcer of left calf limited to breakdown skin"},
484: {"code": "L97.222 ", "description": " Nonpressure chronic ulcer of left calf with fat layer exposed"},
485: {"code": "L97.223 ", "description": " Nonpressure chronic ulcer of left calf with necrosis of muscle"},
486: {"code": "L97.224 ", "description": " Nonpressure chronic ulcer of left calf with necrosis of bone"},
487: {"code": "L97.229 ", "description": " Nonpressure chronic ulcer of left calf with unspecified severity"},
488: {"code": "L97.301 ", "description": " Nonpressure chronic ulcer of unspecified ankle limited to breakdown skin"},
489: {"code": "L97.302 ", "description": " Nonpressure chronic ulcer of unspecified ankle with fat layer exposed"},
490: {"code": "L97.303 ", "description": " Nonpressure chronic ulcer of unspecified ankle with necrosis of muscle"},
491: {"code": "L97.304 ", "description": " Nonpressure chronic ulcer of unspecified ankle with necrosis of bone"},
492: {"code": "L97.309 ", "description": " Nonpressure chronic ulcer of unspecified ankle with unspecified severity"},
493: {"code": "L97.311 ", "description": " Nonpressure chronic ulcer of right ankle limited to breakdown skin"},
494: {"code": "L97.312 ", "description": " Nonpressure chronic ulcer of right ankle with fat layer exposed"},
495: {"code": "L97.313 ", "description": " Nonpressure chronic ulcer of right ankle with necrosis of muscle"},
496: {"code": "L97.314 ", "description": " Nonpressure chronic ulcer of right ankle with necrosis of bone"},
497: {"code": "L97.319 ", "description": " Nonpressure chronic ulcer of right ankle with unspecified severity"},
498: {"code": "L97.321 ", "description": " Nonpressure chronic ulcer of left ankle limited to breakdown skin"},
499: {"code": "L97.322 ", "description": " Nonpressure chronic ulcer of left ankle with fat layer exposed"},
500: {"code": "L97.323 ", "description": " Nonpressure chronic ulcer of left ankle with necrosis of muscle"},
501: {"code": "L97.324 ", "description": " Nonpressure chronic ulcer of left ankle with necrosis of bone"},
502: {"code": "L97.329 ", "description": " Nonpressure chronic ulcer of left ankle with unspecified severity"},
503: {"code": "L97.401 ", "description": " Nonpressure chronic ulcer of unspecified heel and midfoot limited to breakdown skin"},
504: {"code": "L97.402 ", "description": " Nonpressure chronic ulcer of unspecified heel and midfoot with fat layer exposed"},
505: {"code": "L97.403 ", "description": " Nonpressure chronic ulcer of unspecified heel and midfoot with necrosis muscle"},
506: {"code": "L97.404 ", "description": " Nonpressure chronic ulcer of unspecified heel and midfoot with necrosis bone"},
507: {"code": "L97.409 ", "description": " Nonpressure chronic ulcer of unspecified heel and midfoot with unspecified severity "},
508: {"code": "L97.411 ", "description": " Nonpressure chronic ulcer of right heel and midfoot limited to breakdown skin"},
509: {"code": "L97.412 ", "description": " Nonpressure chronic ulcer of right heel and midfoot with fat layer exposed"},
510: {"code": "L97.413 ", "description": " Nonpressure chronic ulcer of right heel and midfoot with necrosis muscle"},
511: {"code": "L97.414 ", "description": " Nonpressure chronic ulcer of right heel and midfoot with necrosis bone"},
512: {"code": "L97.419 ", "description": " Nonpressure chronic ulcer of right heel and midfoot with unspecified severity "},
513: {"code": "L97.421 ", "description": " Nonpressure chronic ulcer of left heel and midfoot limited to breakdown skin"},
514: {"code": "L97.422 ", "description": " Nonpressure chronic ulcer of left heel and midfoot with fat layer exposed"},
515: {"code": "L97.423 ", "description": " Nonpressure chronic ulcer of left heel and midfoot with necrosis muscle"},
516: {"code": "L97.424 ", "description": " Nonpressure chronic ulcer of left heel and midfoot with necrosis bone"},
517: {"code": "L97.429 ", "description": " Nonpressure chronic ulcer of left heel and midfoot with unspecified severity "},
518: {"code": "L97.501 ", "description": " Nonpressure chronic ulcer of other part of unspecified foot limited to breakdown skin"},
519: {"code": "L97.502 ", "description": " Nonpressure chronic ulcer of other part of unspecified foot with fat layer exposed"},
520: {"code": "L97.503 ", "description": " Nonpressure chronic ulcer of other part of unspecified foot with necrosis of muscle"},
521: {"code": "L97.504 ", "description": " Nonpressure chronic ulcer of other part of unspecified foot with necrosis of bone"},
522: {"code": "L97.509 ", "description": " Nonpressure chronic ulcer of other part of unspecified foot with unspecified severity"},
523: {"code": "L97.511 ", "description": " Nonpressure chronic ulcer of other part of right foot limited to breakdown skin"},
524: {"code": "L97.512 ", "description": " Nonpressure chronic ulcer of other part of right foot with fat layer exposed"},
525: {"code": "L97.513 ", "description": " Nonpressure chronic ulcer of other part of right foot with necrosis of muscle"},
526: {"code": "L97.514 ", "description": " Nonpressure chronic ulcer of other part of right foot with necrosis of bone"},
527: {"code": "L97.519 ", "description": " Nonpressure chronic ulcer of other part of right foot with unspecified severity"},
528: {"code": "L97.521 ", "description": " Nonpressure chronic ulcer of other part of left foot limited to breakdown skin"},
529: {"code": "L97.522 ", "description": " Nonpressure chronic ulcer of other part of left foot with fat layer exposed"},
530: {"code": "L97.523 ", "description": " Nonpressure chronic ulcer of other part of left foot with necrosis of muscle"},
531: {"code": "L97.524 ", "description": " Nonpressure chronic ulcer of other part of left foot with necrosis of bone"},
532: {"code": "L97.529 ", "description": " Nonpressure chronic ulcer of other part of left foot with unspecified severity"},
533: {"code": "L97.801 ", "description": " Nonpressure chronic ulcer of other part of unspecified lower leg limited to breakdown skin"},
534: {"code": "L97.802 ", "description": " Nonpressure chronic ulcer of other part of unspecified lower leg with fat layer exposed"},
535: {"code": "L97.803 ", "description": " Nonpressure chronic ulcer of other part of unspecified lower leg with necrosis muscle"},
536: {"code": "L97.804 ", "description": " Nonpressure chronic ulcer of other part of unspecified lower leg with necrosis bone"},
537: {"code": "L97.809 ", "description": " Nonpressure chronic ulcer of other part of unspecified lower leg with unspecified severity"},
538: {"code": "L97.811 ", "description": " Nonpressure chronic ulcer of other part of right lower leg limited to breakdown skin"},
539: {"code": "L97.812 ", "description": " Nonpressure chronic ulcer of other part of right lower leg with fat layer exposed"},
540: {"code": "L97.813 ", "description": " Nonpressure chronic ulcer of other part of right lower leg with necrosis of muscle"},
541: {"code": "L97.814 ", "description": " Nonpressure chronic ulcer of other part of right lower leg with necrosis of bone"},
542: {"code": "L97.819 ", "description": " Nonpressure chronic ulcer of other part of right lower leg with unspecified severity"},
543: {"code": "L97.821 ", "description": " Nonpressure chronic ulcer of other part of left lower leg limited to breakdown skin"},
544: {"code": "L97.822 ", "description": " Nonpressure chronic ulcer of other part of left lower leg with fat layer exposed"},
545: {"code": "L97.823 ", "description": " Nonpressure chronic ulcer of other part of left lower leg with necrosis of muscle"},
546: {"code": "L97.824 ", "description": " Nonpressure chronic ulcer of other part of left lower leg with necrosis of bone"},
547: {"code": "L97.829 ", "description": " Nonpressure chronic ulcer of other part of left lower leg with unspecified severity"},
548: {"code": "L97.901 ", "description": " Nonpressure chronic ulcer unspecified part of unspecified lower leg limited to breakdown skin"},
549: {"code": "L97.902 ", "description": " Nonpressure chronic ulcer unspecified part of unspecified lower leg with fat layer exposed"},
550: {"code": "L97.903 ", "description": " Nonpressure chronic ulcer unspecified part of unspecified lower leg with necrosis muscle"},
551: {"code": "L97.904 ", "description": " Nonpressure chronic ulcer unspecified part of unspecified lower leg with necrosis bone"},
552: {"code": "L97.909 ", "description": " Nonpressure chronic ulcer unspecified part of unspecified lower leg with unspecified severity"},
553: {"code": "L97.911 ", "description": " Nonpressure chronic ulcer unspecified part of right lower leg limited to breakdown skin"},
554: {"code": "L97.912 ", "description": " Nonpressure chronic ulcer unspecified part of right lower leg with fat layer exposed"},
555: {"code": "L97.913 ", "description": " Nonpressure chronic ulcer unspecified part of right lower leg with necrosis muscle"},
556: {"code": "L97.914 ", "description": " Nonpressure chronic ulcer unspecified part of right lower leg with necrosis of bone"},
557: {"code": "L97.919 ", "description": " Nonpressure chronic ulcer unspecified part of right lower leg with unspecified severity"},
558: {"code": "L97.921 ", "description": " Nonpressure chronic ulcer unspecified part of left lower leg limited to breakdown skin"},
559: {"code": "L97.922 ", "description": " Nonpressure chronic ulcer unspecified part of left lower leg with fat layer exposed"},
560: {"code": "L97.923 ", "description": " Nonpressure chronic ulcer unspecified part of left lower leg with necrosis muscle"},
561: {"code": "L97.924 ", "description": " Nonpressure chronic ulcer unspecified part of left lower leg with necrosis of bone"},
562: {"code": "L97.929 ", "description": " Nonpressure chronic ulcer unspecified part of left lower leg with unspecified severity"},
563: {"code": "L98.411 ", "description": " Nonpressure chronic ulcer of buttock limited to breakdown skin"},
564: {"code": "L98.412 ", "description": " Nonpressure chronic ulcer of buttock with fat layer exposed"},
565: {"code": "L98.413 ", "description": " Nonpressure chronic ulcer of buttock with necrosis of muscle"},
566: {"code": "L98.414 ", "description": " Nonpressure chronic ulcer of buttock with necrosis of bone"},
567: {"code": "L98.419 ", "description": " Nonpressure chronic ulcer of buttock with unspecified severity"},
568: {"code": "L98.421 ", "description": " Nonpressure chronic ulcer of back limited to breakdown skin"},
569: {"code": "L98.422 ", "description": " Nonpressure chronic ulcer of back with fat layer exposed"},
570: {"code": "L98.423 ", "description": " Nonpressure chronic ulcer of back with necrosis of muscle"},
571: {"code": "L98.424 ", "description": " Nonpressure chronic ulcer of back with necrosis of bone"},
572: {"code": "L98.429 ", "description": " Nonpressure chronic ulcer of back with unspecified severity"},
573: {"code": "L98.491 ", "description": " Nonpressure chronic ulcer skin/ sites limited to breakdown skin"},
574: {"code": "L98.492 ", "description": " Nonpressure chronic ulcer of skin of sites with fat layer exposed"},
575: {"code": "L98.493 ", "description": " Nonpressure chronic ulcer of skin of sites with necrosis of muscle"},
576: {"code": "L98.494 ", "description": " Nonpressure chronic ulcer of skin of sites with necrosis of bone"},
577: {"code": "L98.499 ", "description": " Nonpressure chronic ulcer of skin of sites with unspecified severity"},
578: {"code": "S01.00XA ", "description": " Unspecified open wound of scalp, initial encounter"},
579: {"code": "S01.00XD ", "description": " Unspecified open wound of scalp, subsequent encounter"},
580: {"code": "S01.00XS ", "description": " Unspecified open wound of scalp, sequela"},
581: {"code": "S01.80XA ", "description": " Unspecified open wound of other part of head, initial encounter"},
582: {"code": "S01.80XD ", "description": " Unspecified open wound of other part of head, subsequent encounter"},
583: {"code": "S01.80XS ", "description": " Unspecified open wound of other part of head, sequela"},
584: {"code": "S01.90XS ", "description": " Unspecified open wound of unspecified part of head, sequela"},
585: {"code": "S11.80XA ", "description": " Unspecified open wound of other part of neck, initial encounter"},
586: {"code": "S11.80XD ", "description": " Unspecified open wound of other part of neck, subsequent encounter"},
587: {"code": "S11.80XS ", "description": " Unspecified open wound of other part of neck, sequela"},
588: {"code": "S11.89XA ", "description": " Other open wound of other part of neck, initial encounter"},
589: {"code": "S11.89XD ", "description": " Other open wound of other part of neck, subsequent encounter"},
590: {"code": "S11.89XS ", "description": " Other open wound of other specified part of neck, sequela"},
591: {"code": "S11.90XS ", "description": " Unspecified open wound of unspecified part of neck, sequela"},
592: {"code": "S21.001A ", "description": " Unspecified open wound of right breast, initial encounter"},
593: {"code": "S21.001D ", "description": " Unspecified open wound of right breast, subsequent encounter"},
594: {"code": "S21.001S ", "description": " Unspecified open wound of right breast, sequela"},
595: {"code": "S21.002A ", "description": " Unspecified open wound of left breast, initial encounter"},
596: {"code": "S21.002D ", "description": " Unspecified open wound of left breast, subsequent encounter"},
597: {"code": "S21.002S ", "description": " Unspecified open wound of left breast, sequela"},
598: {"code": "S21.009A ", "description": " Unspecified open wound of unspecified breast, initial encounter"},
599: {"code": "S21.009D ", "description": " Unspecified open wound of unspecified breast, subsequent encounter"},
600: {"code": "S21.009S ", "description": " Unspecified open wound of unspecified breast, sequela"},
601: {"code": "S31.809A ", "description": " Unspecified open wound of unspecified buttock, initial encounter"},
602: {"code": "S31.809D ", "description": " Unspecified open wound of unspecified buttock, subsequent encounter"},
603: {"code": "S31.809S ", "description": " Unspecified open wound of unspecified buttock, sequela"},
604: {"code": "S31.819A ", "description": " Unspecified open wound of right buttock, initial encounter"},
605: {"code": "S31.819D ", "description": " Unspecified open wound of right buttock, subsequent encounter"},
606: {"code": "S31.819S ", "description": " Unspecified open wound of right buttock, sequela"},
607: {"code": "S31.829A ", "description": " Unspecified open wound of left buttock, initial encounter"},
608: {"code": "S31.829D ", "description": " Unspecified open wound of left buttock, subsequent encounter"},
609: {"code": "S31.829S ", "description": " Unspecified open wound of left buttock, sequela"},
610: {"code": "S41.001A ", "description": " Unspecified open wound of right shoulder, initial encounter"},
611: {"code": "S41.001D ", "description": " Unspecified open wound of right shoulder, subsequent encounter"},
612: {"code": "S41.001S ", "description": " Unspecified open wound of right shoulder, sequela"},
613: {"code": "S41.002A ", "description": " Unspecified open wound of left shoulder, initial encounter"},
614: {"code": "S41.002D ", "description": " Unspecified open wound of left shoulder, subsequent encounter"},
615: {"code": "S41.002S ", "description": " Unspecified open wound of left shoulder, sequela"},
616: {"code": "S41.009A ", "description": " Unspecified open wound of unspecified shoulder, initial encounter"},
617: {"code": "S41.009D ", "description": " Unspecified open wound of unspecified shoulder, subsequent encounter"},
618: {"code": "S41.009S ", "description": " Unspecified open wound of unspecified shoulder, sequela"},
619: {"code": "S41.101A ", "description": " Unspecified open wound of right upper arm, initial encounter"},
620: {"code": "S41.101D ", "description": " Unspecified open wound of right upper arm, subsequent encounter"},
621: {"code": "S41.101S ", "description": " Unspecified open wound of right upper arm, sequela"},
622: {"code": "S41.102A ", "description": " Unspecified open wound of left upper arm, initial encounter"},
623: {"code": "S41.102D ", "description": " Unspecified open wound of left upper arm, subsequent encounter"},
624: {"code": "S41.102S ", "description": " Unspecified open wound of left upper arm, sequela"},
625: {"code": "S41.109A ", "description": " Unspecified open wound of unspecified upper arm, initial encounter"},
626: {"code": "S41.109D ", "description": " Unspecified open wound of unspecified upper arm, subsequent encounter"},
627: {"code": "S41.109S ", "description": " Unspecified open wound of unspecified upper arm, sequela"},
628: {"code": "S51.001A ", "description": " Unspecified open wound of right elbow, initial encounter"},
629: {"code": "S51.001D ", "description": " Unspecified open wound of right elbow, subsequent encounter"},
630: {"code": "S51.001S ", "description": " Unspecified open wound of right elbow, sequela"},
631: {"code": "S51.002A ", "description": " Unspecified open wound of left elbow, initial encounter"},
632: {"code": "S51.002D ", "description": " Unspecified open wound of left elbow, subsequent encounter"},
633: {"code": "S51.002S ", "description": " Unspecified open wound of left elbow, sequela"},
634: {"code": "S51.009A ", "description": " Unspecified open wound of unspecified elbow, initial encounter"},
635: {"code": "S51.009D ", "description": " Unspecified open wound of unspecified elbow, subsequent encounter"},
636: {"code": "S51.009S ", "description": " Unspecified open wound of unspecified elbow, sequela"},
637: {"code": "S51.801A ", "description": " Unspecified open wound of right forearm, initial encounter"},
638: {"code": "S51.801D ", "description": " Unspecified open wound of right forearm, subsequent encounter"},
639: {"code": "S51.801S ", "description": " Unspecified open wound of right forearm, sequela"},
640: {"code": "S51.802A ", "description": " Unspecified open wound of left forearm, initial encounter"},
641: {"code": "S51.802D ", "description": " Unspecified open wound of left forearm, subsequent encounter"},
642: {"code": "S51.802S ", "description": " Unspecified open wound of left forearm, sequela"},
643: {"code": "S51.809A ", "description": " Unspecified open wound of unspecified forearm, initial encounter"},
644: {"code": "S51.809D ", "description": " Unspecified open wound of unspecified forearm, subsequent encounter"},
645: {"code": "S51.809S ", "description": " Unspecified open wound of unspecified forearm, sequela"},
646: {"code": "S61.401A ", "description": " Unspecified open wound of right hand, initial encounter"},
647: {"code": "S61.401D ", "description": " Unspecified open wound of right hand, subsequent encounter"},
648: {"code": "S61.401S ", "description": " Unspecified open wound of right hand, sequela"},
649: {"code": "S61.402A ", "description": " Unspecified open wound of left hand, initial encounter"},
650: {"code": "S61.402D ", "description": " Unspecified open wound of left hand, subsequent encounter"},
651: {"code": "S61.402S ", "description": " Unspecified open wound of left hand, sequela"},
652: {"code": "S61.409A ", "description": " Unspecified open wound of unspecified hand, initial encounter"},
653: {"code": "S61.409D ", "description": " Unspecified open wound of unspecified hand, subsequent encounter"},
654: {"code": "S61.409S ", "description": " Unspecified open wound of unspecified hand, sequela"},
655: {"code": "S61.501A ", "description": " Unspecified open wound of right wrist, initial encounter"},
656: {"code": "S61.501D ", "description": " Unspecified open wound of right wrist, subsequent encounter"},
657: {"code": "S61.501S ", "description": " Unspecified open wound of right wrist, sequela"},
658: {"code": "S61.502A ", "description": " Unspecified open wound of left wrist, initial encounter"},
659: {"code": "S61.502D ", "description": " Unspecified open wound of left wrist, subsequent encounter"},
660: {"code": "S61.502S ", "description": " Unspecified open wound of left wrist, sequela"},
661: {"code": "S61.509A ", "description": " Unspecified open wound of unspecified wrist, initial encounter"},
662: {"code": "S61.509D ", "description": " Unspecified open wound of unspecified wrist, subsequent encounter"},
663: {"code": "S61.509S ", "description": " Unspecified open wound of unspecified wrist, sequela"},
664: {"code": "S71.001A ", "description": " Unspecified open wound, right hip, initial encounter"},
665: {"code": "S71.001D ", "description": " Unspecified open wound, right hip, subsequent encounter"},
666: {"code": "S71.001S ", "description": " Unspecified open wound, right hip, sequela"},
667: {"code": "S71.002A ", "description": " Unspecified open wound, left hip, initial encounter"},
668: {"code": "S71.002D ", "description": " Unspecified open wound, left hip, subsequent encounter"},
669: {"code": "S71.002S ", "description": " Unspecified open wound, left hip, sequela"},
670: {"code": "S71.009A ", "description": " Unspecified open wound, unspecified hip, initial encounter"},
671: {"code": "S71.009D ", "description": " Unspecified open wound, unspecified hip, subsequent encounter"},
672: {"code": "S71.009S ", "description": " Unspecified open wound, unspecified hip, sequela"},
673: {"code": "S71.101A ", "description": " Unspecified open wound, right thigh, initial encounter"},
674: {"code": "S71.101D ", "description": " Unspecified open wound, right thigh, subsequent encounter"},
675: {"code": "S71.101S ", "description": " Unspecified open wound, right thigh, sequela"},
676: {"code": "S71.102A ", "description": " Unspecified open wound, left thigh, initial encounter"},
677: {"code": "S71.102D ", "description": " Unspecified open wound, left thigh, subsequent encounter"},
678: {"code": "S71.102S ", "description": " Unspecified open wound, left thigh, sequela"},
679: {"code": "S71.109A ", "description": " Unspecified open wound, unspecified thigh, initial encounter"},
680: {"code": "S71.109D ", "description": " Unspecified open wound, unspecified thigh, subsequent encounter"},
681: {"code": "S71.109S ", "description": " Unspecified open wound, unspecified thigh, sequela"},
682: {"code": "S81.001A ", "description": " Unspecified open wound, right knee, initial encounter"},
683: {"code": "S81.001D ", "description": " Unspecified open wound, right knee, subsequent encounter"},
684: {"code": "S81.001S ", "description": " Unspecified open wound, right knee, sequela"},
685: {"code": "S81.002A ", "description": " Unspecified open wound, left knee, initial encounter"},
686: {"code": "S81.002D ", "description": " Unspecified open wound, left knee, subsequent encounter"},
687: {"code": "S81.002S ", "description": " Unspecified open wound, left knee, sequela"},
688: {"code": "S81.009A ", "description": " Unspecified open wound, unspecified knee, initial encounter"},
689: {"code": "S81.009D ", "description": " Unspecified open wound, unspecified knee, subsequent encounter"},
690: {"code": "S81.009S ", "description": " Unspecified open wound, unspecified knee, sequela"},
691: {"code": "S81.801A ", "description": " Unspecified open wound, right lower leg, initial encounter"},
692: {"code": "S81.801D ", "description": " Unspecified open wound, right lower leg, subsequent encounter"},
693: {"code": "S81.801S ", "description": " Unspecified open wound, right lower leg, sequela"},
694: {"code": "S81.802A ", "description": " Unspecified open wound, left lower leg, initial encounter"},
695: {"code": "S81.802D ", "description": " Unspecified open wound, left lower leg, subsequent encounter"},
696: {"code": "S81.802S ", "description": " Unspecified open wound, left lower leg, sequela"},
697: {"code": "S81.809A ", "description": " Unspecified open wound, unspecified lower leg, initial encounter"},
698: {"code": "S81.809D ", "description": " Unspecified open wound, unspecified lower leg, subsequent encounter"},
699: {"code": "S81.809S ", "description": " Unspecified open wound, unspecified lower leg, sequela"},
700: {"code": "S91.001A ", "description": " Unspecified open wound, right ankle, initial encounter"},
701: {"code": "S91.001D ", "description": " Unspecified open wound, right ankle, subsequent encounter"},
702: {"code": "S91.001S ", "description": " Unspecified open wound, right ankle, sequela"},
703: {"code": "S91.002A ", "description": " Unspecified open wound, left ankle, initial encounter"},
704: {"code": "S91.002D ", "description": " Unspecified open wound, left ankle, subsequent encounter"},
705: {"code": "S91.002S ", "description": " Unspecified open wound, left ankle, sequela"},
706: {"code": "S91.009A ", "description": " Unspecified open wound, unspecified ankle, initial encounter"},
707: {"code": "S91.009D ", "description": " Unspecified open wound, unspecified ankle, subsequent encounter"},
708: {"code": "S91.009S ", "description": " Unspecified open wound, unspecified ankle, sequela"},
709: {"code": "S91.301A ", "description": " Unspecified open wound, right foot, initial encounter"},
710: {"code": "S91.301D ", "description": " Unspecified open wound, right foot, subsequent encounter"},
711: {"code": "S91.301S ", "description": " Unspecified open wound, right foot, sequela"},
712: {"code": "S91.302A ", "description": " Unspecified open wound, left foot, initial encounter"},
713: {"code": "S91.302D ", "description": " Unspecified open wound, left foot, subsequent encounter"},
714: {"code": "S91.302S ", "description": " Unspecified open wound, left foot, sequela"},
715: {"code": "S91.309A ", "description": " Unspecified open wound, unspecified foot, initial encounter"},
716: {"code": "S91.309D ", "description": " Unspecified open wound, unspecified foot, subsequent encounter"},
717: {"code": "S91.309S ", "description": " Unspecified open wound, unspecified foot, sequela"},
718: {"code": "T81.30XA ", "description": " Disruption of wound, unspecified, initial encounter"},
719: {"code": "T81.30XD ", "description": " Disruption of wound, unspecified, subsequent encounter"},
720: {"code": "T81.30XS ", "description": " Disruption of wound, unspecified, sequela"},
721: {"code": "T81.31XA ", "description": " Disruption of external operation (surgical) wound, not elsewhere classified, initial encounter"},
722: {"code": "T81.31XD ", "description": " Disruption of external operation (surgical) wound, not elsewhere classified, subsequent encounter"},
723: {"code": "T81.31XS ", "description": " Disrupt of external operation (surgical) wound, not elsewhere classified, sequela"},
724: {"code": "T81.32XA ", "description": " Disruption of internal operation (surgical) wound, not elsewhere classified, initial encounter"},
725: {"code": "T81.32XD ", "description": " Disruption of internal operation (surgical) wound, not elsewhere classified, subsequent encounter"},
726: {"code": "T81.32XS ", "description": " Disrupt of internal operation (surgical) wound, not elsewhere classified, sequela"},
727: {"code": "T81.33XA ", "description": " Disruption of traumatic injury wound repair, initial encounter"},
728: {"code": "T81.33XD ", "description": " Disruption of traumatic injury wound repair, subsequent encounter"},
729: {"code": "T81.33XS ", "description": " Disruption of traumatic injury wound repair, sequela"},
730: {"code": "G30.0 ", "description": " Alzheimer's disease with early onset"},
731: {"code": "G30.1 ", "description": " Alzheimer's disease with late onset"},
732: {"code": "G30.8 ", "description": " Other Alzheimer's disease"},
733: {"code": "G30.9 ", "description": " Alzheimer's disease, unspecified"},
734: {"code": "H35.31 ", "description": " Nonexudative agerelated macular degeneration"},
735: {"code": "H35.32 ", "description": " Exudative agerelated macular degeneration"},
736: {"code": "H35.33 ", "description": " Other agerelated macular degeneration"},
737: {"code": "H35.39 ", "description": " Other macular degeneration"},
738: {"code": "I15.0 ", "description": " Renovascular hypertension"},
739: {"code": "I15.1 ", "description": " Hypertension secondary to other renal disorders"},
740: {"code": "I15.2 ", "description": " Hypertension secondary to endocrine disorders"},
741: {"code": "I15.8 ", "description": " Other secondary hypertension"},
742: {"code": "I15.9 ", "description": " Secondary hypertension, unspecified"},
743: {"code": "I20.0 ", "description": " Unstable angina"},
744: {"code": "I20.1 ", "description": " Angina pectoris with documented spasm"},
745: {"code": "I20.8 ", "description": " Other forms of angina pectoris"},
746: {"code": "I20.9 ", "description": " Angina pectoris, unspecified"},
747: {"code": "I24.0 ", "description": " Acute coronary thrombosis not resulting in myocardial infarction"},
748: {"code": "I24.1 ", "description": " Dressler's syndrome"},
749: {"code": "I24.8 ", "description": " Other forms of acute ischemic heart disease"},
750: {"code": "I24.9 ", "description": " Acute ischemic heart disease, unspecified"},
751: {"code": "I25.10 ", "description": " Atherosclerotic heart disease of native coronary artery without angina pectoris"},
752: {"code": "I25.110 ", "description": " Atherosclerotic heart disease of native coronary artery with unstable angina pectoris"},
753: {"code": "I25.111 ", "description": " Atherosclerotic heart disease of native coronary artery with angina pectoris with documented spasm"},
754: {"code": "I25.118 ", "description": " Atherosclerotic heart disease of native coronary artery with other forms of angina pectoris"},
755: {"code": "I25.119 ", "description": " Atherosclerotic heart disease of native coronary artery with unspecified angina pectoris"},
756: {"code": "I25.2 ", "description": " Old myocardial infarction"},
757: {"code": "I25.42 ", "description": " Coronary artery aneurysm"},
758: {"code": "I25.5 ", "description": " Ischemic cardiomyopathy"},
759: {"code": "I25.6 ", "description": " Silent myocardial ischemia"},
760: {"code": "I25.700 ", "description": " Atherosclerosis of coronary artery bypass graft(s), unspecified, with unstable angina pectoris"},
761: {"code": "I25.701 ", "description": " Atherosclerosis of coronary artery bypass graft(s), unspecified, with angina pectoris with documented spasm"},
762: {"code": "I25.708 ", "description": " Atherosclerosis of coronary artery bypass graft(s), unspecified, with other forms of angina pectoris"},
763: {"code": "I25.709 ", "description": " Atherosclerosis of coronary artery bypass graft(s), unspecified, with unspecified angina pectoris"},
764: {"code": "I25.710 ", "description": " Atherosclerosis of autologous vein coronary artery bypass graft(s) with unstable angina pectoris"},
765: {"code": "I25.711 ", "description": " Atherosclerosis of autologous vein coronary artery bypass graft(s) with angina pectoris with documented spasm"},
766: {"code": "I25.718 ", "description": " Atherosclerosis of autologous vein coronary artery bypass graft(s) with other forms of angina pectoris"},
767: {"code": "I25.719 ", "description": " Atherosclerosis of autologous vein coronary artery bypass graft(s) with unspecified angina pectoris"},
768: {"code": "I25.720 ", "description": " Atherosclerosis of autologous artery coronary artery bypass graft(s) with unstable angina pectoris"},
769: {"code": "I25.721 ", "description": " Atherosclerosis of autologous artery coronary artery bypass graft(s) with angina pectoris with documented spasm"},
770: {"code": "I25.728 ", "description": " Atherosclerosis of autologous artery coronary artery bypass graft(s) with other forms of angina pectoris"},
771: {"code": "I25.729 ", "description": " Atherosclerosis of autologous artery coronary artery bypass graft(s) with unspecified angina pectoris"},
772: {"code": "I25.730 ", "description": " Atherosclerosis of nonautologous biological coronary artery bypass graft(s) with unstable angina pectoris"},
773: {"code": "I25.731 ", "description": " Atherosclerosis of nonautologous biological coronary artery bypass graft(s) with angina pectoris with documented spasm"},
774: {"code": "I25.738 ", "description": " Atherosclerosis of nonautologous biological coronary artery bypass graft(s) with other forms of angina pectoris"},
775: {"code": "I25.739 ", "description": " Atherosclerosis of nonautologous biological coronary artery bypass graft(s) with unspecified angina pectoris"},
776: {"code": "I25.750 ", "description": " Atherosclerosis of other coronary artery bypass graft(s) with unstable angina pectoris"},
777: {"code": "I25.751 ", "description": " Atherosclerosis of other coronary artery bypass graft(s) with angina pectoris with documented spasm"},
778: {"code": "I25.758 ", "description": " Atherosclerosis of other coronary artery bypass graft(s) with other forms of angina pectoris"},
779: {"code": "I25.759 ", "description": " Atherosclerosis of other coronary artery bypass graft(s) with unspecified angina pectoris"},
780: {"code": "I25.760 ", "description": " Atherosclerosis of coronary artery bypass graft(s), unspecified, with unstable angina pectoris"},
781: {"code": "I25.761 ", "description": " Atherosclerosis of coronary artery bypass graft(s), unspecified, with angina pectoris with documented spasm"},
782: {"code": "I25.768 ", "description": " Atherosclerosis of coronary artery bypass graft(s), unspecified, with other forms of angina pectoris"},
783: {"code": "I25.769 ", "description": " Atherosclerosis of coronary artery bypass graft(s), unspecified, with unspecified angina pectoris"},
784: {"code": "I25.790 ", "description": " Atherosclerosis of other coronary artery bypass graft(s) with unstable angina pectoris"},
785: {"code": "I25.791 ", "description": " Atherosclerosis of other coronary artery bypass graft(s) with angina pectoris with documented spasm"},
786: {"code": "I25.798 ", "description": " Atherosclerosis of other coronary artery bypass graft(s) with other forms of angina pectoris"},
787: {"code": "I25.799 ", "description": " Atherosclerosis of other coronary artery bypass graft(s) with unspecified angina pectoris"},
788: {"code": "I25.810 ", "description": " Atherosclerosis of coronary artery bypass graft(s), unspecified, with unstable angina pectoris"},
789: {"code": "I25.811 ", "description": " Atherosclerosis of coronary artery bypass graft(s), unspecified, with angina pectoris with documented spasm"},
790: {"code": "I25.812 ", "description": " Atherosclerosis of coronary artery bypass graft(s), unspecified, with other forms of angina pectoris"},
791: {"code": "I25.82 ", "description": " Chronic total occlusion of coronary artery"},
792: {"code": "I25.83 ", "description": " Coronary artery dissection"},
793: {"code": "I25.84 ", "description": " Coronary microvascular dysfunction"},
794: {"code": "I25.89 ", "description": " Other forms of chronic"},
795: {"code": "J44.81 ", "description": " Chronic obstructive pulmonary disease with acute exacerbation, lower respiratory infection"},
796: {"code": "J44.89 ", "description": " Other specified chronic obstructive pulmonary disease"}
        }
    
    def _load_test_mapping(self) -> Dict[int, Dict[str, str]]:
        """
        Load diagnostic test mapping
        """
        return {
            0: {"test": "Chest X-ray (PA/AP)", "code": "71020"},
            1: {"test": "Complete Blood Count (CBC)", "code": "85025"},
            2: {"test": "Basic Metabolic Panel", "code": "80048"},
            3: {"test": "Urinalysis", "code": "81001"},
            4: {"test": "ECG (12-lead)", "code": "93000"},
            5: {"test": "Blood Culture", "code": "87040"},
            6: {"test": "CT Chest without contrast", "code": "71250"},
            7: {"test": "Lipid Panel", "code": "80061"},
            8: {"test": "Thyroid Function Tests", "code": "84439"},
            9: {"test": "Liver Function Tests", "code": "80076"}
        }
    
    def _load_medication_mapping(self) -> Dict[int, Dict[str, str]]:
        """
        Load medication mapping
        """
        return {
            0: {"medication": "Amoxicillin-clavulanate", "generic": "Amoxicillin-clavulanate", "dose": "500 mg PO TID"},
            1: {"medication": "Acetaminophen", "generic": "Acetaminophen", "dose": "650 mg PO q6h PRN"},
            2: {"medication": "Ibuprofen", "generic": "Ibuprofen", "dose": "400 mg PO q6h PRN"},
            3: {"medication": "Azithromycin", "generic": "Azithromycin", "dose": "250 mg PO daily"},
            4: {"medication": "Omeprazole", "generic": "Omeprazole", "dose": "20 mg PO daily"},
            5: {"medication": "Lisinopril", "generic": "Lisinopril", "dose": "10 mg PO daily"},
            6: {"medication": "Metformin", "generic": "Metformin", "dose": "500 mg PO BID"},
            7: {"medication": "Albuterol inhaler", "generic": "Albuterol", "dose": "2 puffs q4-6h PRN"},
            8: {"medication": "Loratadine", "generic": "Loratadine", "dose": "10 mg PO daily"},
            9: {"medication": "Simvastatin", "generic": "Simvastatin", "dose": "20 mg PO daily"}
        }
    
    def _generate_dummy_predictions(self, input_data: Dict[str, Any]) -> List[DiseasePrediction]:
        """
        Generate dummy predictions when model is not available
        This simulates real model behavior for demonstration
        """
        # Simple rule-based logic for demonstration
        predictions = []
        
        symptoms = input_data.get("symptom_list", [])
        temp = input_data.get("vital_temperature_c")
        
        # Rule 1: Fever + cough = likely respiratory infection
        if temp and temp > 38.0 and any("cough" in s.lower() for s in symptoms):
            predictions.append(DiseasePrediction(
                icd10_code="J18.9",
                diagnosis="Pneumonia, unspecified organism",
                confidence=0.82,
                recommended_tests=[
                    TestRecommendation(test="Chest X-ray (PA/AP)", confidence=0.9, urgency="routine"),
                    TestRecommendation(test="Complete Blood Count (CBC)", confidence=0.8, urgency="routine")
                ],
                recommended_medications=[
                    MedicationRecommendation(
                        medication="Amoxicillin-clavulanate",
                        confidence=0.78,
                        dose_suggestion="500 mg PO TID",
                        duration="7-10 days"
                    )
                ],
                assessment_plan="Likely community-acquired pneumonia. Obtain chest x-ray and CBC; start empiric oral antibiotics considering allergy history. Re-evaluate in 48 hours.",
                rationale=[
                    f"Fever ({temp}°C)",
                    "Productive cough reported",
                    "Clinical presentation consistent with respiratory infection"
                ]
            ))
        
        # Rule 2: Fever alone
        elif temp and temp > 37.5:
            predictions.append(DiseasePrediction(
                icd10_code="R50.9",
                diagnosis="Fever, unspecified",
                confidence=0.65,
                recommended_tests=[
                    TestRecommendation(test="Complete Blood Count (CBC)", confidence=0.8, urgency="routine"),
                    TestRecommendation(test="Urinalysis", confidence=0.6, urgency="routine")
                ],
                recommended_medications=[
                    MedicationRecommendation(
                        medication="Acetaminophen",
                        confidence=0.9,
                        dose_suggestion="650 mg PO q6h PRN",
                        duration="As needed"
                    )
                ],
                assessment_plan="Fever of unknown origin. Supportive care and symptomatic treatment. Monitor for additional symptoms.",
                rationale=[
                    f"Elevated temperature ({temp}°C)",
                    "No clear source identified"
                ]
            ))
        
        # Rule 3: Headache
        if any("headache" in s.lower() for s in symptoms):
            predictions.append(DiseasePrediction(
                icd10_code="R51",
                diagnosis="Headache",
                confidence=0.70,
                recommended_tests=[
                    TestRecommendation(test="Basic Metabolic Panel", confidence=0.5, urgency="routine")
                ],
                recommended_medications=[
                    MedicationRecommendation(
                        medication="Ibuprofen",
                        confidence=0.85,
                        dose_suggestion="400 mg PO q6h PRN",
                        duration="As needed"
                    )
                ],
                assessment_plan="Primary headache. Symptomatic treatment with NSAIDs. Consider neurological evaluation if persistent or severe.",
                rationale=["Patient reports headache"]
            ))
        
        # Default prediction if no specific rules match
        if not predictions:
            predictions.append(DiseasePrediction(
                icd10_code="R69",
                diagnosis="Illness, unspecified",
                confidence=0.40,
                recommended_tests=[
                    TestRecommendation(test="Complete Blood Count (CBC)", confidence=0.6, urgency="routine")
                ],
                recommended_medications=[],
                assessment_plan="Non-specific symptoms. Recommend follow-up if symptoms persist or worsen.",
                rationale=["Non-specific clinical presentation"]
            ))
        
        # Ensure we have up to 3 predictions
        while len(predictions) < 3 and len(predictions) < len(self.icd10_mapping):
            # Add additional differential diagnoses with lower confidence
            next_idx = len(predictions)
            if next_idx in self.icd10_mapping:
                icd_data = self.icd10_mapping[next_idx]
                predictions.append(DiseasePrediction(
                    icd10_code=icd_data["code"],
                    diagnosis=icd_data["description"],
                    confidence=max(0.3 - next_idx * 0.1, 0.1),
                    recommended_tests=[],
                    recommended_medications=[],
                    assessment_plan="Consider as differential diagnosis. Additional evaluation may be needed.",
                    rationale=["Differential diagnosis consideration"],
                    risk_factors=[],
                    differential_diagnoses=[]
                ))
        
        return predictions[:3]  # Return top 3
    
    def predict(self, input_data: Dict[str, Any]) -> List[DiseasePrediction]:
        """
        Main prediction method
        """
        try:
            if self.model is not None:
                # Use trained model
                processed_input = self.preprocessor.preprocess_input(input_data)
                processed_input = processed_input.to(self.device)
                
                # Get model predictions
                with torch.no_grad():
                    top_diseases = self.model.predict_top_diseases(processed_input, top_k=3)
                    recommended_tests = self.model.predict_tests(processed_input, threshold=0.5)
                    recommended_meds = self.model.predict_medications(processed_input, threshold=0.4)
                
                # Convert to response format
                predictions = []
                for i, (disease_idx, confidence) in enumerate(top_diseases):
                    if disease_idx in self.icd10_mapping:
                        icd_data = self.icd10_mapping[disease_idx]
                        
                        # Get relevant tests and medications for this disease
                        relevant_tests = [
                            TestRecommendation(
                                test=self.test_mapping[test_idx]["test"],
                                confidence=test_conf,
                                urgency="routine"
                            )
                            for test_idx, test_conf in recommended_tests[:3]
                            if test_idx in self.test_mapping
                        ]
                        
                        relevant_meds = [
                            MedicationRecommendation(
                                medication=self.medication_mapping[med_idx]["medication"],
                                confidence=med_conf,
                                dose_suggestion=self.medication_mapping[med_idx]["dose"]
                            )
                            for med_idx, med_conf in recommended_meds[:2]
                            if med_idx in self.medication_mapping
                        ]
                        
                        predictions.append(DiseasePrediction(
                            icd10_code=icd_data["code"],
                            diagnosis=icd_data["description"],
                            confidence=confidence,
                            recommended_tests=relevant_tests,
                            recommended_medications=relevant_meds,
                            assessment_plan=f"Clinical assessment suggests {icd_data['description'].lower()}. Recommend appropriate diagnostic workup and treatment.",
                            rationale=["ML model prediction based on clinical features"]
                        ))
                
                return predictions
            
            else:
                # Use dummy predictions
                return self._generate_dummy_predictions(input_data)
                
        except Exception as e:
            print(f"Prediction error: {e}")
            # Return fallback prediction
            return [DiseasePrediction(
                icd10_code="R69",
                diagnosis="Illness, unspecified",
                confidence=0.30,
                recommended_tests=[],
                recommended_medications=[],
                assessment_plan="Unable to generate specific prediction. Recommend clinical evaluation.",
                rationale=[f"Prediction error: {str(e)}"]
            )]