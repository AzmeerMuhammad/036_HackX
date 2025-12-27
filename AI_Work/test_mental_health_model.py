"""
Test and evaluate the fine-tuned mental health empathetic response model.

This script evaluates the model on test data and provides metrics.
"""

import json
import torch
from pathlib import Path
from typing import Dict, List
import warnings

from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel
from rouge_score import rouge_scorer
import numpy as np
import pandas as pd

warnings.filterwarnings('ignore')

BASE_DIR = Path(__file__).parent
MODELS_DIR = BASE_DIR / "models"
RESULTS_DIR = BASE_DIR / "results"
DATA_DIR = BASE_DIR / "data"

def load_model_and_tokenizer(model_path: str, base_model: str = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"):
    """Load fine-tuned model and tokenizer"""
    model_path = Path(model_path)
    
    if not model_path.exists():
        raise FileNotFoundError(f"Model not found at: {model_path}")
    
    print(f"📥 Loading model from: {model_path}")
    
    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
        tokenizer.pad_token_id = tokenizer.eos_token_id
    
    # Load base model
    base_model_obj = AutoModelForCausalLM.from_pretrained(
        base_model,
        device_map="auto",
        torch_dtype=torch.float16,
        trust_remote_code=True
    )
    
    # Load PEFT adapter if it exists
    try:
        model = PeftModel.from_pretrained(base_model_obj, model_path)
        print("✓ Loaded PEFT adapter")
    except:
        # If no PEFT adapter, load full model
        model = AutoModelForCausalLM.from_pretrained(
            model_path,
            device_map="auto",
            torch_dtype=torch.float16,
            trust_remote_code=True
        )
        print("✓ Loaded full model")
    
    model.eval()
    return model, tokenizer

def format_prompt(journal_entry: str, emotions: List[Dict]) -> str:
    """Format prompt for inference (TinyLlama-Chat format)"""
    emotions_str = ", ".join([f"{e['emotion']} ({e.get('intensity', 0.7):.1f})" 
                             for e in emotions])
    
    # TinyLlama-Chat format uses <|system|>, <|user|>, <|assistant|> tokens
    system_msg = "You are a compassionate mental health professional. Generate an empathetic psychological response to the following journal entry, considering the identified emotions and their intensities."
    user_msg = f"""Journal Entry: {journal_entry}

Identified Emotions: {emotions_str}

Empathetic Response:"""
    
    return f"<|system|>\n{system_msg}<|user|>\n{user_msg}<|assistant|>\n"

def generate_response(
    model,
    tokenizer,
    journal_entry: str,
    emotions: List[Dict],
    generation_config: Dict,
    max_input_length: int = 1024
) -> str:
    """Generate response for a journal entry with emotions"""
    prompt = format_prompt(journal_entry, emotions)
    
    # Tokenize
    inputs = tokenizer(
        prompt,
        return_tensors="pt",
        truncation=True,
        max_length=max_input_length
    ).to(model.device)
    
    # Generate
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=generation_config["max_new_tokens"],
            temperature=generation_config["temperature"],
            top_p=generation_config["top_p"],
            top_k=generation_config.get("top_k", 50),
            num_beams=generation_config.get("num_beams", 1),
            length_penalty=generation_config.get("length_penalty", 1.0),
            early_stopping=generation_config.get("early_stopping", True),
            do_sample=generation_config.get("do_sample", True),
            pad_token_id=tokenizer.pad_token_id,
            eos_token_id=tokenizer.eos_token_id,
            repetition_penalty=generation_config.get("repetition_penalty", 1.1)
        )
    
    # Decode
    generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    # Extract only the response part (after <|assistant|>)
    if "<|assistant|>" in generated_text:
        response = generated_text.split("<|assistant|>")[-1].strip()
        # Remove any trailing special tokens
        response = response.replace("</s>", "").replace("<|endoftext|>", "").strip()
    elif "Empathetic Response:" in generated_text:
        response = generated_text.split("Empathetic Response:")[-1].strip()
    else:
        response = generated_text.replace(prompt, "").strip()
        response = response.replace("</s>", "").replace("<|endoftext|>", "").strip()
    
    return response

