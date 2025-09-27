# 환경 변수 로드 - OpenAI API 키와 Notion API 키를 .env 파일에서 불러옵니다
from dotenv import load_dotenv

# .env 파일에서 환경 변수 로드 (OpenAI API 키, Notion API 키 등)
load_dotenv()

from typing_extensions import TypedDict
from langgraph.graph import StateGraph

# 워크플로우에서 사용할 고급 상태 구조 정의
class AgentState(TypedDict):
    url: str           # YouTube 영상 URL
    transcript: str    # Whisper로 추출한 텍스트
    outline: str       # 생성된 마크다운 아웃라인
    title: str         # 영상/문서 제목
    database_id: str   # Notion 데이터베이스 ID
    page_id: str       # 생성된 Notion 페이지 ID
    save_dir: str      # 다운로드한 영상 파일 저장 경로
    
# 상태 그래프 빌더 초기화
graph_builder = StateGraph(AgentState)

from langchain_openai import ChatOpenAI
from langchain_community.document_loaders.parsers.audio import OpenAIWhisperParser
from langchain_community.document_loaders.blob_loaders.youtube_audio import (
    YoutubeAudioLoader,  # YouTube 영상 오디오 다운로더
)
from langchain_community.document_loaders.generic import GenericLoader  # 범용 로더

# ChatGPT 모델 초기화 - 텍스트 요약과 아웃라인 생성에 사용
llm = ChatOpenAI(model="gpt-4o", temperature=0)  # 더 높은 품질의 결과를 위해 gpt-4o 사용

from langchain_core.documents.base import Blob
from langchain_community.document_loaders.parsers.audio import OpenAIWhisperParser

def extract_transcript(state: AgentState) -> AgentState:
    """
    YouTube URL에서 영상을 다운로드하고 음성을 텍스트로 변환하는 함수
    """
    # 상태에서 YouTube URL과 저장 경로 가져오기
    url = state["url"]
    save_dir = state["save_dir"]
    
    # YouTube 오디오 다운로더와 Whisper 파서를 결합한 로더 생성
    loader = GenericLoader(
        YoutubeAudioLoader([url], save_dir),  # YouTube 영상 다운로드
        OpenAIWhisperParser()                 # Whisper를 사용한 음성-텍스트 변환
    )
    
    # 변환된 텍스트들을 하나의 문자열로 결합
    transcript = ""
    documents = loader.load()
    for doc in documents:
        transcript += doc.page_content
    
    # 결과를 상태로 반환
    return {"transcript": transcript}


from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# 아웃라인 생성용 모델 (고품질 결과를 위해 gpt-4o 사용)
llm = ChatOpenAI(model="gpt-4o", temperature=0)

def generate_outline(state: AgentState) -> AgentState:
    """
    추출된 텍스트를 바탕으로 구조화된 마크다운 형식의 한국어 아웃라인을 생성하는 함수
    """
    # 상태에서 트랜스크립트 가져오기
    transcript = state["transcript"]
    
    # 마크다운 형식의 아웃라인 생성을 위한 프롬프트 템플릿 설정
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

# MCP 클라이언트 설정 - Notion API와의 고급 상호작용을 위한 프로토콜
mcp_client = MultiServerMCPClient({
  "notionApi": {
      "command": "npx",  # Node.js 패키지 실행 명령
      "args": ["-y", "@notionhq/notion-mcp-server"],  # Notion MCP 서버 패키지 실행
      "env": {
        # OpenAPI MCP 헤더 설정 (인증 정보 포함)
        "OPENAPI_MCP_HEADERS": f"{{\"Authorization\": \"Bearer {notion_api_key}\", \"Notion-Version\": \"2022-06-28\" }}"
      },
      "transport": "stdio"  # 표준 입출력을 통한 통신
    }  
})

# MCP 클라이언트에서 사용 가능한 도구 목록 가져오기
# 이 도구들은 Notion API와의 상호작용에 사용됩니다
tool_list = mcp_client.get_tools()

from langgraph.prebuilt import create_react_agent

# ReAct 에이전트 생성 - 복잡한 작업을 위한 추론과 행동을 반복하는 에이전트
agent = create_react_agent(
    model=llm,       # 사용할 언어 모델
    tools=tool_list, # MCP에서 가져온 도구 목록
    prompt="Use the tools provided to you to answer the user's question"  # 에이전트의 기본 프롬프트
)

