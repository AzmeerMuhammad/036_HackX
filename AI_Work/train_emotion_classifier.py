"""
Train Emotion Classifier on DepressionEmo Dataset
Trains RoBERTa/BERT to predict depression-relevant emotions with improved accuracy
"""
import os
import pandas as pd
import numpy as np
from pathlib import Path
import json
from datetime import datetime
import warnings
import re
warnings.filterwarnings('ignore')

# ML Libraries
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    classification_report, confusion_matrix, accuracy_score, 
    f1_score, precision_score, recall_score, hamming_loss
)
import torch
import torch.nn as nn
import torch.nn.functional as F
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

# Depression emotions to predict (will be auto-detected from data)
# Standard emotions
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

# Additional emotions that may be in the dataset
ADDITIONAL_EMOTIONS = [
    'worthlessness',
    'suicide_intent',
    'brain_dysfunction'
]


def preprocess_text(text):
    """
    Clean and preprocess Reddit text for better model performance.
    Handles Reddit-specific formatting, URLs, emojis, etc.
    """
    if not isinstance(text, str):
        text = str(text)
    
    # Remove URLs
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    
    # Remove Reddit-specific patterns
    text = re.sub(r'/r/\w+|/u/\w+', '', text)  # Subreddit/user mentions
    text = re.sub(r'\[deleted\]|\[removed\]', '', text, flags=re.IGNORECASE)
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove leading/trailing whitespace
    text = text.strip()
    
    # Handle common contractions (optional - can expand if needed)
    # For now, just ensure text is not empty
    if len(text) < 3:
        return "[empty]"
    
    return text


class FocalLoss(nn.Module):
    """
    Focal Loss for addressing class imbalance in multi-label classification.
    FL(p_t) = -α_t(1-p_t)^γ log(p_t)
    """
    def __init__(self, alpha=1.0, gamma=2.0, reduction='mean'):
        super(FocalLoss, self).__init__()
        self.alpha = alpha
        self.gamma = gamma
        self.reduction = reduction
    
    def forward(self, inputs, targets):
        # Apply sigmoid to get probabilities
        probs = torch.sigmoid(inputs)
        
        # Calculate p_t
        p_t = probs * targets + (1 - probs) * (1 - targets)
        
        # Calculate focal weight
        focal_weight = (1 - p_t) ** self.gamma
        
        # Calculate BCE loss
        bce_loss = F.binary_cross_entropy_with_logits(inputs, targets, reduction='none')
        
        # Apply focal weight
        focal_loss = self.alpha * focal_weight * bce_loss
        
        if self.reduction == 'mean':
            return focal_loss.mean()
        elif self.reduction == 'sum':
            return focal_loss.sum()
        else:
            return focal_loss


class WeightedBCELoss(nn.Module):
    """
    Weighted Binary Cross Entropy Loss for handling class imbalance.
    """
    def __init__(self, pos_weight=None, reduction='mean'):
        super(WeightedBCELoss, self).__init__()
        self.pos_weight = pos_weight
        self.reduction = reduction
    
    def forward(self, inputs, targets):
        if self.pos_weight is not None:
            # Ensure pos_weight is on the same device
            if isinstance(self.pos_weight, torch.Tensor):
                pos_weight = self.pos_weight.to(inputs.device)
            else:
                pos_weight = torch.tensor(self.pos_weight, device=inputs.device)
            
            return F.binary_cross_entropy_with_logits(
                inputs, targets, pos_weight=pos_weight, reduction=self.reduction
            )
        else:
            return F.binary_cross_entropy_with_logits(
                inputs, targets, reduction=self.reduction
            )


def calculate_class_weights(labels):
    """
    Calculate class weights for imbalanced multi-label classification.
    Returns weights for positive class (1) for each emotion.
    """
    n_samples, n_classes = labels.shape
    pos_weights = []
    
    for i in range(n_classes):
        pos_count = labels[:, i].sum()
        neg_count = n_samples - pos_count
        
        if pos_count > 0 and neg_count > 0:
            # Inverse frequency weighting
            weight = neg_count / pos_count
            # Cap weights to prevent extreme values
            weight = min(weight, 10.0)
            pos_weights.append(weight)
        else:
            pos_weights.append(1.0)
    
    return np.array(pos_weights)


