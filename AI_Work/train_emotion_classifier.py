"""
Train Emotion Classifier on DepressionEmo Dataset
Trains DistilBERT/mobileBERT to predict depression-relevant emotions
"""
import os
import pandas as pd
import numpy as np
from pathlib import Path
import json
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# ML Libraries
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, f1_score
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import (
    AutoTokenizer, 
    AutoModelForSequenceClassification,
    TrainingArguments,
    Trainer,
    EarlyStoppingCallback
)
import joblib

# Set device
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Using device: {device}")

# Paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"
MODELS_DIR.mkdir(exist_ok=True)
RESULTS_DIR = BASE_DIR / "results"
RESULTS_DIR.mkdir(exist_ok=True)

# Depression emotions to predict
DEPRESSION_EMOTIONS = [
    'sadness',
    'emptiness',
    'hopelessness',
    'loneliness',
    'anger',
    'guilt',
    'shame',
    'fear'
]


class MultiLabelEmotionDataset(Dataset):
    """Custom dataset for multi-label emotion classification"""
    def __init__(self, texts, labels, tokenizer, max_length=256):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length
    
    def __len__(self):
        return len(self.texts)
    
    def __getitem__(self, idx):
        text = str(self.texts[idx])
        label = self.labels[idx]
        
        encoding = self.tokenizer(
            text,
            truncation=True,
            padding='max_length',
            max_length=self.max_length,
            return_tensors='pt'
        )
        
        return {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'labels': torch.tensor(label, dtype=torch.float)
        }


def load_depression_emo_data():
    """Load prepared DepressionEmo data"""
    print("\n" + "="*60)
    print("Loading DepressionEmo Data")
    print("="*60)
    
    # Try prepared data first
    prepared_path = DATA_DIR / "depression_emo_prepared.csv"
    if prepared_path.exists():
        print(f"\nLoading from: {prepared_path}")
        df = pd.read_csv(prepared_path)
        print(f"Shape: {df.shape}")
        print(f"Columns: {df.columns.tolist()}")
        return df
    
    # Try raw data
    depression_emo_dir = DATA_DIR / "DepressionEmo"
    if depression_emo_dir.exists():
        csv_files = list(depression_emo_dir.glob("*.csv"))
        if csv_files:
            print(f"\nLoading from: {csv_files[0]}")
            df = pd.read_csv(csv_files[0])
            print(f"Shape: {df.shape}")
            print(f"Columns: {df.columns.tolist()}")
            
            # Prepare it
            from data_loaders import prepare_depression_emo_data
            df = prepare_depression_emo_data(df)
            return df
    
    raise FileNotFoundError(
        f"DepressionEmo data not found. Please run data_loaders.py first.\n"
        f"Expected location: {prepared_path} or {depression_emo_dir}"
    )


def prepare_emotion_labels(df):
    """Prepare emotion labels from dataframe"""
    print("\n" + "="*60)
    print("Preparing Emotion Labels")
    print("="*60)
    
    # Get text column
    if 'text' not in df.columns:
        raise ValueError("'text' column not found in dataframe")
    
    texts = df['text'].astype(str).values
    
    # Get emotion columns
    emotion_labels = []
    available_emotions = []
    
    for emotion in DEPRESSION_EMOTIONS:
        if emotion in df.columns:
            labels = df[emotion].values
            # Convert to binary if needed
            if labels.dtype == 'object':
                labels = (labels.astype(str).str.lower() == 'true').astype(float)
            else:
                labels = labels.astype(float)
            emotion_labels.append(labels)
            available_emotions.append(emotion)
            print(f"  {emotion}: {labels.sum()} positive samples ({labels.sum()/len(labels)*100:.2f}%)")
    
    if not emotion_labels:
        raise ValueError("No emotion columns found in dataframe")
    
    # Stack into matrix: (n_samples, n_emotions)
    labels_matrix = np.stack(emotion_labels, axis=1)
    
    print(f"\nLabel matrix shape: {labels_matrix.shape}")
    print(f"Available emotions: {available_emotions}")
    
    return texts, labels_matrix, available_emotions


