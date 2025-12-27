"""
Fine-tune Llama model for generating empathetic responses from journal entries and emotions.

This script:
1. Loads empathetic dialogues dataset
2. Formats data as: Journal Entry + Emotions (with intensity) -> Empathetic Response
3. Fine-tunes Llama using LoRA for efficient training
4. Saves the fine-tuned model for inference
"""

import os
import json
import torch
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict, List
import warnings
import re

from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    TrainingArguments,
    Trainer,
    EarlyStoppingCallback,
    BitsAndBytesConfig,
    set_seed
)
from peft import (
    LoraConfig,
    get_peft_model,
    prepare_model_for_kbit_training,
    TaskType
)
from datasets import Dataset
import numpy as np

warnings.filterwarnings('ignore')

# Paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"
RESULTS_DIR = BASE_DIR / "results"

for d in [MODELS_DIR, RESULTS_DIR]:
    d.mkdir(exist_ok=True)

def load_config(config_path: str = "config_mental_health.json") -> Dict:
    """Load hyperparameter configuration"""
    config_file = BASE_DIR / config_path
    if not config_file.exists():
        raise FileNotFoundError(f"Config file not found: {config_file}")
    
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    print(f"✓ Loaded config from: {config_file}")
    return config

def format_emotions(emotion_label: str, intensity: float = 0.7) -> str:
    """Format emotions with intensity for the prompt"""
    # Map common emotion labels to more descriptive format
    emotion_map = {
        'sentimental': 'sentimentality',
        'afraid': 'fear',
        'proud': 'pride',
        'faithful': 'faithfulness',
        'terrified': 'terror',
        'hopeful': 'hope',
        'angry': 'anger',
        'disappointed': 'disappointment',
        'impressed': 'impression',
        'anxious': 'anxiety',
        'excited': 'excitement',
        'annoyed': 'annoyance',
        'grateful': 'gratitude',
        'lonely': 'loneliness',
        'ashamed': 'shame',
        'sad': 'sadness',
        'joyful': 'joy',
        'nostalgic': 'nostalgia',
        'guilty': 'guilt',
        'surprised': 'surprise',
        'content': 'contentment',
        'devastated': 'devastation',
        'embarrassed': 'embarrassment',
        'furious': 'fury',
        'anticipating': 'anticipation',
        'jealous': 'jealousy',
        'prepared': 'preparation',
        'pensive': 'pensiveness',
        'trusting': 'trust'
    }
    
    emotion_display = emotion_map.get(emotion_label.lower(), emotion_label.lower())
    intensity_label = "high" if intensity > 0.7 else "medium" if intensity > 0.4 else "low"
    
    return f"{emotion_display} (intensity: {intensity_label})"

