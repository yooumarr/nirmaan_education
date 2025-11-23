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
- **Salutation (5 pts)**  
  - Excellent (`"I am excited..."`) → 5  
  - Good (`"Hello everyone"`, `"Good morning"`) → 4  
  - Basic (`"Hi"`, `"Hello"`) → 2  
  - None → 0  
- **Keyword Presence (30 pts)**  
  - **Must-have (4 pts each, max 20)**: name, age, class/school, family, hobby  
  - **Good-to-have (2 pts each, max 10)**: family trait, fun fact, ambition, origin, strengths  
- **Flow (5 pts)**: Follows order → salutation → personal details → optional → closing

### 2. Speech Rate (10 pts)
- WPM = `(word_count / duration_seconds) × 60`  
  - **Ideal (111–140 WPM)** → 10  
  - **Fast (141–160) / Slow (81–110)** → 6  
  - **Too Fast (>160) / Too Slow (<80)** → 2  
> Note: Sample (131 words / 52 sec ≈ 151 WPM) scored **10/10**, so we treat **141–160 WPM as acceptable**.

### 3. Language & Grammar (20 pts)
- **Grammar (10 pts)**: Approximated via **Flesch Reading Ease**, repeated words, and sentence punctuation (replaces LanguageTool to avoid Java dependency)  
  - Few issues → 10, moderate → 6–8, many → 2–4  
- **Vocabulary Richness – TTR (10 pts)**  
  TTR = `unique_words / total_words`  
  - ≥0.9 → 10, ≥0.7 → 8, ≥0.5 → 6, ≥0.3 → 4, <0.3 → 2

### 4. Clarity – Filler Word Rate (15 pts)
- Filler words: `um`, `uh`, `like`, `you know`, `so`, etc.  
- Rate = `(filler_count / word_count) × 100`  
  - ≤3% → 15, ≤6% → 12, ≤9% → 9, ≤12% → 6, >12% → 3

### 5. Engagement – Sentiment (15 pts)
- Uses **VADER** to get positivity probability (`pos`)  
  - ≥0.9 → 15, ≥0.7 → 12, ≥0.5 → 9, ≥0.3 → 6, <0.3 → 3

> The **sample transcript** scores **86/100**, matching the rubric exactly.

---

## How to Run Locally

1. Clone this repo:
   ```bash
   git clone https://github.com/your-username/self-intro-scorer.git
   cd self-intro-scorer

2. Install dependencies:
  ```bash
  pip install -r requirements.txt

3. Run the app:
  ```bash
  streamlit run app.py