"""
Evaluation Script for Psychological Summary Generation
Computes metrics like ROUGE, BERTScore, and perplexity
"""
import os
import json
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

try:
    from rouge_score import rouge_scorer
    ROUGE_AVAILABLE = True
except ImportError:
    ROUGE_AVAILABLE = False
    print("Warning: rouge-score not installed. Install with: pip install rouge-score")

try:
    from bert_score import score as bert_score
    BERTSCORE_AVAILABLE = True
except ImportError:
    BERTSCORE_AVAILABLE = False
    print("Warning: bert-score not installed. Install with: pip install bert-score")

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel
import numpy as np

from inference_pipeline import PsychologicalSummaryGenerator

BASE_DIR = Path(__file__).parent
MODELS_DIR = BASE_DIR / "models"
RESULTS_DIR = BASE_DIR / "results"
RESULTS_DIR.mkdir(exist_ok=True)


def compute_rouge_scores(references, predictions):
    """Compute ROUGE scores"""
    if not ROUGE_AVAILABLE:
        return None
    
    scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
    
    rouge1_scores = []
    rouge2_scores = []
    rougeL_scores = []
    
    for ref, pred in zip(references, predictions):
        scores = scorer.score(ref, pred)
        rouge1_scores.append(scores['rouge1'].fmeasure)
        rouge2_scores.append(scores['rouge2'].fmeasure)
        rougeL_scores.append(scores['rougeL'].fmeasure)
    
    return {
        'rouge1': {
            'mean': np.mean(rouge1_scores),
            'std': np.std(rouge1_scores)
        },
        'rouge2': {
            'mean': np.mean(rouge2_scores),
            'std': np.std(rouge2_scores)
        },
        'rougeL': {
            'mean': np.mean(rougeL_scores),
            'std': np.std(rougeL_scores)
        }
    }


def compute_bertscore(references, predictions):
    """Compute BERTScore"""
    if not BERTSCORE_AVAILABLE:
        return None
    
    P, R, F1 = bert_score(predictions, references, lang='en', verbose=False)
    
    return {
        'precision': {
            'mean': P.mean().item(),
            'std': P.std().item()
        },
        'recall': {
            'mean': R.mean().item(),
            'std': R.std().item()
        },
        'f1': {
            'mean': F1.mean().item(),
            'std': F1.std().item()
        }
    }


def compute_perplexity(model, tokenizer, texts, device='cuda'):
    """Compute perplexity for generated summaries"""
    model.eval()
    perplexities = []
    
    for text in texts:
        inputs = tokenizer(text, return_tensors='pt', truncation=True, max_length=512)
        inputs = {k: v.to(device) for k, v in inputs.items()}
        
        with torch.no_grad():
            outputs = model(**inputs, labels=inputs['input_ids'])
            loss = outputs.loss
            perplexity = torch.exp(loss).item()
            perplexities.append(perplexity)
    
    return {
        'mean': np.mean(perplexities),
        'std': np.std(perplexities),
        'values': perplexities
    }


