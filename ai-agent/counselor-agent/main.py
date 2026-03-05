from lina.agent import root_agent as lina_agent
from adk_chat import chat


ai_response = chat(agent=lina_agent, message="안녕? 너는 이름이 뭐야?")

print(ai_response)