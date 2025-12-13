import os
from typing import List
from pydantic import BaseModel
from crewai.flow.flow import Flow, listen, start, router, or_
from crewai.agent import LiteAgentOutput
from crewai import Agent, Task, Crew, LLM
from crewai.project import CrewBase, agent, task, crew
from env import OPENAI_API_KEY
from tools import web_search_tool

os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY


class Post(BaseModel):
    title: str
    content: str
    hashtag: List[str]

class ScoreManager(BaseModel):
    score: int = 0
    reason: str = ""


class BlogContentMakerState(BaseModel):
    topic: str = ""
    max_length: int = 1000
    research_data: LiteAgentOutput | None = None
    score_manager: ScoreManager | None = None
    post: Post | None = None

@CrewBase
class SEOManagerCrew:

    @agent
    def seo_agent(self):
        return Agent(
            role="SEO 전문가",
            goal="블로그 게시물의 SEO 효율성을 엄격하고 정확하게 평가하여 검색 엔진 최적화 품질을 측정합니다. 각 평가 요소에 대해 구체적이고 실용적인 피드백을 제공하며, 객관적인 기준에 따라 정확한 점수를 산출합니다.",
            backstory="""
            당신은 10년 이상의 경력을 가진 SEO 전문 컨설턴트로, 구글 알고리즘 변화와 검색 트렌드에 정통합니다.
            키워드 밀도, 제목 최적화, 콘텐츠 구조화, 사용자 의도 분석, 가독성 평가 등 모든 SEO 요소를 체계적으로 분석합니다.
            데이터 기반의 정확한 평가를 통해 콘텐츠가 검색 결과에서 상위 랭킹을 달성할 수 있도록 구체적이고 실행 가능한 개선안을 제시합니다.
            """,
            llm="openai/o4-mini",
            verbose=True,
        )

    @task
    def check_seo_task(self):
        return Task(
            description="""
            주어진 블로그 게시물을 다음 SEO 기준으로 종합 분석하여 정확한 점수와 개선 방안을 제시하세요:

            ## 평가 기준 (각 항목별 세부 분석 필수):
            1. **키워드 최적화 (25점)**
               - 타겟 키워드의 자연스러운 배치와 밀도
               - 제목, 소제목, 본문 내 키워드 활용도
               - 관련 키워드 및 동의어 사용

            2. **제목 및 구조 최적화 (25점)**
               - 제목의 검색 친화성과 클릭 유도성
               - 헤딩 태그(H1, H2, H3) 구조화
               - 논리적 콘텐츠 흐름

            3. **콘텐츠 품질 및 길이 (25점)**
               - 정보의 정확성과 유용성
               - 적절한 콘텐츠 길이와 깊이
               - 독창성과 가치 제공

            4. **사용자 경험 및 가독성 (25점)**
               - 문장 길이와 가독성
               - 단락 구성과 시각적 구조
               - 검색 의도와의 일치도

            ## 출력 요구사항:
            - **총점**: 0-100점 (각 항목별 점수 합산)
            - **상세 분석**: 각 평가 기준별 현재 상태와 구체적 개선점
            - **우선순위**: 가장 중요한 개선 영역 3가지
            - **실행 가능한 개선안**: 구체적이고 즉시 적용 가능한 방법

            분석 대상 게시물: {post}
            타겟 주제: {topic}
            """,
            expected_output="""
            다음을 포함하는 Score 객체:
            - score: SEO 품질을 평가하는 0-100 사이의 정수
            - reason: 점수에 영향을 미치는 주요 요인을 설명하는 문자열
            """,
            agent=self.seo_agent(),
            output_pydantic=ScoreManager,
        )

    @crew
    def crew(self):
        return Crew(
            agents=[self.seo_agent()], tasks=[self.check_seo_task()], verbose=True
        )

class BlogContentMarkerFlow(Flow):

    @start()
    def init_make_blog_content(self):
        if self.state.topic == "":
            raise ValueError("주제는 비워둘 수 없습니다.")
        

    @listen(init_make_blog_content)
    def research_by_topic(self):
        researcher = Agent(
            role="수석 연구원",
            backstory="당신은 다양한 분야의 전문 데이터베이스와 최신 트렌드에 정통한 전문 리서처입니다. 과학적 연구 방법론을 기반으로 신뢰성 높은 정보를 수집하고, 복잡한 데이터를 읽기 쉽게 정리하여 핵심 인사이트를 추출하는 능력을 갖추고 있습니다.",
            goal=f"{self.state.topic}에 대한 최신 트렌드, 과학적 근거, 실용적 활용 방안을 종합적으로 조사하여 독자에게 가치 있는 인사이트를 제공하세요.",
            tools=[web_search_tool],
            llm="openai/o4-mini",
        )

        self.state.research_data = researcher.kickoff(
            f"""
            '{self.state.topic}' 주제에 대해 다음 요소들을 중심으로 종합적인 리서치를 수행하세요:

            1. **최신 동향 및 트렌드**: 최근 1년 내 주요 발전 사항
            2. **과학적/기술적 근거**: 신뢰성 있는 연구 데이터나 전문가 의견
            3. **실용적 적용 사례**: 실제 활용 방법이나 사례 연구
            4. **미래 전망**: 향후 발전 방향이나 예상 대안
            5. **일반인을 위한 설명**: 전문용어를 쉽게 설명할 수 있는 자료

            각 정보는 출처와 신뢰도를 포함하여 제공해 주세요.
            """
        )

    @listen(or_(research_by_topic, "remake"))
    def handle_make_blog(self):
        pass

    @listen(handle_make_blog)
    def manage_seo(self):
        pass

    @router(manage_seo)
    def manage_score_router(self):

        if self.state.score_manager.score >= 70:
            return None
        
        else:
            return "remake"
        
flow = BlogContentMarkerFlow()

flow.kickoff(inputs={"topic": "AI 로보틱스"})

flow.plot()