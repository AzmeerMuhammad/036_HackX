"""
Prepare DepressionEmo Dataset for Training
Loads JSON files and converts to format suitable for emotion classification training
"""
import json
import pandas as pd
import numpy as np
from pathlib import Path
from collections import Counter
import warnings
warnings.filterwarnings('ignore')

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DEPRESSION_EMO_DIR = DATA_DIR / "DepressionEmo" / "Dataset"
OUTPUT_DIR = DATA_DIR
OUTPUT_DIR.mkdir(exist_ok=True)

# Standard 8 depression emotions (from original specification)
STANDARD_EMOTIONS = [
    'sadness',
    'emptiness',
    'hopelessness',
    'loneliness',
    'anger',
    'guilt',
    'shame',
    'fear'
]

# Additional emotions found in the dataset
ADDITIONAL_EMOTIONS = [
    'worthlessness',
    'suicide intent',
    'brain dysfunction (forget)',
    'cognitive_dysfunction'  # Alternative name
]

# All emotions (standard + additional)
ALL_EMOTIONS = STANDARD_EMOTIONS + ADDITIONAL_EMOTIONS

# Emotion name mapping (normalize variations)
EMOTION_MAPPING = {
    'suicide intent': 'suicide_intent',
    'brain dysfunction (forget)': 'brain_dysfunction',
    'cognitive_dysfunction': 'brain_dysfunction',
    'cognitive dysfunction': 'brain_dysfunction'
}


def normalize_emotion_name(emotion):
    """Normalize emotion names to handle variations"""
    emotion = emotion.lower().strip()
    if emotion in EMOTION_MAPPING:
        return EMOTION_MAPPING[emotion]
    return emotion


def load_json_file(file_path):
    """Load JSON file (handles both single objects and arrays)"""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # If it's a single object, convert to list
    if isinstance(data, dict):
        return [data]
    return data


def extract_emotions_from_entry(entry):
    """Extract and normalize emotions from an entry"""
    emotions = entry.get('emotions', [])
    
    # Normalize emotion names
    normalized_emotions = [normalize_emotion_name(e) for e in emotions]
    
    return normalized_emotions


def create_emotion_labels(emotions_list, emotion_set):
    """Create binary labels for each emotion"""
    labels = {}
    for emotion in emotion_set:
        labels[emotion] = 1 if emotion in emotions_list else 0
    return labels