def load_empathetic_dialogues(data_dir: Path, use_processed: bool = True) -> List[Dict]:
    """Load and format empathetic dialogues dataset
    
    Args:
        data_dir: Base data directory
        use_processed: If True, use preprocessed data. If False, process raw data.
    """
    processed_dir = data_dir / "processed_empathetic_dialogues"
    
    # Try to load processed data first
    if use_processed and processed_dir.exists():
        train_processed = processed_dir / "train_processed.json"
        val_processed = processed_dir / "val_processed.json"
        
        if train_processed.exists():
            print(f"📥 Loading processed data from: {processed_dir}")
            dialogues = []
            
            # Load training data
            with open(train_processed, 'r', encoding='utf-8') as f:
                train_data = json.load(f)
                for item in train_data:
                    dialogues.append({
                        "journal_entry": item['journal_entry'],
                        "emotion": item['emotion'],
                        "empathetic_response": item['empathetic_response'],
                        "split": "train"
                    })
            
            # Load validation data
            if val_processed.exists():
                with open(val_processed, 'r', encoding='utf-8') as f:
                    val_data = json.load(f)
                    for item in val_data:
                        dialogues.append({
                            "journal_entry": item['journal_entry'],
                            "emotion": item['emotion'],
                            "empathetic_response": item['empathetic_response'],
                            "split": "val"
                        })
            
            train_count = len([d for d in dialogues if d['split'] == 'train'])
            val_count = len([d for d in dialogues if d['split'] == 'val'])
            print(f"✓ Loaded {train_count} training samples")
            print(f"✓ Loaded {val_count} validation samples")
            return dialogues
    
    # Fallback: process raw data on the fly
    print("⚠️  Processed data not found. Processing raw data...")
    print("💡 Run 'python process_empathetic_dialogues.py' first for better performance.")
    
    train_path = data_dir / "empatheticdialogues" / "empatheticdialogues" / "train.csv"
    val_path = data_dir / "empatheticdialogues" / "empatheticdialogues" / "valid.csv"
    
    if not train_path.exists():
        raise FileNotFoundError(f"Empathetic dialogues not found at {train_path}")
    
    dialogues = []
    
    # Helper function to clean text
    def clean_text(text):
        if pd.isna(text) or str(text) == 'nan':
            return ""
        text = str(text).strip()
        text = text.replace('_comma_', ',')
        text = text.replace('_period_', '.')
        text = text.replace('_exclamation_', '!')
        text = text.replace('_question_', '?')
        return text.strip()
    
    # Load and process training data
    print(f"📥 Loading raw data from: {train_path}")
    train_df = pd.read_csv(train_path)
    
    # Group by conversation and extract first response
    seen_convs = set()
    for conv_id, group in train_df.groupby('conv_id'):
        if conv_id in seen_convs:
            continue
        group = group.sort_values('utterance_idx')
        
        # Get initial prompt and emotion
        initial = group[group['utterance_idx'] == 1]
        if len(initial) == 0:
            continue
        
        initial_row = initial.iloc[0]
        journal_entry = clean_text(initial_row['prompt'])
        emotion = clean_text(initial_row['context'])
        initial_speaker = initial_row['speaker_idx']
        
        if not journal_entry or not emotion:
            continue
        
        # Find first response from different speaker
        for _, row in group.iterrows():
            if row['utterance_idx'] == 1:
                continue
            if row['speaker_idx'] != initial_speaker:
                response = clean_text(row['utterance'])
                if response and len(response) > 10:
                    dialogues.append({
                        "journal_entry": journal_entry,
                        "emotion": emotion,
                        "empathetic_response": response,
                        "split": "train"
                    })
                    seen_convs.add(conv_id)
                    break
    
    # Process validation data
    if val_path.exists():
        print(f"📥 Loading validation set from: {val_path}")
        val_df = pd.read_csv(val_path)
        seen_convs = set()
        
        for conv_id, group in val_df.groupby('conv_id'):
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
                        dialogues.append({
                            "journal_entry": journal_entry,
                            "emotion": emotion,
                            "empathetic_response": response,
                            "split": "val"
                        })
                        seen_convs.add(conv_id)
                        break
    
    train_count = len([d for d in dialogues if d['split'] == 'train'])
    val_count = len([d for d in dialogues if d['split'] == 'val'])
    print(f"✓ Loaded {train_count} training samples")
    print(f"✓ Loaded {val_count} validation samples")
    return dialogues

def format_prompt(journal_entry: str, emotions: List[Dict]) -> str:
    """Format the prompt for the model with journal entry and emotions (TinyLlama-Chat format)"""
    # Format emotions list
    emotions_str = ", ".join([f"{e['emotion']} ({e.get('intensity', 0.7):.1f})" 
                             for e in emotions])
    
    # TinyLlama-Chat format uses <|system|>, <|user|>, <|assistant|> tokens
    system_msg = "You are a compassionate mental health professional. Generate an empathetic psychological response to the following journal entry, considering the identified emotions and their intensities."
    user_msg = f"""Journal Entry: {journal_entry}

Identified Emotions: {emotions_str}

Empathetic Response:"""
    
    return f"<|system|>\n{system_msg}<|user|>\n{user_msg}<|assistant|>\n"

