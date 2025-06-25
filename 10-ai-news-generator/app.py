import os
import re
import streamlit as st
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, LLM
from crewai_tools import SerperDevTool

# Load .env variables
load_dotenv()

# Streamlit Page Setup
st.set_page_config(page_title=" YouTube Video Finder", page_icon="📺", layout="wide")

st.title(" YouTube Video Finder")
st.markdown("Enter a query and get the top 3 YouTube videos using AI search agents!")

# Sidebar Input
with st.sidebar:
    st.header("Search Settings")
    query = st.text_area(
        "Enter your YouTube search query",
        height=100,
        placeholder="e.g., Python web development tutorials"
    )
    search_button = st.button("Find Videos", type="primary", use_container_width=True)

    with st.expander(" How to use"):
        st.markdown("""
        1. Type your search query in the box above  
        2. Click 'Find Videos'  
        3. The top 3 YouTube videos will appear on the right  
        """)

# Function to find YouTube videos using CrewAI + SerperDevTool
def find_youtube_videos(query):
    llm = LLM(model="command-r", temperature=0.3)

    search_tool = SerperDevTool(n_results=10)

    search_agent = Agent(
        role="YouTube Video Searcher",
        goal=f"Search for YouTube videos about: {query}",
        backstory="You're an expert web search agent who finds relevant YouTube videos using advanced search tools.",
        tools=[search_tool],
        llm=llm,
        verbose=True
    )

    search_task = Task(
        description=f"""
        Use the query: "{query} site:youtube.com" to find the top YouTube videos.  
        Your job is to extract 3 real, working YouTube URLs like:  
        https://www.youtube.com/watch?v=xxxxxxx  
        Only return actual video links from YouTube, no summaries or made-up URLs.
        """,
        expected_output="A list of 3 real YouTube video URLs.",
        agent=search_agent
    )

    crew = Crew(
        agents=[search_agent],
        tasks=[search_task],
        verbose=True
    )

    return crew.kickoff(inputs={"topic": query})

# Main Functionality
if search_button:
    if not query.strip():
        st.warning("Please enter a search query.")
    else:
        with st.spinner("Searching YouTube..."):
            try:
                result = find_youtube_videos(query)

                # Show raw output (for debug)
                st.markdown("###  Raw Agent Output")
                st.code(result.raw, language="text")

                # Extract YouTube links using regex
                urls = re.findall(r'https?://www\.youtube\.com/watch\?v=[\w-]+', result.raw)
                urls = urls[:3]

                if not urls:
                    st.error("No YouTube links found. Try a different query.")
                else:
                    st.markdown("### Top 3 YouTube Videos")
                    for i, url in enumerate(urls, 1):
                        st.markdown(f"**Video {i}:** [{url}]({url})")
                        st.video(url)

            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

# Footer
st.markdown("---")
st.markdown("Built with  CrewAI, Streamlit, and Serper. Powered by LLMs.")
