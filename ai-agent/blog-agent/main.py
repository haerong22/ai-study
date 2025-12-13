import os
from typing import List
from pydantic import BaseModel
from crewai.flow.flow import Flow, listen, start, router, or_
from crewai.agent import LiteAgentOutput
from crewai import Agent, Task, Crew, LLM
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