import os
import streamlit as st
from dotenv import load_dotenv
from crewai import Crew, Agent, Task, LLM

# Load environment variables
load_dotenv()

# Set up Streamlit UI
st.set_page_config(page_title=" Code Generator with Groq", layout="wide")
st.title(" Groq-Powered Python Code Generator")
st.markdown("Ask for any Python code snippet. The AI will generate code and tests for it.")

# User input
user_task = st.text_area(" What code do you want?", placeholder="e.g., Give me code to reverse a word")

run_button = st.button("Generate Code")

# Load Groq API key
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    st.error(" GROQ_API_KEY not found in .env file")
    st.stop()

# LLM with Groq
llm = LLM(
    model="groq/llama3-70b-8192",
    api_key=api_key
)

# Define agents
coder = Agent(
    role="Python Developer",
    goal="Write Python code to solve the user's request.",
    backstory="You are an expert Python developer. You generate clean, correct code for any prompt.",
    allow_delegation=False,
    llm=llm
)

tester = Agent(
    role="Test Writer",
    goal="Write Pytest-compatible test cases for the Python code.",
    backstory="You're a QA engineer who ensures every function is covered by tests.",
    allow_delegation=False,
    llm=llm
)

# Define tasks (no output_key/context – just sequential execution)
def get_tasks(user_prompt):
    coding_task = Task(
        description=f"The user asked: {user_prompt}\nWrite Python code to solve the request.",
        expected_output="Python code as per the request.",
        agent=coder
    )

    testing_task = Task(
        description=f"""Based on the code written to solve this task: "{user_prompt}",
write pytest-compatible unit tests covering the logic and edge cases.""",
        expected_output="Pytest test functions.",
        agent=tester
    )

    return [coding_task, testing_task]


# Run Crew
if run_button and user_task.strip():
    st.info(" AI is generating your code...")
    with st.spinner("Generating Python code and test cases..."):
        try:
            crew = Crew(
                agents=[coder, tester],
                tasks=get_tasks(user_task),
                llm=llm,
                verbose=False
            )
            final_output = crew.kickoff()

            st.success(" Code and tests generated!")

            # Optional split: Separate code and test using a delimiter if needed
            st.markdown("###  Final Output")
            st.code(final_output, language="python")

        except Exception as e:
            st.error(" An error occurred during execution.")
            st.code(str(e))

elif run_button:
    st.warning("Please enter your coding request above.")
