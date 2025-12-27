"""
Synthesize Training Data for LLaMA Fine-tuning
Combines emotion scores from classifier with empathetic summaries
"""
import os
import pandas as pd
import numpy as np
from pathlib import Path
import json
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import warnings
warnings.filterwarnings('ignore')

# Import emotion classifier
import sys
sys.path.append(str(Path(__file__).parent))

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"
OUTPUT_DIR = BASE_DIR / "training_data"
OUTPUT_DIR.mkdir(exist_ok=True)

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


def preprocess_text(text):
    """
    Clean and preprocess Reddit text for better model performance.
    Handles Reddit-specific formatting, URLs, emojis, etc.
    """
    import re
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


class EmotionClassifier:
    """Wrapper for emotion classifier inference"""
    def __init__(self, model_path=None):
        if model_path is None:
            model_path = MODELS_DIR / "emotion_classifier"
        
        if not model_path.exists():
            raise FileNotFoundError(
                f"Emotion classifier not found at {model_path}. "
                f"Please train it first using train_emotion_classifier.py"
            )
        
        print(f"Loading emotion classifier from {model_path}...")
        self.tokenizer = AutoTokenizer.from_pretrained(str(model_path))
        self.model = AutoModelForSequenceClassification.from_pretrained(str(model_path))
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model.to(self.device)
        self.model.eval()
        
        # Load emotion names and thresholds
        emotion_info_path = model_path / "emotion_info.json"
        if emotion_info_path.exists():
            with open(emotion_info_path, 'r') as f:
                emotion_info = json.load(f)
                self.emotion_names = emotion_info['emotion_names']
                self.optimal_thresholds = emotion_info.get('optimal_thresholds', [0.5] * len(self.emotion_names))
        else:
            self.emotion_names = DEPRESSION_EMOTIONS
            self.optimal_thresholds = [0.5] * len(self.emotion_names)
        
        print(f"Loaded classifier with {len(self.emotion_names)} emotions")
    
    def predict_emotions(self, texts, batch_size=16, use_thresholds=True, preprocess=True):
        """
        Predict emotion scores for texts.
        
        Args:
            texts: Input text(s) - string or list of strings
            batch_size: Batch size for inference
            use_thresholds: Whether to use optimal thresholds for binary predictions
            preprocess: Whether to preprocess text (default: True)
        """
        if isinstance(texts, str):
            texts = [texts]
        
        # Preprocess texts if enabled
        if preprocess:
            texts = [preprocess_text(text) for text in texts]
        
        all_probs = []
        
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i+batch_size]
            
            # Tokenize (using max_length=512 to match training)
            encodings = self.tokenizer(
                batch_texts,
                truncation=True,
                padding='max_length',
                max_length=512,  # Updated to match training
                return_tensors='pt'
            )
            
            encodings = {k: v.to(self.device) for k, v in encodings.items()}
            
            # Predict
            with torch.no_grad():
                outputs = self.model(**encodings)
                logits = outputs.logits
                probs = torch.sigmoid(logits).cpu().numpy()
            
            all_probs.append(probs)
        
        all_probs = np.vstack(all_probs)
        
        # Create emotion score dictionary for each text
        results = []
        for probs_row in all_probs:
            if use_thresholds and len(self.optimal_thresholds) == len(probs_row):
                # Use probabilities (continuous scores)
                emotion_scores = {emotion: float(score) for emotion, score in zip(self.emotion_names, probs_row)}
            else:
                # Use probabilities (continuous scores)
                emotion_scores = {emotion: float(score) for emotion, score in zip(self.emotion_names, probs_row)}
            results.append(emotion_scores)
        
        return results


