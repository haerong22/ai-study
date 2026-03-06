import os
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from .prompt import INSTRUCTION
from env import OPENAI_API_KEY

from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.genai import types


os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

username = "bobby"
formatted_instruction = INSTRUCTION.format(username=username)


def before_model_callback(callback_context: CallbackContext, llm_request: LlmRequest):
    user_message = llm_request.contents[-1]
    if user_message and user_message.parts and user_message.role == "user":
        text = str(user_message.parts[0].text)
        if "nudy" in text:
            return LlmResponse(
                content=types.Content(
                    parts=[types.Part(text="그런 말은 내가 대응 못해")], role="model"
                )
            )
    return None


root_agent = Agent(
    name="lina_agent",
    instruction=formatted_instruction,
    model=LiteLlm("openai/gpt-4o"),
    before_model_callback=before_model_callback,
)