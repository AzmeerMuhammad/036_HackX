"""
Test and evaluate the fine-tuned mental health summary model.

This script evaluates the model on test data and provides metrics
for summary quality.
"""

import json
import torch
from pathlib import Path
from typing import List, Dict
import warnings

from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from peft import PeftModel
from rouge_score import rouge_scorer
import numpy as np

warnings.filterwarnings('ignore')

BASE_DIR = Path(__file__).parent
MODELS_DIR = BASE_DIR / "models"
RESULTS_DIR = BASE_DIR / "results"
DATA_DIR = BASE_DIR / "data"

def load_model_and_tokenizer(model_path: str, base_model: str = "meta-llama/Llama-2-7b-chat-hf"):
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

def format_prompt(journal_entry: str) -> str:
    """Format prompt for inference"""
    return f"""<s>[INST] <<SYS>>
You are a mental health professional. Generate a concise psychological summary and breakdown of the following journal entry.
<</SYS>>

Journal Entry: {journal_entry}

Psychological Summary: [/INST]"""

def generate_summary(
    model,
    tokenizer,
    journal_entry: str,
    generation_config: Dict,
    max_input_length: int = 1024
) -> str:
    """Generate summary for a journal entry"""
    prompt = format_prompt(journal_entry)
    
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
            eos_token_id=tokenizer.eos_token_id
        )
    
    # Decode
    generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    # Extract only the summary part (after the prompt)
    if "Psychological Summary:" in generated_text:
        summary = generated_text.split("Psychological Summary:")[-1].strip()
    else:
        # Fallback: remove prompt
        summary = generated_text.replace(prompt, "").strip()
    
    return summary

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

def load_test_data(data_dir: Path) -> List[Dict]:
    """Load test data"""
    test_data = []
    
    # Try loading from psychological summary dataset
    psych_dir = data_dir / "psychological_summary"
    if psych_dir.exists():
        json_files = list(psych_dir.glob("*.json"))
        for json_file in json_files:
            if "template" in json_file.name:
                continue
            try:
                with open(json_file, 'r') as f:
                    data = json.load(f)
                if isinstance(data, list):
                    test_data.extend(data)
                elif isinstance(data, dict):
                    test_data.append(data)
            except:
                pass
    
    return test_data

def evaluate_model(
    model_path: str,
    base_model: str = "meta-llama/Llama-2-7b-chat-hf",
    test_data: List[Dict] = None,
    generation_config: Dict = None
):
    """Evaluate model on test data"""
    print("=" * 60)
    print("🧪 Mental Health Summary Model Evaluation")
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
            "do_sample": True
        }
    
    # Load test data if not provided
    if test_data is None:
        test_data = load_test_data(DATA_DIR)
    
    if not test_data:
        print("⚠️  No test data found. Running on sample data.")
        test_data = [
            {
                "journal_entry": "I've been feeling really down lately. Nothing seems to bring me joy anymore, and I find myself isolating from friends and family. Work has become overwhelming, and I can't seem to focus on anything.",
                "summary": "Patient reports symptoms of depression including anhedonia, social withdrawal, and difficulty concentrating. Work-related stress may be contributing factor."
            }
        ]
    
    print(f"\n📊 Evaluating on {len(test_data)} test samples...")
    
    predictions = []
    references = []
    
    for i, item in enumerate(test_data):
        journal_entry = item.get("journal_entry", item.get("text", ""))
        reference_summary = item.get("summary", item.get("tldr", ""))
        
        if not journal_entry:
            continue
        
        print(f"\n[{i+1}/{len(test_data)}] Processing...")
        print(f"Journal Entry: {journal_entry[:100]}...")
        
        # Generate summary
        predicted_summary = generate_summary(
            model, tokenizer, journal_entry, generation_config
        )
        
        predictions.append(predicted_summary)
        references.append(reference_summary)
        
        print(f"Reference: {reference_summary[:100]}...")
        print(f"Predicted: {predicted_summary[:100]}...")
    
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
    
    parser = argparse.ArgumentParser(description="Evaluate mental health summary model")
    parser.add_argument(
        "--model_path",
        type=str,
        default="models/mental_health_summary_model",
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

