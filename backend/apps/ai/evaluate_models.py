"""
Script to evaluate the accuracy of sentiment and emotion models.
Run this to check model performance metrics.
"""
import os
import sys
from pathlib import Path

# Import from current directory
from .model_predictors import get_sentiment_predictor, get_emotion_predictor

BASE_DIR = Path(__file__).resolve().parent.parent.parent
AI_WORK_DIR = BASE_DIR / "AI_Work"
import torch
import numpy as np
from sklearn.metrics import accuracy_score, f1_score, classification_report, confusion_matrix

def evaluate_sentiment_model():
    """Evaluate sentiment model accuracy"""
    print("\n" + "="*60)
    print("SENTIMENT MODEL EVALUATION")
    print("="*60)
    
    try:
        predictor = get_sentiment_predictor()
        if not predictor:
            print("❌ Sentiment model not available")
            return
        
        # Test cases with known labels
        test_cases = [
            ("I feel great today! This is amazing!", "positive"),
            ("I'm so happy and excited about this!", "positive"),
            ("Today was okay, nothing special happened.", "neutral"),
            ("It's a normal day, nothing to report.", "neutral"),
            ("I feel sad and hopeless right now.", "negative"),
            ("This is terrible, I'm so depressed.", "negative"),
            ("I love this product! It's wonderful!", "positive"),
            ("I'm feeling anxious and worried about tomorrow.", "negative"),
            ("The weather is fine today.", "neutral"),
            ("I'm grateful for everything in my life.", "positive"),
        ]
        
        predictions = []
        true_labels = []
        confidences = []
        
        print(f"\nTesting on {len(test_cases)} examples...")
        for text, true_label in test_cases:
            try:
                pred_label, confidence = predictor.predict(text)
                predictions.append(pred_label.lower())
                true_labels.append(true_label.lower())
                confidences.append(confidence)
                status = "✓" if pred_label.lower() == true_label.lower() else "✗"
                print(f"  {status} '{text[:50]}...' → Predicted: {pred_label}, True: {true_label}, Conf: {confidence:.3f}")
            except Exception as e:
                print(f"  ✗ Error predicting '{text[:50]}...': {e}")
        
        if len(predictions) > 0:
            accuracy = accuracy_score(true_labels, predictions)
            f1 = f1_score(true_labels, predictions, average='weighted')
            avg_confidence = np.mean(confidences)
            
            print(f"\n📊 Results:")
            print(f"  Accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")
            print(f"  F1-Score (weighted): {f1:.4f}")
            print(f"  Average Confidence: {avg_confidence:.4f}")
            
            print(f"\n📋 Classification Report:")
            print(classification_report(true_labels, predictions, target_names=['negative', 'neutral', 'positive']))
            
            print(f"\n📊 Confusion Matrix:")
            cm = confusion_matrix(true_labels, predictions, labels=['negative', 'neutral', 'positive'])
            print("      Predicted:")
            print("      Neg  Neu  Pos")
            for i, label in enumerate(['Neg', 'Neu', 'Pos']):
                print(f"  {label}  {cm[i]}")
        
    except Exception as e:
        print(f"❌ Error evaluating sentiment model: {e}")
        import traceback
        traceback.print_exc()


def evaluate_emotion_model():
    """Evaluate emotion model"""
    print("\n" + "="*60)
    print("EMOTION MODEL EVALUATION")
    print("="*60)
    
    try:
        predictor = get_emotion_predictor()
        if not predictor:
            print("❌ Emotion model not available")
            return
        
        # Test cases with expected emotions
        test_cases = [
            ("I feel so sad and empty inside, nothing matters anymore.", ["sadness", "emptiness"]),
            ("I'm hopeless and feel worthless, there's no point.", ["hopelessness", "worthlessness"]),
            ("I'm so lonely, nobody cares about me.", ["loneliness"]),
            ("I'm angry and frustrated with everything!", ["anger"]),
            ("I feel guilty and ashamed of what I did.", ["guilt", "shame"]),
            ("I'm scared and fearful of what might happen.", ["fear"]),
        ]
        
        print(f"\nTesting on {len(test_cases)} examples...")
        correct_detections = 0
        total_expected = 0
        
        for text, expected_emotions in test_cases:
            try:
                detected = predictor.predict(text)
                detected_emotions = [e['emotion'] for e in detected]
                
                # Check if any expected emotion was detected
                found = any(emo in detected_emotions for emo in expected_emotions)
                total_expected += len(expected_emotions)
                if found:
                    correct_detections += 1
                
                status = "✓" if found else "✗"
                print(f"  {status} '{text[:50]}...'")
                print(f"      Expected: {expected_emotions}")
                print(f"      Detected: {[e['emotion'] for e in detected[:3]]} (showing top 3)")
                
            except Exception as e:
                print(f"  ✗ Error predicting '{text[:50]}...': {e}")
        
        if total_expected > 0:
            detection_rate = correct_detections / len(test_cases)
            print(f"\n📊 Results:")
            print(f"  Detection Rate: {detection_rate:.4f} ({detection_rate*100:.2f}%)")
            print(f"  Correct Detections: {correct_detections}/{len(test_cases)}")
        
    except Exception as e:
        print(f"❌ Error evaluating emotion model: {e}")
        import traceback
        traceback.print_exc()


def check_training_results():
    """Check if training results file exists"""
    results_file = AI_WORK_DIR / "results" / "training_results.json"
    
    if results_file.exists():
        import json
        print("\n" + "="*60)
        print("TRAINING RESULTS (from training)")
        print("="*60)
        with open(results_file, 'r') as f:
            results = json.load(f)
            print(f"\n📊 Sentiment Model Training Results:")
            print(f"  Model: {results.get('model', 'N/A')}")
            print(f"  Accuracy: {results.get('accuracy', 0):.4f} ({results.get('accuracy', 0)*100:.2f}%)")
            print(f"  F1-Score: {results.get('f1', 0):.4f}")
            print(f"  Labels: {results.get('labels', [])}")
            print(f"  Trained: {results.get('timestamp', 'N/A')}")
    else:
        print(f"\n⚠️  Training results file not found at: {results_file}")
        print("   This is normal if you haven't run the training script recently.")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("MODEL ACCURACY EVALUATION")
    print("="*60)
    
    # Check for saved training results
    check_training_results()
    
    # Evaluate sentiment model
    evaluate_sentiment_model()
    
    # Evaluate emotion model
    evaluate_emotion_model()
    
    print("\n" + "="*60)
    print("EVALUATION COMPLETE")
    print("="*60)
    print("\nNote: This is a quick evaluation on test cases.")
    print("For full accuracy, you need the original test dataset.")

