import streamlit as st
import google.generativeai as genai
import os
import tempfile
import time
from pathlib import Path
import mimetypes
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="🎙️ Candidate Video Analyzer",
    page_icon="🎥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===========================
#   Video Processing Class
# ===========================
class VideoProcessor:
    def __init__(self, api_key):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def upload_video(self, video_path, display_name=None):
        try:
            video_file = genai.upload_file(
                path=video_path,
                display_name=display_name or "uploaded_video"
            )
            return video_file
        except Exception as e:
            st.error(f"Error uploading video: {str(e)}")
            return None

    def wait_for_file_processing(self, video_file):
        try:
            while video_file.state.name == "PROCESSING":
                time.sleep(2)
                video_file = genai.get_file(video_file.name)
            if video_file.state.name == "FAILED":
                raise ValueError("Video processing failed")
            return video_file
        except Exception as e:
            st.error(f"Error processing video: {str(e)}")
            return None

    def summarize_candidate_video(self, video_file):
        prompt = (
            "This is a candidate's self-introduction video. Please summarize their skills, experience, tone, and confidence. "
            "Then give them a rating out of 10 based on communication, clarity, and confidence. Provide output in this format:\n\n"
            "**Summary**: ...\n**Skills Mentioned**: ...\n**Tone & Confidence**: ...\n**Rating (out of 10)**: ..."
        )
        try:
            response = self.model.generate_content([video_file, prompt])
            return response.text
        except Exception as e:
            st.error(f"Error generating summary: {str(e)}")
            return None

    def chat_with_video(self, video_file, prompt):
        try:
            response = self.model.generate_content([
                video_file,
                prompt
            ])
            return response.text
        except Exception as e:
            st.error(f"Error generating response: {str(e)}")
            return None

# ===========================
#   Helper Functions
# ===========================
def is_video_file(file):
    if file is None:
        return False
    mime_type, _ = mimetypes.guess_type(file.name)
    return mime_type and mime_type.startswith('video/')

def get_file_size_mb(file):
    return len(file.getvalue()) / (1024 * 1024)

def reset_all():
    for key in ["video_file", "video_name", "video_processor", "summary", "messages"]:
        st.session_state.pop(key, None)
    st.rerun()

# ===========================
#   Sidebar Upload + Preview
# ===========================
with st.sidebar:
    st.title("📂 Upload Candidate Video")
    api_key = os.getenv("GEMINI_API_KEY", "")
    
    if api_key and "video_processor" not in st.session_state:
        st.session_state.video_processor = VideoProcessor(api_key)

    uploaded_file = st.file_uploader(
        "Upload a self-introduction video",
        type=['mp4', 'mov', 'avi', 'mkv'],
        help="Supported formats: mp4, mov, avi, mkv"
    )

    if uploaded_file and is_video_file(uploaded_file):
        file_size = get_file_size_mb(uploaded_file)
        st.info(f"File size: {file_size:.2f} MB")

        if file_size > 100:
            st.warning("Large files may fail. Try a smaller/compressed video.")

        if ("video_file" not in st.session_state or 
            st.session_state.get("video_name") != uploaded_file.name):

            if "video_processor" not in st.session_state:
                st.error("API key not set.")
            else:
                with st.spinner("Uploading and processing video..."):
                    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp:
                        tmp.write(uploaded_file.getvalue())
                        tmp_path = tmp.name
                    try:
                        video_file = st.session_state.video_processor.upload_video(tmp_path, uploaded_file.name)
                        if video_file:
                            processed_file = st.session_state.video_processor.wait_for_file_processing(video_file)
                            if processed_file:
                                st.session_state.video_file = processed_file
                                st.session_state.video_name = uploaded_file.name
                                summary = st.session_state.video_processor.summarize_candidate_video(processed_file)
                                st.session_state.summary = summary
                                st.session_state.messages = []
                    finally:
                        os.unlink(tmp_path)

        # Display the small video preview in sidebar
        st.markdown("#### 🎥 Preview")
        st.video(uploaded_file.getvalue())

        st.markdown("---")
        if st.button("🔄 Reset"):
            reset_all()

# ===========================
#   Main Content Area
# ===========================
st.title("🎙️ Candidate Video Analyzer")
st.markdown("This tool analyzes a candidate's self-introduction video and provides a skill summary, rating, and chat interface.")

if not api_key:
    st.error("❌ API key missing. Set `GEMINI_API_KEY` in your .env file.")
elif "video_file" not in st.session_state:
    st.info("Upload a video from the left sidebar to begin.")
else:
    st.subheader("📝 Candidate Summary")
    st.markdown(st.session_state.summary)

    st.divider()
    st.subheader("💬 Ask questions about the candidate")

    for message in st.session_state.get("messages", []):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ask anything about the candidate's intro..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Analyzing..."):
                response = st.session_state.video_processor.chat_with_video(
                    st.session_state.video_file, prompt
                )
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})

# ===========================
#   Footer
# ===========================
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray;'>
    Built using <strong>Gemini API</strong> + <strong>Streamlit</strong> for candidate screening. <br>
    <a href='https://ai.google.dev/gemini-api/docs/video-understanding' target='_blank'>Learn more about Gemini Video API</a>
</div>
""", unsafe_allow_html=True)
