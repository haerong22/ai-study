from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm


content_planner_agent = Agent(
    name="ContentPlannerAgent",
    model=LiteLlm(model="openai/gpt-4o"),
    description="",
    instruction="",
)