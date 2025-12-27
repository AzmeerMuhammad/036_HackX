"""
Generate mental health notes summaries from journal entries using the fine-tuned model.

Usage:
    python predict_mental_health.py --text "Your journal entry here..."
    python predict_mental_health.py --file journal_entry.txt
"""

import json
import torch
from pathlib import Path
from typing import Dict, Optional
import argparse
import warnings

from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
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

def format_prompt(journal_entry: str, summary_type: str = "summary") -> str:
    """Format the prompt for the model"""
    if summary_type == "empathetic":
        return f"""<s>[INST] <<SYS>>
You are a compassionate mental health professional. Generate an empathetic psychological response to the following journal entry.
<</SYS>>

Journal Entry: {journal_entry}

Psychological Response: [/INST]"""
    else:
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
    summary_type: str = "summary",
    max_input_length: int = 1024
) -> str:
    """
    Generate psychological summary for a journal entry
    
    Args:
        model: Fine-tuned model
        tokenizer: Tokenizer
        journal_entry: Input journal entry text
        generation_config: Generation parameters
        summary_type: "summary" or "empathetic"
        max_input_length: Maximum input length
    
    Returns:
        Generated summary text
    """
    prompt = format_prompt(journal_entry, summary_type)
    
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
    
    # Extract only the summary part (after the prompt)
    if summary_type == "empathetic":
        if "Psychological Response:" in generated_text:
            summary = generated_text.split("Psychological Response:")[-1].strip()
        else:
            summary = generated_text.replace(prompt, "").strip()
    else:
        if "Psychological Summary:" in generated_text:
            summary = generated_text.split("Psychological Summary:")[-1].strip()
        else:
            # Fallback: remove prompt
            summary = generated_text.replace(prompt, "").strip()
    
    return summary

def predict_from_text(
    journal_entry: str,
    model_path: str = "models/mental_health_summary_model",
    base_model: str = "meta-llama/Llama-2-7b-chat-hf",
    config_path: str = "config_mental_health.json",
    summary_type: str = "summary"
) -> str:
    """
    Generate summary from journal entry text
    
    Args:
        journal_entry: Input journal entry
        model_path: Path to fine-tuned model
        base_model: Base model name
        config_path: Path to config file
        summary_type: "summary" or "empathetic"
    
    Returns:
        Generated summary
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
    
    # Generate summary
    print(f"\n📝 Generating {summary_type}...")
    summary = generate_summary(
        model, tokenizer, journal_entry, generation_config, summary_type
    )
    
    return summary

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Generate mental health summaries from journal entries"
    )
    parser.add_argument(
        "--text",
        type=str,
        help="Journal entry text to summarize"
    )
    parser.add_argument(
        "--file",
        type=str,
        help="Path to file containing journal entry"
    )
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
    parser.add_argument(
        "--type",
        type=str,
        choices=["summary", "empathetic"],
        default="summary",
        help="Type of output: 'summary' for psychological summary, 'empathetic' for empathetic response"
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Path to save output (optional)"
    )
    
    args = parser.parse_args()
    
    # Get journal entry
    journal_entry = None
    
    if args.text:
        journal_entry = args.text
    elif args.file:
        file_path = Path(args.file)
        if not file_path.exists():
            print(f"❌ File not found: {file_path}")
            return
        with open(file_path, 'r', encoding='utf-8') as f:
            journal_entry = f.read()
    else:
        # Interactive mode
        print("📝 Enter journal entry (press Ctrl+D or Ctrl+Z when done):")
        try:
            lines = []
            while True:
                line = input()
                lines.append(line)
        except EOFError:
            journal_entry = "\n".join(lines)
    
    if not journal_entry or not journal_entry.strip():
        print("❌ No journal entry provided")
        return
    
    try:
        # Generate summary
        summary = predict_from_text(
            journal_entry,
            args.model_path,
            args.base_model,
            args.config,
            args.type
        )
        
        # Display results
        print("\n" + "=" * 60)
        print("📋 Journal Entry:")
        print("=" * 60)
        print(journal_entry[:500] + ("..." if len(journal_entry) > 500 else ""))
        
        print("\n" + "=" * 60)
        if args.type == "empathetic":
            print("💬 Empathetic Psychological Response:")
        else:
            print("🧠 Psychological Summary:")
        print("=" * 60)
        print(summary)
        
        # Save output if requested
        if args.output:
            output_path = Path(args.output)
            output_data = {
                "journal_entry": journal_entry,
                "summary": summary,
                "type": args.type
            }
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2)
            print(f"\n✅ Output saved to: {output_path}")
        
    except Exception as e:
        print(f"\n❌ Error generating summary: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