def preprocess_data(data: List[Dict], tokenizer, config: Dict) -> Dataset:
    """Preprocess data for training"""
    print("\n🔄 Preprocessing data...")
    
    max_input_length = config["data"]["max_input_length"]
    max_output_length = config["data"]["max_output_length"]
    
    processed_data = []
    
    for item in data:
        journal_entry = item["journal_entry"]
        emotion = item["emotion"]
        response = item["empathetic_response"]
        
        # Create emotions list (using emotion from dataset, default intensity 0.7)
        emotions = [{"emotion": emotion, "intensity": 0.7}]
        
        # Format prompt
        prompt = format_prompt(journal_entry, emotions)
        # TinyLlama uses <|assistant|> token, response should end with <|endoftext|> or just be appended
        full_text = prompt + response
        
        # Tokenize
        tokenized = tokenizer(
            full_text,
            truncation=True,
            max_length=max_input_length + max_output_length,
            padding=False,
            return_tensors=None
        )
        
        # Tokenize prompt separately to find where labels start
        prompt_tokenized = tokenizer(
            prompt,
            truncation=True,
            max_length=max_input_length,
            padding=False,
            return_tensors=None
        )
        
        prompt_len = len(prompt_tokenized["input_ids"])
        
        # Create labels (only for the response part, -100 for prompt)
        labels = [-100] * prompt_len + tokenized["input_ids"][prompt_len:]
        
        # Ensure same length
        max_len = max_input_length + max_output_length
        input_ids = tokenized["input_ids"][:max_len]
        attention_mask = tokenized["attention_mask"][:max_len]
        labels = labels[:max_len]
        
        # Pad if necessary
        if len(input_ids) < max_len:
            pad_len = max_len - len(input_ids)
            input_ids = input_ids + [tokenizer.pad_token_id] * pad_len
            attention_mask = attention_mask + [0] * pad_len
            labels = labels + [-100] * pad_len
        
        processed_data.append({
            "input_ids": input_ids,
            "attention_mask": attention_mask,
            "labels": labels
        })
    
    print(f"✓ Preprocessed {len(processed_data)} samples")
    return Dataset.from_list(processed_data)

def setup_model_and_tokenizer(config: Dict):
    """Setup model and tokenizer with quantization if needed"""
    model_config = config["model"]
    base_model = model_config["base_model"]
    
    print(f"\n📥 Loading model: {base_model}")
    
    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(base_model)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
        tokenizer.pad_token_id = tokenizer.eos_token_id
    
    # Setup quantization if needed
    quantization_config = None
    if model_config.get("load_in_8bit"):
        quantization_config = BitsAndBytesConfig(
            load_in_8bit=True,
            llm_int8_threshold=6.0
        )
    elif model_config.get("load_in_4bit"):
        quantization_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4"
        )
    
    # Load model
    model = AutoModelForCausalLM.from_pretrained(
        base_model,
        quantization_config=quantization_config,
        device_map="auto",
        torch_dtype=torch.float16 if quantization_config is None else None,
        trust_remote_code=True
    )
    
    # Prepare for PEFT if using quantization
    if quantization_config:
        model = prepare_model_for_kbit_training(model)
    
    # Setup LoRA if enabled
    if model_config.get("use_peft", True):
        lora_config = config["lora"]
        peft_config = LoraConfig(
            task_type=TaskType.CAUSAL_LM,
            inference_mode=False,
            r=lora_config["r"],
            lora_alpha=lora_config["lora_alpha"],
            lora_dropout=lora_config["lora_dropout"],
            target_modules=lora_config["target_modules"],
            bias="none"
        )
        model = get_peft_model(model, peft_config)
        model.print_trainable_parameters()
    
    return model, tokenizer

