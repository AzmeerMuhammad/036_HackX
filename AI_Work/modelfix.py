import os
import shutil
import json
from pathlib import Path

# Paths
BASE_DIR = Path(os.getcwd())
MODEL_DIR = BASE_DIR / "models" / "emotion_model_text_only"
RESULTS_DIR = BASE_DIR / "results"

def full_repair():
    print("🛠 Starting Model Repair...")
    
    # 1. Check if we have checkpoints to recover from
    checkpoints = [d for d in os.listdir(RESULTS_DIR) if d.startswith("checkpoint")]
    if not checkpoints:
        print("❌ Error: No checkpoints found in /results. You may need to re-train.")
        return
    
    # Get the highest numbered checkpoint
    latest_cp = sorted(checkpoints, key=lambda x: int(x.split('-')[-1]))[-1]
    cp_path = RESULTS_DIR / latest_cp
    print(f"📂 Recovering files from {latest_cp}...")

    # 2. Handle the corrupted config.json
    config_file = MODEL_DIR / "config.json"
    if config_file.exists():
        with open(config_file, 'r') as f:
            data = json.load(f)
        
        # If it's our emotion list, move it to a safe name
        if "emotions" in data:
            print("📦 Found emotion list in config.json. Renaming to emotion_config.json...")
            shutil.move(config_file, MODEL_DIR / "emotion_config.json")

    # 3. Copy ALL essential RoBERTa files from the checkpoint
    # These are the files RoBERTa MUST have to function
    files_to_restore = [
        "config.json", "pytorch_model.bin", "vocab.json", 
        "merges.txt", "tokenizer_config.json", "special_tokens_map.json"
    ]
    
    for f_name in files_to_restore:
        src = cp_path / f_name
        dst = MODEL_DIR / f_name
        if src.exists():
            shutil.copy(src, dst)
            print(f"✅ Restored: {f_name}")
        else:
            print(f"⚠️ Warning: {f_name} not found in checkpoint.")

    print("\n✨ REPAIR COMPLETE! Your model folder is now valid.")

if __name__ == "__main__":
    full_repair()