def stratified_split_multi_label(texts, labels, test_size=0.3, random_state=42):
    """
    Stratified split for multi-label data.
    Uses iterative stratification to preserve label distribution.
    Falls back to regular split if stratification fails.
    """
    try:
        from iterstrat.ml_stratifiers import MultilabelStratifiedShuffleSplit
        
        msss = MultilabelStratifiedShuffleSplit(
            n_splits=1, test_size=test_size, random_state=random_state
        )
        train_idx, temp_idx = next(msss.split(texts, labels))
        
        X_train = texts[train_idx]
        y_train = labels[train_idx]
        X_temp = texts[temp_idx]
        y_temp = labels[temp_idx]
        
        return X_train, X_temp, y_train, y_temp
    except ImportError:
        print("Warning: iterstrat not available. Using regular split.")
        print("Install with: pip install iterative-stratification")
        return train_test_split(texts, labels, test_size=test_size, random_state=random_state)


class MultiLabelEmotionDataset(Dataset):
    """Custom dataset for multi-label emotion classification with text preprocessing"""
    def __init__(self, texts, labels, tokenizer, max_length=512, preprocess=True):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length
        self.preprocess = preprocess
    
    def __len__(self):
        return len(self.texts)
    
    def __getitem__(self, idx):
        text = str(self.texts[idx])
        
        # Apply preprocessing if enabled
        if self.preprocess:
            text = preprocess_text(text)
        
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
    
    # Try prepared data first (from prepare_depression_emo.py)
    prepared_path = DATA_DIR / "depression_emo_prepared.csv"
    if prepared_path.exists():
        print(f"\nLoading from: {prepared_path}")
        df = pd.read_csv(prepared_path)
        print(f"Shape: {df.shape}")
        print(f"Columns: {df.columns.tolist()}")
        return df
    
    # Try train split
    train_path = DATA_DIR / "depression_emo_train.csv"
    if train_path.exists():
        print(f"\nLoading from: {train_path}")
        df = pd.read_csv(train_path)
        print(f"Shape: {df.shape}")
        print(f"Columns: {df.columns.tolist()}")
        return df
    
    # Try raw data (fallback)
    depression_emo_dir = DATA_DIR / "DepressionEmo"
    if depression_emo_dir.exists():
        csv_files = list(depression_emo_dir.glob("**/*.csv"))
        if csv_files:
            print(f"\nWarning: Using raw CSV file. Consider running prepare_depression_emo.py first.")
            print(f"Loading from: {csv_files[0]}")
            df = pd.read_csv(csv_files[0])
            print(f"Shape: {df.shape}")
            print(f"Columns: {df.columns.tolist()}")
            return df
    
    raise FileNotFoundError(
        f"DepressionEmo data not found. Please run prepare_depression_emo.py first.\n"
        f"Expected location: {prepared_path} or {train_path}"
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
    
    # Get emotion columns - check all possible emotions
    all_possible_emotions = DEPRESSION_EMOTIONS + ADDITIONAL_EMOTIONS
    emotion_labels = []
    available_emotions = []
    
    # First, try to find emotion columns in the dataframe
    for emotion in all_possible_emotions:
        if emotion in df.columns:
            labels = df[emotion].values
            # Convert to binary if needed
            if labels.dtype == 'object':
                labels = (labels.astype(str).str.lower().isin(['true', '1', 'yes'])).astype(float)
            else:
                labels = labels.astype(float)
            # Only include if there are positive samples
            if labels.sum() > 0:
                emotion_labels.append(labels)
                available_emotions.append(emotion)
                print(f"  {emotion}: {labels.sum()} positive samples ({labels.sum()/len(labels)*100:.2f}%)")
    
    # If no emotions found, try to extract from emotions_list column
    if not emotion_labels and 'emotions_list' in df.columns:
        print("\nNo emotion columns found, extracting from emotions_list...")
        from collections import Counter
        all_emotions_found = Counter()
        
        for emotions_list in df['emotions_list']:
            if isinstance(emotions_list, str):
                import ast
                try:
                    emotions_list = ast.literal_eval(emotions_list)
                except:
                    emotions_list = [emotions_list]
            if isinstance(emotions_list, list):
                all_emotions_found.update(emotions_list)
        
        print(f"Found emotions in data: {sorted(all_emotions_found.keys())}")
        
        # Create binary labels from emotions_list
        for emotion in sorted(all_emotions_found.keys()):
            labels = df['emotions_list'].apply(
                lambda x: 1 if emotion in (x if isinstance(x, list) else []) else 0
            ).values.astype(float)
            
            if labels.sum() > 0:
                emotion_labels.append(labels)
                available_emotions.append(emotion)
                print(f"  {emotion}: {labels.sum()} positive samples ({labels.sum()/len(labels)*100:.2f}%)")
    
    if not emotion_labels:
        raise ValueError(
            "No emotion columns found in dataframe. "
            "Please run prepare_depression_emo.py first to prepare the data."
        )
    
    # Stack into matrix: (n_samples, n_emotions)
    labels_matrix = np.stack(emotion_labels, axis=1)
    
    print(f"\nLabel matrix shape: {labels_matrix.shape}")
    print(f"Available emotions: {available_emotions}")
    
    return texts, labels_matrix, available_emotions


def train_emotion_classifier(
    texts, labels, emotion_names, 
    model_name='roberta-base',
    use_focal_loss=False,
    use_class_weights=True,
    max_length=512,
    early_stopping_patience=4
):
    """
    Train multi-label emotion classifier with improved accuracy techniques.
    
    Args:
        texts: Input texts
        labels: Multi-label emotion labels
        emotion_names: List of emotion names
        model_name: Base model name (default: roberta-base)
        use_focal_loss: Whether to use focal loss (default: False, uses weighted BCE)
        use_class_weights: Whether to use class weights (default: True)
        max_length: Maximum sequence length (default: 512)
        early_stopping_patience: Early stopping patience (default: 4)
    """
    print("\n" + "="*60)
    print(f"Training Emotion Classifier: {model_name}")
    print("="*60)
    
    # Stratified split for better label distribution
    print("\nSplitting data with stratification...")
    X_train, X_temp, y_train, y_temp = stratified_split_multi_label(
        texts, labels, test_size=0.3, random_state=42
    )
    X_val, X_test, y_val, y_test = stratified_split_multi_label(
        X_temp, y_temp, test_size=0.5, random_state=42
    )
    
    print(f"\nData splits:")
    print(f"  Train: {len(X_train)} samples")
    print(f"  Validation: {len(X_val)} samples")
    print(f"  Test: {len(X_test)} samples")
    
    # Calculate class weights
    class_weights = None
    if use_class_weights:
        print("\nCalculating class weights for imbalanced data...")
        class_weights = calculate_class_weights(y_train)
        print("Class weights (positive class):")
        for emotion, weight in zip(emotion_names, class_weights):
            print(f"  {emotion}: {weight:.3f}")
        class_weights = torch.tensor(class_weights, dtype=torch.float32)
    
    # Load tokenizer and model
    print(f"\nLoading tokenizer and model: {model_name}...")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    
    # Add pad token if it doesn't exist (for RoBERTa)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    
    num_labels = len(emotion_names)
    model = AutoModelForSequenceClassification.from_pretrained(
        model_name,
        num_labels=num_labels,
        problem_type="multi_label_classification"
    )
    model.to(device)
    
    # Create datasets with preprocessing
    print(f"\nCreating datasets with max_length={max_length}...")
    train_dataset = MultiLabelEmotionDataset(X_train, y_train, tokenizer, max_length=max_length, preprocess=True)
    val_dataset = MultiLabelEmotionDataset(X_val, y_val, tokenizer, max_length=max_length, preprocess=True)
    test_dataset = MultiLabelEmotionDataset(X_test, y_test, tokenizer, max_length=max_length, preprocess=True)
    
    # Setup loss function
    if use_focal_loss:
        print("\nUsing Focal Loss (alpha=1.0, gamma=2.0)")
        loss_fn = FocalLoss(alpha=1.0, gamma=2.0)
    elif use_class_weights and class_weights is not None:
        print("\nUsing Weighted BCE Loss with class weights")
        loss_fn = WeightedBCELoss(pos_weight=class_weights)
    else:
        print("\nUsing standard BCE Loss")
        loss_fn = None  # Use default from model
    
    # Training arguments with improved settings
    training_args = TrainingArguments(
        output_dir=str(MODELS_DIR / "emotion_classifier_checkpoints"),
        
        # 1. Increase Epochs (we have EarlyStopping, so let it run longer)
        num_train_epochs=20,  # Increased from 15
        
        # 2. Learning Rate & Schedule
        learning_rate=3e-5,            # Slightly lower for RoBERTa
        lr_scheduler_type="cosine",    # Smoother decay than linear
        warmup_ratio=0.1,              # Reduced warmup for RoBERTa
        
        # 3. Regularization
        weight_decay=0.01,             # Reduced for better learning
        
        # 4. Batch Size & Hardware
        per_device_train_batch_size=16,  # Reduced for longer sequences
        per_device_eval_batch_size=16,
        fp16=torch.cuda.is_available(),
        gradient_accumulation_steps=2,   # Effective batch size = 32
        
        # 5. Evaluation & Strategy
        eval_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="f1_macro", # Focus on balanced performance
        greater_is_better=True,
        save_total_limit=2,               # Keep best 2 models
        
        # 6. Logging
        logging_dir=str(RESULTS_DIR / "emotion_classifier_logs"),
        logging_steps=50,
        report_to="none",                 # Prevents extra clutter
    )
    
    # Compute metrics function for multi-label with per-emotion metrics
    def compute_metrics(eval_pred):
        predictions, labels = eval_pred
        # Apply sigmoid to get probabilities
        sigmoid = torch.nn.Sigmoid()
        probs = sigmoid(torch.tensor(predictions))
        # Threshold at 0.5
        predictions_binary = (probs > 0.5).float().numpy()
        
        # Overall metrics
        accuracy = accuracy_score(labels, predictions_binary)
        f1_micro = f1_score(labels, predictions_binary, average='micro')
        f1_macro = f1_score(labels, predictions_binary, average='macro')
        hamming = hamming_loss(labels, predictions_binary)
        
        # Per-emotion metrics
        per_emotion_metrics = {}
        for i, emotion in enumerate(emotion_names):
            if labels[:, i].sum() > 0:  # Only if emotion exists in labels
                precision = precision_score(labels[:, i], predictions_binary[:, i], zero_division=0)
                recall = recall_score(labels[:, i], predictions_binary[:, i], zero_division=0)
                f1 = f1_score(labels[:, i], predictions_binary[:, i], zero_division=0)
                per_emotion_metrics[f'{emotion}_precision'] = precision
                per_emotion_metrics[f'{emotion}_recall'] = recall
                per_emotion_metrics[f'{emotion}_f1'] = f1
        
        metrics = {
            'accuracy': accuracy,
            'f1_micro': f1_micro,
            'f1_macro': f1_macro,
            'hamming_loss': hamming,
            **per_emotion_metrics
        }
        
        return metrics
    
    # Custom compute_loss if using focal loss or weighted BCE
    def compute_loss(model, inputs, return_outputs=False):
        labels = inputs.get("labels")
        # Create a copy of inputs without labels for model forward pass
        model_inputs = {k: v for k, v in inputs.items() if k != "labels"}
        outputs = model(**model_inputs)
        logits = outputs.get("logits")
        
        if loss_fn is not None:
            loss = loss_fn(logits, labels)
        else:
            loss = outputs.loss
        
        return (loss, outputs) if return_outputs else loss
    
    # Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        compute_metrics=compute_metrics,
        compute_loss=compute_loss if (use_focal_loss or (use_class_weights and class_weights is not None)) else None,
        callbacks=[EarlyStoppingCallback(early_stopping_patience=early_stopping_patience)]
    )
    
   # Train
    print("\nStarting training...")
    trainer.train()

    # --- NEW: THRESHOLD OPTIMIZATION ON VALIDATION SET ---
    print("\nStep 1: Finding optimal thresholds on Validation Set...")
    val_predictions = trainer.predict(val_dataset)
    val_probs = torch.nn.Sigmoid()(torch.tensor(val_predictions.predictions)).numpy()
    
    # Find the best thresholds using our helper function
    optimal_thresholds = find_optimal_thresholds(y_val, val_probs, emotion_names)

    # --- APPLY TO TEST SET ---
    print("\nStep 2: Evaluating on Test Set with optimized thresholds...")
    test_predictions = trainer.predict(test_dataset)
    test_probs = torch.nn.Sigmoid()(torch.tensor(test_predictions.predictions)).numpy()
    
    # Apply the specific threshold for each column (emotion)
    y_pred_optimized = (test_probs >= optimal_thresholds).astype(float)
    
    # Calculate Optimized Metrics
    opt_accuracy = accuracy_score(y_test, y_pred_optimized)
    opt_f1_micro = f1_score(y_test, y_pred_optimized, average='micro')
    opt_f1_macro = f1_score(y_test, y_pred_optimized, average='macro')

    # Per-emotion metrics
    print("\n" + "="*60)
    print("Optimized Test Set Results:")
    print("="*60)
    print(f"\nOverall Accuracy (Subset): {opt_accuracy:.4f}")
    print(f"F1 Score (Micro): {opt_f1_micro:.4f}")
    print(f"F1 Score (Macro): {opt_f1_macro:.4f}")
    
    # Detailed per-emotion metrics
    print("\n" + "="*60)
    print("Per-Emotion Metrics (with optimized thresholds):")
    print("="*60)
    for i, emotion in enumerate(emotion_names):
        if y_test[:, i].sum() > 0:
            precision = precision_score(y_test[:, i], y_pred_optimized[:, i], zero_division=0)
            recall = recall_score(y_test[:, i], y_pred_optimized[:, i], zero_division=0)
            f1 = f1_score(y_test[:, i], y_pred_optimized[:, i], zero_division=0)
            print(f"\n{emotion}:")
            print(f"  Precision: {precision:.4f}")
            print(f"  Recall: {recall:.4f}")
            print(f"  F1-Score: {f1:.4f}")
            print(f"  Threshold: {optimal_thresholds[i]:.3f}")
            print(f"  Support: {int(y_test[:, i].sum())} positive samples")
    
    # Save model and thresholds
    model_save_path = MODELS_DIR / "emotion_classifier"
    model_save_path.mkdir(exist_ok=True)
    
    trainer.save_model(str(model_save_path))
    tokenizer.save_pretrained(str(model_save_path))
    
    # --- IMPORTANT: Save thresholds for inference ---
    emotion_info = {
        'emotion_names': emotion_names,
        'num_emotions': num_labels,
        'optimal_thresholds': optimal_thresholds.tolist() # Save these!
    }
    with open(model_save_path / "emotion_info.json", 'w') as f:
        json.dump(emotion_info, f, indent=2)
    
    results = {
        'model_name': model_name,
        'test_accuracy': float(opt_accuracy),
        'test_f1_micro': float(opt_f1_micro),
        'test_f1_macro': float(opt_f1_macro),
        'thresholds': optimal_thresholds.tolist()
    }
    
    return model, tokenizer, emotion_names, results