def load_journal_texts():
    """Load journal-style texts for training data synthesis"""
    print("\n" + "="*60)
    print("Loading Journal Texts")
    print("="*60)
    
    # Try to load from DepressionEmo (these are Reddit posts, good for journal-style)
    depression_emo_path = DATA_DIR / "depression_emo_prepared.csv"
    if depression_emo_path.exists():
        print(f"\nLoading from: {depression_emo_path}")
        df = pd.read_csv(depression_emo_path)
        texts = df['text'].astype(str).values
        print(f"Loaded {len(texts)} texts")
        return texts
    
    # Try raw DepressionEmo
    depression_emo_dir = DATA_DIR / "DepressionEmo"
    if depression_emo_dir.exists():
        csv_files = list(depression_emo_dir.glob("*.csv"))
        if csv_files:
            df = pd.read_csv(csv_files[0])
            # Find text column
            text_col = None
            for col in df.columns:
                if col.lower() in ['text', 'post', 'content']:
                    text_col = col
                    break
            if text_col:
                texts = df[text_col].astype(str).values
                print(f"Loaded {len(texts)} texts from {csv_files[0]}")
                return texts
    
    # Fallback: use EmpatheticDialogues context
    empathetic_path = DATA_DIR / "empathetic_dialogues_prepared.csv"
    if empathetic_path.exists():
        df = pd.read_csv(empathetic_path)
        if 'context' in df.columns:
            texts = df['context'].astype(str).values
            print(f"Loaded {len(texts)} texts from EmpatheticDialogues")
            return texts
    
    raise FileNotFoundError(
        "No journal texts found. Please run data_loaders.py first."
    )


def generate_empathetic_summary_template(journal_text, emotion_scores):
    """Generate a template-based empathetic summary"""
    # Filter emotions with score > 0.3
    significant_emotions = {
        emotion: score for emotion, score in emotion_scores.items() 
        if score > 0.3
    }
    
    if not significant_emotions:
        # Default to top emotion
        top_emotion = max(emotion_scores.items(), key=lambda x: x[1])
        significant_emotions = {top_emotion[0]: top_emotion[1]}
    
    # Sort by score
    sorted_emotions = sorted(significant_emotions.items(), key=lambda x: x[1], reverse=True)
    
    # Build summary
    emotion_descriptions = []
    for emotion, score in sorted_emotions[:3]:  # Top 3 emotions
        if emotion == 'sadness':
            emotion_descriptions.append(f"deep sadness (intensity: {score:.2f})")
        elif emotion == 'emptiness':
            emotion_descriptions.append(f"a pronounced sense of emptiness (intensity: {score:.2f})")
        elif emotion == 'hopelessness':
            emotion_descriptions.append(f"feelings of hopelessness (intensity: {score:.2f})")
        elif emotion == 'loneliness':
            emotion_descriptions.append(f"loneliness (intensity: {score:.2f})")
        elif emotion == 'anger':
            emotion_descriptions.append(f"anger (intensity: {score:.2f})")
        elif emotion == 'guilt':
            emotion_descriptions.append(f"guilt (intensity: {score:.2f})")
        elif emotion == 'shame':
            emotion_descriptions.append(f"shame (intensity: {score:.2f})")
        elif emotion == 'fear':
            emotion_descriptions.append(f"fear (intensity: {score:.2f})")
        else:
            emotion_descriptions.append(f"{emotion} (intensity: {score:.2f})")
    
    if len(emotion_descriptions) == 1:
        summary = f"The entry reflects {emotion_descriptions[0]}, suggesting a significant emotional experience that shapes the narrative of the writing."
    elif len(emotion_descriptions) == 2:
        summary = f"The entry reflects {emotion_descriptions[0]} and {emotion_descriptions[1]}, suggesting a complex emotional experience that shapes the narrative of the writing."
    else:
        summary = f"The entry reflects {', '.join(emotion_descriptions[:-1])}, and {emotion_descriptions[-1]}, suggesting a multifaceted emotional experience that shapes the narrative of the writing."
    
    return summary


def create_training_example(journal_text, emotion_scores, summary=None):
    """Create a training example in the prompt format"""
    if summary is None:
        summary = generate_empathetic_summary_template(journal_text, emotion_scores)
    
    # Format emotion scores
    emotion_lines = []
    for emotion in DEPRESSION_EMOTIONS:
        score = emotion_scores.get(emotion, 0.0)
        emotion_lines.append(f"- {emotion}: {score:.2f}")
    
    # Create prompt
    prompt = f"""[CONTEXT]

Journal Entry:
"{journal_text}"

Detected Emotions:
{chr(10).join(emotion_lines)}

[INSTRUCTION]
Based on the journal entry and the detected emotion scores above, write a
humanized psychological summary that reflects the emotional experience
expressed in the text. Do not give advice or diagnosis—just interpret
how the emotions manifest in the writing.

[HUMANIZED SUMMARY]
{summary}"""
    
    return prompt


