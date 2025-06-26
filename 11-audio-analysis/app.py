import streamlit as st
import assemblyai as aai
import os
from dotenv import load_dotenv
import base64

# Load your API key
load_dotenv()
aai.settings.api_key = os.getenv("ASSEMBLYAI_API_KEY")

# Title
st.set_page_config(page_title="🎙️ Interview Audio Analyzer", layout="centered")
st.title("🎙️ Interview Audio Analyzer")
st.markdown("Upload a candidate’s audio answer and receive automated feedback, summary, and performance rating.")

# File upload
audio_file = st.file_uploader("📁 Upload Interview Audio (MP3, WAV, M4A, etc.)", type=["mp3", "wav", "m4a", "flac"])

# Utility functions
def get_score(summary_len, sentiment_score, topic_score):
    clarity = min(10, summary_len // 15)
    confidence = sentiment_score
    relevance = topic_score
    total = clarity + confidence + relevance
    return total, clarity, confidence, relevance

def analyze_audio(file):
    config = aai.TranscriptionConfig(
        speaker_labels=True,
        iab_categories=True,
        sentiment_analysis=True,
        summarization=True
    )
    transcriber = aai.Transcriber()
    transcript = transcriber.transcribe(file, config=config)
    return transcript

if audio_file:
    st.audio(audio_file)
    with st.spinner("🔍 Analyzing the candidate’s audio..."):
        transcript = analyze_audio(audio_file)

    # Summary
    st.subheader("📋 Summary")
    st.write(transcript.summary)

    # Sentiment Analysis
    sentiments = {"POSITIVE": 0, "NEUTRAL": 0, "NEGATIVE": 0}
    for s in transcript.sentiment_analysis:
        sentiments[s.sentiment.upper()] += 1
    
    sentiment_score = 8 if sentiments["POSITIVE"] > sentiments["NEGATIVE"] else 5

    st.markdown(f"**😊 Positive:** {sentiments['POSITIVE']}  | 😐 Neutral: {sentiments['NEUTRAL']} | 😞 Negative: {sentiments['NEGATIVE']}")
    
    # Topic Detection
    topics = transcript.iab_categories.summary
    top_topics = sorted(topics.items(), key=lambda x: x[1], reverse=True)[:3]
    
    topic_score = 8 if top_topics else 5
    st.subheader("🏷️ Topics Identified")
    for topic, score in top_topics:
        st.markdown(f"- **{topic}** ({score*100:.1f}%)")
    
    # Final Score
    summary_len = len(transcript.summary.split())
    total_score, clarity, confidence, relevance = get_score(summary_len, sentiment_score, topic_score)

    st.subheader("📊 Performance Rating")
    st.markdown(f"""
    - 🗣️ **Clarity**: {clarity}/10  
    - 💬 **Confidence**: {confidence}/10  
    - 🎯 **Relevance**: {relevance}/10  
    - 🏁 **Final Score**: `{total_score}/30`
    """)

    if total_score >= 25:
        st.success("✅ Great job! The candidate performed excellently.")
    elif total_score >= 18:
        st.info("ℹ️ Good effort. Some improvements needed.")
    else:
        st.warning("⚠️ Needs improvement. Consider giving more structured and confident responses.")

    # Transcript
    with st.expander("📄 Full Transcript"):
        for sentence in transcript.get_sentences():
            st.markdown(f"**[{sentence.start // 1000}s]** {sentence.text}")