def find_optimal_thresholds(labels, probs, emotion_names):
    """Find the best threshold for each emotion to maximize F1-score"""
    print("\nOptimizing thresholds for each emotion...")
    best_thresholds = []
    
    for i, emotion in enumerate(emotion_names):
        best_f1 = 0
        best_threshold = 0.5
        
        # Test 100 different threshold values
        for threshold in np.linspace(0.01, 0.99, 100):
            preds = (probs[:, i] >= threshold).astype(int)
            f1 = f1_score(labels[:, i], preds, zero_division=0)
            
            if f1 > best_f1:
                best_f1 = f1
                best_threshold = threshold
        
        best_thresholds.append(best_threshold)
        print(f"  {emotion:15} | Best Threshold: {best_threshold:.2f} | F1: {best_f1:.4f}")
        
    return np.array(best_thresholds)

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
        
        # Train model with improved settings
        model, tokenizer, emotion_names, results = train_emotion_classifier(
            texts, 
            labels, 
            emotion_names,
            model_name='roberta-base',  # Upgraded from DistilBERT to RoBERTa
            use_focal_loss=False,  # Set to True to use focal loss instead of weighted BCE
            use_class_weights=True,  # Use class weights to handle imbalance
            max_length=512,  # Increased from 256 for better context
            early_stopping_patience=4  # Increased from 2
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

