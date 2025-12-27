"""
Generate empathetic responses from journal entries and emotions using the fine-tuned model.

Usage:
    python predict_mental_health.py --text "Your journal entry" --emotions "sad:0.8,anxious:0.6"
    python predict_mental_health.py --file journal_entry.json
"""

import json
import torch
from pathlib import Path
from typing import Dict, List
import argparse
import warnings

from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel

warnings.filterwarnings('ignore')

BASE_DIR = Path(__file__).parent
MODELS_DIR = BASE_DIR / "models"

def load_model_and_tokenizer(
    model_path: str,
    base_model: str = "meta-llama/Llama-2-7b-chat-hf"
):
    """Load fine-tuned model and tokenizer"""
    model_path = Path(model_path)
    
    if not model_path.exists():
        raise FileNotFoundError(
            f"Model not found at: {model_path}\n"
            f"Please train the model first using train_mental_health_model.py"
        )
    
    print(f"📥 Loading model from: {model_path}")
    
    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
        tokenizer.pad_token_id = tokenizer.eos_token_id
    
    # Load base model
    try:
        base_model_obj = AutoModelForCausalLM.from_pretrained(
            base_model,
            device_map="auto",
            torch_dtype=torch.float16,
            trust_remote_code=True,
            low_cpu_mem_usage=True
        )
        
        # Try to load PEFT adapter
        try:
            model = PeftModel.from_pretrained(base_model_obj, model_path)
            print("✓ Loaded PEFT adapter")
        except:
            # If no PEFT adapter, load full model
            model = AutoModelForCausalLM.from_pretrained(
                model_path,
                device_map="auto",
                torch_dtype=torch.float16,
                trust_remote_code=True,
                low_cpu_mem_usage=True
            )
            print("✓ Loaded full model")
    except Exception as e:
        print(f"⚠️  Error loading base model, trying direct load: {e}")
        model = AutoModelForCausalLM.from_pretrained(
            model_path,
            device_map="auto",
            torch_dtype=torch.float16,
            trust_remote_code=True,
            low_cpu_mem_usage=True
        )
        print("✓ Loaded model directly")
    
    model.eval()
    return model, tokenizer

def parse_emotions(emotions_str: str) -> List[Dict]:
    """Parse emotions string into list of emotion dictionaries
    
    Format: "emotion1:intensity1,emotion2:intensity2" or "emotion1,emotion2"
    """
    emotions = []
    
    if not emotions_str:
        return emotions
    
    for item in emotions_str.split(','):
        item = item.strip()
        if ':' in item:
            emotion, intensity = item.split(':', 1)
            try:
                intensity = float(intensity)
            except:
                intensity = 0.7
        else:
            emotion = item
            intensity = 0.7  # Default intensity
        
        emotions.append({
            "emotion": emotion.strip(),
            "intensity": max(0.0, min(1.0, intensity))  # Clamp between 0 and 1
        })
    
    return emotions

def format_prompt(journal_entry: str, emotions: List[Dict]) -> str:
    """Format the prompt for the model with journal entry and emotions"""
    # Format emotions list
    emotions_str = ", ".join([f"{e['emotion']} ({e.get('intensity', 0.7):.1f})" 
                             for e in emotions])
    
    return f"""<s>[INST] <<SYS>>
You are a compassionate mental health professional. Generate an empathetic psychological response to the following journal entry, considering the identified emotions and their intensities.
<</SYS>>

Journal Entry: {journal_entry}

Identified Emotions: {emotions_str}

Empathetic Response: [/INST]"""

def generate_response(
    model,
    tokenizer,
    journal_entry: str,
    emotions: List[Dict],
    generation_config: Dict,
    max_input_length: int = 1024
) -> str:
    """
    Generate empathetic response for a journal entry with emotions
    
    Args:
        model: Fine-tuned model
        tokenizer: Tokenizer
        journal_entry: Input journal entry text
        emotions: List of emotion dicts with 'emotion' and 'intensity' keys
        generation_config: Generation parameters
        max_input_length: Maximum input length
    
    Returns:
        Generated empathetic response text
    """
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
    
    # Extract only the response part (after the prompt)
    if "Empathetic Response:" in generated_text:
        response = generated_text.split("Empathetic Response:")[-1].strip()
    else:
        # Fallback: remove prompt
        response = generated_text.replace(prompt, "").strip()
    
    return response

