"""
PyTorch Neural Network Model for Clinical Decision Support
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, List, Tuple
import numpy as np


class ClinicalDecisionModel(nn.Module):
    """
    Multi-task PyTorch model for clinical decision support
    
    Tasks:
    1. Disease classification (ICD-10 codes)
    2. Test recommendation
    3. Medication recommendation  
    4. Assessment plan generation
    """
    
    def __init__(
        self,
        input_size: int = 150,  # Total feature size from preprocessor
        hidden_size: int = 512,
        dropout_rate: float = 0.3,
        num_diseases: int = 100,  # Top 100 common diseases
        num_tests: int = 50,      # Common diagnostic tests
        num_medications: int = 200 # Common medications
    ):
        super(ClinicalDecisionModel, self).__init__()
        
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.num_diseases = num_diseases
        self.num_tests = num_tests
        self.num_medications = num_medications
        
        # Shared encoder layers
        self.encoder = nn.Sequential(
            nn.Linear(input_size, hidden_size),
            nn.BatchNorm1d(hidden_size),
            nn.ReLU(),
            nn.Dropout(dropout_rate),
            
            nn.Linear(hidden_size, hidden_size),
            nn.BatchNorm1d(hidden_size),
            nn.ReLU(),
            nn.Dropout(dropout_rate),
            
            nn.Linear(hidden_size, hidden_size // 2),
            nn.BatchNorm1d(hidden_size // 2),
            nn.ReLU(),
            nn.Dropout(dropout_rate)
        )
        
        # Task-specific heads
        # Disease classification head
        self.disease_classifier = nn.Sequential(
            nn.Linear(hidden_size // 2, hidden_size // 4),
            nn.ReLU(),
            nn.Dropout(dropout_rate),
            nn.Linear(hidden_size // 4, num_diseases)
        )
        
        # Test recommendation head
        self.test_recommender = nn.Sequential(
            nn.Linear(hidden_size // 2, hidden_size // 4),
            nn.ReLU(),
            nn.Dropout(dropout_rate),
            nn.Linear(hidden_size // 4, num_tests)
        )
        
        # Medication recommendation head
        self.medication_recommender = nn.Sequential(
            nn.Linear(hidden_size // 2, hidden_size // 4),
            nn.ReLU(),
            nn.Dropout(dropout_rate),
            nn.Linear(hidden_size // 4, num_medications)
        )
        
        # Assessment confidence head (for overall assessment quality)
        self.assessment_head = nn.Sequential(
            nn.Linear(hidden_size // 2, hidden_size // 4),
            nn.ReLU(),
            nn.Dropout(dropout_rate),
            nn.Linear(hidden_size // 4, 1),
            nn.Sigmoid()
        )
        
    def forward(self, x: torch.Tensor) -> Dict[str, torch.Tensor]:
        """
        Forward pass through the model
        
        Args:
            x: Input tensor of shape (batch_size, input_size)
            
        Returns:
            Dictionary containing task outputs
        """
        # Shared encoding
        encoded = self.encoder(x)
        
        # Task-specific predictions
        disease_logits = self.disease_classifier(encoded)
        test_scores = self.test_recommender(encoded)
        medication_scores = self.medication_recommender(encoded)
        assessment_confidence = self.assessment_head(encoded)
        
        # Apply activations
        disease_probs = F.softmax(disease_logits, dim=1)
        test_probs = torch.sigmoid(test_scores)
        medication_probs = torch.sigmoid(medication_scores)
        
        return {
            "disease_probabilities": disease_probs,
            "disease_logits": disease_logits,
            "test_probabilities": test_probs,
            "medication_probabilities": medication_probs,
            "assessment_confidence": assessment_confidence
        }
    
    def predict_top_diseases(self, x: torch.Tensor, top_k: int = 3) -> List[Tuple[int, float]]:
        """
        Get top-k disease predictions
        """
        self.eval()
        with torch.no_grad():
            outputs = self.forward(x)
            disease_probs = outputs["disease_probabilities"]
            
            # Get top-k predictions
            top_probs, top_indices = torch.topk(disease_probs, k=top_k, dim=1)
            
            results = []
            for i in range(top_k):
                disease_idx = top_indices[0][i].item()
                confidence = top_probs[0][i].item()
                results.append((disease_idx, confidence))
            
            return results
    
    def predict_tests(self, x: torch.Tensor, threshold: float = 0.5) -> List[Tuple[int, float]]:
        """
        Get recommended tests above threshold
        """
        self.eval()
        with torch.no_grad():
            outputs = self.forward(x)
            test_probs = outputs["test_probabilities"]
            
            # Get tests above threshold
            recommended_tests = []
            for i, prob in enumerate(test_probs[0]):
                if prob.item() >= threshold:
                    recommended_tests.append((i, prob.item()))
            
            # Sort by probability
            recommended_tests.sort(key=lambda x: x[1], reverse=True)
            return recommended_tests
    
    def predict_medications(self, x: torch.Tensor, threshold: float = 0.4) -> List[Tuple[int, float]]:
        """
        Get recommended medications above threshold
        """
        self.eval()
        with torch.no_grad():
            outputs = self.forward(x)
            med_probs = outputs["medication_probabilities"]
            
            # Get medications above threshold
            recommended_meds = []
            for i, prob in enumerate(med_probs[0]):
                if prob.item() >= threshold:
                    recommended_meds.append((i, prob.item()))
            
            # Sort by probability
            recommended_meds.sort(key=lambda x: x[1], reverse=True)
            return recommended_meds[:10]  # Limit to top 10
    
    def get_assessment_confidence(self, x: torch.Tensor) -> float:
        """
        Get overall assessment confidence
        """
        self.eval()
        with torch.no_grad():
            outputs = self.forward(x)
            return outputs["assessment_confidence"][0][0].item()


class ClinicalLoss(nn.Module):
    """
    Multi-task loss function for clinical decision model
    """
    
    def __init__(
        self,
        disease_weight: float = 1.0,
        test_weight: float = 0.5,
        medication_weight: float = 0.5,
        assessment_weight: float = 0.3
    ):
        super(ClinicalLoss, self).__init__()
        self.disease_weight = disease_weight
        self.test_weight = test_weight
        self.medication_weight = medication_weight
        self.assessment_weight = assessment_weight
        
        # Loss functions
        self.disease_loss = nn.CrossEntropyLoss()
        self.test_loss = nn.BCELoss()
        self.medication_loss = nn.BCELoss()
        self.assessment_loss = nn.MSELoss()
    
    def forward(
        self,
        predictions: Dict[str, torch.Tensor],
        targets: Dict[str, torch.Tensor]
    ) -> Dict[str, torch.Tensor]:
        """
        Calculate multi-task loss
        """
        losses = {}
        
        # Disease classification loss
        if "disease_targets" in targets:
            disease_loss = self.disease_loss(
                predictions["disease_logits"],
                targets["disease_targets"]
            )
            losses["disease_loss"] = disease_loss * self.disease_weight
        
        # Test recommendation loss
        if "test_targets" in targets:
            test_loss = self.test_loss(
                predictions["test_probabilities"],
                targets["test_targets"]
            )
            losses["test_loss"] = test_loss * self.test_weight
        
        # Medication recommendation loss
        if "medication_targets" in targets:
            med_loss = self.medication_loss(
                predictions["medication_probabilities"],
                targets["medication_targets"]
            )
            losses["medication_loss"] = med_loss * self.medication_weight
        
        # Assessment confidence loss
        if "assessment_targets" in targets:
            assessment_loss = self.assessment_loss(
                predictions["assessment_confidence"],
                targets["assessment_targets"]
            )
            losses["assessment_loss"] = assessment_loss * self.assessment_weight
        
        # Total loss
        total_loss = sum(losses.values())
        losses["total_loss"] = total_loss
        
        return losses