async def process_stream(stream_generator):
    """
    에이전트 실행 중 생성되는 스트림을 처리하는 함수
    실시간으로 에이전트의 행동과 도구 사용을 추적합니다
    """
    results = []
    try:
        # 스트림에서 각 청크를 비동기적으로 처리
        async for chunk in stream_generator:
            # 청크에서 첫 번째 키 가져오기
            key = list(chunk.keys())[0]
            
            if key == 'agent':
                # Agent 메시지의 내용을 가져옴. 메세지가 비어있는 경우 어떤 도구를 어떻게 호출할지 정보를 가져옴
                content = chunk['agent']['messages'][0].content if chunk['agent']['messages'][0].content != '' else chunk['agent']['messages'][0].additional_kwargs
                print(f"'agent': '{content}'")
            
            elif key == 'tools':
                # 도구 메시지의 내용을 가져옴
                for tool_msg in chunk['tools']['messages']:
                    print(f"'tools': '{tool_msg.content}'")
            
            # 결과에 청크 추가
            results.append(chunk)
        return results
    except Exception as e:
        print(f"Error processing stream: {e}")
        return results
    

import requests
import os

def create_notion_page(state: AgentState) -> AgentState:
    """
    Notion 데이터베이스에 새로운 페이지를 생성하는 함수
    직접적인 API 호출을 사용하여 제목만 설정된 빈 페이지를 생성합니다
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
    
    # 새 페이지 생성을 위한 데이터 구성
    data = {
        'parent': {'database_id': database_id},  # 부모 데이터베이스 지정
        'properties': {
            'Title': {'title': [{'text': {'content': title}}]},  # 페이지 제목만 설정
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
    
    # 생성된 페이지 ID를 상태로 반환
    return {'page_id': response.json()['id']}


from langchain_core.messages import HumanMessage
from langchain_core.prompts import PromptTemplate

async def upload_to_notion(state: AgentState) -> AgentState:
    """
    생성된 Notion 페이지에 마크다운 형식의 아웃라인을 구조화된 블록으로 추가하는 함수
    ReAct 에이전트와 MCP를 사용하여 복잡한 작업을 수행합니다
    """
    # 상태에서 필요한 정보 가져오기
    page_id = state['page_id']  # 이전 단계에서 생성된 페이지 ID
    outline = state['outline']  # 생성된 마크다운 아웃라인
    
    # 에이전트에게 전달할 메시지 프롬프트 템플릿 생성
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
    
    # 프롬프트 템플릿에 페이지 ID와 아웃라인 내용 삽입
    human_message = human_message_prompt.format(page_id=page_id, outline=outline)
    
    # 에이전트 실행 - 비동기 스트림 모드로 실행
    stream_generator = agent.astream({"messages": [HumanMessage(human_message)]}, stream_mode="updates")
    
    # 스트림 처리 함수를 사용하여 실행 과정 추적
    all_chunks = await process_stream(stream_generator)

    # 최종 결과 출력
    if all_chunks:
        final_result = all_chunks[-1]
        print("\nFinal result:", final_result)


# 워크플로우 그래프에 노드 추가
graph_builder.add_node(extract_transcript)   # YouTube 트랜스크립트 추출 노드
graph_builder.add_node(generate_outline)     # 마크다운 아웃라인 생성 노드
graph_builder.add_node(create_notion_page)   # Notion 페이지 생성 노드
graph_builder.add_node(upload_to_notion)     # Notion 콘텐츠 업로드 노드


from langgraph.graph import START, END

# 워크플로우 실행 순서 정의 (엣지 연결) - 4단계 워크플로우
graph_builder.add_edge(START, 'extract_transcript')                    # 시작 → YouTube 트랜스크립트 추출
graph_builder.add_edge('extract_transcript', 'generate_outline')       # 트랜스크립트 추출 → 마크다운 아웃라인 생성
graph_builder.add_edge('generate_outline', 'create_notion_page')       # 아웃라인 생성 → Notion 페이지 생성
graph_builder.add_edge('create_notion_page', 'upload_to_notion')       # 페이지 생성 → 콘텐츠 업로드
graph_builder.add_edge('upload_to_notion', END)                        # 콘텐츠 업로드 → 종료

# 그래프 컴파일 (실행 가능한 상태로 변환)
graph = graph_builder.compile()


# 워크플로우 실행 - 비동기 방식으로 실행
# YouTube 영상 URL, Notion 데이터베이스 ID, 제목, 저장 경로를 설정하여 전체 프로세스 실행
graph.ainvoke({
    "url": "https://youtu.be/JYZuZRADCBc?si=oH9UGl-_eLLrzecZ",  # 처리할 YouTube 영상 URL
    "database_id": "22fe40c477c5806798a7f51edc0ab976",         # Notion 데이터베이스 ID
    "title": "RAG란 무엇인가?",                                    # 페이지 제목
    "save_dir": "./videos"                                      # 다운로드한 영상 파일 저장 경로
})