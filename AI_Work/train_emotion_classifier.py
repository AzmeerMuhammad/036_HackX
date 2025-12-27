import os
import pandas as pd
import numpy as np
import json
import re
import warnings
import torch
import torch.nn as nn
import torch.nn.functional as F
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score
from torch.utils.data import Dataset
from transformers import (
    AutoTokenizer, 
    AutoModelForSequenceClassification,
    TrainingArguments,
    Trainer,
    EarlyStoppingCallback
)

warnings.filterwarnings('ignore')

# --- CONFIG ---
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
MODEL_NAME = 'roberta-base'
SAVE_DIR = "./models/emotion_model_text_only"
DATA_PATH = "./data/depression_emo_prepared.csv"

TARGET_EMOTIONS = [
    'sadness', 'emptiness', 'hopelessness', 'loneliness', 
    'anger', 'guilt', 'shame', 'fear', 'worthlessness', 
    'suicide intent', 'brain dysfunction (forget)', 'cognitive_dysfunction'
]

# --- HELPER FUNCTIONS ---
def clean_text(text):
    if not isinstance(text, str): return ""
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    text = re.sub(r'/r/\w+|/u/\w+', '', text)
    text = re.sub(r'\[deleted\]|\[removed\]', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

class FocalLoss(nn.Module):
    def __init__(self, alpha=1.0, gamma=2.0):
        super(FocalLoss, self).__init__()
        self.alpha = alpha
        self.gamma = gamma
    
    def forward(self, inputs, targets):
        probs = torch.sigmoid(inputs)
        p_t = probs * targets + (1 - probs) * (1 - targets)
        focal_weight = (1 - p_t) ** self.gamma
        bce_loss = F.binary_cross_entropy_with_logits(inputs, targets, reduction='none')
        return (self.alpha * focal_weight * bce_loss).mean()

class EmotionTrainer(Trainer):
    def __init__(self, *args, loss_fn=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.loss_fn = loss_fn

    def compute_loss(self, model, inputs, return_outputs=False, num_items_in_batch=None, **kwargs):
        labels = inputs.get("labels")
        outputs = model(**inputs)
        logits = outputs.get("logits")
        loss = self.loss_fn(logits, labels) if self.loss_fn else outputs.loss
        return (loss, outputs) if return_outputs else loss

class MultiLabelDataset(Dataset):
    def __init__(self, texts, labels, tokenizer, max_length=512):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length
    
    def __len__(self): return len(self.texts)
    
    def __getitem__(self, idx):
        encoding = self.tokenizer(
            self.texts[idx],
            truncation=True, padding='max_length',
            max_length=self.max_length, return_tensors='pt'
        )
        return {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'labels': torch.tensor(self.labels[idx], dtype=torch.float)
        }

def compute_metrics(eval_pred):
    logits, labels = eval_pred
    probs = torch.sigmoid(torch.tensor(logits)).numpy()
    preds = (probs >= 0.5).astype(float)
    return {
        'f1_macro': f1_score(labels, preds, average='macro', zero_division=0),
        'accuracy': accuracy_score(labels, preds)
    }

# --- MAIN TRAINING LOOP ---
def train():
    print(f"Checking for data at {DATA_PATH}...")
    if not os.path.exists(DATA_PATH):
        print("❌ Error: CSV file not found!")
        return

    # 1. Prepare Data
    df = pd.read_csv(DATA_PATH)
    df['clean_input'] = df['text'].fillna('').apply(clean_text)
    
    emotion_cols = [c for c in TARGET_EMOTIONS if c in df.columns]
    X = df['clean_input'].values
    y = df[emotion_cols].values

    # 2. Setup Model
    print(f"Loading {MODEL_NAME} on {DEVICE}...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSequenceClassification.from_pretrained(
        MODEL_NAME, num_labels=len(emotion_cols), problem_type="multi_label_classification"
    ).to(DEVICE)

    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)
    train_ds = MultiLabelDataset(X_train, y_train, tokenizer)
    val_ds = MultiLabelDataset(X_val, y_val, tokenizer)

    # 3. Training Arguments
    training_args = TrainingArguments(
        output_dir="./results",
        num_train_epochs=8,
        per_device_train_batch_size=8,
        gradient_accumulation_steps=4,
        eval_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="f1_macro",
        save_total_limit=1,
        save_only_model=True,
        fp16=torch.cuda.is_available(),
        report_to="none"
    )

    # 4. Initialize Trainer
    trainer = EmotionTrainer(
        model=model,
        args=training_args,
        train_dataset=train_ds,
        eval_dataset=val_ds,
        compute_metrics=compute_metrics,
        loss_fn=FocalLoss(gamma=2.0),
        callbacks=[EarlyStoppingCallback(early_stopping_patience=3)]
    )

    print("🚀 Starting Training...")
    trainer.train()

    # 5. Final Saving (The part that fixed the previous errors)
    print(f"💾 Saving complete model and tokenizer to {SAVE_DIR}...")
    os.makedirs(SAVE_DIR, exist_ok=True)
    
    trainer.save_model(SAVE_DIR)      # Saves config.json and pytorch_model.bin
    tokenizer.save_pretrained(SAVE_DIR) # Saves vocab.json, merges.txt, etc.
    
    # Calculate thresholds for the predictor
    val_preds = trainer.predict(val_ds)
    val_probs = torch.sigmoid(torch.tensor(val_preds.predictions)).numpy()
    best_thresholds = []
    for i in range(len(emotion_cols)):
        bt, bf1 = 0.5, 0
        for t in np.linspace(0.1, 0.7, 50):
            score = f1_score(y_val[:, i], (val_probs[:, i] >= t).astype(int), zero_division=0)
            if score > bf1: bt, bf1 = t, score
        best_thresholds.append(float(bt))

    # Save our custom config as a DIFFERENT name to avoid overwriting model config
    with open(os.path.join(SAVE_DIR, "emotion_config.json"), 'w') as f:
        json.dump({'emotions': emotion_cols, 'thresholds': best_thresholds}, f)

    print("✨ Process Complete! Your model is ready for predict_sentiment.py")

if __name__ == "__main__":
    train()