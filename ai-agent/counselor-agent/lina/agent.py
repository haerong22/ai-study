import os
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from .prompt import INSTRUCTION
from env import OPENAI_API_KEY


os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

root_agent = Agent(
    name="lina_agent",
    instruction= INSTRUCTION,
    model=LiteLlm("openai/gpt-4o")
)
