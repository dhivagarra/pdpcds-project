"""
PyTorch Model Training Script for Clinical Decision Support System
Trains the ClinicalDecisionModel using database-stored training data
"""

import os
import json
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from sklearn.metrics import classification_report, accuracy_score, f1_score
from datetime import datetime
import argparse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add parent directory to path
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.ml.model import ClinicalDecisionModel
from app.ml.preprocessor import DataPreprocessor
from app.models import TrainingData, ValidationData
from app.database import Base


class DatabaseClinicalDataset(Dataset):
    """
    PyTorch Dataset that loads clinical data from database
    """
    
    def __init__(self, data_records, preprocessor):
        """
        Initialize dataset from database records
        
        Args:
            data_records: List of TrainingData or ValidationData objects
            preprocessor: Trained DataPreprocessor instance
        """
        self.data_records = data_records
        self.preprocessor = preprocessor
        
        # Pre-process all data
        self.features = []
        self.disease_targets = []
        self.test_targets = []
        self.med_targets = []
        
        print(f"🔄 Processing {len(data_records)} samples...")
        
        for record in data_records:
            # Convert database record to input format
            sample = {
                'age': record.age,
                'sex': record.sex,
                'vital_temperature_c': record.vital_temperature_c,
                'vital_heart_rate': record.vital_heart_rate,
                'vital_blood_pressure_systolic': record.vital_blood_pressure_systolic,
                'vital_blood_pressure_diastolic': record.vital_blood_pressure_diastolic,
                'symptom_list': record.symptom_list,
                'pmh_list': record.pmh_list,
                'free_text_notes': record.free_text_notes or ""
            }
            
            # Process features using preprocess_input method
            features_tensor = preprocessor.preprocess_input(sample)
            features = features_tensor.numpy() if isinstance(features_tensor, torch.Tensor) else features_tensor
            
            # Handle dimension mismatch - flatten if needed
            if len(features.shape) > 1:
                features = features.flatten()
            
            self.features.append(features)
            
            # Process targets
            self.disease_targets.append(record.target_disease)
            
            # Convert test and medication targets to multi-hot encoding
            test_target = np.zeros(25)  # 25 medical tests
            for test_id in record.target_tests:
                if 0 <= test_id < 25:
                    test_target[test_id] = 1
            self.test_targets.append(test_target)
            
            med_target = np.zeros(18)  # 18 medications
            for med_id in record.target_medications:
                if 0 <= med_id < 18:
                    med_target[med_id] = 1
            self.med_targets.append(med_target)
        
        # Convert to tensors
        self.features = torch.tensor(self.features, dtype=torch.float32)
        self.disease_targets = torch.tensor(self.disease_targets, dtype=torch.long)
        self.test_targets = torch.tensor(self.test_targets, dtype=torch.float32)
        self.med_targets = torch.tensor(self.med_targets, dtype=torch.float32)
        
        print(f"✅ Dataset ready: {len(self)} samples")
        print(f"📊 Feature shape: {self.features.shape}")
    
    def __len__(self):
        return len(self.features)
    
    def __getitem__(self, idx):
        return {
            'features': self.features[idx],
            'disease': self.disease_targets[idx],
            'tests': self.test_targets[idx],
            'medications': self.med_targets[idx]
        }