def synthesize_training_data(num_samples=1000, use_empathetic_dialogues=True):
    """Synthesize training data for LLaMA fine-tuning"""
    print("\n" + "="*60)
    print("Synthesizing Training Data")
    print("="*60)
    
    # Load emotion classifier
    classifier = EmotionClassifier()
    
    # Load journal texts
    journal_texts = load_journal_texts()
    
    # Limit number of samples
    if len(journal_texts) > num_samples:
        np.random.seed(42)
        indices = np.random.choice(len(journal_texts), num_samples, replace=False)
        journal_texts = journal_texts[indices]
    
    print(f"\nProcessing {len(journal_texts)} journal entries...")
    
    # Get emotion scores
    print("Predicting emotions...")
    emotion_results = classifier.predict_emotions(journal_texts.tolist())
    
    # Load EmpatheticDialogues for style if available
    empathetic_summaries = None
    if use_empathetic_dialogues:
        empathetic_path = DATA_DIR / "empathetic_dialogues_prepared.csv"
        if empathetic_path.exists():
            df = pd.read_csv(empathetic_path)
            if 'response' in df.columns:
                empathetic_summaries = df['response'].astype(str).values
                print(f"Loaded {len(empathetic_summaries)} empathetic responses for style reference")
    
    # Create training examples
    training_examples = []
    
    print("\nCreating training examples...")
    for i, (text, emotion_scores) in enumerate(zip(journal_texts, emotion_results)):
        # Use empathetic response as summary if available and similar emotion context
        summary = None
        if empathetic_summaries is not None and i < len(empathetic_summaries):
            # Use empathetic response as inspiration
            empathetic_response = empathetic_summaries[i]
            # Combine with template
            summary = generate_empathetic_summary_template(text, emotion_scores)
            # Optionally blend with empathetic response style
            if len(empathetic_response) > 20:
                # Use empathetic response as base, adapt to emotion scores
                summary = empathetic_response[:100] + " " + summary
        
        example = create_training_example(text, emotion_scores, summary)
        training_examples.append(example)
        
        if (i + 1) % 100 == 0:
            print(f"  Processed {i + 1}/{len(journal_texts)} examples")
    
    # Save training data
    output_path = OUTPUT_DIR / "llama_training_data.txt"
    with open(output_path, 'w', encoding='utf-8') as f:
        for example in training_examples:
            f.write(example + "\n\n" + "="*80 + "\n\n")
    
    print(f"\nSaved {len(training_examples)} training examples to: {output_path}")
    
    # Also save as JSON for easier loading
    json_output_path = OUTPUT_DIR / "llama_training_data.json"
    json_data = []
    for text, emotion_scores in zip(journal_texts, emotion_results):
        summary = generate_empathetic_summary_template(text, emotion_scores)
        json_data.append({
            'journal_text': text,
            'emotion_scores': emotion_scores,
            'summary': summary
        })
    
    with open(json_output_path, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, indent=2, ensure_ascii=False)
    
    print(f"Saved JSON format to: {json_output_path}")
    
    # Print sample
    print("\n" + "="*60)
    print("Sample Training Example:")
    print("="*60)
    print(training_examples[0])
    
    return training_examples


def main():
    """Main function"""
    print("\n" + "="*60)
    print("Training Data Synthesis Pipeline")
    print("="*60)
    
    try:
        # Synthesize training data
        training_examples = synthesize_training_data(
            num_samples=1000,  # Adjust based on available data
            use_empathetic_dialogues=True
        )
        
        print("\n" + "="*60)
        print("Synthesis Complete!")
        print("="*60)
        print(f"\nGenerated {len(training_examples)} training examples")
        print(f"Saved to: {OUTPUT_DIR}")
        
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    main()

