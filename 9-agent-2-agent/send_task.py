from python_a2a import AgentNetwork, A2AClient, AIAgentRouter

# Step 1: Create an agent network
network = AgentNetwork(name="Text Utility Network")

# Step 2: Add all agents
network.add("Palindrome", "http://localhost:4753")
network.add("EmailValidator", "http://localhost:4752")
network.add("ReverseText", "http://localhost:4754")

# Step 3: Create router using a local LLM endpoint
router = AIAgentRouter(
    llm_client=A2AClient("https://api.groq.com/openai/v1"),  
    agent_network=network
)

# Step 4: Input from user
queries = [
    "Can you reverse OpenAI?"
]

# Step 5: Route each query to the appropriate agent
for query in queries:
    agent_name, confidence = router.route_query(query)
    print(f"\n Routed to: {agent_name} (confidence: {confidence:.2f})")

    agent = network.get_agent(agent_name)
    response = agent.ask(query)
    print(f" Response: {response}")
