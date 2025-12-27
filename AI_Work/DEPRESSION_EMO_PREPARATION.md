# DepressionEmo Dataset Preparation Guide

## Overview

The DepressionEmo dataset comes in JSON format with the following structure:
- **Location**: `data/DepressionEmo/Dataset/`
- **Files**: `train.json`, `val.json`, `test.json`
- **Format**: JSON Lines format (one JSON object per line) or JSON array format
- **Each entry contains**:
  - `id`: Unique identifier
  - `title`: Post title
  - `post`: Original post text
  - `text`: Combined title + post
  - `emotions`: List of emotion labels (e.g., `["anger", "hopelessness", "sadness"]`)
  - `label_id`: Binary encoded label
  - Other metadata (upvotes, date, etc.)

## Emotions in the Dataset

### Standard 8 Emotions (Original Specification)
1. `sadness`
2. `emptiness`
3. `hopelessness`
4. `loneliness`
5. `anger`
6. `guilt`
7. `shame`
8. `fear`

### Additional Emotions Found in Dataset
- `worthlessness`
- `suicide intent` (normalized to `suicide_intent`)
- `brain dysfunction (forget)` (normalized to `brain_dysfunction`)

## Usage

### Step 1: Prepare the Dataset

Run the preparation script:

```bash
python prepare_depression_emo.py
```

This will:
1. Load `train.json`, `val.json`, and `test.json`
2. Extract text and emotion labels
3. Normalize emotion names
4. Create binary labels for each emotion
5. Save prepared data as CSV and JSON

### Step 2: Review Prepared Data

The script creates:
- `data/depression_emo_prepared.csv` - Main training file
- `data/depression_emo_train.csv` - Train split
- `data/depression_emo_val.csv` - Validation split
- `data/depression_emo_test.csv` - Test split
- `data/depression_emo_prepared.json` - JSON format with all splits

### Step 3: Train Emotion Classifier

After preparation, train the classifier:

```bash
python train_emotion_classifier.py
```

The training script will automatically:
- Load the prepared data
- Detect available emotions from the data
- Train a multi-label emotion classifier

## Data Format

### Input Format (JSON)
```json
{
  "id": "hhcq6e",
  "title": "Found out something awful",
  "post": "My mum had a boyfriend...",
  "text": "Found out something awful ### My mum had a boyfriend...",
  "emotions": ["anger", "hopelessness", "sadness"],
  "label_id": 10010100
}
```

### Output Format (CSV)
```csv
id,text,title,emotions_list,sadness,emptiness,hopelessness,loneliness,anger,guilt,shame,fear,worthlessness,suicide_intent,brain_dysfunction
hhcq6e,"Found out something awful ### My mum...","Found out something awful","['anger', 'hopelessness', 'sadness']",0,0,1,0,1,0,0,0,0,0,0
```

## Configuration Options

In `prepare_depression_emo.py`, you can configure:

```python
prepare_depression_emo_dataset(
    use_standard_emotions_only=False,  # Use all emotions or just 8 standard
    include_additional=True,              # Include additional emotions
    min_text_length=10                   # Minimum text length to include
)
```

## Emotion Normalization

The script normalizes emotion names:
- `"suicide intent"` → `"suicide_intent"`
- `"brain dysfunction (forget)"` → `"brain_dysfunction"`
- `"cognitive_dysfunction"` → `"brain_dysfunction"`

## Statistics

After preparation, you'll see:
- Total number of samples per split
- Emotion distribution (how many samples have each emotion)
- Sample entries for verification

## Troubleshooting

### JSON Parsing Errors

**Error: `json.decoder.JSONDecodeError: Extra data: line 2 column 1`**

This means the file is in **JSON Lines format** (one JSON object per line), not a single JSON array. The `prepare_depression_emo.py` script now handles both formats automatically:

- ✅ **JSON Lines format** (one object per line):
  ```json
  {"id": "1", "text": "...", "emotions": [...]}
  {"id": "2", "text": "...", "emotions": [...]}
  ```

- ✅ **JSON Array format**:
  ```json
  [{"id": "1", ...}, {"id": "2", ...}]
  ```

The script automatically detects and handles both formats.

### "No emotion columns found"
- Make sure you ran `prepare_depression_emo.py` first
- Check that the JSON files exist in `data/DepressionEmo/Dataset/`

### "Dataset not found"
- Verify the dataset is in `data/DepressionEmo/Dataset/`
- Check that `train.json`, `val.json`, and `test.json` exist

### "Empty emotions"
- Some entries may have no emotions labeled
- The script filters these out automatically
- Check `min_text_length` parameter if too many are filtered

## Next Steps

1. ✅ Prepare dataset: `python prepare_depression_emo.py`
2. ✅ Train classifier: `python train_emotion_classifier.py`
3. ✅ Synthesize training data: `python synthesize_training_data.py`
4. ✅ Fine-tune LLaMA: `python fine_tune_llama.py`
5. ✅ Generate summaries: `python inference_pipeline.py`

## Notes

- The dataset uses **multi-label classification** (multiple emotions per entry)
- Emotions are not mutually exclusive
- Some entries may have no emotions (filtered out)
- The `label_id` field uses binary encoding but we use the `emotions` list directly

