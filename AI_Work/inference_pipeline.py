"""
Inference Pipeline for Psychological Summary Generation
End-to-end pipeline: Journal Entry -> Emotion Scores -> Psychological Summary
"""
import os
import json
from pathlib import Path
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel
import warnings
warnings.filterwarnings('ignore')

# Import emotion classifier
import sys
sys.path.append(str(Path(__file__).parent))
from synthesize_training_data import EmotionClassifier

BASE_DIR = Path(__file__).parent
MODELS_DIR = BASE_DIR / "models"
RESULTS_DIR = BASE_DIR / "results"
RESULTS_DIR.mkdir(exist_ok=True)

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


class PsychologicalSummaryGenerator:
    """Complete pipeline for generating psychological summaries"""
    
    def __init__(
        self,
        emotion_classifier_path=None,
        llama_model_path=None,
        base_model_name='meta-llama/Llama-2-7b-hf',
        use_lora=True
    ):
        # Load emotion classifier
        print("Loading emotion classifier...")
        self.emotion_classifier = EmotionClassifier(emotion_classifier_path)
        
        # Load LLaMA model
        print("Loading LLaMA model...")
        if llama_model_path is None:
            llama_model_path = MODELS_DIR / "llama_psychological_summary"
        
        if not llama_model_path.exists():
            raise FileNotFoundError(
                f"LLaMA model not found at {llama_model_path}. "
                f"Please fine-tune it first using fine_tune_llama.py"
            )
        
        self.tokenizer = AutoTokenizer.from_pretrained(str(llama_model_path))
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        
        if use_lora:
            # Load base model
            self.base_model = AutoModelForCausalLM.from_pretrained(
                base_model_name,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                device_map="auto" if torch.cuda.is_available() else None,
                trust_remote_code=True
            )
            
            # Load LoRA adapters
            lora_path = llama_model_path / "lora_adapters"
            if lora_path.exists():
                self.model = PeftModel.from_pretrained(self.base_model, str(lora_path))
            else:
                # Try loading from main directory
                self.model = PeftModel.from_pretrained(self.base_model, str(llama_model_path))
        else:
            self.model = AutoModelForCausalLM.from_pretrained(
                str(llama_model_path),
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                device_map="auto" if torch.cuda.is_available() else None,
                trust_remote_code=True
            )
        
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        if not torch.cuda.is_available():
            self.model.to(self.device)
        
        self.model.eval()
        print("Models loaded successfully!")
    
    def format_prompt(self, journal_text, emotion_scores):
        """Format the input prompt"""
        emotion_lines = []
        for emotion in DEPRESSION_EMOTIONS:
            score = emotion_scores.get(emotion, 0.0)
            emotion_lines.append(f"- {emotion}: {score:.2f}")
        
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
"""
        
        return prompt
    
    def generate_summary(self, journal_text, max_length=200, temperature=0.7, top_p=0.9):
        """Generate psychological summary for a journal entry"""
        # Step 1: Get emotion scores
        emotion_results = self.emotion_classifier.predict_emotions([journal_text])
        emotion_scores = emotion_results[0]
        
        # Step 2: Format prompt
        prompt = self.format_prompt(journal_text, emotion_scores)
        
        # Step 3: Generate summary
        inputs = self.tokenizer(
            prompt,
            return_tensors='pt',
            truncation=True,
            max_length=512
        )
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_length,
                temperature=temperature,
                top_p=top_p,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id,
                eos_token_id=self.tokenizer.eos_token_id
            )
        
        # Decode
        full_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract summary (everything after [HUMANIZED SUMMARY])
        if "[HUMANIZED SUMMARY]" in full_text:
            summary = full_text.split("[HUMANIZED SUMMARY]")[-1].strip()
        else:
            # Fallback: take the generated part
            summary = self.tokenizer.decode(outputs[0][inputs['input_ids'].shape[1]:], skip_special_tokens=True).strip()
        
        return {
            'journal_text': journal_text,
            'emotion_scores': emotion_scores,
            'summary': summary,
            'full_prompt': prompt
        }
    
    def generate_batch(self, journal_texts, max_length=200, temperature=0.7, top_p=0.9):
        """Generate summaries for multiple journal entries"""
        results = []
        for text in journal_texts:
            result = self.generate_summary(text, max_length, temperature, top_p)
            results.append(result)
        return results


def main():
    """Main inference function"""
    print("\n" + "="*60)
    print("Psychological Summary Generation Pipeline")
    print("="*60)
    
    try:
        # Initialize generator
        generator = PsychologicalSummaryGenerator(
            use_lora=True
        )
        
        # Example journal entries
        example_entries = [
            "I've been feeling numb and drained, nothing excites me like it used to. Every day feels the same, and I can't remember the last time I felt genuinely happy.",
            "I keep pushing people away, but I'm so lonely. I want connection but I'm afraid of being hurt again. It's like I'm stuck in this cycle.",
            "I'm angry all the time, at everything and nothing. Small things set me off and I don't know why. I feel like I'm losing control."
        ]
        
        print("\n" + "="*60)
        print("Generating Summaries for Example Entries")
        print("="*60)
        
        results = generator.generate_batch(example_entries)
        
        # Display results
        for i, result in enumerate(results, 1):
            print(f"\n{'='*60}")
            print(f"Example {i}")
            print(f"{'='*60}")
            print(f"\nJournal Entry:")
            print(f"  {result['journal_text']}")
            
            print(f"\nDetected Emotions:")
            for emotion, score in result['emotion_scores'].items():
                if score > 0.3:
                    print(f"  {emotion}: {score:.2f}")
            
            print(f"\nPsychological Summary:")
            print(f"  {result['summary']}")
        
        # Save results
        output_path = RESULTS_DIR / "inference_results.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\n\nResults saved to: {output_path}")
        
        # Interactive mode
        print("\n" + "="*60)
        print("Interactive Mode")
        print("="*60)
        print("Enter journal entries to generate summaries (type 'quit' to exit)")
        
        while True:
            journal_text = input("\nJournal Entry: ").strip()
            if journal_text.lower() in ['quit', 'exit', 'q']:
                break
            
            if not journal_text:
                continue
            
            result = generator.generate_summary(journal_text)
            
            print(f"\nDetected Emotions:")
            for emotion, score in sorted(result['emotion_scores'].items(), key=lambda x: x[1], reverse=True):
                if score > 0.2:
                    print(f"  {emotion}: {score:.2f}")
            
            print(f"\nPsychological Summary:")
            print(f"  {result['summary']}")
    
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        print("\nTroubleshooting:")
        print("1. Make sure emotion classifier is trained (train_emotion_classifier.py)")
        print("2. Make sure LLaMA model is fine-tuned (fine_tune_llama.py)")
        print("3. Check that model paths are correct")


if __name__ == "__main__":
    main()

