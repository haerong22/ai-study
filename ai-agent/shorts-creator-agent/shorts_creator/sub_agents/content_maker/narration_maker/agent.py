from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm


narration_maker_agent = Agent(
    name="NarrationMakerAgent",
    model=LiteLlm(model="openai/gpt-4o"),
    description="",
    instruction="",
)