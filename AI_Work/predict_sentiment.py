"""
Sentiment Prediction Script
Loads the trained model and makes predictions on new text.
"""
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import joblib
from pathlib import Path
import numpy as np

# Paths
BASE_DIR = Path(__file__).parent
MODELS_DIR = BASE_DIR / "models"
MODEL_PATH = MODELS_DIR / "sentiment_model"
LABEL_ENCODER_PATH = MODELS_DIR / "label_encoder.pkl"

# Set device
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')


class SentimentPredictor:
    """Sentiment prediction class"""
    
    def __init__(self, model_path=None, label_encoder_path=None):
        """Initialize the predictor"""
        model_path = model_path or MODEL_PATH
        label_encoder_path = label_encoder_path or LABEL_ENCODER_PATH
        
        if not model_path.exists():
            raise FileNotFoundError(f"Model not found at {model_path}. Please train the model first.")
        
        if not label_encoder_path.exists():
            raise FileNotFoundError(f"Label encoder not found at {label_encoder_path}. Please train the model first.")
        
        print(f"Loading model from {model_path}...")
        self.tokenizer = AutoTokenizer.from_pretrained(str(model_path))
        self.model = AutoModelForSequenceClassification.from_pretrained(str(model_path))
        self.model.to(device)
        self.model.eval()
        
        print(f"Loading label encoder from {label_encoder_path}...")
        self.label_encoder = joblib.load(label_encoder_path)
        
        print("Model loaded successfully!")
    
    def predict(self, text, return_probabilities=False):
        """
        Predict sentiment for a given text.
        
        Args:
            text: Input text string
            return_probabilities: If True, return probability distribution
        
        Returns:
            If return_probabilities=False: (sentiment_label, confidence_score)
            If return_probabilities=True: (sentiment_label, confidence_score, probabilities_dict)
        """
        # Tokenize
        encoding = self.tokenizer(
            text,
            truncation=True,
            padding='max_length',
            max_length=128,
            return_tensors='pt'
        )
        
        # Move to device
        input_ids = encoding['input_ids'].to(device)
        attention_mask = encoding['attention_mask'].to(device)
        
        # Predict
        with torch.no_grad():
            outputs = self.model(input_ids=input_ids, attention_mask=attention_mask)
            logits = outputs.logits
            probabilities = torch.nn.functional.softmax(logits, dim=-1)
        
        # Get prediction
        predicted_id = torch.argmax(probabilities, dim=-1).item()
        confidence = probabilities[0][predicted_id].item()
        predicted_label = self.label_encoder.inverse_transform([predicted_id])[0]
        
        if return_probabilities:
            # Get all probabilities
            probs_dict = {}
            for i, label in enumerate(self.label_encoder.classes_):
                probs_dict[label] = probabilities[0][i].item()
            
            return predicted_label, confidence, probs_dict
        else:
            return predicted_label, confidence
    
    def predict_batch(self, texts, return_probabilities=False):
        """
        Predict sentiment for multiple texts.
        
        Args:
            texts: List of input text strings
            return_probabilities: If True, return probability distributions
        
        Returns:
            List of predictions (same format as predict method)
        """
        results = []
        for text in texts:
            result = self.predict(text, return_probabilities=return_probabilities)
            results.append(result)
        return results


def main():
    """Example usage"""
    try:
        # Initialize predictor
        predictor = SentimentPredictor()
        
        # Example predictions
        test_texts = [
            "I love this product! It's amazing and works perfectly.",
            "This is terrible. I'm very disappointed with the quality.",
            "It's okay, nothing special but it works.",
            "I'm feeling great today! Everything is going well."
        ]
        
        print("\n" + "="*60)
        print("Example Predictions")
        print("="*60)
        
        for text in test_texts:
            label, confidence = predictor.predict(text)
            print(f"\nText: {text}")
            print(f"Predicted Sentiment: {label}")
            print(f"Confidence: {confidence:.4f}")
            
            # Get full probability distribution
            _, _, probs = predictor.predict(text, return_probabilities=True)
            print("Probability Distribution:")
            for sentiment, prob in sorted(probs.items(), key=lambda x: x[1], reverse=True):
                print(f"  {sentiment}: {prob:.4f}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

