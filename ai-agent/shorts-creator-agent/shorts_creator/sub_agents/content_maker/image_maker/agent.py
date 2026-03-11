from google.adk.agents import Agent, SequentialAgent
from google.adk.models.lite_llm import LiteLlm


image_maker_agent = Agent(
    name="ImageMakerAgent",
    model=LiteLlm(model="openai/gpt-4o"),
    description="",
    instruction="",
)