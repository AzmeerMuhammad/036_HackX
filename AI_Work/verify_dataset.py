"""
Dataset Verification Script

This script verifies that the empathetic dialogues dataset is available.
The dataset should already be in: data/empatheticdialogues/empatheticdialogues/
"""

from pathlib import Path

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
EMPATHETIC_DIALOGUES_DIR = DATA_DIR / "empatheticdialogues" / "empatheticdialogues"

def verify_dataset():
    """Verify empathetic dialogues dataset exists"""
    print("=" * 60)
    print("📋 Empathetic Dialogues Dataset Verification")
    print("=" * 60)
    
    required_files = ["train.csv", "valid.csv", "test.csv"]
    missing_files = []
    
    for file in required_files:
        file_path = EMPATHETIC_DIALOGUES_DIR / file
        if file_path.exists():
            # Count lines
            with open(file_path, 'r', encoding='utf-8') as f:
                line_count = sum(1 for _ in f) - 1  # Subtract header
            print(f"✓ {file}: {line_count:,} samples")
        else:
            print(f"❌ {file}: NOT FOUND")
            missing_files.append(file)
    
    if missing_files:
        print(f"\n⚠️  Missing files: {', '.join(missing_files)}")
        print(f"📁 Expected location: {EMPATHETIC_DIALOGUES_DIR}")
        print("\n💡 The empathetic dialogues dataset should be extracted in the above directory.")
        return False
    else:
        print("\n✅ All required dataset files are present!")
        return True

if __name__ == "__main__":
    verify_dataset()

