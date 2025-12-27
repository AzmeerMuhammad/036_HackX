# Sentiment Analysis Model Training

This folder contains the complete pipeline for training a high-accuracy multi-class sentiment analysis classifier.

## Overview

The pipeline includes:
- Dataset download from Kaggle
- Data preprocessing and exploration
- Transformer-based model training (DistilBERT/BERT)
- Model evaluation and metrics
- Model saving and inference

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Make sure you have Kaggle credentials set up (if needed):
   - Place your `kaggle.json` in `~/.kaggle/` (Linux/Mac) or `C:\Users\<username>\.kaggle\` (Windows)

## Usage

### Step 1: Download Dataset

```bash
python sentiment-data.py
```

This will download the sentiment analysis dataset from Kaggle and save it to the `data/` folder.

### Step 2: Train Model

```bash
python train_sentiment_model.py
```

This will:
- Load and explore the dataset
- Preprocess the data
- Train a transformer-based sentiment classifier
- Evaluate on test set
- Save the trained model to `models/sentiment_model/`
- Save training results to `results/training_results.json`

### Step 3: Make Predictions

```bash
python predict_sentiment.py
```

Or use the `SentimentPredictor` class in your code:

```python
from predict_sentiment import SentimentPredictor

# Initialize
predictor = SentimentPredictor()

# Predict single text
label, confidence = predictor.predict("I love this product!")
print(f"Sentiment: {label}, Confidence: {confidence:.4f}")

# Predict with probabilities
label, confidence, probs = predictor.predict("This is great!", return_probabilities=True)
print(f"Sentiment: {label}")
print(f"Probabilities: {probs}")

# Predict batch
texts = ["Great!", "Terrible!", "Okay"]
results = predictor.predict_batch(texts)
```

## Model Architecture

The pipeline uses **DistilBERT** (distilbert-base-uncased) by default, which provides:
- High accuracy (typically 85-95% depending on dataset)
- Fast training and inference
- Lower memory requirements than full BERT

To use full BERT for potentially better accuracy, modify `train_sentiment_model.py`:
```python
model_name='bert-base-uncased'  # Instead of 'distilbert-base-uncased'
```

## Directory Structure

```
AI_Work/
├── sentiment-data.py          # Dataset download script
├── train_sentiment_model.py   # Main training pipeline
├── predict_sentiment.py       # Inference script
├── requirements.txt           # Python dependencies
├── README.md                  # This file
├── data/                      # Downloaded dataset (created after download)
├── models/                    # Trained models (created after training)
│   ├── sentiment_model/       # Saved model and tokenizer
│   └── label_encoder.pkl      # Label encoder
└── results/                   # Training results (created after training)
    ├── training_results.json  # Training metrics and reports
    └── logs/                  # Training logs
```

## Model Performance

The model will output:
- Test set accuracy
- Weighted F1 score
- Detailed classification report per class
- Confusion matrix

Results are saved to `results/training_results.json` for reference.

## Notes

- The model automatically handles text preprocessing (tokenization, truncation, padding)
- Maximum sequence length is set to 128 tokens
- Early stopping is enabled to prevent overfitting
- The model uses GPU if available, otherwise CPU
- All paths are relative to the `AI_Work` folder

