"""
Data Loading Scripts for DepressionEmo and EmpatheticDialogues Datasets
"""
import os
import pandas as pd
import numpy as np
from pathlib import Path
import json
import requests
import tarfile
import zipfile
from tqdm import tqdm
import warnings
warnings.filterwarnings('ignore')

# Hugging Face datasets
try:
    from datasets import load_dataset
    HF_AVAILABLE = True
except ImportError:
    HF_AVAILABLE = False
    print("Warning: datasets library not available. Install with: pip install datasets")

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

# DepressionEmo emotion labels
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


def download_file(url, destination, chunk_size=8192):
    """Download a file with progress bar"""
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    
    with open(destination, 'wb') as f, tqdm(
        desc=destination.name,
        total=total_size,
        unit='B',
        unit_scale=True,
        unit_divisor=1024,
    ) as bar:
        for chunk in response.iter_content(chunk_size=chunk_size):
            if chunk:
                f.write(chunk)
                bar.update(len(chunk))


def load_depression_emo_from_github():
    """
    Load DepressionEmo dataset from GitHub
    GitHub: https://github.com/abuBakarSiddiqurRahman/DepressionEmo
    """
    print("\n" + "="*60)
    print("Loading DepressionEmo Dataset")
    print("="*60)
    
    depression_emo_dir = DATA_DIR / "DepressionEmo"
    depression_emo_dir.mkdir(exist_ok=True)
    
    # Check if data already exists
    csv_files = list(depression_emo_dir.glob("*.csv"))
    if csv_files:
        print(f"\nFound existing DepressionEmo files in {depression_emo_dir}")
        print("Files found:", [f.name for f in csv_files])
        
        # Try to load the CSV files
        for csv_file in csv_files:
            try:
                df = pd.read_csv(csv_file)
                print(f"\nLoaded {csv_file.name}:")
                print(f"  Shape: {df.shape}")
                print(f"  Columns: {df.columns.tolist()}")
                return df
            except Exception as e:
                print(f"Error loading {csv_file.name}: {e}")
                continue
    
    print("\nDepressionEmo dataset not found locally.")
    print("Please download it manually from:")
    print("  GitHub: https://github.com/abuBakarSiddiqurRahman/DepressionEmo")
    print(f"\nOr place CSV files in: {depression_emo_dir}")
    print("\nExpected format:")
    print("  - Text column with Reddit posts")
    print("  - Emotion label columns (sadness, emptiness, hopelessness, etc.)")
    
    return None


def load_empathetic_dialogues_from_hf():
    """
    Load EmpatheticDialogues from Hugging Face
    Uses the reformatted version: Estwld/empathetic_dialogues_llm
    """
    print("\n" + "="*60)
    print("Loading EmpatheticDialogues Dataset from Hugging Face")
    print("="*60)
    
    if not HF_AVAILABLE:
        print("\nError: datasets library not installed.")
        print("Install with: pip install datasets")
        return None
    
    try:
        print("\nLoading from Hugging Face: Estwld/empathetic_dialogues_llm")
        dataset = load_dataset("Estwld/empathetic_dialogues_llm", split="train")
        
        print(f"\nDataset loaded successfully!")
        print(f"  Number of examples: {len(dataset)}")
        print(f"  Features: {dataset.features}")
        
        # Convert to pandas for easier manipulation
        df = dataset.to_pandas()
        
        # Save locally for future use
        save_path = DATA_DIR / "empathetic_dialogues.csv"
        df.to_csv(save_path, index=False)
        print(f"\nSaved to: {save_path}")
        
        return df
        
    except Exception as e:
        print(f"\nError loading from Hugging Face: {e}")
        print("\nTrying alternative: facebook/empathetic_dialogues")
        try:
            dataset = load_dataset("facebook/empathetic_dialogues", split="train")
            df = dataset.to_pandas()
            save_path = DATA_DIR / "empathetic_dialogues.csv"
            df.to_csv(save_path, index=False)
            print(f"Saved to: {save_path}")
            return df
        except Exception as e2:
            print(f"Error with alternative source: {e2}")
            return None


def load_empathetic_dialogues_from_url():
    """
    Download EmpatheticDialogues from original source
    URL: https://dl.fbaipublicfiles.com/parlai/empatheticdialogues/empatheticdialogues.tar.gz
    """
    print("\n" + "="*60)
    print("Downloading EmpatheticDialogues from Original Source")
    print("="*60)
    
    url = "https://dl.fbaipublicfiles.com/parlai/empatheticdialogues/empatheticdialogues.tar.gz"
    tar_path = DATA_DIR / "empatheticdialogues.tar.gz"
    extract_dir = DATA_DIR / "empatheticdialogues"
    
    # Check if already extracted
    if extract_dir.exists() and any(extract_dir.iterdir()):
        print(f"\nFound existing extracted data in {extract_dir}")
        # Try to find and load the data files
        csv_files = list(extract_dir.rglob("*.csv"))
        if csv_files:
            print(f"Found CSV files: {[f.name for f in csv_files]}")
            # Load the train.csv if available
            train_csv = extract_dir / "train.csv"
            if train_csv.exists():
                df = pd.read_csv(train_csv)
                print(f"Loaded train.csv: {df.shape}")
                return df
    
    # Download if needed
    if not tar_path.exists():
        print(f"\nDownloading from {url}...")
        print("This may take a while...")
        try:
            download_file(url, tar_path)
        except Exception as e:
            print(f"Error downloading: {e}")
            return None
    
    # Extract if needed
    if not extract_dir.exists() or not any(extract_dir.iterdir()):
        print(f"\nExtracting {tar_path.name}...")
        extract_dir.mkdir(exist_ok=True)
        try:
            with tarfile.open(tar_path, 'r:gz') as tar:
                tar.extractall(extract_dir)
            print("Extraction complete!")
        except Exception as e:
            print(f"Error extracting: {e}")
            return None
    
    # Load the data
    train_csv = extract_dir / "train.csv"
    if train_csv.exists():
        df = pd.read_csv(train_csv)
        print(f"\nLoaded train.csv: {df.shape}")
        return df
    else:
        print(f"\nCould not find train.csv in {extract_dir}")
        return None


