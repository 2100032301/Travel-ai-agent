# travel.py
import asyncio
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.ui import Console
from autogen_agentchat.messages import TextMessage  # Import TextMessage for type hinting

# Set OpenAI API key directly (consider moving to environment variables for security)
API_KEY = "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"

# Initialize OpenAI client
model_client = OpenAIChatCompletionClient(
    model="gpt-3.5-turbo",
    api_key=API_KEY
)

# ------------------------- Define AI Agents -------------------------

# 1️⃣ Travel Planner Agent - Creates a structured trip plan
planner_agent = AssistantAgent(
    "planner_agent",
    model_client=model_client,
    description="Plans trips by creating an itinerary.",
    system_message="You are an expert travel planner. Create a structured, detailed itinerary for the given destination and duration."
)

# 2️⃣ Local Guide Agent - Adds local attractions and recommendations
local_agent = AssistantAgent(
    "local_agent",
    model_client=model_client,
    description="Suggests local attractions, food, and activities.",
    system_message="You are a local guide. Enhance the travel itinerary by adding local experiences, must-visit places, food recommendations, and hidden gems."
)

# 3️⃣ Language Tips Agent - Provides communication advice for travelers
language_agent = AssistantAgent(
    "language_agent",
    model_client=model_client,
    description="Provides language and communication tips.",
    system_message="You provide essential language and communication tips for the travel destination, including basic phrases, cultural etiquette, and important considerations."
)

# 4️⃣ Travel Summary Agent - Compiles all inputs into a final itinerary
travel_summary_agent = AssistantAgent(
    "travel_summary_agent",
    model_client=model_client,
    description="Summarizes the travel plan into a final itinerary.",
    system_message="You compile inputs from all agents into a well-structured, final travel plan. Your response must be a complete itinerary. Once done, respond with TERMINATE."
)

# ------------------------- API Function for Web Interface -------------------------
async def run_travel_planner(task: str):
    """
    Runs the travel planner with a specific task and captures only the final itinerary
    from the travel_summary_agent for the web interface.
    
    Args:
        task (str): The travel planning task (e.g., "Plan a 1-day trip to Hyderabad").
                    Must not be empty.
        
    Returns:
        list: A list containing a single dictionary with 'agent' and 'response' for the
              travel_summary_agent's final itinerary, with "TERMINATE" removed from the response.
        
    Raises:
        ValueError: If the task is empty or invalid.
        Exception: If an error occurs during agent execution.
    """
    if not task or not isinstance(task, str):
        raise ValueError("Task must be a non-empty string.")

    responses = []
    
    try:
        # Create a new group chat instance for each request
        termination = TextMentionTermination("TERMINATE")
        group_chat = RoundRobinGroupChat(
            [planner_agent, local_agent, language_agent, travel_summary_agent],
            termination_condition=termination
        )
        
        async for msg in group_chat.run_stream(task=task):
            # Debug: Print the message object and its attributes to find the agent name
            print(f"Debug: msg = {msg}, dir(msg) = {dir(msg)}")
            
            # Try to get the agent name from possible attributes or metadata
            agent_name = None
            if hasattr(msg, 'metadata') and isinstance(msg.metadata, dict):
                agent_name = msg.metadata.get('sender') or msg.metadata.get('agent')
            if not agent_name:
                agent_name = getattr(msg, 'source', None) or getattr(msg, 'sender', None) or getattr(msg, 'name', None)
            if not agent_name and hasattr(msg, 'agent'):
                agent_name = getattr(msg.agent, 'name', None)
            if not agent_name:
                agent_name = 'unknown'  # Fallback if all attempts fail
            
            # Get the response content
            agent_response = getattr(msg, 'content', 'No response available')
            
            # Only append the response if it’s from travel_summary_agent and contains TERMINATE
            if agent_name == 'travel_summary_agent' and 'TERMINATE' in agent_response:
                # Remove "TERMINATE" from the response
                clean_response = agent_response.replace('TERMINATE', '').strip()
                responses.append({
                    "agent": agent_name,
                    "response": clean_response
                })
                break  # Stop after capturing the final summary
    except Exception as e:
        responses.append({
            "agent": "error",
            "response": f"An error occurred: {str(e)}"
        })
    
    return responses

# ------------------------- Run the System (for testing locally) -------------------------
async def main():
    print("\n🚀 Starting AI-powered Travel Planning System...\n")
    # Create a new group chat for local testing
    termination = TextMentionTermination("TERMINATE")
    group_chat = RoundRobinGroupChat(
        [planner_agent, local_agent, language_agent, travel_summary_agent],
        termination_condition=termination
    )
    await Console(group_chat.run_stream(task="Plan a 3-day trip to San Francisco."))

# Run the event loop
if __name__ == "__main__":
    asyncio.run(main())