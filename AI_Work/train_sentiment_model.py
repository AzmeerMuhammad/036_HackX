"""
Sentiment Analysis Model Training Pipeline
Trains a high-accuracy multi-class sentiment classifier using transformer models.
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
from sklearn.preprocessing import LabelEncoder
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


class SentimentDataset(Dataset):
    """Custom dataset for sentiment analysis"""
    def __init__(self, texts, labels, tokenizer, max_length=128):
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
            'labels': torch.tensor(label, dtype=torch.long)
        }


def read_csv_with_encoding(file_path):
    """Read CSV file trying multiple encodings"""
    encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252', 'windows-1252']
    
    for encoding in encodings:
        try:
            df = pd.read_csv(file_path, encoding=encoding)
            print(f"Successfully loaded {file_path.name} with encoding: {encoding}")
            return df
        except UnicodeDecodeError:
            continue
        except Exception as e:
            print(f"Error loading {file_path.name} with encoding {encoding}: {e}")
            continue
    
    # If all encodings fail, try with error handling
    try:
        df = pd.read_csv(file_path, encoding='utf-8', errors='replace')
        print(f"Loaded {file_path.name} with UTF-8 and error replacement")
        return df
    except Exception as e:
        raise ValueError(f"Could not load {file_path.name} with any encoding. Last error: {e}")


def load_and_explore_data(data_dir):
    """Load dataset and explore its structure"""
    print("\n" + "="*60)
    print("Loading and exploring dataset...")
    print("="*60)
    
    # Look for train.csv and test.csv specifically
    train_path = data_dir / "train.csv"
    test_path = data_dir / "test.csv"
    
    if not train_path.exists():
        raise FileNotFoundError(f"train.csv not found in {data_dir}. Please run sentiment-data.py first.")
    
    # Load training data
    print(f"\nLoading train.csv...")
    df_train = read_csv_with_encoding(train_path)
    print(f"Shape: {df_train.shape}")
    print(f"\nColumns: {df_train.columns.tolist()}")
    print(f"\nFirst few rows:")
    print(df_train.head())
    print(f"\nData types:")
    print(df_train.dtypes)
    print(f"\nMissing values:")
    print(df_train.isnull().sum())
    
    # Check for text and sentiment columns
    text_col = None
    sentiment_col = None
    
    # Check for exact column names first
    if 'text' in df_train.columns:
        text_col = 'text'
    if 'sentiment' in df_train.columns:
        sentiment_col = 'sentiment'
    
    # If not found, try case-insensitive search
    if text_col is None:
        for col in df_train.columns:
            if col.lower() == 'text':
                text_col = col
                break
    
    if sentiment_col is None:
        for col in df_train.columns:
            if col.lower() == 'sentiment':
                sentiment_col = col
                break
    
    if text_col is None or sentiment_col is None:
        print("\nAvailable columns:", df_train.columns.tolist())
        raise ValueError(f"Could not find text and sentiment columns. Found text_col={text_col}, sentiment_col={sentiment_col}")
    
    print(f"\nUsing columns:")
    print(f"  Text: {text_col}")
    print(f"  Sentiment: {sentiment_col}")
    
    # Extract relevant columns
    df_clean = df_train[[text_col, sentiment_col]].copy()
    df_clean.columns = ['text', 'sentiment']
    
    # Remove null values
    df_clean = df_clean.dropna()
    
    # Remove empty texts
    df_clean = df_clean[df_clean['text'].astype(str).str.strip() != '']
    
    print(f"\nAfter cleaning:")
    print(f"  Shape: {df_clean.shape}")
    print(f"\nSentiment distribution:")
    print(df_clean['sentiment'].value_counts())
    print(f"\nNumber of unique sentiments: {df_clean['sentiment'].nunique()}")
    
    # Load test data if available
    test_df_clean = None
    if test_path.exists():
        print(f"\n" + "="*60)
        print("Loading test.csv for final evaluation...")
        print("="*60)
        df_test = read_csv_with_encoding(test_path)
        print(f"Test shape: {df_test.shape}")
        
        # Extract same columns
        test_df_clean = df_test[[text_col, sentiment_col]].copy()
        test_df_clean.columns = ['text', 'sentiment']
        test_df_clean = test_df_clean.dropna()
        test_df_clean = test_df_clean[test_df_clean['text'].astype(str).str.strip() != '']
        print(f"Test data after cleaning: {test_df_clean.shape}")
        print(f"\nTest sentiment distribution:")
        print(test_df_clean['sentiment'].value_counts())
    
    return df_clean, test_df_clean


def preprocess_data(df, test_df=None, label_encoder=None):
    """Preprocess the data"""
    print("\n" + "="*60)
    print("Preprocessing data...")
    print("="*60)
    
    # Clean text
    df['text'] = df['text'].astype(str)
    df['text'] = df['text'].str.strip()
    
    # Encode labels - fit on training data, transform both train and test
    if label_encoder is None:
        label_encoder = LabelEncoder()
        df['label_encoded'] = label_encoder.fit_transform(df['sentiment'])
    else:
        df['label_encoded'] = label_encoder.transform(df['sentiment'])
    
    print(f"\nLabel mapping:")
    for i, label in enumerate(label_encoder.classes_):
        print(f"  {i}: {label}")
    
    # Preprocess test data if provided
    test_df_processed = None
    if test_df is not None:
        test_df = test_df.copy()
        test_df['text'] = test_df['text'].astype(str)
        test_df['text'] = test_df['text'].str.strip()
        
        # Filter out test samples with labels not seen in training
        train_labels = set(label_encoder.classes_)
        test_labels = set(test_df['sentiment'].unique())
        unknown_labels = test_labels - train_labels
        
        if unknown_labels:
            print(f"\nWarning: Found {len(unknown_labels)} label(s) in test set not in training: {unknown_labels}")
            print(f"Filtering out {len(test_df[test_df['sentiment'].isin(unknown_labels)])} samples with unknown labels")
            test_df = test_df[test_df['sentiment'].isin(train_labels)]
        
        # Only transform, don't fit on test data
        test_df['label_encoded'] = label_encoder.transform(test_df['sentiment'])
        test_df_processed = test_df
        print(f"Test data after filtering: {len(test_df_processed)} samples")
    
    return df, test_df_processed, label_encoder


def train_model(df, label_encoder, test_df=None, model_name='distilbert-base-uncased'):
    """Train the sentiment classification model"""
    print("\n" + "="*60)
    print(f"Training model: {model_name}")
    print("="*60)
    
    # Split data - use provided test_df if available, otherwise split from train
    X = df['text'].values
    y = df['label_encoded'].values
    
    if test_df is not None:
        # Use provided test set
        X_train, X_val, y_train, y_val = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        X_test = test_df['text'].values
        y_test = test_df['label_encoded'].values
    else:
        # Split from training data
        X_train, X_temp, y_train, y_temp = train_test_split(
            X, y, test_size=0.3, random_state=42, stratify=y
        )
        X_val, X_test, y_val, y_test = train_test_split(
            X_temp, y_temp, test_size=0.5, random_state=42, stratify=y_temp
        )
    
    print(f"\nData splits:")
    print(f"  Train: {len(X_train)} samples")
    print(f"  Validation: {len(X_val)} samples")
    print(f"  Test: {len(X_test)} samples")
    
    # Load tokenizer and model
    print(f"\nLoading tokenizer and model...")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    
    num_labels = len(label_encoder.classes_)
    model = AutoModelForSequenceClassification.from_pretrained(
        model_name,
        num_labels=num_labels
    )
    model.to(device)
    
    # Create datasets
    train_dataset = SentimentDataset(X_train, y_train, tokenizer)
    val_dataset = SentimentDataset(X_val, y_val, tokenizer)
    test_dataset = SentimentDataset(X_test, y_test, tokenizer)
    
    # Training arguments
    training_args = TrainingArguments(
        output_dir=str(MODELS_DIR / "checkpoints"),
        num_train_epochs=5,
        per_device_train_batch_size=16,
        per_device_eval_batch_size=16,
        warmup_steps=500,
        weight_decay=0.01,
        logging_dir=str(RESULTS_DIR / "logs"),
        logging_steps=100,
        eval_strategy="epoch",  # Changed from evaluation_strategy to eval_strategy
        save_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="f1",
        greater_is_better=True,
        save_total_limit=2,
        learning_rate=2e-5,
        fp16=torch.cuda.is_available(),
    )
    
    # Compute metrics function
    def compute_metrics(eval_pred):
        predictions, labels = eval_pred
        predictions = np.argmax(predictions, axis=1)
        accuracy = accuracy_score(labels, predictions)
        f1 = f1_score(labels, predictions, average='weighted')
        return {
            'accuracy': accuracy,
            'f1': f1
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
    
    # Get predictions
    predictions = trainer.predict(test_dataset)
    y_pred = np.argmax(predictions.predictions, axis=1)
    
    # Classification report
    print("\n" + "="*60)
    print("Test Set Results:")
    print("="*60)
    print(f"\nAccuracy: {test_results['eval_accuracy']:.4f}")
    print(f"F1 Score: {test_results['eval_f1']:.4f}")
    
    print("\nDetailed Classification Report:")
    print(classification_report(
        y_test, 
        y_pred, 
        target_names=label_encoder.classes_,
        digits=4
    ))
    
    print("\nConfusion Matrix:")
    cm = confusion_matrix(y_test, y_pred)
    print(cm)
    
    # Save model and tokenizer
    model_save_path = MODELS_DIR / "sentiment_model"
    model_save_path.mkdir(exist_ok=True)
    
    print(f"\nSaving model to {model_save_path}...")
    trainer.save_model(str(model_save_path))
    tokenizer.save_pretrained(str(model_save_path))
    
    # Save label encoder
    label_encoder_path = MODELS_DIR / "label_encoder.pkl"
    joblib.dump(label_encoder, label_encoder_path)
    print(f"Saved label encoder to {label_encoder_path}")
    
    # Save results
    results = {
        'model_name': model_name,
        'num_labels': num_labels,
        'label_mapping': {int(i): label for i, label in enumerate(label_encoder.classes_)},
        'train_samples': len(X_train),
        'val_samples': len(X_val),
        'test_samples': len(X_test),
        'test_accuracy': float(test_results['eval_accuracy']),
        'test_f1': float(test_results['eval_f1']),
        'training_date': datetime.now().isoformat(),
        'classification_report': classification_report(
            y_test, y_pred, 
            target_names=label_encoder.classes_,
            output_dict=True
        )
    }
    
    results_path = RESULTS_DIR / "training_results.json"
    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"Saved results to {results_path}")
    
    return model, tokenizer, label_encoder, results


def main():
    """Main training pipeline"""
    print("\n" + "="*60)
    print("Sentiment Analysis Model Training Pipeline")
    print("="*60)
    
    try:
        # Load data (returns train_df and optionally test_df)
        df, test_df = load_and_explore_data(DATA_DIR)
        
        # Preprocess - fit encoder on training data
        df, test_df, label_encoder = preprocess_data(df, test_df=test_df)
        
        # Train model (using DistilBERT for faster training, can switch to BERT for better accuracy)
        model, tokenizer, label_encoder, results = train_model(
            df, 
            label_encoder,
            test_df=test_df,
            model_name='distilbert-base-uncased'  # Can use 'bert-base-uncased' for better accuracy
        )
        
        print("\n" + "="*60)
        print("Training Complete!")
        print("="*60)
        print(f"\nModel saved to: {MODELS_DIR / 'sentiment_model'}")
        print(f"Label encoder saved to: {MODELS_DIR / 'label_encoder.pkl'}")
        print(f"Results saved to: {RESULTS_DIR / 'training_results.json'}")
        print(f"\nFinal Test Accuracy: {results['test_accuracy']:.4f}")
        print(f"Final Test F1 Score: {results['test_f1']:.4f}")
        
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    main()

