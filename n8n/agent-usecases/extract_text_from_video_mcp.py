# 환경 변수 로드 - OpenAI API 키와 Notion API 키를 .env 파일에서 불러옵니다
from dotenv import load_dotenv

# .env 파일에서 환경 변수 로드
load_dotenv()

from typing_extensions import TypedDict
from langgraph.graph import StateGraph

# 워크플로우에서 사용할 상태 구조 정의
class AgentState(TypedDict):
    file_path: str      # 처리할 영상 파일 경로
    transcript: str     # Whisper로 추출한 텍스트
    outline: str        # 생성된 마크다운 아웃라인
    title: str          # 영상/문서 제목
    database_id: str    # Notion 데이터베이스 ID
    page_id: str        # 생성된 Notion 페이지 ID (2단계 업로드를 위해 추가)
    
# 상태 그래프 빌더 초기화
graph_builder = StateGraph(AgentState)

from langchain_openai import ChatOpenAI
from langchain_community.document_loaders.parsers.audio import OpenAIWhisperParser

# ChatGPT 모델 초기화 - 마크다운 아웃라인 생성에 사용
llm = ChatOpenAI(model="gpt-4o", temperature=0)  # temperature=0으로 설정하여 일관된 결과 생성

# Whisper 파서 초기화 - 음성/영상 파일에서 텍스트 추출에 사용
audio_parser = OpenAIWhisperParser()

from langchain_core.documents.base import Blob
from langchain_community.document_loaders.parsers.audio import OpenAIWhisperParser

def extract_transcript(state: AgentState) -> AgentState:
    """
    영상 파일에서 음성을 추출하여 텍스트로 변환하는 함수
    """
    # 상태에서 파일 경로 가져오기
    file_path = state["file_path"]
    
    # 파일을 Blob 객체로 변환 (Whisper가 처리할 수 있는 형태)
    audio_blob = Blob(path=file_path)
    
    # Whisper를 사용하여 음성을 텍스트로 변환
    documents = audio_parser.lazy_parse(audio_blob)
    
    # 변환된 텍스트들을 하나의 문자열로 결합
    transcript = ""
    for doc in documents:
        transcript += doc.page_content
    
    # 결과를 상태로 반환
    return {"transcript": transcript}

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# 아웃라인 생성용 모델 (더 정확한 결과를 위해 gpt-4o 사용)
llm = ChatOpenAI(model="gpt-4o", temperature=0)

def generate_outline(state: AgentState) -> AgentState:
    """
    추출된 텍스트를 바탕으로 구조화된 마크다운 아웃라인을 생성하는 함수
    """
    # 상태에서 트랜스크립트 가져오기
    transcript = state["transcript"]
    
    # 마크다운 아웃라인 생성을 위한 프롬프트 템플릿 설정
    outline_prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a helpful assistant that generates an outline for a transcript. 
Your outline must be in the markdown format using necessary headings and subheadings.
You can also use bullet points and numbered lists where you think necessary.
Make sure to use Korean when you generate the outline."""),
        ("user", "Generate an outline for the following transcript: {transcript}"),
    ])
    
    # 체인 구성: 프롬프트 -> LLM -> 문자열 파서
    outline_chain = outline_prompt | llm | StrOutputParser()
    
    # 마크다운 아웃라인 생성
    outline = outline_chain.invoke({"transcript": transcript})
    
    # 결과를 상태로 반환
    return {"outline": outline}

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# 아웃라인 생성용 모델 (더 정확한 결과를 위해 gpt-4o 사용)
llm = ChatOpenAI(model="gpt-4o", temperature=0)

def generate_outline(state: AgentState) -> AgentState:
    """
    추출된 텍스트를 바탕으로 구조화된 마크다운 아웃라인을 생성하는 함수
    """
    # 상태에서 트랜스크립트 가져오기
    transcript = state["transcript"]
    
    # 마크다운 아웃라인 생성을 위한 프롬프트 템플릿 설정
    outline_prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a helpful assistant that generates an outline for a transcript. 
Your outline must be in the markdown format using necessary headings and subheadings.
You can also use bullet points and numbered lists where you think necessary.
Make sure to use Korean when you generate the outline."""),
        ("user", "Generate an outline for the following transcript: {transcript}"),
    ])
    
    # 체인 구성: 프롬프트 -> LLM -> 문자열 파서
    outline_chain = outline_prompt | llm | StrOutputParser()
    
    # 마크다운 아웃라인 생성
    outline = outline_chain.invoke({"transcript": transcript})
    
    # 결과를 상태로 반환
    return {"outline": outline}