def train_model(config: Dict):
    """Main training function"""
    # Set seed
    seed = config.get("seed", 42)
    set_seed(seed)
    torch.manual_seed(seed)
    np.random.seed(seed)
    
    # Load data
    print("\n" + "="*60)
    print("🧠 Mental Health Empathetic Response Model Training")
    print("="*60)
    
    all_data = load_empathetic_dialogues(DATA_DIR)
    
    if not all_data:
        raise ValueError("No training data found!")
    
    print(f"\n📊 Total samples: {len(all_data)}")
    
    # Setup model and tokenizer
    model, tokenizer = setup_model_and_tokenizer(config)
    
    # Preprocess data
    dataset = preprocess_data(all_data, tokenizer, config)
    
    # Split dataset - preserve original train/val split if available
    train_data = [d for d in all_data if d.get('split') == 'train']
    val_data = [d for d in all_data if d.get('split') == 'val']
    
    if not val_data:
        # If no explicit val split, create one
        train_test_split = dataset.train_test_split(
            test_size=1 - config["data"]["train_split"],
            seed=seed
        )
        train_dataset = train_test_split["train"]
        
        # Further split test into val and test
        val_test_size = config["data"]["test_split"] / (config["data"]["val_split"] + config["data"]["test_split"])
        val_test_split = train_test_split["test"].train_test_split(
            test_size=val_test_size,
            seed=seed
        )
        val_dataset = val_test_split["train"]
        test_dataset = val_test_split["test"]
    else:
        # Use original splits
        train_dataset = preprocess_data(train_data, tokenizer, config)
        val_dataset = preprocess_data(val_data, tokenizer, config)
        test_dataset = val_dataset  # Use val as test if no separate test set
    
    print(f"\n📊 Dataset splits:")
    print(f"   - Train: {len(train_dataset)}")
    print(f"   - Validation: {len(val_dataset)}")
    print(f"   - Test: {len(test_dataset)}")
    
    # Setup training arguments
    training_config = config["training"]
    training_args = TrainingArguments(
        output_dir=str(MODELS_DIR / training_config["output_dir"]),
        num_train_epochs=training_config["num_train_epochs"],
        per_device_train_batch_size=training_config["per_device_train_batch_size"],
        per_device_eval_batch_size=training_config["per_device_eval_batch_size"],
        gradient_accumulation_steps=training_config["gradient_accumulation_steps"],
        learning_rate=training_config["learning_rate"],
        warmup_ratio=training_config["warmup_ratio"],
        weight_decay=training_config["weight_decay"],
        lr_scheduler_type=training_config["lr_scheduler_type"],
        logging_steps=training_config["logging_steps"],
        save_steps=training_config["save_steps"],
        eval_steps=training_config["eval_steps"],
        save_total_limit=training_config["save_total_limit"],
        evaluation_strategy=training_config["evaluation_strategy"],
        save_strategy=training_config["save_strategy"],
        load_best_model_at_end=training_config["load_best_model_at_end"],
        metric_for_best_model=training_config["metric_for_best_model"],
        greater_is_better=training_config["greater_is_better"],
        fp16=training_config["fp16"],
        bf16=training_config["bf16"],
        gradient_checkpointing=training_config["gradient_checkpointing"],
        report_to=training_config["report_to"],
        seed=seed
    )
    
    # Create trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        callbacks=[EarlyStoppingCallback(early_stopping_patience=3)]
    )
    
    # Train
    print("\n🚀 Starting training...")
    trainer.train()
    
    # Evaluate
    print("\n📊 Evaluating on test set...")
    test_results = trainer.evaluate(eval_dataset=test_dataset)
    print(f"Test Loss: {test_results.get('eval_loss', 'N/A')}")
    
    # Save model
    print("\n💾 Saving model...")
    final_model_path = MODELS_DIR / training_config["output_dir"]
    trainer.save_model(str(final_model_path))
    tokenizer.save_pretrained(str(final_model_path))
    
    # Save training metadata
    metadata = {
        "model": config["model"]["base_model"],
        "training_samples": len(all_data),
        "train_samples": len(train_dataset),
        "val_samples": len(val_dataset),
        "test_samples": len(test_dataset),
        "test_loss": float(test_results.get('eval_loss', 0)),
        "config": config,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    metadata_path = RESULTS_DIR / "mental_health_training_metadata.json"
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"\n✅ Training complete!")
    print(f"📁 Model saved to: {final_model_path}")
    print(f"📁 Metadata saved to: {metadata_path}")
    
    return trainer, model, tokenizer

def main():
    """Main entry point"""
    try:
        config = load_config()
        train_model(config)
    except Exception as e:
        print(f"\n❌ Error during training: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
