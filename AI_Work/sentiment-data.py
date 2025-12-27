"""
Dataset Download Script
Downloads the sentiment analysis dataset from Kaggle and saves it locally.
"""
import kagglehub
import os
import shutil
from pathlib import Path

# Create data directory if it doesn't exist
DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)

print("Downloading dataset from Kaggle...")
# Download latest version
path = kagglehub.dataset_download("abhi8923shriv/sentiment-analysis-dataset")

print(f"Dataset downloaded to: {path}")

# Copy files to our data directory
if os.path.exists(path):
    for item in os.listdir(path):
        src = os.path.join(path, item)
        dst = os.path.join(DATA_DIR, item)
        if os.path.isfile(src):
            shutil.copy2(src, dst)
            print(f"Copied {item} to {DATA_DIR}")
        elif os.path.isdir(src):
            dst_dir = os.path.join(DATA_DIR, item)
            if os.path.exists(dst_dir):
                shutil.rmtree(dst_dir)
            shutil.copytree(src, dst_dir)
            print(f"Copied directory {item} to {DATA_DIR}")

print(f"\nDataset saved to: {DATA_DIR}")
print("Download complete!")