def calculate_rouge_scores(predictions: List[str], references: List[str]) -> Dict:
    """Calculate ROUGE scores"""
    scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
    
    scores = {
        'rouge1': {'precision': [], 'recall': [], 'fmeasure': []},
        'rouge2': {'precision': [], 'recall': [], 'fmeasure': []},
        'rougeL': {'precision': [], 'recall': [], 'fmeasure': []}
    }
    
    for pred, ref in zip(predictions, references):
        score = scorer.score(ref, pred)
        for metric in ['rouge1', 'rouge2', 'rougeL']:
            scores[metric]['precision'].append(score[metric].precision)
            scores[metric]['recall'].append(score[metric].recall)
            scores[metric]['fmeasure'].append(score[metric].fmeasure)
    
    # Average scores
    avg_scores = {}
    for metric in ['rouge1', 'rouge2', 'rougeL']:
        avg_scores[metric] = {
            'precision': np.mean(scores[metric]['precision']),
            'recall': np.mean(scores[metric]['recall']),
            'fmeasure': np.mean(scores[metric]['fmeasure'])
        }
    
    return avg_scores

def load_test_data(data_dir: Path, max_samples: int = 100) -> List[Dict]:
    """Load test data from empathetic dialogues (prefer processed data)"""
    processed_dir = data_dir / "processed_empathetic_dialogues"
    test_processed = processed_dir / "test_processed.json"
    
    # Try processed data first
    if test_processed.exists():
        print(f"📥 Loading processed test data from: {test_processed}")
        with open(test_processed, 'r', encoding='utf-8') as f:
            test_data = json.load(f)
        return test_data[:max_samples]
    
    # Fallback to raw data
    test_path = data_dir / "empatheticdialogues" / "empatheticdialogues" / "test.csv"
    
    if not test_path.exists():
        print(f"⚠️  Test file not found, using validation set")
        test_path = data_dir / "empatheticdialogues" / "empatheticdialogues" / "valid.csv"
    
    if not test_path.exists():
        return []
    
    print(f"📥 Loading raw test data from: {test_path}")
    print("💡 Run 'python process_empathetic_dialogues.py' first for better data quality.")
    
    df = pd.read_csv(test_path)
    
    def clean_text(text):
        if pd.isna(text) or str(text) == 'nan':
            return ""
        text = str(text).strip()
        text = text.replace('_comma_', ',')
        text = text.replace('_period_', '.')
        return text.strip()
    
    test_data = []
    seen_convs = set()
    
    # Process similar to training script
    for conv_id, group in df.groupby('conv_id'):
        if len(test_data) >= max_samples:
            break
        if conv_id in seen_convs:
            continue
        
        group = group.sort_values('utterance_idx')
        initial = group[group['utterance_idx'] == 1]
        
        if len(initial) == 0:
            continue
        
        initial_row = initial.iloc[0]
        journal_entry = clean_text(initial_row['prompt'])
        emotion = clean_text(initial_row['context'])
        initial_speaker = initial_row['speaker_idx']
        
        if not journal_entry or not emotion:
            continue
        
        for _, row in group.iterrows():
            if row['utterance_idx'] == 1:
                continue
            if row['speaker_idx'] != initial_speaker:
                response = clean_text(row['utterance'])
                if response and len(response) > 10:
                    test_data.append({
                        "journal_entry": journal_entry,
                        "emotion": emotion,
                        "empathetic_response": response
                    })
                    seen_convs.add(conv_id)
                    break
    
    return test_data