def prepare_depression_emo_data(df):
    """
    Prepare DepressionEmo data for emotion classification
    Returns DataFrame with text and emotion labels
    """
    if df is None:
        return None
    
    print("\n" + "="*60)
    print("Preparing DepressionEmo Data")
    print("="*60)
    
    # Identify text column
    text_col = None
    for col in df.columns:
        if col.lower() in ['text', 'post', 'content', 'sentence', 'utterance']:
            text_col = col
            break
    
    if text_col is None:
        # Try first column
        text_col = df.columns[0]
        print(f"Using first column as text: {text_col}")
    
    # Identify emotion columns
    emotion_cols = []
    for emotion in DEPRESSION_EMOTIONS:
        for col in df.columns:
            if emotion.lower() in col.lower():
                emotion_cols.append((emotion, col))
                break
    
    print(f"\nText column: {text_col}")
    print(f"Emotion columns found: {len(emotion_cols)}")
    for emotion, col in emotion_cols:
        print(f"  {emotion}: {col}")
    
    # Create prepared dataframe
    prepared_data = {'text': df[text_col].astype(str)}
    
    for emotion, col in emotion_cols:
        if col in df.columns:
            # Convert to binary or keep as is
            if df[col].dtype in ['int64', 'float64']:
                prepared_data[emotion] = df[col].values
            else:
                # Try to convert binary labels
                prepared_data[emotion] = (df[col].astype(str).str.lower() == 'true').astype(int)
    
    prepared_df = pd.DataFrame(prepared_data)
    
    # Remove rows with empty text
    prepared_df = prepared_df[prepared_df['text'].str.strip() != '']
    
    print(f"\nPrepared data shape: {prepared_df.shape}")
    print(f"Emotion label distribution:")
    for emotion in DEPRESSION_EMOTIONS:
        if emotion in prepared_df.columns:
            print(f"  {emotion}: {prepared_df[emotion].sum()} positive samples")
    
    return prepared_df


def prepare_empathetic_dialogues_data(df):
    """
    Prepare EmpatheticDialogues data for style learning
    Returns DataFrame with dialogues and emotional context
    """
    if df is None:
        return None
    
    print("\n" + "="*60)
    print("Preparing EmpatheticDialogues Data")
    print("="*60)
    
    print(f"\nOriginal shape: {df.shape}")
    print(f"Columns: {df.columns.tolist()}")
    
    # The reformatted version should have columns like 'context', 'response', etc.
    # Original version has 'utterance', 'context', 'context_emotion', etc.
    
    # Try to identify key columns
    context_col = None
    response_col = None
    emotion_col = None
    
    for col in df.columns:
        col_lower = col.lower()
        if 'context' in col_lower and context_col is None:
            context_col = col
        if 'response' in col_lower or 'utterance' in col_lower:
            response_col = col
        if 'emotion' in col_lower:
            emotion_col = col
    
    print(f"\nIdentified columns:")
    print(f"  Context: {context_col}")
    print(f"  Response: {response_col}")
    print(f"  Emotion: {emotion_col}")
    
    # Create prepared dataframe
    prepared_data = {}
    if context_col:
        prepared_data['context'] = df[context_col].astype(str)
    if response_col:
        prepared_data['response'] = df[response_col].astype(str)
    if emotion_col:
        prepared_data['emotion'] = df[emotion_col].astype(str)
    
    if not prepared_data:
        # Fallback: use first few columns
        print("\nUsing first columns as fallback")
        for i, col in enumerate(df.columns[:3]):
            prepared_data[f'col_{i}'] = df[col].astype(str)
    
    prepared_df = pd.DataFrame(prepared_data)
    prepared_df = prepared_df[prepared_df.iloc[:, 0].str.strip() != '']
    
    print(f"\nPrepared data shape: {prepared_df.shape}")
    
    return prepared_df


def main():
    """Main function to load both datasets"""
    print("\n" + "="*60)
    print("Data Loading Pipeline")
    print("="*60)
    
    # Load DepressionEmo
    depression_emo_df = load_depression_emo_from_github()
    if depression_emo_df is not None:
        depression_emo_prepared = prepare_depression_emo_data(depression_emo_df)
        if depression_emo_prepared is not None:
            save_path = DATA_DIR / "depression_emo_prepared.csv"
            depression_emo_prepared.to_csv(save_path, index=False)
            print(f"\nSaved prepared DepressionEmo data to: {save_path}")
    
    # Load EmpatheticDialogues
    empathetic_df = load_empathetic_dialogues_from_hf()
    if empathetic_df is None:
        empathetic_df = load_empathetic_dialogues_from_url()
    
    if empathetic_df is not None:
        empathetic_prepared = prepare_empathetic_dialogues_data(empathetic_df)
        if empathetic_prepared is not None:
            save_path = DATA_DIR / "empathetic_dialogues_prepared.csv"
            empathetic_prepared.to_csv(save_path, index=False)
            print(f"\nSaved prepared EmpatheticDialogues data to: {save_path}")
    
    print("\n" + "="*60)
    print("Data Loading Complete!")
    print("="*60)


if __name__ == "__main__":
    main()

