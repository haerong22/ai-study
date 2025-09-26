import requests
import os
from dotenv import load_dotenv
from typing_extensions import TypedDict
from langgraph.graph import StateGraph
from langgraph.graph import START, END
from langchain_openai import ChatOpenAI
from langchain_community.document_loaders.parsers.audio import OpenAIWhisperParser
from langchain_core.documents.base import Blob
from langchain_community.document_loaders.parsers.audio import OpenAIWhisperParser
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


load_dotenv()

# 워크플로우에서 사용할 상태 구조 정의
class AgentState(TypedDict):
    file_path: str      # 처리할 영상 파일 경로
    transcript: str     # Whisper로 추출한 텍스트
    outline: str        # 생성된 아웃라인
    title: str          # 영상/문서 제목
    database_id: str    # Notion 데이터베이스 ID
    
# 상태 그래프 빌더 초기화
graph_builder = StateGraph(AgentState)

# ChatGPT 모델 초기화 - 텍스트 요약과 아웃라인 생성에 사용
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)  # temperature=0으로 설정하여 일관된 결과 생성

# Whisper 파서 초기화 - 음성/영상 파일에서 텍스트 추출에 사용
audio_parser = OpenAIWhisperParser()

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

# 아웃라인 생성용 모델 (더 정확한 결과를 위해 gpt-4o 사용)
llm = ChatOpenAI(model="gpt-4o", temperature=0)

def generate_outline(state: AgentState) -> AgentState:
    """
    추출된 텍스트를 바탕으로 한국어 아웃라인을 생성하는 함수
    """
    # 상태에서 트랜스크립트 가져오기
    transcript = state["transcript"]
    
    # 아웃라인 생성을 위한 프롬프트 템플릿 설정
    outline_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant that generates an outline for a transcript. Make sure to use Korean when you generate the outline."),
        ("user", "Generate an outline for the following transcript: {transcript}"),
    ])
    
    # 체인 구성: 프롬프트 -> LLM -> 문자열 파서
    outline_chain = outline_prompt | llm | StrOutputParser()
    
    # 아웃라인 생성
    outline = outline_chain.invoke({"transcript": transcript})
    
    # 결과를 상태로 반환
    return {"outline": outline}

def upload_to_notion(state: AgentState) -> AgentState:
    """
    생성된 아웃라인을 Notion 데이터베이스에 업로드하는 함수
    """
    # 상태에서 필요한 정보 가져오기
    database_id = state['database_id']  # Notion 데이터베이스 ID
    title = state['title']              # 페이지 제목
    outline = state['outline']          # 생성된 아웃라인
    
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
            'Title': {'title': [{'text': {'content': title}}]},  # 페이지 제목 설정
        },
        'children': [
            {
                'object': 'block',
                'type': 'paragraph',
                'paragraph': {'rich_text': [{'type': 'text', 'text': {'content': outline}}]},  # 아웃라인 내용 추가
            }
        ]
    }
    
    # Notion API에 페이지 생성 요청
    response = requests.post(
        'https://api.notion.com/v1/pages',
        headers=headers,
        json=data
    )
    
    # 응답 결과 출력
    print(response.json())
    return {}

# 워크플로우 그래프에 노드 추가
graph_builder.add_node(extract_transcript)  # 트랜스크립트 추출 노드
graph_builder.add_node(generate_outline)    # 아웃라인 생성 노드
graph_builder.add_node(upload_to_notion)    # Notion 업로드 노드

# 워크플로우 실행 순서 정의 (엣지 연결)
graph_builder.add_edge(START, 'extract_transcript')                   # 시작 → 트랜스크립트 추출
graph_builder.add_edge('extract_transcript', 'generate_outline')      # 트랜스크립트 추출 → 아웃라인 생성
graph_builder.add_edge('generate_outline', 'upload_to_notion')        # 아웃라인 생성 → Notion 업로드
graph_builder.add_edge('upload_to_notion', END)                       # Notion 업로드 → 종료

# 그래프 컴파일 (실행 가능한 상태로 변환)
graph = graph_builder.compile()

graph.invoke({
    "file_path": "./videos/news.mp4",  # 처리할 영상 파일 경로
    "database_id": "277fc9ac714c806a9cc6ecb2f24bf7cc",  # Notion 데이터베이스 ID
    "title": "영상 요약"                      # 페이지 제목
})