def prepare_depression_emo_dataset(
    use_standard_emotions_only=True,
    include_additional=True,
    min_text_length=10
):
    """
    Prepare DepressionEmo dataset for training
    
    Args:
        use_standard_emotions_only: If True, only use the 8 standard emotions
        include_additional: If True, include additional emotions (worthlessness, suicide_intent, etc.)
        min_text_length: Minimum text length to include
    """
    print("\n" + "="*60)
    print("Preparing DepressionEmo Dataset")
    print("="*60)
    
    # Determine which emotions to use
    if use_standard_emotions_only:
        target_emotions = STANDARD_EMOTIONS
        print(f"\nUsing standard emotions only: {target_emotions}")
    else:
        if include_additional:
            target_emotions = ALL_EMOTIONS
            print(f"\nUsing all emotions: {len(target_emotions)} emotions")
        else:
            target_emotions = STANDARD_EMOTIONS
            print(f"\nUsing standard emotions: {target_emotions}")
    
    # Load train, val, and test files
    train_path = DEPRESSION_EMO_DIR / "train.json"
    val_path = DEPRESSION_EMO_DIR / "val.json"
    test_path = DEPRESSION_EMO_DIR / "test.json"
    
    datasets = {}
    
    for split_name, file_path in [("train", train_path), ("val", val_path), ("test", test_path)]:
        if not file_path.exists():
            print(f"\nWarning: {file_path} not found, skipping {split_name} split")
            continue
        
        print(f"\nLoading {split_name} split from {file_path.name}...")
        entries = load_json_file(file_path)
        print(f"  Loaded {len(entries)} entries")
        
        # Process entries
        processed_data = []
        emotion_counter = Counter()
        
        for entry in entries:
            # Get text (prefer 'text' field, fallback to 'post')
            text = entry.get('text', entry.get('post', ''))
            
            if not text or len(text.strip()) < min_text_length:
                continue
            
            # Extract emotions
            emotions = extract_emotions_from_entry(entry)
            
            # Count all emotions found
            for emotion in emotions:
                emotion_counter[emotion] += 1
            
            # Create binary labels for target emotions
            emotion_labels = create_emotion_labels(emotions, target_emotions)
            
            # Create data entry
            data_entry = {
                'id': entry.get('id', ''),
                'text': text.strip(),
                'title': entry.get('title', ''),
                'emotions_list': emotions,  # Keep original list for reference
                **emotion_labels  # Add binary labels
            }
            
            processed_data.append(data_entry)
        
        datasets[split_name] = processed_data
        print(f"  Processed {len(processed_data)} valid entries")
        print(f"  Emotion distribution:")
        for emotion in sorted(emotion_counter.keys()):
            print(f"    {emotion}: {emotion_counter[emotion]}")
    
    # Create DataFrames
    dfs = {}
    for split_name, data in datasets.items():
        if data:
            df = pd.DataFrame(data)
            dfs[split_name] = df
            print(f"\n{split_name.upper()} DataFrame:")
            print(f"  Shape: {df.shape}")
            print(f"  Columns: {df.columns.tolist()}")
            
            # Show emotion label distribution
            print(f"  Emotion label distribution:")
            for emotion in target_emotions:
                if emotion in df.columns:
                    count = df[emotion].sum()
                    pct = (count / len(df)) * 100
                    print(f"    {emotion}: {count} ({pct:.1f}%)")
    
    # Save prepared data
    print("\n" + "="*60)
    print("Saving Prepared Data")
    print("="*60)
    
    # Save as CSV (combined and separate)
    if 'train' in dfs:
        train_df = dfs['train']
        output_path = OUTPUT_DIR / "depression_emo_prepared.csv"
        train_df.to_csv(output_path, index=False, encoding='utf-8')
        print(f"\nSaved training data to: {output_path}")
        print(f"  Shape: {train_df.shape}")
    
    # Save separate splits
    for split_name, df in dfs.items():
        output_path = OUTPUT_DIR / f"depression_emo_{split_name}.csv"
        df.to_csv(output_path, index=False, encoding='utf-8')
        print(f"Saved {split_name} split to: {output_path}")
    
    # Save as JSON for easy loading
    if 'train' in dfs:
        json_output = OUTPUT_DIR / "depression_emo_prepared.json"
        with open(json_output, 'w', encoding='utf-8') as f:
            json.dump({
                'train': dfs['train'].to_dict('records') if 'train' in dfs else [],
                'val': dfs['val'].to_dict('records') if 'val' in dfs else [],
                'test': dfs['test'].to_dict('records') if 'test' in dfs else [],
                'emotions': target_emotions,
                'num_emotions': len(target_emotions)
            }, f, indent=2, ensure_ascii=False)
        print(f"Saved JSON format to: {json_output}")
    
    # Print summary statistics
    print("\n" + "="*60)
    print("Dataset Summary")
    print("="*60)
    
    total_samples = sum(len(df) for df in dfs.values())
    print(f"\nTotal samples: {total_samples}")
    for split_name, df in dfs.items():
        print(f"  {split_name}: {len(df)} samples")
    
    print(f"\nEmotions used: {len(target_emotions)}")
    print(f"  {target_emotions}")
    
    # Show sample entry
    if 'train' in dfs and len(dfs['train']) > 0:
        print("\n" + "="*60)
        print("Sample Entry")
        print("="*60)
        sample = dfs['train'].iloc[0]
        print(f"\nID: {sample.get('id', 'N/A')}")
        print(f"Text (first 200 chars): {sample['text'][:200]}...")
        print(f"\nEmotions detected: {sample.get('emotions_list', [])}")
        print(f"\nBinary labels:")
        for emotion in target_emotions:
            if emotion in sample:
                print(f"  {emotion}: {sample[emotion]}")
    
    return dfs


def main():
    """Main function"""
    print("\n" + "="*60)
    print("DepressionEmo Dataset Preparation")
    print("="*60)
    
    try:
        # Check if dataset exists
        if not DEPRESSION_EMO_DIR.exists():
            print(f"\nError: DepressionEmo dataset not found at {DEPRESSION_EMO_DIR}")
            print("Please ensure the dataset is downloaded and placed in the correct location.")
            return
        
        # Prepare dataset with standard emotions only (for compatibility with original design)
        dfs = prepare_depression_emo_dataset(
            use_standard_emotions_only=False,  # Use all emotions found in dataset
            include_additional=True,
            min_text_length=10
        )
        
        print("\n" + "="*60)
        print("Preparation Complete!")
        print("="*60)
        print(f"\nPrepared files saved to: {OUTPUT_DIR}")
        print("\nNext steps:")
        print("1. Review the prepared data in data/depression_emo_prepared.csv")
        print("2. Run train_emotion_classifier.py to train the emotion classifier")
        
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    main()

