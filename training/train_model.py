"""
PyTorch Model Training Script for Clinical Decision Support System
Trains the ClinicalDecisionModel on synthetic medical data
"""

import os
import json
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from sklearn.metrics import classification_report, accuracy_score, f1_score
# import matplotlib.pyplot as plt  # Optional for plotting
from datetime import datetime
import argparse

# Add parent directory to path
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.ml.model import ClinicalDecisionModel
from app.ml.preprocessor import DataPreprocessor


class ClinicalDataset(Dataset):
    """
    Custom PyTorch Dataset for clinical data
    """
    
    def __init__(self, features, disease_targets, test_targets, med_targets):
        self.features = features
        self.disease_targets = disease_targets
        self.test_targets = test_targets
        self.med_targets = med_targets
    
    def __len__(self):
        return len(self.features)
    
    def __getitem__(self, idx):
        return {
            'features': self.features[idx],
            'disease': self.disease_targets[idx],
            'tests': self.test_targets[idx],
            'medications': self.med_targets[idx]
        }


class ClinicalTrainer:
    """
    Trainer class for Clinical Decision Support Model
    """
    
    def __init__(self, config: dict):
        self.config = config
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"🎯 Using device: {self.device}")
        
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
    
    def train_epoch(self, train_loader):
        """Train for one epoch"""
        self.model.train()
        total_loss = 0
        total_samples = 0
        correct_diseases = 0
        
        for batch_idx, batch in enumerate(train_loader):
            # Move data to device
            features = batch['features'].to(self.device)
            disease_targets = batch['disease'].to(self.device)
            test_targets = batch['tests'].to(self.device)
            med_targets = batch['medications'].to(self.device)
            
            # Zero gradients
            self.optimizer.zero_grad()
            
            # Forward pass
            outputs = self.model(features)
            disease_pred = outputs['disease_logits']  # Use logits for classification loss
            test_pred = outputs['test_probabilities']
            med_pred = outputs['medication_probabilities']
            
            # Calculate losses
            disease_loss = self.disease_criterion(disease_pred, disease_targets)
            test_loss = self.test_criterion(test_pred, test_targets)
            med_loss = self.med_criterion(med_pred, med_targets)
            
            # Combined loss with weights
            total_batch_loss = (
                self.config['disease_weight'] * disease_loss +
                self.config['test_weight'] * test_loss +
                self.config['med_weight'] * med_loss
            )
            
            # Backward pass
            total_batch_loss.backward()
            torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
            self.optimizer.step()
            
            # Statistics
            total_loss += total_batch_loss.item()
            total_samples += features.size(0)
            
            # Disease accuracy
            _, predicted = torch.max(disease_pred, 1)
            correct_diseases += (predicted == disease_targets).sum().item()
            
            if batch_idx % 50 == 0:
                print(f'   Batch {batch_idx:3d}: Loss={total_batch_loss.item():.4f}, '
                      f'Disease Acc={100.*correct_diseases/total_samples:.1f}%')
        
        avg_loss = total_loss / len(train_loader)
        avg_acc = correct_diseases / total_samples
        
        return avg_loss, avg_acc
    
    def validate_epoch(self, val_loader):
        """Validate for one epoch"""
        self.model.eval()
        total_loss = 0
        total_samples = 0
        correct_diseases = 0
        
        all_disease_preds = []
        all_disease_targets = []
        
        with torch.no_grad():
            for batch in val_loader:
                # Move data to device
                features = batch['features'].to(self.device)
                disease_targets = batch['disease'].to(self.device)
                test_targets = batch['tests'].to(self.device)
                med_targets = batch['medications'].to(self.device)
                
                # Forward pass
                outputs = self.model(features)
                disease_pred = outputs['disease_logits']  # Use logits for classification loss
                test_pred = outputs['test_probabilities']
                med_pred = outputs['medication_probabilities']
                
                # Calculate losses
                disease_loss = self.disease_criterion(disease_pred, disease_targets)
                test_loss = self.test_criterion(test_pred, test_targets)
                med_loss = self.med_criterion(med_pred, med_targets)
                
                total_batch_loss = (
                    self.config['disease_weight'] * disease_loss +
                    self.config['test_weight'] * test_loss +
                    self.config['med_weight'] * med_loss
                )
                
                # Statistics
                total_loss += total_batch_loss.item()
                total_samples += features.size(0)
                
                # Disease accuracy
                _, predicted = torch.max(disease_pred, 1)
                correct_diseases += (predicted == disease_targets).sum().item()
                
                # Store predictions for detailed metrics
                all_disease_preds.extend(predicted.cpu().numpy())
                all_disease_targets.extend(disease_targets.cpu().numpy())
        
        avg_loss = total_loss / len(val_loader)
        avg_acc = correct_diseases / total_samples
        
        return avg_loss, avg_acc, all_disease_preds, all_disease_targets
    
    def train(self, train_loader, val_loader, num_epochs):
        """Main training loop"""
        print(f"🚀 Starting training for {num_epochs} epochs...")
        print(f"📊 Model parameters: {sum(p.numel() for p in self.model.parameters()):,}")
        
        best_val_loss = float('inf')
        patience = self.config['patience']
        patience_counter = 0
        
        for epoch in range(num_epochs):
            print(f"\n🔄 Epoch {epoch+1}/{num_epochs}")
            print("-" * 50)
            
            # Training
            train_loss, train_acc = self.train_epoch(train_loader)
            
            # Validation
            val_loss, val_acc, val_preds, val_targets = self.validate_epoch(val_loader)
            
            # Learning rate scheduling
            self.scheduler.step()
            current_lr = self.optimizer.param_groups[0]['lr']
            
            # Store history
            self.history['train_loss'].append(train_loss)
            self.history['val_loss'].append(val_loss)
            self.history['train_acc'].append(train_acc)
            self.history['val_acc'].append(val_acc)
            self.history['learning_rates'].append(current_lr)
            
            # Print epoch results
            print(f"✅ Epoch {epoch+1} Results:")
            print(f"   Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.4f}")
            print(f"   Val Loss:   {val_loss:.4f}, Val Acc:   {val_acc:.4f}")
            print(f"   Learning Rate: {current_lr:.6f}")
            
            # Early stopping check
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                patience_counter = 0
                # Save best model
                self.save_checkpoint(epoch, is_best=True)
                print(f"   💾 New best model saved! (Val Loss: {val_loss:.4f})")
            else:
                patience_counter += 1
                print(f"   ⏳ Patience: {patience_counter}/{patience}")
            
            if patience_counter >= patience:
                print(f"\n⏹️ Early stopping triggered after {epoch+1} epochs")
                break
            
            # Save regular checkpoint every 10 epochs
            if (epoch + 1) % 10 == 0:
                self.save_checkpoint(epoch, is_best=False)
        
        print("\n🎉 Training completed!")
        self.plot_training_history()
        return self.history
    
    def save_checkpoint(self, epoch, is_best=False):
        """Save model checkpoint"""
        checkpoint = {
            'epoch': epoch,
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'scheduler_state_dict': self.scheduler.state_dict(),
            'config': self.config,
            'history': self.history
        }
        
        # Save checkpoint
        if is_best:
            checkpoint_path = os.path.join(self.config['checkpoint_dir'], 'best_model.pth')
            final_path = os.path.join(self.config['model_dir'], 'clinical_model_v1.0.pth')
        else:
            checkpoint_path = os.path.join(self.config['checkpoint_dir'], f'checkpoint_epoch_{epoch+1}.pth')
            final_path = None
        
        torch.save(checkpoint, checkpoint_path)
        
        # Also save to models directory if best model
        if is_best and final_path:
            torch.save(self.model.state_dict(), final_path)
            print(f"   📁 Model also saved to: {final_path}")
    
    def plot_training_history(self):
        """Plot training history - disabled (requires matplotlib)"""
        print("📈 Training history plotting disabled (matplotlib not available)")
        print("📊 Training metrics summary:")
        print(f"   Final train loss: {self.history['train_loss'][-1]:.4f}")
        print(f"   Final val loss: {self.history['val_loss'][-1]:.4f}")
        print(f"   Final train acc: {self.history['train_acc'][-1]:.4f}")
        print(f"   Final val acc: {self.history['val_acc'][-1]:.4f}")
        
        # Save history as JSON instead
        history_path = os.path.join(self.config['checkpoint_dir'], 'training_history.json')
        with open(history_path, 'w') as f:
            json.dump(self.history, f, indent=2)
        print(f"� Training history saved: {history_path}")


