import streamlit as st
import assemblyai as aai
import os
from dotenv import load_dotenv
import tempfile
from pathlib import Path

# Load environment variables
load_dotenv()

# Configure AssemblyAI
aai.settings.api_key = os.getenv("ASSEMBLYAI_API_KEY")

# Page configuration
st.set_page_config(
    page_title="Audio Analysis Toolkit",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
@st.cache_data
def load_css():
    """Load custom CSS styles"""
    css_file = Path("styles.css")
    if css_file.exists():
        with open(css_file, "r") as f:
            return f.read()
    return ""

# Apply CSS
css = load_css()
if css:
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

def process_audio(audio_file):
    """Process audio file with AssemblyAI"""
    config = aai.TranscriptionConfig(
        speaker_labels=True,
        sentiment_analysis=True,
        summarization=True,
        iab_categories=True,
        language_detection=True
    )
    
    transcriber = aai.Transcriber()
    transcript = transcriber.transcribe(audio_file, config=config)
    
    if transcript.status == aai.TranscriptStatus.error:
        st.error(f"Transcription failed: {transcript.error}")
        return None
    
    return transcript

def format_timestamp(milliseconds):
    """Convert milliseconds to MM:SS format"""
    seconds = milliseconds // 1000
    minutes, seconds = divmod(seconds, 60)
    return f"{minutes:02d}:{seconds:02d}"

def display_transcription(transcript):
    """Display full transcription with timestamps"""
    st.subheader("📝 Transcription")
    
    if hasattr(transcript, 'utterances') and transcript.utterances:
        for utterance in transcript.utterances:
            timestamp = format_timestamp(utterance.start)
            st.markdown(f"**[{timestamp}] Speaker {utterance.speaker}:** {utterance.text}")
    else:
        sentences = transcript.get_sentences()
        for sentence in sentences:
            timestamp = format_timestamp(sentence.start)
            st.markdown(f"**[{timestamp}]** {sentence.text}")

def display_summary(transcript):
    """Display AI-generated summary"""
    st.subheader("📋 Summary")
    if hasattr(transcript, 'summary') and transcript.summary:
        st.write(transcript.summary)
    else:
        st.info("Summary not available for this audio.")

def display_speakers(transcript):
    """Display speaker analysis"""
    st.subheader("👥 Speaker Analysis")
    
    if hasattr(transcript, 'utterances') and transcript.utterances:
        speakers = {}
        for utterance in transcript.utterances:
            speaker = f"Speaker {utterance.speaker}"
            if speaker not in speakers:
                speakers[speaker] = []
            speakers[speaker].append(utterance.text)
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Speakers", len(speakers))
        with col2:
            st.metric("Total Utterances", len(transcript.utterances))
        
        st.subheader("Speaker Breakdown")
        for speaker, utterances in speakers.items():
            with st.expander(f"{speaker} ({len(utterances)} utterances)"):
                for i, utterance in enumerate(utterances[:5], 1):  # Show first 5
                    st.write(f"{i}. {utterance}")
                if len(utterances) > 5:
                    st.write(f"... and {len(utterances) - 5} more")
    else:
        st.info("Speaker analysis not available for this audio.")

def display_sentiment(transcript):
    """Display sentiment analysis"""
    st.subheader("😊 Sentiment Analysis")
    
    if hasattr(transcript, 'sentiment_analysis') and transcript.sentiment_analysis:
        sentiment_counts = {"POSITIVE": 0, "NEUTRAL": 0, "NEGATIVE": 0}
        
        for sentiment in transcript.sentiment_analysis:
            sentiment_type = str(sentiment.sentiment).upper()
            if "POSITIVE" in sentiment_type:
                sentiment_counts["POSITIVE"] += 1
            elif "NEGATIVE" in sentiment_type:
                sentiment_counts["NEGATIVE"] += 1
            else:
                sentiment_counts["NEUTRAL"] += 1
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("😊 Positive", sentiment_counts["POSITIVE"])
        with col2:
            st.metric("😐 Neutral", sentiment_counts["NEUTRAL"])
        with col3:
            st.metric("😞 Negative", sentiment_counts["NEGATIVE"])
        
        st.subheader("Sentiment Timeline")
        for sentiment in transcript.sentiment_analysis[:10]:  # Show first 10
            timestamp = format_timestamp(sentiment.start)
            emotion = "😊" if "POSITIVE" in str(sentiment.sentiment).upper() else "😞" if "NEGATIVE" in str(sentiment.sentiment).upper() else "😐"
            st.write(f"{emotion} **[{timestamp}]** {sentiment.text}")
    else:
        st.info("Sentiment analysis not available for this audio.")

def display_topics(transcript):
    """Display topic analysis"""
    st.subheader("🏷️ Topics")
    
    if hasattr(transcript, 'iab_categories') and transcript.iab_categories:
        topics = transcript.iab_categories.summary
        if topics:
            sorted_topics = sorted(topics.items(), key=lambda x: x[1], reverse=True)[:10]
            
            for topic, confidence in sorted_topics:
                percentage = confidence * 100
                st.progress(confidence, text=f"{topic} ({percentage:.1f}%)")
        else:
            st.info("No topics detected in this audio.")
    else:
        st.info("Topic analysis not available for this audio.")

def chat_interface(transcript):
    """Simple Q&A interface"""
    st.subheader("💬 Ask Questions")
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask a question about your audio..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    # Use AssemblyAI's LeMUR for Q&A
                    response = transcript.lemur.task(
                        f"Based on the transcript, answer this question: {prompt}",
                        final_model=aai.LemurModel.claude3_5_sonnet
                    )
                    answer = response.response
                    st.markdown(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                except Exception as e:
                    error_msg = "I'm sorry, I couldn't process your question. Please try again."
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})