def evaluate_model(
    model_path: str,
    base_model: str = "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
    test_data: List[Dict] = None,
    generation_config: Dict = None
):
    """Evaluate model on test data"""
    print("=" * 60)
    print("🧪 Mental Health Empathetic Response Model Evaluation")
    print("=" * 60)
    
    # Load model
    model, tokenizer = load_model_and_tokenizer(model_path, base_model)
    
    # Default generation config
    if generation_config is None:
        generation_config = {
            "max_new_tokens": 256,
            "temperature": 0.7,
            "top_p": 0.9,
            "top_k": 50,
            "num_beams": 4,
            "length_penalty": 1.2,
            "early_stopping": True,
            "do_sample": True,
            "repetition_penalty": 1.1
        }
    
    # Load test data if not provided
    if test_data is None:
        test_data = load_test_data(DATA_DIR)
    
    if not test_data:
        print("⚠️  No test data found. Running on sample data.")
        test_data = [
            {
                "journal_entry": "I've been feeling really down lately. Nothing seems to bring me joy anymore.",
                "emotion": "sad",
                "empathetic_response": "I'm sorry you're going through this difficult time. It sounds like you're experiencing a period of sadness that's making it hard to find joy in things you used to enjoy."
            }
        ]
    
    print(f"\n📊 Evaluating on {len(test_data)} test samples...")
    
    predictions = []
    references = []
    
    for i, item in enumerate(test_data):
        journal_entry = item.get("journal_entry", "")
        emotion = item.get("emotion", "neutral")
        reference_response = item.get("empathetic_response", "")
        
        if not journal_entry:
            continue
        
        # Format emotions
        emotions = [{"emotion": emotion, "intensity": 0.7}]
        
        print(f"\n[{i+1}/{len(test_data)}] Processing...")
        print(f"Journal Entry: {journal_entry[:80]}...")
        print(f"Emotion: {emotion}")
        
        # Generate response
        predicted_response = generate_response(
            model, tokenizer, journal_entry, emotions, generation_config
        )
        
        predictions.append(predicted_response)
        references.append(reference_response)
        
        print(f"Reference: {reference_response[:80]}...")
        print(f"Predicted: {predicted_response[:80]}...")
    
    # Calculate metrics
    print("\n📊 Calculating ROUGE scores...")
    rouge_scores = calculate_rouge_scores(predictions, references)
    
    # Print results
    print("\n" + "=" * 60)
    print("📈 Evaluation Results")
    print("=" * 60)
    
    for metric in ['rouge1', 'rouge2', 'rougeL']:
        print(f"\n{metric.upper()}:")
        print(f"  Precision: {rouge_scores[metric]['precision']:.4f}")
        print(f"  Recall: {rouge_scores[metric]['recall']:.4f}")
        print(f"  F1-Score: {rouge_scores[metric]['fmeasure']:.4f}")
    
    # Save results
    results = {
        "rouge_scores": {k: {kk: float(vv) for kk, vv in v.items()} 
                        for k, v in rouge_scores.items()},
        "num_samples": len(test_data),
        "predictions": predictions[:10],  # Save first 10 for inspection
        "references": references[:10]
    }
    
    results_path = RESULTS_DIR / "mental_health_evaluation_results.json"
    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n✅ Evaluation complete!")
    print(f"📁 Results saved to: {results_path}")
    
    return rouge_scores, predictions, references

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Evaluate mental health empathetic response model")
    parser.add_argument(
        "--model_path",
        type=str,
        default="models/mental_health_empathetic_model",
        help="Path to fine-tuned model"
    )
    parser.add_argument(
        "--base_model",
        type=str,
        default="meta-llama/Llama-2-7b-chat-hf",
        help="Base model name"
    )
    parser.add_argument(
        "--config",
        type=str,
        default="config_mental_health.json",
        help="Path to config file"
    )
    parser.add_argument(
        "--max_samples",
        type=int,
        default=100,
        help="Maximum number of test samples to evaluate"
    )
    
    args = parser.parse_args()
    
    # Load generation config from main config if available
    generation_config = None
    config_path = BASE_DIR / args.config
    if config_path.exists():
        with open(config_path, 'r') as f:
            config = json.load(f)
            generation_config = config.get("generation", None)
    
    try:
        evaluate_model(
            args.model_path,
            args.base_model,
            generation_config=generation_config
        )
    except Exception as e:
        print(f"\n❌ Error during evaluation: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