def train_emotion_classifier(texts, labels, emotion_names, model_name='distilbert-base-uncased'):
    """Train multi-label emotion classifier"""
    print("\n" + "="*60)
    print(f"Training Emotion Classifier: {model_name}")
    print("="*60)
    
    # Split data
    X_train, X_temp, y_train, y_temp = train_test_split(
        texts, labels, test_size=0.3, random_state=42
    )
    X_val, X_test, y_val, y_test = train_test_split(
        X_temp, y_temp, test_size=0.5, random_state=42
    )
    
    print(f"\nData splits:")
    print(f"  Train: {len(X_train)} samples")
    print(f"  Validation: {len(X_val)} samples")
    print(f"  Test: {len(X_test)} samples")
    
    # Load tokenizer and model
    print(f"\nLoading tokenizer and model...")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    
    num_labels = len(emotion_names)
    model = AutoModelForSequenceClassification.from_pretrained(
        model_name,
        num_labels=num_labels,
        problem_type="multi_label_classification"
    )
    model.to(device)
    
    # Create datasets
    train_dataset = MultiLabelEmotionDataset(X_train, y_train, tokenizer)
    val_dataset = MultiLabelEmotionDataset(X_val, y_val, tokenizer)
    test_dataset = MultiLabelEmotionDataset(X_test, y_test, tokenizer)
    
    # Training arguments
    training_args = TrainingArguments(
        output_dir=str(MODELS_DIR / "emotion_classifier_checkpoints"),
        num_train_epochs=5,
        per_device_train_batch_size=16,
        per_device_eval_batch_size=16,
        warmup_steps=500,
        weight_decay=0.01,
        logging_dir=str(RESULTS_DIR / "emotion_classifier_logs"),
        logging_steps=100,
        eval_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="f1",
        greater_is_better=True,
        save_total_limit=2,
        learning_rate=2e-5,
        fp16=torch.cuda.is_available(),
    )
    
    # Compute metrics function for multi-label
    def compute_metrics(eval_pred):
        predictions, labels = eval_pred
        # Apply sigmoid to get probabilities
        sigmoid = torch.nn.Sigmoid()
        probs = sigmoid(torch.tensor(predictions))
        # Threshold at 0.5
        predictions_binary = (probs > 0.5).float().numpy()
        
        # Calculate metrics
        accuracy = accuracy_score(labels, predictions_binary)
        f1_micro = f1_score(labels, predictions_binary, average='micro')
        f1_macro = f1_score(labels, predictions_binary, average='macro')
        
        return {
            'accuracy': accuracy,
            'f1_micro': f1_micro,
            'f1_macro': f1_macro
        }
    
    # Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        compute_metrics=compute_metrics,
        callbacks=[EarlyStoppingCallback(early_stopping_patience=2)]
    )
    
    # Train
    print("\nStarting training...")
    train_result = trainer.train()
    
    # Evaluate on test set
    print("\nEvaluating on test set...")
    test_results = trainer.evaluate(test_dataset)
    
    # Get predictions for detailed analysis
    predictions = trainer.predict(test_dataset)
    sigmoid = torch.nn.Sigmoid()
    probs = sigmoid(torch.tensor(predictions.predictions))
    y_pred_binary = (probs > 0.5).float().numpy()
    
    # Per-emotion metrics
    print("\n" + "="*60)
    print("Test Set Results:")
    print("="*60)
    print(f"\nOverall Accuracy: {test_results['eval_accuracy']:.4f}")
    print(f"F1 Score (Micro): {test_results['eval_f1_micro']:.4f}")
    print(f"F1 Score (Macro): {test_results['eval_f1_macro']:.4f}")
    
    print("\nPer-Emotion Performance:")
    for i, emotion in enumerate(emotion_names):
        emotion_f1 = f1_score(y_test[:, i], y_pred_binary[:, i])
        emotion_precision = np.sum((y_pred_binary[:, i] == 1) & (y_test[:, i] == 1)) / (np.sum(y_pred_binary[:, i] == 1) + 1e-8)
        emotion_recall = np.sum((y_pred_binary[:, i] == 1) & (y_test[:, i] == 1)) / (np.sum(y_test[:, i] == 1) + 1e-8)
        print(f"  {emotion}:")
        print(f"    F1: {emotion_f1:.4f}, Precision: {emotion_precision:.4f}, Recall: {emotion_recall:.4f}")
    
    # Save model and tokenizer
    model_save_path = MODELS_DIR / "emotion_classifier"
    model_save_path.mkdir(exist_ok=True)
    
    print(f"\nSaving model to {model_save_path}...")
    trainer.save_model(str(model_save_path))
    tokenizer.save_pretrained(str(model_save_path))
    
    # Save emotion names
    emotion_info = {
        'emotion_names': emotion_names,
        'num_emotions': num_labels
    }
    emotion_info_path = model_save_path / "emotion_info.json"
    with open(emotion_info_path, 'w') as f:
        json.dump(emotion_info, f, indent=2)
    print(f"Saved emotion info to {emotion_info_path}")
    
    # Save results
    results = {
        'model_name': model_name,
        'num_emotions': num_labels,
        'emotion_names': emotion_names,
        'train_samples': len(X_train),
        'val_samples': len(X_val),
        'test_samples': len(X_test),
        'test_accuracy': float(test_results['eval_accuracy']),
        'test_f1_micro': float(test_results['eval_f1_micro']),
        'test_f1_macro': float(test_results['eval_f1_macro']),
        'training_date': datetime.now().isoformat()
    }
    
    results_path = RESULTS_DIR / "emotion_classifier_results.json"
    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"Saved results to {results_path}")
    
    return model, tokenizer, emotion_names, results


def main():
    """Main training pipeline"""
    print("\n" + "="*60)
    print("Emotion Classifier Training Pipeline")
    print("="*60)
    
    try:
        # Load data
        df = load_depression_emo_data()
        
        # Prepare labels
        texts, labels, emotion_names = prepare_emotion_labels(df)
        
        # Train model
        model, tokenizer, emotion_names, results = train_emotion_classifier(
            texts, 
            labels, 
            emotion_names,
            model_name='distilbert-base-uncased'  # Can use 'google/mobilebert-uncased' for smaller model
        )
        
        print("\n" + "="*60)
        print("Training Complete!")
        print("="*60)
        print(f"\nModel saved to: {MODELS_DIR / 'emotion_classifier'}")
        print(f"Results saved to: {RESULTS_DIR / 'emotion_classifier_results.json'}")
        print(f"\nFinal Test Accuracy: {results['test_accuracy']:.4f}")
        print(f"Final Test F1 (Micro): {results['test_f1_micro']:.4f}")
        print(f"Final Test F1 (Macro): {results['test_f1_macro']:.4f}")
        
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    main()

