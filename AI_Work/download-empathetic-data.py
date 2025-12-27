"""
Download Empathetic Dialogues dataset (Meta AI - raw)

This script ONLY downloads and extracts the dataset.
No preprocessing, no conversion.

Source:
https://dl.fbaipublicfiles.com/parlai/empatheticdialogues/empatheticdialogues.tar.gz
"""

import tarfile
import urllib.request
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
TARGET_DIR = DATA_DIR / "empatheticdialogues"
ARCHIVE_PATH = DATA_DIR / "empatheticdialogues.tar.gz"

DATASET_URL = "https://dl.fbaipublicfiles.com/parlai/empatheticdialogues/empatheticdialogues.tar.gz"


def download_dataset():
    print("=" * 60)
    print("📥 Downloading Empathetic Dialogues (Meta AI)")
    print("=" * 60)

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if not ARCHIVE_PATH.exists():
        print("⬇️  Downloading archive...")
        urllib.request.urlretrieve(DATASET_URL, ARCHIVE_PATH)
    else:
        print("✔ Archive already downloaded")

    print("📦 Extracting archive...")
    with tarfile.open(ARCHIVE_PATH, "r:gz") as tar:
        tar.extractall(DATA_DIR)

    print("\n✅ Dataset downloaded and extracted!")
    print(f"📁 Location: {TARGET_DIR.resolve()}")
    print("\nContents:")
    for p in TARGET_DIR.iterdir():
        print(" -", p.name)


if __name__ == "__main__":
    download_dataset()
