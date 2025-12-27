import os
import pandas as pd
import numpy as np
import json
import random
import torch
import joblib
import warnings
from pathlib import Path
from datetime import datetime

# ML Libraries
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, f1_score
from sklearn.preprocessing import LabelEncoder
from torch.utils.data import Dataset
from transformers import (
    AutoTokenizer, 
    AutoModelForSequenceClassification,
    TrainingArguments,
    Trainer,
    EarlyStoppingCallback,
    set_seed
)

warnings.filterwarnings('ignore')

# --- 1. GLOBAL RANDOMIZATION CONTROL ---
def set_global_determinism(seed=42):
    set_seed(seed) 
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
    os.environ['PYTHONHASHSEED'] = str(seed)

set_global_determinism(42)

# Paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"
RESULTS_DIR = BASE_DIR / "results"
for d in [MODELS_DIR, RESULTS_DIR]: d.mkdir(exist_ok=True)

# --- 2. DATASET CLASS ---
class SentimentDataset(Dataset):
    def __init__(self, texts, labels, tokenizer, max_length=128): # Optimized for tweets
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length
    
    def __len__(self):
        return len(self.texts)
    
    def __getitem__(self, idx):
        # Ensure text is string (handles cases where tweet is just numbers)
        text = str(self.texts[idx])
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
            'labels': torch.tensor(self.labels[idx], dtype=torch.long)
        }

# --- 3. CORE LOGIC FUNCTIONS ---
def load_and_clean_data(data_dir):
    train_path = data_dir / "train.csv"
    if not train_path.exists():
        raise FileNotFoundError(f"Missing train.csv in {data_dir}")

    # Use 'latin-1' to handle Twitter-specific special characters and emojis
    try:
        df = pd.read_csv(train_path, encoding='latin-1')
    except Exception:
        df = pd.read_csv(train_path, encoding='utf-8', errors='replace')
    
    # Selecting columns based on your provided data structure
    text_col = 'text'
    sentiment_col = 'sentiment'
    
    # Filter and Drop Missing
    df = df[[text_col, sentiment_col]].copy()
    df = df.dropna(subset=[text_col, sentiment_col])
    
    # Standardize whitespace
    df[text_col] = df[text_col].astype(str).str.strip()
    df = df[df[text_col] != ""]
    
    print("\n📊 Sentiment Distribution:")
    print(df[sentiment_col].value_counts())
    
    return df

def train_model(df, model_name='microsoft/deberta-v3-base'):
    print(f"\n🚀 Initializing High-Accuracy Training with {model_name}...")
    
    # Encode Labels
    le = LabelEncoder()
    df['label'] = le.fit_transform(df['sentiment'])
    num_labels = len(le.classes_)
    
    # Split (Stratified ensures equal distribution of 3 classes)
    X_train, X_val, y_train, y_val = train_test_split(
        df['text'].values, df['label'].values, 
        test_size=0.15, random_state=42, stratify=df['label'].values
    )

    # 1. Tokenizer Fix: Use Slow Tokenizer for stability with DeBERTa-v3
    print("📥 Loading Tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=False)

    # 2. Security Fix: Use SafeTensors to bypass the torch.load vulnerability
    print("📥 Loading Model Weights (SafeTensors Mode)...")
    model = AutoModelForSequenceClassification.from_pretrained(
        model_name, 
        num_labels=num_labels,
        use_safetensors=True
    )

    train_ds = SentimentDataset(X_train, y_train, tokenizer)
    val_ds = SentimentDataset(X_val, y_val, tokenizer)

    # --- 4. HYPERMEASURE OPTIMIZATION ---
    training_args = TrainingArguments(
        output_dir=str(MODELS_DIR / "checkpoints"),
        num_train_epochs=5,               # Ideal for 3-class Twitter data
        per_device_train_batch_size=16,
        per_device_eval_batch_size=16,
        
        # Pro Hyperparameters
        learning_rate=2e-5,               
        lr_scheduler_type="cosine",       
        warmup_ratio=0.1,                 
        weight_decay=0.05,                
        
        eval_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="accuracy",
        fp16=torch.cuda.is_available(),   # GPU Acceleration
        logging_steps=50,
        report_to="none"
    )

    def compute_metrics(eval_pred):
        logits, labels = eval_pred
        preds = np.argmax(logits, axis=1)
        return {
            'accuracy': accuracy_score(labels, preds),
            'f1_weighted': f1_score(labels, preds, average='weighted')
        }

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_ds,
        eval_dataset=val_ds,
        compute_metrics=compute_metrics,
        callbacks=[EarlyStoppingCallback(early_stopping_patience=2)]
    )

    trainer.train()

    # --- 5. EVALUATION & SAVING ---
    metrics = trainer.evaluate()
    print(f"\n✅ Final Validation Accuracy: {metrics['eval_accuracy']:.4f}")

    # Save Everything
    save_path = MODELS_DIR / "sentiment_model_final"
    trainer.save_model(str(save_path))
    tokenizer.save_pretrained(str(save_path))
    joblib.dump(le, MODELS_DIR / "label_encoder.pkl")
    
    # Save Metadata for Hackathon Presentation
    results = {
        "accuracy": float(metrics['eval_accuracy']),
        "f1": float(metrics['eval_f1_weighted']),
        "model": model_name,
        "labels": list(le.classes_),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    with open(RESULTS_DIR / "training_results.json", 'w') as f:
        json.dump(results, f, indent=4)

    return trainer, le

def main():
    try:
        data = load_and_clean_data(DATA_DIR)
        train_model(data)
        print("\n✨ Training Complete. Model and Encoder saved in /models")
    except Exception as e:
        print(f"❌ Error during training: {e}")

if __name__ == "__main__":
    main()