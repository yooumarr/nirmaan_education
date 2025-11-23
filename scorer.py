import re
import nltk
from collections import Counter
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from sentence_transformers import SentenceTransformer, util
import textstat

_analyzer = None
_embedder = None

def get_models():
    global _analyzer, _embedder
    if _analyzer is None:
        _analyzer = SentimentIntensityAnalyzer()
    if _embedder is None:
        _embedder = SentenceTransformer('all-MiniLM-L6-v2')
    return _analyzer, _embedder

# Rubric definitions
MUST_HAVE_CONCEPTS = [
    'name', 'age', 'class/school', 'family', 'hobby'
]
GOOD_TO_HAVE_CONCEPTS = [
    'family trait', 'fun fact', 'ambition'
]

FILLER_WORDS = {
    'um', 'uh', 'like', 'you know', 'so', 'actually', 'basically',
    'right', 'i mean', 'well', 'kinda', 'sort of', 'okay', 'hmm', 'ah'
}

IDEAL_INTRO = (
    "The speaker introduces themselves with a greeting, mentions their name, age, "
    "school and class, describes their family, talks about hobbies or interests, "
    "shares a fun fact or personal story, and ends politely."
)

def preprocess_text(text):
    return re.sub(r'\s+', ' ', text).strip()

def get_salutation_score(text):
    t = text.lower()
    if any(phrase in t for phrase in ["i am excited to introduce", "feeling great"]):
        return 5, "Excellent salutation"
    elif any(phrase in t for phrase in [
        "good morning", "good afternoon", "good evening", "good day", "hello everyone"
    ]):
        return 4, "Good salutation: 'Hello everyone'"
    elif any(phrase in t for phrase in ["hi", "hello"]):
        return 2, "Basic salutation ('Hi' or 'Hello')"
    else:
        return 0, "No recognizable salutation"

def check_keywords(text):
    t = text.lower()
    found_must = []
    found_good = []

    # Must-have checks
    if any(w in t for w in ['myself', 'i am', "i'm"]):
        found_must.append('name')
    if any(w in t for w in ['13 years old', '13 year', 'age', 'years old']):
        found_must.append('age')
    if any(w in t for w in ['class', '8th', 'section', 'school']) and ('christ' in t or 'school' in t):
        found_must.append('class/school')
    if 'family' in t or 'mother' in t or 'father' in t:
        found_must.append('family')
    if any(w in t for w in ['cricket', 'play', 'playing', 'hobby', 'enjoy']):
        found_must.append('hobby')

    # Good-to-have
    if 'kind hearted' in t or 'soft spoken' in t:
        found_good.append('family trait')
    if 'mirror' in t or 'stole a toy' in t or 'fun fact' in t:
        found_good.append('fun fact')

    must_score = min(len(found_must) * 4, 20)
    good_score = min(len(found_good) * 2, 10)
    feedback = (
        f"Must-have concepts: {', '.join(found_must) or 'none'} ({must_score}/20). "
        f"Good-to-have: {', '.join(found_good) or 'none'} ({good_score}/10)."
    )
    return must_score + good_score, feedback

def check_flow(text):
    sentences = nltk.sent_tokenize(text)
    if len(sentences) < 3:
        return 0, "Too few sentences"
    first = sentences[0].lower()
    last = sentences[-1].lower()
    has_opening = any(w in first for w in ['hello', 'hi', 'good'])
    has_closing = any(w in last for w in ['thank', 'thanks', 'listening'])
    if has_opening and has_closing:
        return 5, "Clear opening and closing"
    return 0, "Missing proper opening or closing"

def speech_rate_score(word_count, duration_sec):
    if duration_sec <= 0:
        return 0, "Invalid duration"
    wpm = (word_count / duration_sec) * 60
    if wpm > 160:
        return 2, f"Too fast ({wpm:.0f} WPM)"
    elif wpm >= 141:
        return 6, f"Fast ({wpm:.0f} WPM)"
    elif wpm >= 111:
        return 10, f"Ideal pace ({wpm:.0f} WPM)"
    elif wpm >= 81:
        return 6, f"Slow ({wpm:.0f} WPM)"
    else:
        return 2, f"Too slow ({wpm:.0f} WPM)"