def evaluate_on_test_set(generator, test_data_path=None):
    """Evaluate model on test set"""
    print("\n" + "="*60)
    print("Model Evaluation")
    print("="*60)
    
    # Load test data
    if test_data_path is None:
        test_data_path = BASE_DIR / "training_data" / "llama_training_data.json"
    
    if not test_data_path.exists():
        print(f"Test data not found at {test_data_path}")
        print("Using sample data for evaluation...")
        test_data = [
            {
                'journal_text': "I've been feeling numb and drained, nothing excites me like it used to.",
                'summary': "The entry reflects deep sadness and a pronounced sense of emptiness."
            }
        ]
    else:
        with open(test_data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Use a subset for evaluation
            test_data = data[:50]  # Evaluate on first 50 examples
    
    print(f"\nEvaluating on {len(test_data)} examples...")
    
    # Generate predictions
    references = []
    predictions = []
    journal_texts = []
    
    print("\nGenerating predictions...")
    for i, item in enumerate(test_data):
        journal_text = item['journal_text']
        reference_summary = item.get('summary', '')
        
        if not reference_summary:
            # Generate reference from template if not available
            from synthesize_training_data import generate_empathetic_summary_template
            emotion_results = generator.emotion_classifier.predict_emotions([journal_text])
            reference_summary = generate_empathetic_summary_template(journal_text, emotion_results[0])
        
        # Generate prediction
        result = generator.generate_summary(journal_text)
        predicted_summary = result['summary']
        
        references.append(reference_summary)
        predictions.append(predicted_summary)
        journal_texts.append(journal_text)
        
        if (i + 1) % 10 == 0:
            print(f"  Processed {i + 1}/{len(test_data)}")
    
    # Compute metrics
    results = {}
    
    # ROUGE scores
    if ROUGE_AVAILABLE:
        print("\nComputing ROUGE scores...")
        rouge_scores = compute_rouge_scores(references, predictions)
        if rouge_scores:
            results['rouge'] = rouge_scores
            print(f"ROUGE-1: {rouge_scores['rouge1']['mean']:.4f}")
            print(f"ROUGE-2: {rouge_scores['rouge2']['mean']:.4f}")
            print(f"ROUGE-L: {rouge_scores['rougeL']['mean']:.4f}")
    
    # BERTScore
    if BERTSCORE_AVAILABLE:
        print("\nComputing BERTScore...")
        bert_scores = compute_bertscore(references, predictions)
        if bert_scores:
            results['bertscore'] = bert_scores
            print(f"BERTScore F1: {bert_scores['f1']['mean']:.4f}")
            print(f"BERTScore Precision: {bert_scores['precision']['mean']:.4f}")
            print(f"BERTScore Recall: {bert_scores['recall']['mean']:.4f}")
    
    # Perplexity (on generated summaries)
    print("\nComputing perplexity...")
    try:
        perplexity = compute_perplexity(
            generator.model,
            generator.tokenizer,
            predictions,
            device=generator.device
        )
        results['perplexity'] = perplexity
        print(f"Perplexity: {perplexity['mean']:.4f} ± {perplexity['std']:.4f}")
    except Exception as e:
        print(f"Could not compute perplexity: {e}")
    
    # Save results
    results['num_examples'] = len(test_data)
    results['sample_predictions'] = [
        {
            'journal_text': journal_texts[i],
            'reference': references[i],
            'prediction': predictions[i]
        }
        for i in range(min(5, len(test_data)))  # Save first 5 examples
    ]
    
    output_path = RESULTS_DIR / "evaluation_results.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\nEvaluation results saved to: {output_path}")
    
    return results


def main():
    """Main evaluation function"""
    print("\n" + "="*60)
    print("Model Evaluation Pipeline")
    print("="*60)
    
    try:
        # Initialize generator
        print("\nLoading models...")
        generator = PsychologicalSummaryGenerator(use_lora=True)
        
        # Evaluate
        results = evaluate_on_test_set(generator)
        
        print("\n" + "="*60)
        print("Evaluation Complete!")
        print("="*60)
        
        # Print summary
        if 'rouge' in results:
            print(f"\nROUGE-1: {results['rouge']['rouge1']['mean']:.4f}")
            print(f"ROUGE-2: {results['rouge']['rouge2']['mean']:.4f}")
            print(f"ROUGE-L: {results['rouge']['rougeL']['mean']:.4f}")
        
        if 'bertscore' in results:
            print(f"\nBERTScore F1: {results['bertscore']['f1']['mean']:.4f}")
        
        if 'perplexity' in results:
            print(f"\nPerplexity: {results['perplexity']['mean']:.4f}")
    
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        print("\nNote: Some metrics require additional packages:")
        print("  pip install rouge-score bert-score")


if __name__ == "__main__":
    main()

