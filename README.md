# Self-Introduction Scoring Tool

This tool evaluates student self-introduction transcripts using a rubric-based approach combining rule-based checks, NLP, and semantic analysis.

## Features
- Accepts transcript via text or `.txt` upload  
- Requires speech duration (in seconds)  
- Scores across 5 criteria:  
  1. **Content & Structure** (40 pts)  
  2. **Speech Rate** (10 pts)  
  3. **Language & Grammar** (20 pts)  
  4. **Clarity** (15 pts)  
  5. **Engagement** (15 pts)  
- Provides per-criterion feedback and overall score (0–100)

---

## Scoring Formula

The final score is the **sum of all criterion scores** (max 100). Below is how each is computed:

### 1. Content & Structure (40 pts)
Salutation, keyword presence, and logical flow

### 2. Speech Rate (10 pts)
Words per minute (WPM) based on transcript length and duration

### 3. Language & Grammar (20 pts)
Grammar quality (approximated via readability) and vocabulary richness (TTR)

### 4. Clarity – Filler Word Rate (15 pts)
Filler word rate (e.g., “um”, “like”)

### 5. Engagement – Sentiment (15 pts)
Sentiment positivity (using VADER)

---

## How to Run Locally

1. Clone this repo:
   ```bash
   git clone https://github.com/yooumarr/nirmaan_education.git
   cd nirmaan_education

2. Install dependencies:
  ```bash
  pip install -r requirements.txt

3. Run the app:
  ```bash
  streamlit run app.py