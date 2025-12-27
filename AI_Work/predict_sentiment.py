import torch
import json
import os
import numpy as np
from transformers import AutoTokenizer, AutoModelForSequenceClassification

class EmotionPredictor:
    def __init__(self, model_path):
        print("Loading model... please wait.")
        
        # 1. Load the labels and thresholds from our CUSTOM file
        config_path = os.path.join(model_path, "emotion_config.json")
        with open(config_path, 'r') as f:
            meta = json.load(f)
        
        self.emotions = meta['emotions']
        self.thresholds = np.array(meta['thresholds'])
        
        # 2. Load the actual model and tokenizer
        # (This now works because config.json is restored!)
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_path)
        self.model.eval()

    def predict(self, text):
        # Tokenize
        inputs = self.tokenizer(
            text, 
            return_tensors="pt", 
            truncation=True, 
            padding=True, 
            max_length=512
        )
        
        # Inference
        with torch.no_grad():
            outputs = self.model(**inputs)
            # Use sigmoid for multi-label probabilities
            probs = torch.sigmoid(outputs.logits).cpu().numpy()[0]
        
        # Create results dictionary
        results = []
        for i, emo_name in enumerate(self.emotions):
            if probs[i] >= self.thresholds[i]:
                results.append({
                    "emotion": emo_name,
                    "confidence": round(float(probs[i]), 4)
                })
        
        # Sort by highest confidence
        return sorted(results, key=lambda x: x['confidence'], reverse=True)

if __name__ == "__main__":
    # Ensure this points to your specific model folder
    MODEL_PATH = "./models/emotion_model_text_only"
    
    try:
        predictor = EmotionPredictor(MODEL_PATH)
        
        print("\n--- Emotion Analysis System ---")
        while True:
            user_input = input("\nEnter text to analyze (or 'exit'): ")
            if user_input.lower() == 'exit': break
            
            predictions = predictor.predict(user_input)
            
            if not predictions:
                print("No strong emotions detected.")
            else:
                print(f"Detected Emotions:")
                for p in predictions:
                    print(f"  • {p['emotion']:<20} | {p['confidence']*100:>5.1f}%")
                    
    except Exception as e:
        print(f"❌ Error: {e}")