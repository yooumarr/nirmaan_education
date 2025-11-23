import streamlit as st
from scorer import score_transcript

import nltk
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

st.set_page_config(page_title="Self-Intro Scorer", layout="wide")
st.title("Student Self-Introduction Scorer")
st.markdown(
    "Paste a transcript of self-introduction,"
    " and enter the speech duration to get an AI-powered rubric score."
)

# Input
col1, col2 = st.columns([3, 1])
with col1:
    transcript = st.text_area("Transcript", height=200, placeholder="e.g., Hello everyone, I'm Muskan...")
with col2:
    duration_sec = st.number_input("Speech Duration (seconds)", min_value=1, value=52, step=1)
    uploaded_file = st.file_uploader("Or upload a .txt file", type=["txt"])
    if uploaded_file:
        transcript = uploaded_file.read().decode("utf-8")

if st.button("Score This Introduction"):
    if not transcript.strip():
        st.warning("Please provide a transcript.")
    else:
        result = score_transcript(transcript.strip(), duration_sec)
        st.subheader("Scoring Results")
        st.metric("Overall Score", f"{result['overall_score']}/100")

        # Per-criterion output
        for crit in result["criteria"]:
            with st.expander(f"{crit['name']} – {crit['score']}/{crit['max_score']}"):
                st.write(f"**Feedback**: {crit['feedback']}")
else:
    st.info("Click **Score This Introduction** to analyze the transcript.")