import os
from langchain_mcp_adapters.client import MultiServerMCPClient

# 환경 변수에서 Notion API 키 가져오기
notion_api_key = os.getenv("NOTION_API_KEY")

# MCP (Model Context Protocol) 클라이언트 설정
# Notion API와 통신하기 위한 다중 서버 MCP 클라이언트 생성
mcp_client = MultiServerMCPClient({
  "notionApi": {
      "command": "npx",                                    
      "args": ["-y", "@notionhq/notion-mcp-server"],      # Notion MCP 서버 패키지 실행 (자동 설치)
      "env": {                                             # 환경 변수 설정
        "OPENAPI_MCP_HEADERS": f"{{\"Authorization\": \"Bearer {notion_api_key}\", \"Notion-Version\": \"2022-06-28\" }}"
      },
      "transport": "stdio"                                 # 표준 입출력을 통한 통신
    }  
})

# MCP 클라이언트에서 사용 가능한 도구 목록 가져오기 (비동기 함수)
# 이 도구들은 ReAct 에이전트가 Notion API와 상호작용하는 데 사용됩니다
tool_list = mcp_client.get_tools()

from langgraph.prebuilt import create_react_agent

# ReAct 에이전트 생성
# 이 에이전트는 추론(Reasoning)과 행동(Acting)을 결합하여 복잡한 작업을 수행
agent = create_react_agent(
    model=llm,                                                    # 사용할 언어 모델
    tools=tool_list,                                             # MCP에서 가져온 도구 목록
    prompt="Use the tools provided to you to answer the user's question"  # 에이전트에게 주는 기본 지시사항
)

async def process_stream(stream_generator):
    """
    에이전트의 실행 과정을 실시간으로 모니터링하고 결과를 수집하는 함수
    """
    results = []  # 모든 결과를 저장할 리스트
    try:
        # 스트림 생성기에서 청크 단위로 데이터를 비동기적으로 처리
        async for chunk in stream_generator:
            # 각 청크에서 첫 번째 키를 가져와 메시지 타입 확인
            key = list(chunk.keys())[0]
            
            if key == 'agent':
                # Agent 메시지의 내용을 가져옴. 메시지가 비어있는 경우 어떤 도구를 어떻게 호출할지 정보를 가져옴
                content = chunk['agent']['messages'][0].content if chunk['agent']['messages'][0].content != '' else chunk['agent']['messages'][0].additional_kwargs
                print(f"'agent': '{content}'")
            
            elif key == 'tools':
                # 도구 메시지의 내용을 가져옴 (도구 실행 결과)
                for tool_msg in chunk['tools']['messages']:
                    print(f"'tools': '{tool_msg.content}'")
            
            # 모든 청크를 결과 리스트에 추가
            results.append(chunk)
        return results
    except Exception as e:
        print(f"Error processing stream: {e}")
        return results
    
import requests
import os

def create_notion_page(state: AgentState) -> AgentState:
    """
    Notion 데이터베이스에 새로운 페이지를 생성하는 함수 (2단계 업로드의 첫 번째 단계)
    """
    # 상태에서 필요한 정보 가져오기
    database_id = state['database_id']  # Notion 데이터베이스 ID
    title = state['title']              # 페이지 제목
    
    # 환경 변수에서 Notion API 키 가져오기
    notion_api_key = os.getenv("NOTION_API_KEY")
    
    # Notion API 요청 헤더 설정
    headers = {
        'Authorization': f'Bearer {notion_api_key}',
        'Content-Type': 'application/json',
        'Notion-Version': '2022-06-28'  # Notion API 버전 지정
    }
    
    # 새 페이지 생성을 위한 데이터 구성 (제목만 포함)
    data = {
        'parent': {'database_id': database_id},  # 부모 데이터베이스 지정
        'properties': {
            'Title': {'title': [{'text': {'content': title}}]},  # 페이지 제목 설정
        },
    }
    
    # Notion API에 페이지 생성 요청
    response = requests.post(
        'https://api.notion.com/v1/pages',
        headers=headers,
        json=data
    )
    
    # 응답 결과 출력
    print(response.json())
    
    # 생성된 페이지 ID를 상태로 반환 (두 번째 단계에서 사용)
    return {'page_id': response.json()['id']}

