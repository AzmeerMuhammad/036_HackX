# Psychological Summary Generation System

A complete pipeline for generating humanized psychological summaries from journal entries using emotion detection and fine-tuned language models.

## Overview

This system combines:
1. **Emotion Classifier**: Trained on DepressionEmo dataset to detect 8 depression-relevant emotions
2. **LLaMA Fine-tuning**: Fine-tuned with LoRA on synthesized training data for empathetic summary generation
3. **End-to-End Pipeline**: Journal entry → Emotion scores → Psychological summary

## Architecture

```
Journal Entry
    ↓
Emotion Classifier (DistilBERT)
    ↓
Emotion Scores (sadness, emptiness, hopelessness, etc.)
    ↓
Fine-tuned LLaMA (with LoRA)
    ↓
Humanized Psychological Summary
```

## Key Datasets

### DepressionEmo
- **Purpose**: Emotion classification training
- **Source**: [GitHub](https://github.com/abuBakarSiddiqurRahman/DepressionEmo)
- **Content**: Reddit posts labeled with 8 depression-relevant emotions
- **Emotions**: sadness, emptiness, hopelessness, loneliness, anger, guilt, shame, fear

### EmpatheticDialogues
- **Purpose**: Style learning for empathetic, humanized language
- **Source**: 
  - Original: [Facebook Research](https://github.com/facebookresearch/EmpatheticDialogues)
  - Hugging Face (reformatted): [Estwld/empathetic_dialogues_llm](https://huggingface.co/datasets/Estwld/empathetic_dialogues_llm)
- **Content**: ~25,000 dialogues grounded in emotional situations

## Installation

1. **Clone or navigate to the project directory**

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Authenticate with Hugging Face** (required for LLaMA models):
```bash
huggingface-cli login
```
Or set environment variable:
```bash
export HF_TOKEN=your_token_here
```

## Usage

### Step 1: Load Datasets

Download and prepare the datasets:

```bash
python data_loaders.py
```

This will:
- Download/load DepressionEmo dataset
- Download/load EmpatheticDialogues from Hugging Face
- Prepare and save processed data to `data/`

**Note**: If you need to download DepressionEmo manually:
1. Visit: https://github.com/abuBakarSiddiqurRahman/DepressionEmo
2. Download the dataset
3. Place CSV files in `data/DepressionEmo/`

### Step 2: Train Emotion Classifier

Train a multi-label emotion classifier on DepressionEmo:

```bash
python train_emotion_classifier.py
```

This will:
- Load DepressionEmo data
- Train DistilBERT for multi-label emotion classification
- Save model to `models/emotion_classifier/`
- Save results to `results/emotion_classifier_results.json`

**Model Options**:
- `distilbert-base-uncased` (default, faster)
- `google/mobilebert-uncased` (smaller, mobile-friendly)

### Step 3: Synthesize Training Data

Create training examples for LLaMA fine-tuning:

```bash
python synthesize_training_data.py
```

This will:
- Use trained emotion classifier to get emotion scores
- Combine with empathetic summaries from EmpatheticDialogues
- Generate training examples in the prompt format
- Save to `training_data/llama_training_data.json` and `.txt`

**Parameters** (edit in script):
- `num_samples`: Number of training examples (default: 1000)
- `use_empathetic_dialogues`: Whether to use EmpatheticDialogues for style (default: True)

### Step 4: Fine-tune LLaMA with LoRA

Fine-tune LLaMA for psychological summary generation:

```bash
python fine_tune_llama.py
```

This will:
- Load training data
- Fine-tune LLaMA-2-7B (or specified model) with LoRA adapters
- Use 4-bit quantization for memory efficiency
- Save model to `models/llama_psychological_summary/`

**Model Options**:
- `meta-llama/Llama-2-7b-hf` (default, requires Hugging Face access)
- `meta-llama/Llama-2-7b-chat-hf` (chat version)
- `microsoft/phi-2` (smaller alternative)
- `gpt2` (for testing without LLaMA access)

**Training Parameters** (edit in script):
- `num_epochs`: Training epochs (default: 3)
- `batch_size`: Batch size (default: 2, adjust for GPU memory)
- `learning_rate`: Learning rate (default: 2e-4)
- `use_4bit`: Use 4-bit quantization (default: True)

### Step 5: Generate Summaries

Run the inference pipeline:

```bash
python inference_pipeline.py
```

This will:
- Load emotion classifier and fine-tuned LLaMA
- Process example journal entries
- Generate psychological summaries
- Enter interactive mode for custom entries

**Example Usage in Code**:

```python
from inference_pipeline import PsychologicalSummaryGenerator

# Initialize
generator = PsychologicalSummaryGenerator()

# Generate summary for a journal entry
result = generator.generate_summary(
    "I've been feeling numb and drained, nothing excites me like it used to."
)

print(f"Emotion Scores: {result['emotion_scores']}")
print(f"Summary: {result['summary']}")
```

## Prompt Template

The system uses this prompt format for training and inference:

```
[CONTEXT]

Journal Entry:
"{journal_text}"

Detected Emotions:
- sadness: {sadness_score}
- emptiness: {emptiness_score}
- hopelessness: {hopelessness_score}
- loneliness: {loneliness_score}
- anger: {anger_score}
...

[INSTRUCTION]
Based on the journal entry and the detected emotion scores above, write a
humanized psychological summary that reflects the emotional experience
expressed in the text. Do not give advice or diagnosis—just interpret
how the emotions manifest in the writing.

[HUMANIZED SUMMARY]
{generated_summary}
```

## Directory Structure

```
AI_Work/
├── data_loaders.py                    # Dataset loading scripts
├── train_emotion_classifier.py        # Emotion classifier training
├── synthesize_training_data.py        # Training data synthesis
├── fine_tune_llama.py                 # LLaMA fine-tuning with LoRA
├── inference_pipeline.py              # End-to-end inference
├── requirements.txt                   # Dependencies
├── README_PSYCHOLOGICAL_SUMMARY.md    # This file
│
├── data/                              # Datasets
│   ├── DepressionEmo/                 # DepressionEmo raw data
│   ├── depression_emo_prepared.csv   # Prepared emotion data
│   ├── empathetic_dialogues_prepared.csv  # Prepared dialogue data
│   └── ...
│
├── models/                            # Trained models
│   ├── emotion_classifier/            # Emotion classifier
│   │   ├── emotion_info.json
│   │   └── ...
│   └── llama_psychological_summary/   # Fine-tuned LLaMA
│       ├── lora_adapters/             # LoRA weights
│       └── ...
│
├── training_data/                     # Synthesized training data
│   ├── llama_training_data.json
│   └── llama_training_data.txt
│
└── results/                           # Training results
    ├── emotion_classifier_results.json
    └── inference_results.json
```

## Model Performance

### Emotion Classifier
- **Architecture**: DistilBERT (multi-label classification)
- **Metrics**: 
  - Overall Accuracy
  - F1 Score (Micro & Macro)
  - Per-emotion Precision/Recall/F1

### LLaMA Fine-tuning
- **Base Model**: LLaMA-2-7B
- **Method**: LoRA (Low-Rank Adaptation)
- **Benefits**: 
  - Efficient training (only ~1% of parameters)
  - Lower memory requirements
  - Faster training and inference

## Best Practices

1. **Emotion Classifier**:
   - Train on DepressionEmo for emotion detection only
   - Use multi-label classification (emotions are not mutually exclusive)
   - Threshold at 0.5 for binary predictions, or use probabilities

2. **Training Data Synthesis**:
   - Don't use DepressionEmo texts directly as summaries (they have no human summaries)
   - Use EmpatheticDialogues to teach empathetic, humanized style
   - Combine emotion signals with empathetic language

3. **LLaMA Fine-tuning**:
   - Use LoRA for efficient training
   - Use 4-bit quantization to fit on modest GPUs
   - Start with 3 epochs, adjust based on validation loss
   - Monitor for overfitting

4. **Inference**:
   - Use temperature=0.7 for balanced creativity/consistency
   - Adjust max_length based on desired summary length
   - Filter emotions with score > 0.3 for cleaner output

## Troubleshooting

### Dataset Loading Issues
- **DepressionEmo not found**: Download manually from GitHub and place in `data/DepressionEmo/`
- **EmpatheticDialogues download fails**: Check internet connection, try Hugging Face version first

### Model Training Issues
- **Out of memory**: Reduce batch size, use 4-bit quantization, or use smaller model
- **LLaMA access denied**: Authenticate with `huggingface-cli login` or use alternative model
- **Slow training**: Use GPU if available, reduce batch size, or use smaller model

### Inference Issues
- **Model not found**: Ensure you've completed all training steps
- **Poor summaries**: 
  - Check emotion classifier performance
  - Verify training data quality
  - Adjust generation parameters (temperature, top_p)
  - Train for more epochs if underfitting

## Alternative Models

If you don't have access to LLaMA-2, consider:

1. **microsoft/phi-2** (2.7B parameters)
   - Smaller, good quality
   - No special access required
   - Good for testing

2. **gpt2** (for testing)
   - No access required
   - Lower quality but works for pipeline testing

3. **microsoft/DialoGPT-medium**
   - Dialogue-focused
   - Good for conversational summaries

## Evaluation

### Automatic Metrics
- **ROUGE**: For summary quality
- **BERTScore**: For semantic similarity
- **Perplexity**: For language model quality

### Human Evaluation
- **Tone**: Is the summary empathetic and humanized?
- **Accuracy**: Does it reflect the detected emotions?
- **Clarity**: Is it interpretable without being diagnostic?

## References

1. **DepressionEmo Dataset**:
   - Paper: "DepressionEmo: A novel dataset for multilabel classification of depression emotions"
   - GitHub: https://github.com/abuBakarSiddiqurRahman/DepressionEmo

2. **EmpatheticDialogues**:
   - GitHub: https://github.com/facebookresearch/EmpatheticDialogues
   - Hugging Face: https://huggingface.co/datasets/Estwld/empathetic_dialogues_llm

3. **LoRA Fine-tuning**:
   - PEFT Library: https://github.com/huggingface/peft
   - LoRA Paper: "LoRA: Low-Rank Adaptation of Large Language Models"

## License

Please check the licenses of:
- DepressionEmo dataset
- EmpatheticDialogues dataset
- LLaMA models (Meta AI)
- All dependencies

## Notes

- This system is for **interpretation only**, not diagnosis or advice
- Emotion scores are probabilities, not certainties
- Summaries reflect detected emotions but may not capture all nuances
- Always use responsibly and ethically

## Support

For issues or questions:
1. Check the troubleshooting section
2. Verify all dependencies are installed
3. Ensure datasets are properly loaded
4. Check model paths and file structure

