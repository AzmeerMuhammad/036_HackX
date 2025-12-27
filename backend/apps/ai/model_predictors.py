"""
Model predictors for sentiment and emotion analysis.
Loads trained models from AI_Work/models directory.
Automatically uses GPU if available for faster inference.
"""
import os
import torch
import json
import joblib
import numpy as np
from pathlib import Path
from transformers import AutoTokenizer, AutoModelForSequenceClassification

# Detect device (GPU if available, else CPU)
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Using device: {DEVICE}")

# Get base directory (project root, parent of backend)
# From backend/apps/ai/model_predictors.py -> go up 4 levels to project root
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
AI_WORK_DIR = BASE_DIR / "AI_Work"
# Try both "models" and "Models" for case-insensitive compatibility
MODELS_DIR = AI_WORK_DIR / "Models" if (AI_WORK_DIR / "Models").exists() else AI_WORK_DIR / "models"

# Model paths
SENTIMENT_MODEL_PATH = MODELS_DIR / "sentiment_model_final"
EMOTION_MODEL_PATH = MODELS_DIR / "emotion_model_text_only"
LABEL_ENCODER_PATH = MODELS_DIR / "label_encoder.pkl"


class SentimentPredictor:
    """Predictor for sentiment classification (positive, neutral, negative)."""
    
    def __init__(self, model_path=None):
        if model_path is None:
            model_path = SENTIMENT_MODEL_PATH
        
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Sentiment model not found at {model_path}")
        
        print(f"Loading sentiment model from {model_path}...")
        
        # Load tokenizer (use slow tokenizer for DeBERTa-v3)
        self.tokenizer = AutoTokenizer.from_pretrained(str(model_path), use_fast=False)
        
        # Load model and move to GPU if available
        self.model = AutoModelForSequenceClassification.from_pretrained(str(model_path))
        self.model.to(DEVICE)  # Move model to GPU/CPU
        self.model.eval()
        
        # Load label encoder
        if not os.path.exists(LABEL_ENCODER_PATH):
            raise FileNotFoundError(f"Label encoder not found at {LABEL_ENCODER_PATH}")
        
        self.label_encoder = joblib.load(LABEL_ENCODER_PATH)
        self.classes = self.label_encoder.classes_
        
        print(f"Sentiment model loaded on {DEVICE}. Classes: {list(self.classes)}")
    
    def predict(self, text, return_probabilities=False):
        """
        Predict sentiment for given text.
        
        Args:
            text: Input text string
            return_probabilities: If True, return probabilities for all classes
        
        Returns:
            If return_probabilities=False: (label, confidence)
            If return_probabilities=True: (label, confidence, probabilities_dict)
        """
        # Tokenize
        inputs = self.tokenizer(
            str(text),
            return_tensors="pt",
            truncation=True,
            padding=True,
            max_length=128
        )
        
        # Move inputs to same device as model (GPU if available)
        inputs = {k: v.to(DEVICE) for k, v in inputs.items()}
        
        # Inference
        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits
            probs = torch.softmax(logits, dim=-1).cpu().numpy()[0]
        
        # Get predicted class
        predicted_idx = np.argmax(probs)
        predicted_label = self.label_encoder.inverse_transform([predicted_idx])[0]
        confidence = float(probs[predicted_idx])
        
        if return_probabilities:
            probabilities = {
                label: float(prob) 
                for label, prob in zip(self.classes, probs)
            }
            return predicted_label, confidence, probabilities
        
        return predicted_label, confidence


class EmotionPredictor:
    """Predictor for emotion classification (multi-label)."""
    
    def __init__(self, model_path=None):
        if model_path is None:
            model_path = EMOTION_MODEL_PATH
        
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Emotion model not found at {model_path}")
        
        print(f"Loading emotion model from {model_path}...")
        
        # Load emotion config
        config_path = os.path.join(model_path, "emotion_config.json")
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Emotion config not found at {config_path}")
        
        with open(config_path, 'r') as f:
            meta = json.load(f)
        
        self.emotions = meta['emotions']
        self.thresholds = np.array(meta['thresholds'])
        
        # Load tokenizer and model, move to GPU if available
        self.tokenizer = AutoTokenizer.from_pretrained(str(model_path))
        self.model = AutoModelForSequenceClassification.from_pretrained(str(model_path))
        self.model.to(DEVICE)  # Move model to GPU/CPU
        self.model.eval()
        
        print(f"Emotion model loaded on {DEVICE}. Emotions: {self.emotions}")
    
    def predict(self, text, return_all=False):
        """
        Predict emotions for given text.
        
        Args:
            text: Input text string
            return_all: If True, return all emotions with probabilities, else only detected ones
        
        Returns:
            List of dicts with 'emotion' and 'confidence' keys, sorted by confidence
        """
        # Tokenize
        inputs = self.tokenizer(
            str(text),
            return_tensors="pt",
            truncation=True,
            padding=True,
            max_length=512
        )
        
        # Move inputs to same device as model (GPU if available)
        inputs = {k: v.to(DEVICE) for k, v in inputs.items()}
        
        # Inference
        with torch.no_grad():
            outputs = self.model(**inputs)
            # Use sigmoid for multi-label probabilities
            probs = torch.sigmoid(outputs.logits).cpu().numpy()[0]
        
        # Create results
        results = []
        for i, emo_name in enumerate(self.emotions):
            if return_all or probs[i] >= self.thresholds[i]:
                results.append({
                    "emotion": emo_name,
                    "confidence": round(float(probs[i]), 4)
                })
        
        # Sort by highest confidence
        return sorted(results, key=lambda x: x['confidence'], reverse=True)


# Global model instances (lazy loading)
_sentiment_predictor = None
_emotion_predictor = None


def get_sentiment_predictor():
    """Get or create sentiment predictor instance (singleton)."""
    global _sentiment_predictor
    if _sentiment_predictor is None:
        try:
            _sentiment_predictor = SentimentPredictor()
        except Exception as e:
            print(f"Warning: Failed to load sentiment model: {e}")
            _sentiment_predictor = None
    return _sentiment_predictor


def get_emotion_predictor():
    """Get or create emotion predictor instance (singleton)."""
    global _emotion_predictor
    if _emotion_predictor is None:
        try:
            _emotion_predictor = EmotionPredictor()
        except Exception as e:
            print(f"Warning: Failed to load emotion model: {e}")
            _emotion_predictor = None
    return _emotion_predictor

