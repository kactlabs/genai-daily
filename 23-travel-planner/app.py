import os
import streamlit as st
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, LLM

# Load environment variables
load_dotenv()

st.set_page_config(page_title="🗺️ AI Travel Itinerary Planner", layout="wide")
st.markdown("<h1 style='color: #2E86C1;'>🗺️ AI Travel Itinerary Planner</h1>", unsafe_allow_html=True)
st.subheader("Powered by Groq + CrewAI")

# Sidebar API input
with st.sidebar:
    st.image("https://crewai.com/favicon.ico", width=60)
    st.header("Groq Configuration")
    st.markdown("[Get your Groq API key](https://console.groq.com/keys)", unsafe_allow_html=True)
    groq_api_key = st.text_input("Enter your Groq API Key", type="password")

    if groq_api_key:
        os.environ["GROQ_API_KEY"] = groq_api_key
        st.success("API Key saved!")

# Input fields
st.markdown("---")
st.header("Plan Your Itinerary")

col1, col2 = st.columns(2)

with col1:
    location = st.text_input("Destination", "Paris")

with col2:
    days = st.number_input("Number of Days", min_value=1, max_value=14, value=3)

plan_button = st.button("Generate Itinerary")

# LLM setup (Groq only)
llm = LLM(
    model="groq/llama3-70b-8192",  
    api_key=os.getenv("GROQ_API_KEY") 
)

# Agent definitions
planner_agent = Agent(
    role="Travel Planner",
    goal="Create a well-balanced, enjoyable travel itinerary",
    backstory="You're an expert travel planner with deep knowledge of popular and hidden travel attractions.",
    allow_delegation=False,
    llm=llm
)

# Task
itinerary_task = Task(
    description=f"Generate a day-by-day travel itinerary for {days} days in {location}. Include famous landmarks, local food spots, cultural experiences, and relaxation time.",
    expected_output=f"{days}-day travel itinerary for {location}",
    agent=planner_agent
)

# Run Crew
if plan_button:
    with st.spinner("🧳 Planning your trip..."):
        try:
            crew = Crew(
                agents=[planner_agent],
                tasks=[itinerary_task],
                llm=llm,
                verbose=False
            )
            final_plan = crew.kickoff()
            st.success("✅ Itinerary Ready!")
            st.markdown("### Your AI-Powered Travel Plan")
            st.markdown(final_plan)
        except Exception as e:
            st.error("❌ Failed to generate itinerary.")
            st.code(str(e))

# Footer
st.markdown("---")
# st.markdown("Built with ❤️ using [CrewAI](https://docs.crewai.com) and [Groq](https://groq.com)")