def grammar_score(text):
    try:
        fre = textstat.flesch_reading_ease(text)
    except:
        fre = 50

    words = text.split()
    repeated = sum(
        1 for i in range(len(words) - 1)
        if words[i].lower() == words[i+1].lower()
    )
    ends_punct = text.strip()[-1] in '.!?'

    if fre >= 80 and repeated == 0 and ends_punct:
        score = 10
    elif fre >= 60 and repeated <= 1:
        score = 8
    elif fre >= 40:
        score = 6
    elif fre >= 20:
        score = 4
    else:
        score = 2

    return score, f"Flesch Ease: {fre:.1f}; repeated words: {repeated}; ends with punctuation: {ends_punct}"

def ttr_score(text):
    words = [w.lower() for w in re.findall(r'\b\w+\b', text)]
    if not words:
        return 2, "No words"
    ttr = len(set(words)) / len(words)
    if ttr >= 0.9:
        score = 10
    elif ttr >= 0.7:
        score = 8
    elif ttr >= 0.5:
        score = 6
    elif ttr >= 0.3:
        score = 4
    else:
        score = 2
    return score, f"TTR = {ttr:.2f}"

def filler_score(text):
    words = [w.lower() for w in re.findall(r'\b\w+\b', text)]
    if not words:
        return 15, "No words"
    filler_count = sum(1 for w in words if w in FILLER_WORDS)
    rate = (filler_count / len(words)) * 100
    if rate <= 3:
        score = 15
    elif rate <= 6:
        score = 12
    elif rate <= 9:
        score = 9
    elif rate <= 12:
        score = 6
    else:
        score = 3
    return score, f"Filler rate = {rate:.1f}% ({filler_count} fillers)"

def engagement_score(text):
    analyzer, _ = get_models()
    sentiment = analyzer.polarity_scores(text)
    pos = sentiment['pos']
    if pos >= 0.9:
        score = 15
    elif pos >= 0.7:
        score = 12
    elif pos >= 0.5:
        score = 9
    elif pos >= 0.3:
        score = 6
    else:
        score = 3
    return score, f"Positive sentiment = {pos:.2f}"

def semantic_feedback(text):
    try:
        _, embedder = get_models()
        emb1 = embedder.encode(IDEAL_INTRO, convert_to_tensor=True)
        emb2 = embedder.encode(text, convert_to_tensor=True)
        sim = util.cos_sim(emb1, emb2).item()
        return f" (Semantic similarity: {sim:.2f})"
    except Exception:
        return ""

def score_transcript(transcript: str, duration_sec: int):
    text = preprocess_text(transcript)
    words = text.split()
    word_count = len(words)

    # Content & Structure (40)
    sal, sal_fb = get_salutation_score(text)
    key, key_fb = check_keywords(text)
    flow, flow_fb = check_flow(text)
    content_total = sal + key + flow
    content_fb = f"{sal_fb}. {key_fb} {flow_fb}{semantic_feedback(text)}"

    # Speech Rate (10)
    wpm_score, wpm_fb = speech_rate_score(word_count, duration_sec)

    # Language & Grammar (20 = 10 + 10)
    gram, gram_fb = grammar_score(text)
    ttr, ttr_fb = ttr_score(text)
    lang_total = gram + ttr
    lang_fb = f"{gram_fb}; {ttr_fb}"

    # Clarity (15)
    clarity, clarity_fb = filler_score(text)

    # Engagement (15)
    engage, engage_fb = engagement_score(text)

    total = content_total + wpm_score + lang_total + clarity + engage

    return {
        "overall_score": min(100, round(total)),
        "word_count": word_count,
        "duration_sec": duration_sec,
        "criteria": [
            {"name": "Content & Structure", "score": content_total, "max_score": 40, "feedback": content_fb},
            {"name": "Speech Rate", "score": wpm_score, "max_score": 10, "feedback": wpm_fb},
            {"name": "Language & Grammar", "score": lang_total, "max_score": 20, "feedback": lang_fb},
            {"name": "Clarity", "score": clarity, "max_score": 15, "feedback": clarity_fb},
            {"name": "Engagement", "score": engage, "max_score": 15, "feedback": engage_fb},
        ]
    }