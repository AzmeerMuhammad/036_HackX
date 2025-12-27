"""
Fine-tune LLaMA with LoRA for Psychological Summary Generation
Uses PEFT (Parameter-Efficient Fine-Tuning) with LoRA adapters
"""
import os
import json
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

import torch
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling,
    EarlyStoppingCallback
)
from peft import (
    LoraConfig,
    get_peft_model,
    prepare_model_for_kbit_training,
    TaskType
)
from datasets import Dataset
import bitsandbytes as bnb

# Set device
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Using device: {device}")

# Paths
BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "training_data"
MODELS_DIR = BASE_DIR / "models"
MODELS_DIR.mkdir(exist_ok=True)
RESULTS_DIR = BASE_DIR / "results"
RESULTS_DIR.mkdir(exist_ok=True)


class PsychologicalSummaryDataset:
    """Dataset for psychological summary generation"""
    def __init__(self, tokenizer, data_path, max_length=512):
        self.tokenizer = tokenizer
        self.max_length = max_length
        
        # Load training data
        if data_path.suffix == '.json':
            with open(data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.examples = self._prepare_from_json(data)
        else:
            # Load from text file
            with open(data_path, 'r', encoding='utf-8') as f:
                content = f.read()
            # Split by separator
            examples = content.split("="*80)
            self.examples = [ex.strip() for ex in examples if ex.strip()]
        
        print(f"Loaded {len(self.examples)} training examples")
    
    def _prepare_from_json(self, data):
        """Prepare examples from JSON format"""
        examples = []
        for item in data:
            journal_text = item['journal_text']
            emotion_scores = item['emotion_scores']
            summary = item['summary']
            
            # Format emotion scores
            emotion_lines = []
            for emotion, score in emotion_scores.items():
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
            
            examples.append(prompt)
        
        return examples
    
    def __len__(self):
        return len(self.examples)
    
    def __getitem__(self, idx):
        text = self.examples[idx]
        
        # Tokenize
        encoding = self.tokenizer(
            text,
            truncation=True,
            padding='max_length',
            max_length=self.max_length,
            return_tensors='pt'
        )
        
        # Labels are the same as input_ids for language modeling
        return {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'labels': encoding['input_ids'].flatten()
        }


def load_training_data():
    """Load training data"""
    json_path = OUTPUT_DIR / "llama_training_data.json"
    txt_path = OUTPUT_DIR / "llama_training_data.txt"
    
    if json_path.exists():
        return json_path
    elif txt_path.exists():
        return txt_path
    else:
        raise FileNotFoundError(
            f"Training data not found. Please run synthesize_training_data.py first.\n"
            f"Expected: {json_path} or {txt_path}"
        )


def fine_tune_llama(
    model_name='meta-llama/Llama-2-7b-hf',  # Or 'meta-llama/Llama-2-7b-chat-hf'
    data_path=None,
    output_dir=None,
    num_epochs=3,
    batch_size=4,
    learning_rate=2e-4,
    use_4bit=True
):
    """Fine-tune LLaMA with LoRA"""
    print("\n" + "="*60)
    print(f"Fine-tuning LLaMA: {model_name}")
    print("="*60)
    
    if data_path is None:
        data_path = load_training_data()
    
    if output_dir is None:
        output_dir = MODELS_DIR / "llama_psychological_summary"
    
    print(f"\nLoading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    
    # Set padding token if not present
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
        tokenizer.pad_token_id = tokenizer.eos_token_id
    
    print(f"\nLoading model...")
    
    # Load model with 4-bit quantization if available
    if use_4bit and torch.cuda.is_available():
        from transformers import BitsAndBytesConfig
        
        quantization_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4"
        )
        
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            quantization_config=quantization_config,
            device_map="auto",
            trust_remote_code=True
        )
        
        # Prepare model for k-bit training
        model = prepare_model_for_kbit_training(model)
    else:
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            device_map="auto" if torch.cuda.is_available() else None,
            trust_remote_code=True
        )
        if not torch.cuda.is_available():
            model.to(device)
    
    # Configure LoRA
    lora_config = LoraConfig(
        r=16,  # Rank
        lora_alpha=32,  # LoRA alpha
        target_modules=["q_proj", "v_proj", "k_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
        lora_dropout=0.05,
        bias="none",
        task_type=TaskType.CAUSAL_LM
    )
    
    # Apply LoRA
    print("\nApplying LoRA adapters...")
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()
    
    # Create dataset
    print("\nLoading training data...")
    dataset = PsychologicalSummaryDataset(tokenizer, data_path)
    
    # Split into train/val
    from sklearn.model_selection import train_test_split
    train_size = int(0.9 * len(dataset))
    val_size = len(dataset) - train_size
    
    train_indices, val_indices = train_test_split(
        range(len(dataset)), test_size=val_size, random_state=42
    )
    
    train_dataset = Dataset.from_dict({
        'input_ids': [dataset[i]['input_ids'].tolist() for i in train_indices],
        'attention_mask': [dataset[i]['attention_mask'].tolist() for i in train_indices],
        'labels': [dataset[i]['labels'].tolist() for i in train_indices]
    })
    
    val_dataset = Dataset.from_dict({
        'input_ids': [dataset[i]['input_ids'].tolist() for i in val_indices],
        'attention_mask': [dataset[i]['attention_mask'].tolist() for i in val_indices],
        'labels': [dataset[i]['labels'].tolist() for i in val_indices]
    })
    
    print(f"Train samples: {len(train_dataset)}")
    print(f"Validation samples: {len(val_dataset)}")
    
    # Data collator
    data_collator = DataCollatorForLanguageModeling(
        tokenizer=tokenizer,
        mlm=False  # Causal LM, not masked LM
    )
    
    # Training arguments
    training_args = TrainingArguments(
        output_dir=str(output_dir),
        num_train_epochs=num_epochs,
        per_device_train_batch_size=batch_size,
        per_device_eval_batch_size=batch_size,
        gradient_accumulation_steps=4,
        warmup_steps=100,
        logging_steps=10,
        eval_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        save_total_limit=2,
        learning_rate=learning_rate,
        fp16=torch.cuda.is_available(),
        optim="paged_adamw_8bit" if use_4bit else "adamw_torch",
        report_to="none",
    )
    
    # Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        data_collator=data_collator,
        callbacks=[EarlyStoppingCallback(early_stopping_patience=2)]
    )
    
    # Train
    print("\nStarting training...")
    trainer.train()
    
    # Save model
    print(f"\nSaving model to {output_dir}...")
    trainer.save_model()
    tokenizer.save_pretrained(str(output_dir))
    
    # Save LoRA adapters separately
    lora_path = output_dir / "lora_adapters"
    model.save_pretrained(str(lora_path))
    print(f"Saved LoRA adapters to {lora_path}")
    
    print("\n" + "="*60)
    print("Fine-tuning Complete!")
    print("="*60)
    print(f"\nModel saved to: {output_dir}")
    print(f"LoRA adapters saved to: {lora_path}")
    
    return model, tokenizer


