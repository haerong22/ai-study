import os
from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool
from google.adk.models.lite_llm import LiteLlm
from env import OPENAI_API_KEY, REPLICATE_API_TOKEN
from .prompt import DESCRIPTION, INSTRUCTION
from .sub_agents.content_planner.agent import content_planner_agent

os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
os.environ["REPLICATE_API_TOKEN"] = REPLICATE_API_TOKEN

root_agent = Agent(
    name="ShortsCreatorAgent",
    model=LiteLlm(model="openai/gpt-4o"),
    description=DESCRIPTION,
    instruction=INSTRUCTION,
    tools=[
        AgentTool(agent=content_planner_agent),
    ],
)