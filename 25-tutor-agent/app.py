import os
import streamlit as st
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, LLM

# Load .env
load_dotenv()

# Streamlit UI setup
st.set_page_config(page_title="📚 AI Tutor Bot", layout="wide")
st.title("📚 Educational Tutor Bot")
st.markdown("Learn any topic. Get a breakdown, a short lesson, and a quiz!")

# User input
topic = st.text_input("🧠 Enter a topic to learn about", placeholder="e.g., Photosynthesis, Recursion in Python")
run_button = st.button("Teach Me")

# Groq LLM setup
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    st.error("GROQ_API_KEY not found in .env file")
    st.stop()

llm = LLM(
    model="groq/llama3-70b-8192",
    api_key=api_key
)


# Agents
planner = Agent(
    role="Lesson Planner",
    goal="Break the topic into 3-5 key points to teach",
    backstory="You're an educational content designer who plans lessons effectively.",
    allow_delegation=False,
    llm=llm
)

tutor = Agent(
    role="Tutor",
    goal="Write a beginner-friendly explanation of the topic",
    backstory="You're a skilled teacher known for simplifying complex topics.",
    allow_delegation=False,
    llm=llm
)

quizzer = Agent(
    role="Quiz Master",
    goal="Create 3-5 multiple choice or short-answer quiz questions with answers",
    backstory="You're a test creator who builds quizzes to check understanding.",
    allow_delegation=False,
    llm=llm
)

# Tasks
def get_tasks(topic):
    task1 = Task(
        description=f"Break the topic '{topic}' into 3-5 learning subtopics.",
        expected_output="List of key points to teach.",
        agent=planner
    )
    task2 = Task(
        description=f"Write a clear, beginner-friendly explanation of the topic: {topic}. Include examples if helpful.",
        expected_output="A short written lesson.",
        agent=tutor
    )
    task3 = Task(
        description=f"Write a quiz (3-5 questions) to test knowledge of the topic: {topic}. Include answers.",
        expected_output="Quiz questions and answers.",
        agent=quizzer
    )
    return [task1, task2, task3]

# Crew and Execution
if run_button and topic.strip():
    with st.spinner("🧠 Generating your learning materials..."):
        try:
            crew = Crew(
                agents=[planner, tutor, quizzer],
                tasks=get_tasks(topic),
                llm=llm,
                verbose=False
            )
            result = crew.kickoff()

            st.success("✅ Lesson ready!")
            st.markdown("### 📝 Learning Material")
            st.code(result, language="markdown")

        except Exception as e:
            st.error("❌ Something went wrong.")
            st.code(str(e))

elif run_button:
    st.warning("Please enter a topic to get started.")
