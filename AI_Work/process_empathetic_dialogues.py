"""
Data Processing Script for Empathetic Dialogues Dataset

This script processes the raw empathetic dialogues dataset to:
1. Clean special tokens (_comma_, etc.)
2. Extract first empathetic responses from conversations
3. Filter out low-quality samples
4. Create properly formatted training data
5. Handle emotion labels and intensity
"""

import pandas as pd
import json
from pathlib import Path
from typing import List, Dict, Tuple
import re

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
EMPATHETIC_DIALOGUES_DIR = DATA_DIR / "empatheticdialogues" / "empatheticdialogues"
PROCESSED_DATA_DIR = DATA_DIR / "processed_empathetic_dialogues"

PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)

def clean_text(text: str) -> str:
    """Clean text by replacing special tokens and normalizing"""
    if pd.isna(text) or text == 'nan':
        return ""
    
    text = str(text).strip()
    
    # Replace special tokens
    text = text.replace('_comma_', ',')
    text = text.replace('_period_', '.')
    text = text.replace('_exclamation_', '!')
    text = text.replace('_question_', '?')
    text = text.replace('_apostrophe_', "'")
    text = text.replace('_colon_', ':')
    text = text.replace('_semicolon_', ';')
    text = text.replace('_newline_', '\n')
    
    # Clean up multiple spaces
    text = re.sub(r'\s+', ' ', text)
    
    # Remove tags like <HI>
    text = re.sub(r'<[^>]+>', '', text)
    
    return text.strip()

def extract_first_empathetic_response(df: pd.DataFrame) -> pd.DataFrame:
    """
    Extract the first empathetic response from each conversation.
    
    In the dataset:
    - utterance_idx=1: Initial prompt/statement (speaker_idx is usually odd: 1, 3, 5...)
    - utterance_idx=2: First empathetic response (speaker_idx is usually even: 0, 2, 4...)
    
    We want: prompt + emotion -> first empathetic response
    """
    processed_rows = []
    seen_conversations = set()
    
    # Group by conversation
    for conv_id, group in df.groupby('conv_id'):
        if conv_id in seen_conversations:
            continue
        
        # Sort by utterance_idx
        group = group.sort_values('utterance_idx')
        
        # Get the initial prompt (usually utterance_idx=1)
        initial_prompt = None
        emotion = None
        
        for _, row in group.iterrows():
            if row['utterance_idx'] == 1:
                initial_prompt = clean_text(row['prompt'])
                emotion = clean_text(row['context'])
                break
        
        if not initial_prompt or not emotion:
            continue
        
        # Find the first empathetic response (usually utterance_idx=2, speaker_idx is different from initial)
        first_response = None
        initial_speaker = None
        
        for _, row in group.iterrows():
            if row['utterance_idx'] == 1:
                initial_speaker = row['speaker_idx']
                continue
            
            # Get first response from a different speaker
            if row['speaker_idx'] != initial_speaker:
                first_response = clean_text(row['utterance'])
                
                # Skip if it's just a greeting or too short
                if first_response and len(first_response) > 10:
                    # Check for common greeting patterns
                    first_lower = first_response.lower()
                    if not (first_lower.startswith('hi') or 
                           first_lower.startswith('hello') or
                           first_lower.startswith('hey')):
                        processed_rows.append({
                            'journal_entry': initial_prompt,
                            'emotion': emotion,
                            'empathetic_response': first_response,
                            'conv_id': conv_id,
                            'utterance_idx': row['utterance_idx']
                        })
                        seen_conversations.add(conv_id)
                        break
    
    return pd.DataFrame(processed_rows)

def process_dataset(split: str = 'train') -> pd.DataFrame:
    """Process a dataset split"""
    file_path = EMPATHETIC_DIALOGUES_DIR / f"{split}.csv"
    
    if not file_path.exists():
        print(f"⚠️  File not found: {file_path}")
        return pd.DataFrame()
    
    print(f"\nLoading {split} split...")
    # Handle CSV parsing errors gracefully - some rows may have extra commas in text
    # Use quoting=1 (QUOTE_ALL) to properly handle commas in text fields
    try:
        # Try with on_bad_lines (pandas >= 1.3.0)
        df = pd.read_csv(file_path, on_bad_lines='skip', encoding='utf-8', quoting=1)
    except TypeError:
        # Older pandas versions use error_bad_lines
        try:
            df = pd.read_csv(file_path, error_bad_lines=False, encoding='utf-8', quoting=1)
        except:
            df = pd.read_csv(file_path, encoding='latin-1', quoting=1)
    except Exception as e:
        print(f"   Warning: Error reading CSV: {e}")
        print(f"   Trying with latin-1 encoding...")
        try:
            df = pd.read_csv(file_path, encoding='latin-1', quoting=1, on_bad_lines='skip')
        except:
            df = pd.read_csv(file_path, encoding='latin-1', quoting=1, error_bad_lines=False)
    
    print(f"   Original rows: {len(df)}")
    print(f"   Unique conversations: {df['conv_id'].nunique()}")
    
    # Extract first empathetic responses
    processed_df = extract_first_empathetic_response(df)
    
    print(f"   Processed rows: {len(processed_df)}")
    
    # Additional filtering (only if we have data)
    if len(processed_df) > 0:
        # Remove very short or very long entries
        processed_df = processed_df[
            (processed_df['journal_entry'].str.len() > 10) &
            (processed_df['journal_entry'].str.len() < 2000) &
            (processed_df['empathetic_response'].str.len() > 10) &
            (processed_df['empathetic_response'].str.len() < 1000)
        ]
    else:
        # Return empty DataFrame with correct columns
        return pd.DataFrame(columns=['journal_entry', 'emotion', 'empathetic_response', 'conv_id', 'utterance_idx'])
    
    print(f"   After length filtering: {len(processed_df)}")
    
    # Remove duplicates
    initial_len = len(processed_df)
    processed_df = processed_df.drop_duplicates(subset=['journal_entry', 'emotion'])
    print(f"   After deduplication: {len(processed_df)} (removed {initial_len - len(processed_df)})")
    
    return processed_df

