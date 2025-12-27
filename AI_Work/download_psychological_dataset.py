"""
Dataset Download Script for Psychological Summary Fine-tuning

This script downloads and prepares datasets for fine-tuning Llama to generate
mental health notes summaries from journal entries.

Available datasets:
1. MentSum - Requires DUA approval from Georgetown University
2. Mental Health Reddit Posts (if available on HuggingFace)
3. Custom dataset preparation

Before running, please review and approve the dataset choice.
"""

import os
import json
import pandas as pd
from pathlib import Path
import requests
from typing import Optional

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
PSYCHOLOGICAL_DATA_DIR = DATA_DIR / "psychological_summary"

def create_directories():
    """Create necessary directories"""
    PSYCHOLOGICAL_DATA_DIR.mkdir(parents=True, exist_ok=True)
    print(f"✓ Created directory: {PSYCHOLOGICAL_DATA_DIR}")

def download_mentsum_dataset(download_url: Optional[str] = None):
    """
    Download MentSum dataset (requires DUA approval)
    
    Args:
        download_url: URL provided after DUA approval from Georgetown University
                     https://ir.cs.georgetown.edu/resources/mentsum.html
    """
    if download_url is None:
        print("\n⚠️  MentSum Dataset requires Data Usage Agreement (DUA) approval.")
        print("📋 Please visit: https://ir.cs.georgetown.edu/resources/mentsum.html")
        print("📝 Fill out the request form and obtain the download URL.")
        print("\nOnce you have the URL, update the download_url parameter.")
        return False
    
    print(f"\n📥 Downloading MentSum dataset from: {download_url}")
    
    try:
        response = requests.get(download_url, stream=True)
        response.raise_for_status()
        
        zip_path = PSYCHOLOGICAL_DATA_DIR / "mentsum.zip"
        with open(zip_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"✓ Downloaded to: {zip_path}")
        
        # Extract if it's a zip file
        import zipfile
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(PSYCHOLOGICAL_DATA_DIR)
        
        print(f"✓ Extracted to: {PSYCHOLOGICAL_DATA_DIR}")
        return True
        
    except Exception as e:
        print(f"❌ Error downloading MentSum: {e}")
        return False

def prepare_huggingface_dataset(dataset_name: str = "mental-health-reddit"):
    """
    Download dataset from HuggingFace Hub
    
    Args:
        dataset_name: Name of the dataset on HuggingFace
    """
    try:
        from datasets import load_dataset
        
        print(f"\n📥 Loading dataset from HuggingFace: {dataset_name}")
        dataset = load_dataset(dataset_name)
        
        # Save to local directory
        save_path = PSYCHOLOGICAL_DATA_DIR / dataset_name
        save_path.mkdir(parents=True, exist_ok=True)
        
        # Convert to JSON format for easy loading
        for split in dataset.keys():
            df = dataset[split].to_pandas()
            output_file = save_path / f"{split}.json"
            df.to_json(output_file, orient='records', indent=2)
            print(f"✓ Saved {split} split: {len(df)} samples to {output_file}")
        
        return True
        
    except ImportError:
        print("❌ Please install datasets: pip install datasets")
        return False
    except Exception as e:
        print(f"❌ Error loading HuggingFace dataset: {e}")
        print(f"💡 Try searching for available datasets at: https://huggingface.co/datasets")
        return False

def prepare_custom_dataset_format():
    """
    Create a template for custom dataset format.
    Expected format: JSON with 'journal_entry' and 'summary' fields
    """
    template = {
        "journal_entry": "Example journal entry text here...",
        "summary": "Psychological summary/breakdown here..."
    }
    
    template_path = PSYCHOLOGICAL_DATA_DIR / "dataset_template.json"
    with open(template_path, 'w') as f:
        json.dump([template], f, indent=2)
    
    print(f"\n📝 Created dataset template at: {template_path}")
    print("💡 Format your custom dataset as a JSON array with 'journal_entry' and 'summary' fields")

def main():
    """Main function to download and prepare dataset"""
    print("=" * 60)
    print("🧠 Psychological Summary Dataset Download Script")
    print("=" * 60)
    
    create_directories()
    
    print("\n📋 Available Dataset Options:")
    print("1. MentSum (requires DUA approval)")
    print("2. HuggingFace Dataset")
    print("3. Create custom dataset template")
    print("4. Skip (use existing empathetic dialogues only)")
    
    choice = input("\nSelect option (1-4): ").strip()
    
    if choice == "1":
        url = input("Enter MentSum download URL (or press Enter to skip): ").strip()
        if url:
            download_mentsum_dataset(url)
        else:
            print("⏭️  Skipping MentSum download")
    
    elif choice == "2":
        dataset_name = input("Enter HuggingFace dataset name (or press Enter for default): ").strip()
        if not dataset_name:
            dataset_name = "mental-health-reddit"
        prepare_huggingface_dataset(dataset_name)
    
    elif choice == "3":
        prepare_custom_dataset_format()
    
    elif choice == "4":
        print("⏭️  Skipping dataset download. Using empathetic dialogues only.")
    
    else:
        print("❌ Invalid choice")
    
    print("\n✅ Dataset preparation complete!")
    print(f"📁 Data directory: {PSYCHOLOGICAL_DATA_DIR}")

if __name__ == "__main__":
    main()