def main():
    """Main application"""
    st.title("🎵 Audio Analysis Toolkit")
    st.markdown("Upload an audio file to get AI-powered transcription, analysis, and insights.")
    
    # Sidebar for file upload
    with st.sidebar:
        st.header("📁 Upload Audio")
        
        uploaded_file = st.file_uploader(
            "Choose an audio file",
            type=['mp3', 'wav', 'm4a', 'mp4', 'flac'],
            help="Supported formats: MP3, WAV, M4A, MP4, FLAC"
        )
        
        if uploaded_file:
            st.success("✅ File uploaded successfully!")
            
            # Display file info
            st.info(f"**File:** {uploaded_file.name}\n**Size:** {uploaded_file.size:,} bytes")
            
            # Audio player
            st.audio(uploaded_file)
    
    # Main content
    if uploaded_file is None:
        # Welcome screen
        st.markdown("""
        ### 🚀 Get Started
        
        Upload an audio file to unlock powerful AI analysis:
        
        - **📝 Transcription** - Convert speech to text with timestamps
        - **👥 Speaker Detection** - Identify different speakers automatically  
        - **😊 Sentiment Analysis** - Understand emotional tone and context
        - **📋 Summarization** - Get key insights and main points
        - **🏷️ Topic Detection** - Discover main themes and subjects
        - **💬 Q&A Chat** - Ask questions about your audio content
        
        Simply upload a file to begin!
        """)
        
        # Feature cards
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div style="padding: 1rem; background: #f0f2f6; border-radius: 0.5rem; text-align: center;">
                <h4>🎯 Accurate</h4>
                <p>High-quality transcription with speaker identification</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div style="padding: 1rem; background: #f0f2f6; border-radius: 0.5rem; text-align: center;">
                <h4>🧠 Intelligent</h4>
                <p>AI-powered sentiment and topic analysis</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div style="padding: 1rem; background: #f0f2f6; border-radius: 0.5rem; text-align: center;">
                <h4>💬 Interactive</h4>
                <p>Ask questions and get instant answers</p>
            </div>
            """, unsafe_allow_html=True)
    
    else:
        # Process the uploaded file
        if "transcript" not in st.session_state or st.session_state.get("current_file") != uploaded_file.name:
            with st.spinner("🔄 Processing your audio... This may take a few minutes."):
                # Save uploaded file temporarily
                with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    tmp_file_path = tmp_file.name
                
                # Process with AssemblyAI
                transcript = process_audio(tmp_file_path)
                
                # Clean up temp file
                os.unlink(tmp_file_path)
                
                if transcript:
                    st.session_state.transcript = transcript
                    st.session_state.current_file = uploaded_file.name
                    st.success("✅ Audio processed successfully!")
                else:
                    st.error("❌ Failed to process audio. Please try again.")
                    return
        
        # Display results in tabs
        if "transcript" in st.session_state:
            transcript = st.session_state.transcript
            
            tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
                "📝 Transcription", 
                "📋 Summary", 
                "👥 Speakers", 
                "😊 Sentiment", 
                "🏷️ Topics", 
                "💬 Chat"
            ])
            
            with tab1:
                display_transcription(transcript)
            
            with tab2:
                display_summary(transcript)
            
            with tab3:
                display_speakers(transcript)
            
            with tab4:
                display_sentiment(transcript)
            
            with tab5:
                display_topics(transcript)
            
            with tab6:
                chat_interface(transcript)

if __name__ == "__main__":
    main()
