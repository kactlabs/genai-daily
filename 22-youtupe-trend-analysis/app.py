import streamlit as st
import os
import yaml
from tqdm import tqdm
from pytube import Channel, YouTube
from youtube_transcript_api import YouTubeTranscriptApi
from dotenv import load_dotenv
from crewai import Agent, Crew, Process, Task, LLM
from crewai_tools import FileReadTool

# Load .env variables
load_dotenv()

file_tool = FileReadTool()

# LLM loader
@st.cache_resource
def load_llm():
    return LLM(
        model="llama3-70b-8192",
        config={
            "litellm_provider": "groq",
            "api_key": os.getenv("GROQ_API_KEY")
        }
    )

# Create agents and tasks
def create_agents_and_tasks():
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)

    analysis_agent = Agent(
        role=config["agents"][0]["role"],
        goal=config["agents"][0]["goal"],
        backstory=config["agents"][0]["backstory"],
        verbose=True,
        tools=[file_tool],
        llm=load_llm()
    )

    response_agent = Agent(
        role=config["agents"][1]["role"],
        goal=config["agents"][1]["goal"],
        backstory=config["agents"][1]["backstory"],
        verbose=True,
        llm=load_llm()
    )

    task1 = Task(
        description=config["tasks"][0]["description"],
        expected_output=config["tasks"][0]["expected_output"],
        agent=analysis_agent
    )

    task2 = Task(
        description=config["tasks"][1]["description"],
        expected_output=config["tasks"][1]["expected_output"],
        agent=response_agent
    )

    crew = Crew(
        agents=[analysis_agent, response_agent],
        tasks=[task1, task2],
        process=Process.sequential,
        verbose=True
    )
    return crew

# Validate and convert URLs to /channel/ format if needed
def normalize_channel_url(url):
    if "/@" in url:
        return f"https://www.youtube.com{url.split('.com')[-1]}"
    return url

# Get videos + transcripts
def get_videos_and_transcripts(channel_urls, start_date, end_date):
    scraped_data = []
    for url in channel_urls:
        try:
            normalized_url = normalize_channel_url(url)
            ch = Channel(normalized_url)
            videos = list(ch.videos)
            channel_data = []
            for yt in videos:
                try:
                    publish_date = yt.publish_date.strftime("%Y-%m-%d")
                    if start_date <= publish_date <= end_date:
                        transcript = YouTubeTranscriptApi.get_transcript(yt.video_id)
                        channel_data.append({
                            'url': yt.watch_url,
                            'shortcode': yt.video_id,
                            'formatted_transcript': transcript
                        })
                except Exception as e:
                    print(f"Skipping video: {e}")
            scraped_data.append(channel_data)
        except Exception as e:
            print(f"Channel error: {e}")
    return scraped_data

# Start analysis
def start_analysis():
    with st.spinner("Scraping videos..."):
        output = get_videos_and_transcripts(
            st.session_state.youtube_channels,
            st.session_state.start_date,
            st.session_state.end_date
        )

        if not output or not output[0]:
            st.error("No videos found in the selected date range.")
            return

        st.markdown("## Extracted Videos")
        for video in output[0]:
            st.video(video["url"])

        st.session_state.all_files = []
        os.makedirs("transcripts", exist_ok=True)

        for video in output[0]:
            file_path = f"transcripts/{video['shortcode']}.txt"
            with open(file_path, "w") as f:
                for seg in video['formatted_transcript']:
                    f.write(f"({seg['start']:.2f}-{seg['start']+seg['duration']:.2f}): {seg['text']}\n")
            st.session_state.all_files.append(file_path)

        st.success("Scraping complete! Starting analysis...")

    with st.spinner("Analyzing content..."):
        st.session_state.crew = create_agents_and_tasks()
        st.session_state.response = st.session_state.crew.kickoff(inputs={"file_paths": ", ".join(st.session_state.all_files)})

# Sidebar
with st.sidebar:
    st.header("YouTube Channels")
    if "youtube_channels" not in st.session_state:
        st.session_state.youtube_channels = [""]

    def add_channel():
        st.session_state.youtube_channels.append("")

    for i, url in enumerate(st.session_state.youtube_channels):
        col1, col2 = st.columns([6, 1])
        with col1:
            st.session_state.youtube_channels[i] = st.text_input("Channel URL", value=url, key=f"channel_{i}", label_visibility="collapsed")
        with col2:
            if i > 0 and st.button("❌", key=f"remove_{i}"):
                st.session_state.youtube_channels.pop(i)
                st.rerun()

    st.button("Add Channel ➕", on_click=add_channel)
    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        start = st.date_input("Start Date")
        st.session_state.start_date = start.strftime("%Y-%m-%d")
    with col2:
        end = st.date_input("End Date")
        st.session_state.end_date = end.strftime("%Y-%m-%d")

    st.divider()
    st.button("Start Analysis 🚀", type="primary", on_click=start_analysis)

# Main Output
if st.session_state.get("response"):
    st.markdown("## Generated Summary")
    result = st.session_state.response
    st.markdown(result)
    st.download_button("Download", data=result.raw, file_name="youtube_trend_analysis.md", mime="text/markdown")

st.markdown("---")
st.markdown("✅ Built with CrewAI + Streamlit")
