import os
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent

load_dotenv()

github_pat = os.getenv("GITHUB_PAT")
slack_bot_token = os.getenv("SLACK_BOT_TOKEN")
slack_team_id = os.getenv("SLACK_TEAM_ID")
slack_channel_ids = os.getenv("SLACK_CHANNEL_IDS")

mcp_client = MultiServerMCPClient({
    "github": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-e",
        "GITHUB_TOOLSETS",
        "-e",
        "GITHUB_PERSONAL_ACCESS_TOKEN",
        "ghcr.io/github/github-mcp-server"
      ],
      "env": {
        "GITHUB_TOOLSETS": "context,pull_requests",
        "GITHUB_PERSONAL_ACCESS_TOKEN": github_pat
      },
      "transport": "stdio"
    },
     "slack": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-e",
        "SLACK_BOT_TOKEN",
        "-e",
        "SLACK_TEAM_ID",
        "-e",
        "SLACK_CHANNEL_IDS",
        "mcp/slack"
      ],
      "env": {
        "SLACK_BOT_TOKEN": slack_bot_token,
        "SLACK_TEAM_ID": slack_team_id,
        "SLACK_CHANNEL_IDS": slack_channel_ids # ,로 구분된 문자열
      },
      "transport": "stdio"
    }
})

tool_list = mcp_client.get_tools()

agent = create_react_agent(
    model="openai:gpt-4.1",
    tools=tool_list,
    prompt="Use the tools provided to you to answer the user's question"
)

async def process_stream(stream_generator):
    results = []
    try:
        async for chunk in stream_generator:

            key = list(chunk.keys())[0]
            if key == 'agent':
                # Agent 메시지의 내용을 가져옴. 메세지가 비어있는 경우 어떤 도구를 어떻게 호출할지 정보를 가져옴
                content = chunk['agent']['messages'][0].content if chunk['agent']['messages'][0].content != '' else chunk['agent']['messages'][0].additional_kwargs
                print(f"'agent': '{content}'")
            
            elif key == 'tools':
                # 도구 메시지의 내용을 가져옴
                for tool_msg in chunk['tools']['messages']:
                    print(f"'tools': '{tool_msg.content}'")
            
            results.append(chunk)
        return results
    except Exception as e:
        print(f"Error processing stream: {e}")
        return results

human_message = """깃헙의 Pull Request를 확인하고 코드 리뷰를 작성해주세요. 
PR의 코드를 리뷰한 후에, 아래 항목을 확인해주세요;
1. 코드가 개선되었는지
2. 예측하지 못한 side effect가 있는지
3. 보안상 문제가 될 수 있는 부분이 없는지

위 내용을 확인해서 PR에 코멘트로 남겨주세요.
그리고 코멘트를 남긴 후에, 슬랙 채널에도 메세지를 전송해서 엔지니어에게 알려주세요
"""

stream_generator = agent.astream({"messages": [HumanMessage(human_message)]}, stream_mode="updates")

all_chunks = process_stream(stream_generator)


if all_chunks:
    final_result = all_chunks[-1]
    print("\nFinal result:", final_result)