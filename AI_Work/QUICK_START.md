# Quick Start Guide - Psychological Summary Generation

## Prerequisites

1. Python 3.8+
2. GPU recommended (for training), CPU works for inference
3. Hugging Face account (for LLaMA access)

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Authenticate with Hugging Face
huggingface-cli login
```

## 5-Step Pipeline

### 1. Load Datasets (5-10 minutes)
```bash
python data_loaders.py
```
**What it does**: Downloads/loads DepressionEmo and EmpatheticDialogues datasets

**Note**: If DepressionEmo download fails, manually download from:
- https://github.com/abuBakarSiddiqurRahman/DepressionEmo
- Place CSV files in `data/DepressionEmo/`

### 2. Train Emotion Classifier (30-60 minutes)
```bash
python train_emotion_classifier.py
```
**What it does**: Trains DistilBERT to detect 8 depression emotions

**Output**: `models/emotion_classifier/`

### 3. Synthesize Training Data (10-20 minutes)
```bash
python synthesize_training_data.py
```
**What it does**: Creates training examples combining emotion scores with empathetic summaries

**Output**: `training_data/llama_training_data.json`

### 4. Fine-tune LLaMA (2-4 hours on GPU)
```bash
python fine_tune_llama.py
```
**What it does**: Fine-tunes LLaMA-2-7B with LoRA for summary generation

**Output**: `models/llama_psychological_summary/`

**Note**: If you don't have LLaMA access, edit the script to use `microsoft/phi-2` or `gpt2`

### 5. Generate Summaries
```bash
python inference_pipeline.py
```
**What it does**: 
- Processes example journal entries
- Enters interactive mode for custom entries

**Example**:
```
Journal Entry: I've been feeling numb and drained, nothing excites me like it used to.

Detected Emotions:
  sadness: 0.83
  emptiness: 0.79
  hopelessness: 0.52

Psychological Summary:
The entry reflects deep sadness and a pronounced sense of emptiness,
suggesting reduced interest and diminished pleasure in daily activities,
shaping a narrative of emotional withdrawal and low energy.
```

## Quick Test (Without Full Training)

If you want to test the pipeline without full training:

1. **Use pre-trained emotion classifier** (if available) or skip emotion detection
2. **Use base LLaMA** without fine-tuning (lower quality but works)
3. **Test with GPT-2** (no special access needed)

Edit `fine_tune_llama.py`:
```python
model_name = 'gpt2'  # No access required
```

## Common Issues

### "Model not found"
- Run all training steps in order
- Check that files exist in `models/` directory

### "Out of memory"
- Reduce batch size in training scripts
- Use 4-bit quantization (already enabled)
- Use smaller model (phi-2 instead of LLaMA-2)

### "Hugging Face authentication failed"
- Run `huggingface-cli login`
- Or set `HF_TOKEN` environment variable
- Or use alternative model that doesn't require auth

### "Dataset not found"
- Run `data_loaders.py` first
- Check `data/` directory for required files
- Download DepressionEmo manually if needed

## Expected File Structure After Setup

```
AI_Work/
├── models/
│   ├── emotion_classifier/          # Step 2 output
│   └── llama_psychological_summary/ # Step 4 output
├── training_data/
│   └── llama_training_data.json     # Step 3 output
└── data/
    ├── depression_emo_prepared.csv   # Step 1 output
    └── empathetic_dialogues_prepared.csv  # Step 1 output
```

## Next Steps

- Adjust training parameters for better performance
- Add evaluation metrics (ROUGE, BERTScore)
- Fine-tune generation parameters (temperature, top_p)
- Collect human feedback for improvement

## Need Help?

See `README_PSYCHOLOGICAL_SUMMARY.md` for detailed documentation.