def load_training_data(data_dir: str):
    """Load training and validation datasets"""
    train_path = os.path.join(data_dir, "train_dataset.csv")
    val_path = os.path.join(data_dir, "val_dataset.csv")
    
    if not os.path.exists(train_path) or not os.path.exists(val_path):
        raise FileNotFoundError(f"Training data not found. Please run generate_dataset.py first.")
    
    train_df = pd.read_csv(train_path)
    val_df = pd.read_csv(val_path)
    
    # Convert string representations of lists back to actual lists
    for col in ['symptom_list', 'pmh_list', 'current_medications', 'allergies', 'target_tests', 'target_medications']:
        if col in train_df.columns:
            train_df[col] = train_df[col].apply(lambda x: eval(x) if isinstance(x, str) else x)
            val_df[col] = val_df[col].apply(lambda x: eval(x) if isinstance(x, str) else x)
    
    print(f"📊 Loaded training data:")
    print(f"   Training samples: {len(train_df)}")
    print(f"   Validation samples: {len(val_df)}")
    
    return train_df, val_df


def create_data_loaders(train_df, val_df, preprocessor, batch_size=32):
    """Create PyTorch data loaders"""
    
    # Fit preprocessor on training data
    preprocessor.fit_training_data(train_df)
    
    # Transform datasets
    train_x, train_y_disease, train_y_tests, train_y_meds = preprocessor.transform_training_batch(train_df)
    val_x, val_y_disease, val_y_tests, val_y_meds = preprocessor.transform_training_batch(val_df)
    
    # Create datasets
    train_dataset = ClinicalDataset(train_x, train_y_disease, train_y_tests, train_y_meds)
    val_dataset = ClinicalDataset(val_x, val_y_disease, val_y_tests, val_y_meds)
    
    # Create data loaders
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)
    
    print(f"🔄 Created data loaders:")
    print(f"   Batch size: {batch_size}")
    print(f"   Training batches: {len(train_loader)}")
    print(f"   Validation batches: {len(val_loader)}")
    print(f"   Feature dimension: {train_x.shape[1]}")
    
    return train_loader, val_loader, preprocessor