from langchain_core.messages import HumanMessage
from langchain_core.prompts import PromptTemplate

async def upload_to_notion(state: AgentState) -> AgentState:
    """
    생성된 Notion 페이지에 마크다운 아웃라인을 구조화된 블록으로 업로드하는 함수
    ReAct 에이전트를 활용하여 지능적으로 내용을 업로드
    """
    # 상태에서 필요한 정보 가져오기
    page_id = state['page_id']    # 첫 번째 단계에서 생성된 페이지 ID
    outline = state['outline']    # 생성된 마크다운 아웃라인
    
    # 에이전트에게 전달할 메시지 템플릿 생성
    human_message_prompt = PromptTemplate.from_template("""Add block to the page of which id is {page_id}
and add the outline as children blocks to the page. 
Make sure to follow the format of the outline which is in markdown format
When you use headings, make sure to follow the format below:
{{
  //...other keys excluded
  "type": "heading_1", # heading_1, heading_2, heading_3
  //...other keys excluded
  "heading_1": {{
    "rich_text": [{{
      "type": "text",
      "text": {{
        "content": "Lacinato kale",
        "link": null
      }}
    }}],
    "color": "default",
    "is_toggleable": false
  }}
}}

The outline is as follows: 
{outline}""")
    
    # 템플릿을 사용하여 실제 메시지 생성
    human_message = human_message_prompt.format(page_id=page_id, outline=outline)
    
    # 에이전트에 메시지를 전달하고 스트림 모드로 실행
    stream_generator = agent.astream({"messages": [HumanMessage(human_message)]}, stream_mode="updates")
    
    # 스트림을 처리하여 모든 결과 수집
    all_chunks = await process_stream(stream_generator)

    # 최종 결과 출력
    if all_chunks:
        final_result = all_chunks[-1]
        print("\nFinal result:", final_result)

# 워크플로우 그래프에 노드 추가
graph_builder.add_node(extract_transcript)    # 트랜스크립트 추출 노드
graph_builder.add_node(generate_outline)      # 마크다운 아웃라인 생성 노드
graph_builder.add_node(create_notion_page)    # Notion 페이지 생성 노드 (1단계)
graph_builder.add_node(upload_to_notion)      # Notion 콘텐츠 업로드 노드 (2단계)


from langgraph.graph import START, END

# 워크플로우 실행 순서 정의 (엣지 연결)
graph_builder.add_edge(START, 'extract_transcript')                          # 시작 → 트랜스크립트 추출
graph_builder.add_edge('extract_transcript', 'generate_outline')             # 트랜스크립트 추출 → 마크다운 아웃라인 생성
graph_builder.add_edge('generate_outline', 'create_notion_page')             # 아웃라인 생성 → Notion 페이지 생성
graph_builder.add_edge('create_notion_page', 'upload_to_notion')             # 페이지 생성 → 콘텐츠 업로드
graph_builder.add_edge('upload_to_notion', END)                              # 콘텐츠 업로드 → 종료

# 그래프 컴파일 (실행 가능한 상태로 변환)
graph = graph_builder.compile()

# 워크플로우 비동기 실행
# 영상 파일 경로, Notion 데이터베이스 ID, 제목을 설정하여 전체 프로세스 실행
graph.ainvoke({
    "file_path": "./videos/news.mp4",           # 처리할 영상 파일 경로
    "database_id": "22fe40c477c5806798a7f51edc0ab976",          # Notion 데이터베이스 ID
    "title": "뉴스 스크랩 에이전트"                      # 페이지 제목
})