def predict_from_input(
    journal_entry: str,
    emotions: List[Dict],
    model_path: str = "models/mental_health_empathetic_model",
    base_model: str = "meta-llama/Llama-2-7b-chat-hf",
    config_path: str = "config_mental_health.json"
) -> str:
    """
    Generate empathetic response from journal entry and emotions
    
    Args:
        journal_entry: Input journal entry
        emotions: List of emotion dicts with 'emotion' and 'intensity'
        model_path: Path to fine-tuned model
        base_model: Base model name
        config_path: Path to config file
    
    Returns:
        Generated empathetic response
    """
    # Load config
    config_file = BASE_DIR / config_path
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
    
    if config_file.exists():
        with open(config_file, 'r') as f:
            config = json.load(f)
            if "generation" in config:
                generation_config.update(config["generation"])
    
    # Load model
    model, tokenizer = load_model_and_tokenizer(model_path, base_model)
    
    # Generate response
    print(f"\n💬 Generating empathetic response...")
    response = generate_response(
        model, tokenizer, journal_entry, emotions, generation_config
    )
    
    return response

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Generate empathetic responses from journal entries and emotions"
    )
    parser.add_argument(
        "--text",
        type=str,
        help="Journal entry text"
    )
    parser.add_argument(
        "--emotions",
        type=str,
        help="Comma-separated emotions with intensities (e.g., 'sad:0.8,anxious:0.6' or 'sad,anxious')"
    )
    parser.add_argument(
        "--file",
        type=str,
        help="Path to JSON file with 'journal_entry' and 'emotions' fields"
    )
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
        "--output",
        type=str,
        help="Path to save output (optional)"
    )
    
    args = parser.parse_args()
    
    # Get journal entry and emotions
    journal_entry = None
    emotions = []
    
    if args.file:
        file_path = Path(args.file)
        if not file_path.exists():
            print(f"❌ File not found: {file_path}")
            return
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            journal_entry = data.get("journal_entry", "")
            if "emotions" in data:
                if isinstance(data["emotions"], list):
                    emotions = data["emotions"]
                elif isinstance(data["emotions"], str):
                    emotions = parse_emotions(data["emotions"])
    
    if args.text:
        journal_entry = args.text
    
    if args.emotions:
        emotions = parse_emotions(args.emotions)
    
    if not journal_entry or not journal_entry.strip():
        # Interactive mode
        print("📝 Enter journal entry (press Ctrl+D or Ctrl+Z when done):")
        try:
            lines = []
            while True:
                line = input()
                lines.append(line)
        except EOFError:
            journal_entry = "\n".join(lines)
        
        if not emotions:
            emotions_str = input("\nEnter emotions (format: 'emotion1:intensity1,emotion2:intensity2'): ").strip()
            emotions = parse_emotions(emotions_str)
    
    if not journal_entry or not journal_entry.strip():
        print("❌ No journal entry provided")
        return
    
    if not emotions:
        print("⚠️  No emotions provided, using default")
        emotions = [{"emotion": "neutral", "intensity": 0.5}]
    
    try:
        # Generate response
        response = predict_from_input(
            journal_entry,
            emotions,
            args.model_path,
            args.base_model,
            args.config
        )
        
        # Display results
        print("\n" + "=" * 60)
        print("📋 Journal Entry:")
        print("=" * 60)
        print(journal_entry[:500] + ("..." if len(journal_entry) > 500 else ""))
        
        print("\n" + "=" * 60)
        print("😊 Identified Emotions:")
        print("=" * 60)
        for e in emotions:
            print(f"  - {e['emotion']}: {e.get('intensity', 0.7):.1f}")
        
        print("\n" + "=" * 60)
        print("💬 Empathetic Response:")
        print("=" * 60)
        print(response)
        
        # Save output if requested
        if args.output:
            output_path = Path(args.output)
            output_data = {
                "journal_entry": journal_entry,
                "emotions": emotions,
                "empathetic_response": response
            }
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2)
            print(f"\n✅ Output saved to: {output_path}")
        
    except Exception as e:
        print(f"\n❌ Error generating response: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