class DatabaseClinicalTrainer:
    """
    Trainer class for Clinical Decision Support Model using database data
    """
    
    def __init__(self, config: dict, database_url: str = "sqlite:///./pdpcds_dev.db"):
        self.config = config
        self.database_url = database_url
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"🎯 Using device: {self.device}")
        
        # Database setup
        self.engine = create_engine(database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
        # Initialize model
        self.model = ClinicalDecisionModel(
            input_size=config['input_size'],
            hidden_size=config['hidden_size'],
            dropout_rate=config['dropout_rate'],
            num_diseases=config['num_diseases'],
            num_tests=config['num_tests'],
            num_medications=config['num_medications']
        ).to(self.device)
        
        # Initialize optimizer
        self.optimizer = optim.Adam(
            self.model.parameters(),
            lr=config['learning_rate'],
            weight_decay=config['weight_decay']
        )
        
        # Initialize scheduler
        self.scheduler = optim.lr_scheduler.StepLR(
            self.optimizer,
            step_size=config['scheduler_step'],
            gamma=config['scheduler_gamma']
        )
        
        # Loss functions
        self.disease_criterion = nn.CrossEntropyLoss()
        self.test_criterion = nn.BCEWithLogitsLoss()
        self.med_criterion = nn.BCEWithLogitsLoss()
        
        # Training history
        self.history = {
            'train_loss': [],
            'val_loss': [],
            'train_acc': [],
            'val_acc': [],
            'learning_rates': []
        }
    
    def load_data_from_database(self, condition_filter=None, quality_threshold=0.8):
        """
        Load training and validation data from database
        
        Args:
            condition_filter: List of conditions to include (None for all)
            quality_threshold: Minimum quality score to include
        """
        print("🔄 Loading data from database...")
        
        db = self.SessionLocal()
        try:
            # Load training data
            train_query = db.query(TrainingData).filter(
                TrainingData.quality_score >= quality_threshold
            )
            if condition_filter:
                train_query = train_query.filter(
                    TrainingData.condition_name.in_(condition_filter)
                )
            train_records = train_query.all()
            
            # Load validation data
            val_query = db.query(ValidationData).filter(
                ValidationData.quality_score >= quality_threshold
            )
            if condition_filter:
                val_query = val_query.filter(
                    ValidationData.condition_name.in_(condition_filter)
                )
            val_records = val_query.all()
            
            print(f"📚 Loaded {len(train_records)} training samples")
            print(f"🔍 Loaded {len(val_records)} validation samples")
            
            # Show condition distribution
            train_conditions = {}
            for record in train_records:
                train_conditions[record.condition_name] = train_conditions.get(record.condition_name, 0) + 1
            
            val_conditions = {}
            for record in val_records:
                val_conditions[record.condition_name] = val_conditions.get(record.condition_name, 0) + 1
            
            print("📊 Training condition distribution:")
            for condition, count in sorted(train_conditions.items()):
                val_count = val_conditions.get(condition, 0)
                print(f"  {condition}: {count} train, {val_count} val")
            
            return train_records, val_records
            
        finally:
            db.close()
    
    def create_dataloaders(self, train_records, val_records, preprocessor):
        """Create PyTorch DataLoaders from database records"""
        
        # Create datasets
        train_dataset = DatabaseClinicalDataset(train_records, preprocessor)
        val_dataset = DatabaseClinicalDataset(val_records, preprocessor)
        
        # Create dataloaders
        train_loader = DataLoader(
            train_dataset,
            batch_size=self.config['batch_size'],
            shuffle=True,
            num_workers=0  # Set to 0 for Windows compatibility
        )
        
        val_loader = DataLoader(
            val_dataset,
            batch_size=self.config['batch_size'],
            shuffle=False,
            num_workers=0
        )
        
        return train_loader, val_loader
    
    def train_epoch(self, train_loader):
        """Train for one epoch"""
        self.model.train()
        total_loss = 0
        correct_diseases = 0
        total_samples = 0
        
        for batch_idx, batch in enumerate(train_loader):
            # Move to device
            features = batch['features'].to(self.device)
            disease_targets = batch['disease'].to(self.device)
            test_targets = batch['tests'].to(self.device)
            med_targets = batch['medications'].to(self.device)
            
            # Forward pass
            self.optimizer.zero_grad()
            outputs = self.model(features)
            disease_logits = outputs["disease_logits"]
            test_logits = outputs["test_probabilities"]  # Already sigmoid applied
            med_logits = outputs["medication_probabilities"]  # Already sigmoid applied
            
            # Compute losses
            disease_loss = self.disease_criterion(disease_logits, disease_targets)
            # Use binary cross entropy for probabilities (not logits)
            test_loss = F.binary_cross_entropy(test_logits, test_targets)
            med_loss = F.binary_cross_entropy(med_logits, med_targets)
            
            # Combined loss
            total_loss_batch = disease_loss + 0.5 * test_loss + 0.5 * med_loss
            
            # Backward pass
            total_loss_batch.backward()
            self.optimizer.step()
            
            # Statistics
            total_loss += total_loss_batch.item()
            predicted = torch.argmax(disease_logits, dim=1)
            correct_diseases += (predicted == disease_targets).sum().item()
            total_samples += disease_targets.size(0)
        
        avg_loss = total_loss / len(train_loader)
        accuracy = correct_diseases / total_samples
        
        return avg_loss, accuracy
    
    def validate_epoch(self, val_loader):
        """Validate for one epoch"""
        self.model.eval()
        total_loss = 0
        correct_diseases = 0
        total_samples = 0
        
        with torch.no_grad():
            for batch in val_loader:
                # Move to device
                features = batch['features'].to(self.device)
                disease_targets = batch['disease'].to(self.device)
                test_targets = batch['tests'].to(self.device)
                med_targets = batch['medications'].to(self.device)
                
                # Forward pass
                outputs = self.model(features)
                disease_logits = outputs["disease_logits"]
                test_logits = outputs["test_probabilities"]  # Already sigmoid applied
                med_logits = outputs["medication_probabilities"]  # Already sigmoid applied
                
                # Compute losses
                disease_loss = self.disease_criterion(disease_logits, disease_targets)
                # Use binary cross entropy for probabilities (not logits)
                test_loss = F.binary_cross_entropy(test_logits, test_targets)
                med_loss = F.binary_cross_entropy(med_logits, med_targets)
                
                # Combined loss
                total_loss_batch = disease_loss + 0.5 * test_loss + 0.5 * med_loss
                
                # Statistics
                total_loss += total_loss_batch.item()
                predicted = torch.argmax(disease_logits, dim=1)
                correct_diseases += (predicted == disease_targets).sum().item()
                total_samples += disease_targets.size(0)
        
        avg_loss = total_loss / len(val_loader)
        accuracy = correct_diseases / total_samples
        
        return avg_loss, accuracy
    
    def train(self, num_epochs: int, save_path: str = "clinical_model_v2.0.pth"):
        """Train the model using database data"""
        
        print("🚀 Starting database-based training...")
        
        # Load data from database
        train_records, val_records = self.load_data_from_database()
        
        if len(train_records) == 0 or len(val_records) == 0:
            raise ValueError("No training or validation data found in database!")
        
        # Initialize preprocessor and fit on training data
        print("🔧 Initializing preprocessor...")
        preprocessor = DataPreprocessor(training_mode=True)
        
        # Prepare training samples DataFrame for preprocessor
        train_data = []
        for record in train_records:
            row = {
                'age': record.age,
                'sex': record.sex,
                'vital_temperature_c': record.vital_temperature_c,
                'vital_heart_rate': record.vital_heart_rate,
                'vital_blood_pressure_systolic': record.vital_blood_pressure_systolic,
                'vital_blood_pressure_diastolic': record.vital_blood_pressure_diastolic,
                'symptom_list': json.dumps(record.symptom_list) if isinstance(record.symptom_list, list) else str(record.symptom_list),
                'pmh_list': json.dumps(record.pmh_list) if isinstance(record.pmh_list, list) else str(record.pmh_list),
                'free_text_notes': record.free_text_notes or ""
            }
            train_data.append(row)
        
        train_df = pd.DataFrame(train_data)
        preprocessor.fit_training_data(train_df)
        
        # Update model input size based on preprocessor
        actual_input_size = preprocessor.get_feature_dim()
        print(f"📏 Updating model input size to: {actual_input_size}")
        
        # Test preprocessing on one sample to get actual feature size
        test_sample = {
            'age': train_records[0].age,
            'sex': train_records[0].sex,
            'vital_temperature_c': train_records[0].vital_temperature_c,
            'vital_heart_rate': train_records[0].vital_heart_rate,
            'vital_blood_pressure_systolic': train_records[0].vital_blood_pressure_systolic,
            'vital_blood_pressure_diastolic': train_records[0].vital_blood_pressure_diastolic,
            'symptom_list': train_records[0].symptom_list,
            'pmh_list': train_records[0].pmh_list,
            'free_text_notes': train_records[0].free_text_notes or ""
        }
        test_features = preprocessor.preprocess_input(test_sample)
        if isinstance(test_features, torch.Tensor):
            test_features = test_features.numpy()
        if len(test_features.shape) > 1:
            test_features = test_features.flatten()
        
        actual_input_size = len(test_features)
        print(f"📏 Actual feature dimension after preprocessing: {actual_input_size}")
        
        # Recreate model with correct input size
        self.model = ClinicalDecisionModel(
            input_size=actual_input_size,
            hidden_size=self.config['hidden_size'],
            dropout_rate=self.config['dropout_rate'],
            num_diseases=self.config['num_diseases'],
            num_tests=self.config['num_tests'],
            num_medications=self.config['num_medications']
        ).to(self.device)
        
        # Recreate optimizer for new model
        self.optimizer = optim.Adam(
            self.model.parameters(),
            lr=self.config['learning_rate'],
            weight_decay=self.config['weight_decay']
        )
        
        # Create dataloaders
        train_loader, val_loader = self.create_dataloaders(train_records, val_records, preprocessor)
        
        print(f"🎯 Training for {num_epochs} epochs...")
        
        best_val_acc = 0.0
        
        for epoch in range(num_epochs):
            # Training
            train_loss, train_acc = self.train_epoch(train_loader)
            
            # Validation
            val_loss, val_acc = self.validate_epoch(val_loader)
            
            # Update scheduler
            self.scheduler.step()
            current_lr = self.scheduler.get_last_lr()[0]
            
            # Store history
            self.history['train_loss'].append(train_loss)
            self.history['val_loss'].append(val_loss)
            self.history['train_acc'].append(train_acc)
            self.history['val_acc'].append(val_acc)
            self.history['learning_rates'].append(current_lr)
            
            # Print progress
            print(f"Epoch {epoch+1}/{num_epochs} - "
                  f"Train Loss: {train_loss:.4f} - Train Acc: {train_acc:.4f} - "
                  f"Val Loss: {val_loss:.4f} - Val Acc: {val_acc:.4f} - "
                  f"LR: {current_lr:.6f}")
            
            # Save best model
            if val_acc > best_val_acc:
                best_val_acc = val_acc
                
                # Save model, preprocessor, and metadata
                torch.save({
                    'model_state_dict': self.model.state_dict(),
                    'preprocessor': preprocessor,
                    'config': self.config,
                    'input_size': actual_input_size,
                    'val_accuracy': val_acc,
                    'epoch': epoch + 1,
                    'history': self.history
                }, save_path)
                
                print(f"💾 Saved improved model (val_acc: {val_acc:.4f})")
        
        print(f"\n🎉 Training completed!")
        print(f"📊 Best validation accuracy: {best_val_acc:.4f}")
        print(f"💾 Model saved to: {save_path}")
        
        return self.history


def main():
    """Main training function"""
    
    # Training configuration
    config = {
        'input_size': 106,  # Will be updated based on actual preprocessor output
        'hidden_size': 512,
        'dropout_rate': 0.3,
        'num_diseases': 59,  # Number of ICD-10 codes in database
        'num_tests': 25,     # Number of medical tests
        'num_medications': 18,  # Number of medications
        'learning_rate': 0.001,
        'weight_decay': 1e-5,
        'batch_size': 32,
        'scheduler_step': 10,
        'scheduler_gamma': 0.9
    }
    
    print("🏥 Clinical Decision Support System - Database Training")
    print("=" * 60)
    
    # Initialize trainer
    trainer = DatabaseClinicalTrainer(config)
    
    # Train model
    history = trainer.train(
        num_epochs=30,
        save_path="training/models/clinical_model_db_v2.0.pth"
    )
    
    # Save training history
    history_path = f"training/history/training_history_db_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    os.makedirs(os.path.dirname(history_path), exist_ok=True)
    
    # Convert numpy arrays to lists for JSON serialization
    serializable_history = {}
    for key, values in history.items():
        if isinstance(values, list):
            serializable_history[key] = values
        else:
            serializable_history[key] = values.tolist() if hasattr(values, 'tolist') else values
    
    with open(history_path, 'w') as f:
        json.dump(serializable_history, f, indent=2)
    
    print(f"📈 Training history saved to: {history_path}")


if __name__ == "__main__":
    main()