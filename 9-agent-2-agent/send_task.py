from python_a2a import AgentNetwork, AIAgentRouter
from openai import OpenAI  # Use OpenAI client, not A2AClient

# Step 1: Create the agent network
network = AgentNetwork(name="Text Utility Network")

# Step 2: Add agents with names and URLs
network.add("Palindrome", "http://localhost:4753")
network.add("EmailValidator", "http://localhost:4752")
network.add("ReverseText", "http://localhost:4754")

# Step 3: Set up LLM client using Groq (OpenAI-compatible)
llm_client = OpenAI(
    api_key="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",  
    base_url="https://api.groq.com/openai/v1"
)

system_message = (
    "You are an intelligent router. Based on the user input, respond with only one of the following agent names: "
    "Palindrome, ReverseText, EmailValidator. Do not say anything else."
)

# Step 4: Plug into the router
router = AIAgentRouter(
    llm_client=llm_client,
    agent_network=network,
    system_message=system_message
)

# Step 5: User queries to route
queries = [
    "My mail ID is hello@example.com",
    "reverse the word 'hello'",
    "check if 'anna' is a palindrome",
]

# Step 6: Run each query through the router
for query in queries:
    agent_name, confidence = router.route_query(query)
    print(f"\n Routed to: {agent_name} (confidence: {confidence:.2f})")

    agent = network.get_agent(agent_name)
    response = agent.ask(query)
    print(f" Response: {response}")