def get_emotion_statistics(df: pd.DataFrame) -> Dict:
    """Get statistics about emotions in the dataset"""
    emotion_counts = df['emotion'].value_counts()
    
    return {
        'total_emotions': len(emotion_counts),
        'emotion_distribution': emotion_counts.to_dict(),
        'total_samples': len(df)
    }

def save_processed_data(train_df: pd.DataFrame, val_df: pd.DataFrame, test_df: pd.DataFrame):
    """Save processed data in multiple formats"""
    print("\nSaving processed data...")
    
    # Save as CSV
    train_df.to_csv(PROCESSED_DATA_DIR / "train_processed.csv", index=False)
    val_df.to_csv(PROCESSED_DATA_DIR / "val_processed.csv", index=False)
    test_df.to_csv(PROCESSED_DATA_DIR / "test_processed.csv", index=False)
    
    print(f"   Saved CSV files to {PROCESSED_DATA_DIR}")
    
    # Save as JSON (for easy loading)
    train_json = train_df[['journal_entry', 'emotion', 'empathetic_response']].to_dict('records')
    val_json = val_df[['journal_entry', 'emotion', 'empathetic_response']].to_dict('records')
    test_json = test_df[['journal_entry', 'emotion', 'empathetic_response']].to_dict('records')
    
    with open(PROCESSED_DATA_DIR / "train_processed.json", 'w', encoding='utf-8') as f:
        json.dump(train_json, f, indent=2, ensure_ascii=False)
    
    with open(PROCESSED_DATA_DIR / "val_processed.json", 'w', encoding='utf-8') as f:
        json.dump(val_json, f, indent=2, ensure_ascii=False)
    
    with open(PROCESSED_DATA_DIR / "test_processed.json", 'w', encoding='utf-8') as f:
        json.dump(test_json, f, indent=2, ensure_ascii=False)
    
    print(f"   Saved JSON files to {PROCESSED_DATA_DIR}")
    
    # Save statistics
    stats = {
        'train': get_emotion_statistics(train_df),
        'val': get_emotion_statistics(val_df),
        'test': get_emotion_statistics(test_df),
        'total_emotions': len(pd.concat([train_df, val_df, test_df])['emotion'].unique())
    }
    
    with open(PROCESSED_DATA_DIR / "statistics.json", 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)
    
    print(f"   Saved statistics to {PROCESSED_DATA_DIR / 'statistics.json'}")

def main():
    """Main processing function"""
    import sys
    import io
    # Fix Windows console encoding
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    
    print("=" * 60)
    print("Processing Empathetic Dialogues Dataset")
    print("=" * 60)
    
    # Process all splits
    train_df = process_dataset('train')
    val_df = process_dataset('valid')
    test_df = process_dataset('test')
    
    # Print summary
    print("\n" + "=" * 60)
    print("Processing Summary")
    print("=" * 60)
    print(f"Train samples: {len(train_df)}")
    print(f"Validation samples: {len(val_df)}")
    print(f"Test samples: {len(test_df)}")
    print(f"Total samples: {len(train_df) + len(val_df) + len(test_df)}")
    
    # Show emotion distribution
    all_emotions = pd.concat([train_df, val_df, test_df])['emotion'].value_counts()
    print(f"\nTop 10 emotions:")
    for emotion, count in all_emotions.head(10).items():
        print(f"   {emotion}: {count}")
    
    # Save processed data
    if len(train_df) > 0:
        save_processed_data(train_df, val_df, test_df)
        
        # Show sample
        print("\n" + "=" * 60)
        print("Sample Processed Data")
        print("=" * 60)
        sample = train_df.iloc[0]
        print(f"Journal Entry: {sample['journal_entry'][:100]}...")
        print(f"Emotion: {sample['emotion']}")
        print(f"Empathetic Response: {sample['empathetic_response'][:100]}...")
    else:
        print("\nERROR: No data processed. Please check the dataset files.")

if __name__ == "__main__":
    main()