def main():
    """Main training function"""
    parser = argparse.ArgumentParser(description='Train Clinical Decision Support Model')
    parser.add_argument('--epochs', type=int, default=50, help='Number of training epochs')
    parser.add_argument('--batch_size', type=int, default=32, help='Batch size for training')
    parser.add_argument('--lr', type=float, default=0.001, help='Learning rate')
    parser.add_argument('--data_dir', type=str, default='./training/data', help='Data directory')
    args = parser.parse_args()
    
    # Training configuration
    config = {
        # Model architecture
        'input_size': 150,  # Will be updated based on actual features
        'hidden_size': 512,
        'dropout_rate': 0.3,
        'num_diseases': 59,  # Based on our ICD-10 codes
        'num_tests': 25,     # Based on our medical tests
        'num_medications': 18, # Based on our medications
        
        # Training parameters
        'batch_size': args.batch_size,
        'learning_rate': args.lr,
        'weight_decay': 1e-5,
        'num_epochs': args.epochs,
        
        # Loss weights
        'disease_weight': 1.0,
        'test_weight': 0.5,
        'med_weight': 0.5,
        
        # Scheduler
        'scheduler_step': 10,
        'scheduler_gamma': 0.8,
        
        # Early stopping
        'patience': 10,
        
        # Directories
        'data_dir': args.data_dir,
        'model_dir': './models',
        'checkpoint_dir': './training/checkpoints'
    }
    
    # Create directories
    os.makedirs(config['model_dir'], exist_ok=True)
    os.makedirs(config['checkpoint_dir'], exist_ok=True)
    
    print("🚀 Clinical Decision Support Model Training")
    print("=" * 50)
    print(f"Configuration:")
    for key, value in config.items():
        print(f"  {key}: {value}")
    print("=" * 50)
    
    try:
        # Load data
        print("\n📂 Loading training data...")
        train_df, val_df = load_training_data(config['data_dir'])
        
        # Create preprocessor and data loaders
        print("\n🔄 Creating data loaders...")
        preprocessor = DataPreprocessor(training_mode=True)
        train_loader, val_loader, fitted_preprocessor = create_data_loaders(
            train_df, val_df, preprocessor, config['batch_size']
        )
        
        # Update input size based on actual features
        sample_batch = next(iter(train_loader))
        actual_input_size = sample_batch['features'].shape[1]
        config['input_size'] = actual_input_size
        print(f"🎯 Updated input size: {actual_input_size}")
        
        # Initialize trainer
        print("\n🏗️ Initializing trainer...")
        trainer = ClinicalTrainer(config)
        
        # Save preprocessor
        preprocessor_path = os.path.join(config['model_dir'], 'preprocessor.pkl')
        import pickle
        with open(preprocessor_path, 'wb') as f:
            pickle.dump(fitted_preprocessor, f)
        print(f"💾 Preprocessor saved: {preprocessor_path}")
        
        # Start training
        print("\n🎯 Starting training...")
        history = trainer.train(train_loader, val_loader, config['num_epochs'])
        
        # Save training config and history
        results = {
            'config': config,
            'history': history,
            'timestamp': datetime.now().isoformat()
        }
        
        results_path = os.path.join(config['checkpoint_dir'], 'training_results.json')
        with open(results_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n🎉 Training completed successfully!")
        print(f"📁 Results saved to: {results_path}")
        print(f"🏆 Best model saved to: {config['model_dir']}/clinical_model_v1.0.pth")
        
    except Exception as e:
        print(f"❌ Training failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())