def main():
    """Main function"""
    print("\n" + "="*60)
    print("LLaMA Fine-tuning Pipeline with LoRA")
    print("="*60)
    
    # Note: You'll need to authenticate with Hugging Face to access LLaMA models
    # Run: huggingface-cli login
    # Or set HF_TOKEN environment variable
    
    try:
        # Check for Hugging Face token
        hf_token = os.getenv('HF_TOKEN') or os.getenv('HUGGINGFACE_TOKEN')
        if not hf_token:
            print("\nWarning: HF_TOKEN not set. You may need to authenticate:")
            print("  huggingface-cli login")
            print("  Or set HF_TOKEN environment variable")
        
        # Use a smaller model if LLaMA-2 is not available
        # Alternatives: microsoft/phi-2, microsoft/DialoGPT-medium
        model_name = 'meta-llama/Llama-2-7b-hf'
        
        # For testing, you can use a smaller model that doesn't require auth
        # model_name = 'gpt2'  # Uncomment for testing without LLaMA access
        
        print(f"\nUsing model: {model_name}")
        print("Note: If you don't have access to LLaMA-2, consider using:")
        print("  - microsoft/phi-2 (smaller, good quality)")
        print("  - gpt2 (for testing)")
        
        # Fine-tune
        model, tokenizer = fine_tune_llama(
            model_name=model_name,
            num_epochs=3,
            batch_size=2,  # Adjust based on GPU memory
            learning_rate=2e-4,
            use_4bit=True  # Use 4-bit quantization to save memory
        )
        
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        print("\nTroubleshooting:")
        print("1. Make sure you have authenticated with Hugging Face")
        print("2. Check that you have access to the LLaMA model")
        print("3. Try using a smaller model like 'gpt2' for testing")
        print("4. Ensure you have enough GPU memory (or use CPU with smaller batch size)")


if __name__ == "__main__":
    main()

