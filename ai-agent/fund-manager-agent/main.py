import os
from typing import Optional
from pydantic import BaseModel
from crewai.flow.flow import Flow, listen, start, router, or_
from crewai import Crew, Task, CrewOutput
from crewai.agent import Agent
from env import OPENAI_API_KEY
from tools import web_search_tool, yahoo_finance_tool


os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY


class FundManagerState(BaseModel):

    # 사용자 inputs
    investment_goal: str = ""  # 사용자의 투자 목표
    risk_preference: str = ""  # 사용자의 투자 성향 (보수적, 공격적)
    budget: float = 0.0  # 사용자의 예산

    # 라우터의 의사결정
    strategy_type: str = ""

    # 분석 결과들
    tech_trends: Optional[CrewOutput] = None
    growth_scores: Optional[CrewOutput] = None
    stability_scores: Optional[CrewOutput] = None
    divide_scores: Optional[CrewOutput] = None

    portfolio: Optional[CrewOutput] = None


class FundManagerFlow(Flow[FundManagerState]):

    @start()
    def init_fund_analysis(self):
        if not self.state.investment_goal:
            raise ValueError("투자 목표를 입력해주세요")
        if not self.state.risk_preference:
            raise ValueError("투자 성향을 입력해주세요")
        if not self.state.budget:
            raise ValueError("예산을 입력해주세요")

    @listen(init_fund_analysis)
    def analyze_investment_strategy(self):
        """사용자 목표 분석"""

        strategy_router = Agent(
            role="투자 전략 라우터",
            backstory="투자 전문가로서 고객의 투자 목표와 성향을 정확히 파악하여 최적의 투자 전략팀에게 분석을 위임하는 것이 전문입니다.",
            goal="사용자의 투자 목표를 분석하여 성장주 투자인지 가치/배당주 투자인지 결정한다.",
            llm="openai/o4-mini",
        )

        analysis_result = strategy_router.kickoff(
            f"""
            사용자 투자 정보를 분석해주세요:
            - 투자 목표: {self.state.investment_goal}
            - 투자 성향: {self.state.risk_preference}
            - 투자 예산: ${self.state.budget:,.0f}

            투자 목표와 성향을 분석하여 다음 중 하나를 선택해주세요:
            1. 'growth' - 성장주 중심 투자 전략 (기술, 혁신, AI 등)
            2. 'value' - 가치/배당주 중심 투자 전략 (안정, 배당, 보수적 등)

            결과는 반드시 'growth' 또는 'value' 중 하나만 답해주세요.
            """
        )

        # Agent 결과에서 전략 추출
        analysis_text = str(analysis_result).lower()
        if "growth" in analysis_text:
            self.state.strategy_type = "growth"
        else:
            self.state.strategy_type = "value"

    @router(analyze_investment_strategy)
    def strategy_router(self):
        if self.state.strategy_type == "growth":
            return "growth_analysis"
        elif self.state.strategy_type == "value":
            return "value_analysis"

    @listen("growth_analysis")
    def analyze_tech_trends(self):
        """기술 트렌드 분석가 - 성장주 분석팀 1단계"""

        # 단일 Agent 생성
        tech_analyst = Agent(
            role="기술 트렌드 및 기업 분석가",
            backstory="""
            글로벌 기술 시장의 최신 동향을 파악하고 투자 가치가 높은 기업을 발굴하는 전문가입니다.
            시장 리포트, 뉴스, 업계 분석을 통해 떠오르는 기술 분야와 관련 상장 기업을 종합적으로 분석합니다.
            """,
            goal="사용자의 투자 목표를 기반으로 기술 트렌드를 분석하고 투자 후보 기업을 식별하여 구조화된 데이터를 제공한다.",
            tools=[web_search_tool],
            verbose=True,
        )

        # Task 1: 기술 트렌드 조사
        trend_research_task = Task(
            description=f"""
            사용자 투자 목표: {self.state.investment_goal}
            투자 성향: {self.state.risk_preference}

            현재 시장에서 주목받는 기술 트렌드를 조사하세요:

            1. "2025년 주목할 기술 트렌드" 웹 검색
            2. "혁신 기술 투자 전망" 관련 정보 수집
            3. 사용자의 투자 목표에 가장 적합한 기술 분야 3-4개 선별
            4. 각 분야의 시장 규모, 성장률, 투자 전망 분석

            결과는 다음 형식으로 정리해주세요:
            - 섹터명과 성장 가능성
            - 주요 성장 동력
            - 투자 전망 요약
            """,
            agent=tech_analyst,
            expected_output="기술 트렌드 분석 보고서 (3-4개 주요 섹터 포함)",
        )

        # Task 2: 기업 발굴
        company_discovery_task = Task(
            description="""
            이전 트렌드 분석 결과를 바탕으로 투자 후보 기업을 발굴하세요:

            1. 각 기술 섹터마다 "섹터명 관련주", "섹터명 대장주" 키워드로 웹 검색
            2. 나스닥/NYSE 상장 기업 우선 선별 (각 섹터당 최대 3개)
            3. 티커 심볼과 정확한 회사명 확인
            4. 각 기업의 사업 모델, 기술적 우위, 시장 위치 파악

            결과는 섹터별로 정리해주세요:
            - 섹터명
            - 대표 기업들 (티커, 회사명, 사업 요약)
            - 경쟁 우위와 투자 매력 포인트
            """,
            agent=tech_analyst,
            expected_output="섹터별 투자 후보 기업 리스트",
            context=[trend_research_task],
        )

        # Task 3: 데이터 구조화
        data_structuring_task = Task(
            description="""
            앞선 분석 결과를 다음 단계에서 활용할 수 있도록 구조화하세요:

            다음 JSON 배열 형식으로 정확히 응답해주세요:
            [
                {{
                    "sector": "섹터명",
                    "companies": ["TICKER1", "TICKER2", "TICKER3"],
                    "growth_potential": "성장 가능성 평가",
                    "investment_rationale": "이 섹터에 투자해야 하는 이유"
                }}
            ]

            중요한 주의사항:
            - companies 배열에는 정확한 티커 심볼만 포함
            - 각 섹터당 최대 3개 기업
            - 실제 분석된 내용만 포함
            - 마크다운 코드 블록(```)을 사용하지 말고 순수한 JSON만 반환
            - JSON 앞뒤에 어떤 텍스트도 추가하지 마세요
            - 응답은 [ 로 시작하고 ] 로 끝나야 합니다
            """,
            agent=tech_analyst,
            expected_output="""A JSON array starting with [ and ending with ]. No markdown formatting, no code blocks, no additional text. Pure JSON only.""",
            context=[trend_research_task, company_discovery_task],
            output_file="output/analyze_tech_trends.json",
        )

        tech_analysis_crew = Crew(
            agents=[tech_analyst],
            tasks=[trend_research_task, company_discovery_task, data_structuring_task],
            verbose=True,
        )

        self.state.tech_trends = tech_analysis_crew.kickoff()

    @listen(analyze_tech_trends)
    def evaluate_growth_potential(self):
        """성장성 평가 분석가 - 성장주 분석팀 2단계"""

        growth_analyst = Agent(
            role="성장성 평가 전문 분석가",
            backstory="""
            기업의 재무 데이터와 시장 동향을 종합 분석하여 성장 잠재력을 정확히 평가하는 전문가입니다.
            매출 성장률, R&D 투자, 시장 경쟁력, 미래 수익성을 다각도로 분석하여 투자 가치를 정량화합니다.
            """,
            goal="기술 트렌드 분석 결과를 바탕으로 각 기업의 성장 잠재력을 평가하고 투자 우선순위를 제공한다.",
            tools=[web_search_tool, yahoo_finance_tool],
            verbose=True,
            llm="openai/o4-mini",
        )

        # Task 1: 기업 재무 분석
        financial_analysis_task = Task(
            description=f"""
            기술 트렌드 분석 결과: {self.state.tech_trends}

            각 후보 기업에 대해 성장성 관련 재무 지표를 분석하세요:

            1. Yahoo Finance 도구로 각 티커의 정확한 재무 데이터 수집 (P/E 비율, 매출 성장률, ROE 등)
            2. "기업명 재무실적" 웹 검색으로 최신 분기 실적 및 전망 정보 수집
            3. "기업명 R&D 투자" 검색으로 혁신 투자 현황 분석
            4. "기업명 시장 전망" 검색으로 미래 성장 가능성 평가

            Yahoo Finance 도구 사용법:
            - yahoo_finance_tool("NVDA") - NVIDIA 재무 데이터
            - yahoo_finance_tool("MSFT", "2y") - Microsoft 2년 데이터

            결과는 기업별로 정리해주세요:
            - 티커 심볼과 회사명
            - 매출 성장률 (YoY)
            - R&D 투자 비율 또는 투자 규모
            - 주요 성장 동력
            - 시장에서의 경쟁 우위
            """,
            agent=growth_analyst,
            expected_output="기업별 재무 분석 보고서 (성장성 지표 중심)",
        )

        # Task 2: 성장성 점수 산정
        growth_scoring_task = Task(
            description="""
            앞선 재무 분석 결과를 바탕으로 각 기업의 성장 잠재력을 평가하세요:

            평가 기준:
            1. 매출 성장률 (30% 가중치) - 높을수록 좋음
            2. R&D 투자 비율 (25% 가중치) - 지속적 혁신 능력
            3. 시장 점유율 및 경쟁력 (25% 가중치) - 시장 지배력
            4. 미래 성장 전망 (20% 가중치) - 산업 트렌드 적합성

            각 기업에 대해:
            - 성장 잠재력 점수 (1-10점 척도)
            - 점수 산정 근거
            - 주요 성장 동력
            - 투자 시 기대 효과
            """,
            agent=growth_analyst,
            expected_output="기업별 성장성 점수 및 평가 근거",
            context=[financial_analysis_task],
        )

        # Task 3: 결과 구조화
        growth_data_structuring_task = Task(
            description="""
            앞선 분석 결과를 다음 단계에서 활용할 수 있도록 구조화하세요:

            다음 JSON 배열 형식으로 정확히 응답해주세요:
            [
                {{
                    "ticker": "티커심볼",
                    "company": "회사명",
                    "growth_score": 9.2,
                    "growth_factors": [
                        "주요 성장 요인1",
                        "주요 성장 요인2"
                    ],
                    "financial_highlights": {{
                        "revenue_growth": "매출 성장률 정보",
                        "rd_investment": "R&D 투자 정보",
                        "market_position": "시장 위치 정보"
                    }},
                    "investment_rationale": "투자 근거 요약"
                }}
            ]

            중요한 주의사항:
            - growth_score는 숫자 형태 (소수점 1자리)
            - 실제 분석된 내용만 포함
            - 마크다운 코드 블록(```)을 사용하지 말고 순수한 JSON만 반환
            - JSON 앞뒤에 어떤 텍스트도 추가하지 마세요
            - 응답은 [ 로 시작하고 ] 로 끝나야 합니다
            """,
            agent=growth_analyst,
            expected_output="""A JSON array starting with [ and ending with ]. No markdown formatting, no code blocks, no additional text. Pure JSON only.""",
            context=[financial_analysis_task, growth_scoring_task],
            output_file="output/evaluate_growth_potential.json",
        )

        # Crew 생성 및 실행
        growth_analysis_crew = Crew(
            agents=[growth_analyst],
            tasks=[
                financial_analysis_task,
                growth_scoring_task,
                growth_data_structuring_task,
            ],
            verbose=True,
        )

        # Crew 실행
        self.state.growth_scores = growth_analysis_crew.kickoff()

    @listen("value_analysis")
    def screen_stable_companies(self):
        """안정성 스크리너 - 가치/배당주 분석팀 1단계"""

        stability_screener = Agent(
            role="안정성 스크리닝 전문 분석가",
            backstory="""
            재무적으로 안정되고 꾸준한 실적을 보이는 기업들을 선별하는 전문가입니다.
            부채 비율, 수익성, 배당 이력, 시장 지위를 종합적으로 분석하여 장기 투자에 적합한 안전한 기업들을 발굴합니다.
            """,
            goal="사용자의 보수적 투자 목표에 맞춰 재무적으로 안정되고 장기간 꾸준한 실적을 낸 기업들을 선별한다.",
            tools=[web_search_tool, yahoo_finance_tool],
            verbose=True,
            llm="openai/o4-mini",
        )

        # Task 1: 안정적 기업 발굴
        stable_company_discovery_task = Task(
            description=f"""
            사용자의 투자 목표: {self.state.investment_goal}
            투자 성향: {self.state.risk_preference}

            보수적 투자에 적합한 안정적인 기업들을 발굴하세요:

            1. "안정적인 배당주", "블루칩 주식", "S&P 500 대형주" 키워드로 웹 검색
            2. "저PER 가치주", "우량 배당주", "디펜시브 주식" 검색으로 후보 발굴
            3. 다음 섹터 우선 고려: 소비재, 유틸리티, 헬스케어, 금융
            4. 나스닥/NYSE 상장 기업 중 시가총액 상위 기업 선별

            결과는 다음 형식으로 정리해주세요:
            - 발굴된 기업들의 티커 심볼과 회사명
            - 각 기업이 속한 섹터
            - 안정성 근거 (업계 지위, 사업 모델 등)
            - 배당 지급 여부
            """,
            agent=stability_screener,
            expected_output="안정적 기업 후보 리스트 (티커별 기본 정보 포함)",
        )

        # Task 2: 재무 안정성 분석
        financial_stability_task = Task(
            description="""
            발굴된 기업들의 재무 안정성을 심층 분석하세요:

            1. Yahoo Finance 도구로 각 후보 기업의 재무 데이터 수집
            2. 다음 안정성 지표 중점 분석:
               - 부채비율 (Debt-to-Equity): 0.5 미만 선호
               - P/E 비율: 과도하지 않은 수준 (50 미만)
               - ROE: 일관된 수익성 (5% 이상)
               - 이익률: 안정적 영업이익률
               - 배당수익률: 지속가능한 배당

            3. "기업명 재무건전성" 웹 검색으로 추가 정보 수집
            4. "기업명 신용등급" 검색으로 신용도 확인

            Yahoo Finance 도구 활용:
            - yahoo_finance_tool("JNJ") - Johnson & Johnson 데이터
            - yahoo_finance_tool("KO") - Coca-Cola 데이터

            결과는 기업별로 정리해주세요:
            - 주요 재무 지표와 안정성 평가
            - 부채 수준과 수익성 분석
            - 배당 정책과 지속가능성
            """,
            agent=stability_screener,
            expected_output="기업별 재무 안정성 분석 보고서",
            context=[stable_company_discovery_task],
        )

        # Task 3: 안정성 점수 산정
        stability_scoring_task = Task(
            description="""
            재무 분석 결과를 바탕으로 각 기업의 안정성 점수를 산정하세요:

            평가 기준:
            1. 재무 건전성 (35% 가중치) - 부채비율, 유동비율, 이자보상배수
            2. 수익 안정성 (30% 가중치) - 꾸준한 영업이익, ROE 일관성
            3. 배당 정책 (20% 가중치) - 배당 지속성, 배당성장률
            4. 시장 지위 (15% 가중치) - 업계 선도, 브랜드 파워

            각 기업에 대해:
            - 안정성 점수 (1-10점 척도)
            - 점수 산정 근거
            - 주요 안정 요소
            - 보수적 투자에 적합한 이유
            """,
            agent=stability_screener,
            expected_output="기업별 안정성 점수 및 평가 근거",
            context=[stable_company_discovery_task, financial_stability_task],
        )

        # Task 4: 결과 구조화
        stability_data_structuring_task = Task(
            description="""
            앞선 분석 결과를 다음 단계에서 활용할 수 있도록 구조화하세요:

            다음 JSON 배열 형식으로 정확히 응답해주세요:
            [
                {{
                    "ticker": "티커심볼",
                    "company": "회사명",
                    "stability_score": 9.5,
                    "stability_factors": [
                        "주요 안정 요인1",
                        "주요 안정 요인2"
                    ],
                    "financial_metrics": {{
                        "debt_to_equity": "부채비율 정보",
                        "pe_ratio": "P/E 비율 정보",
                        "roe": "ROE 정보",
                        "dividend_yield": "배당수익률 정보"
                    }},
                    "investment_rationale": "안정적 투자 근거"
                }}
            ]

            중요한 주의사항:
            - stability_score는 숫자 형태 (소수점 1자리)
            - 실제 분석된 내용만 포함
            - 마크다운 코드 블록(```)을 사용하지 말고 순수한 JSON만 반환
            - JSON 앞뒤에 어떤 텍스트도 추가하지 마세요
            - 응답은 [ 로 시작하고 ] 로 끝나야 합니다
            """,
            agent=stability_screener,
            expected_output="""A JSON array starting with [ and ending with ]. No markdown formatting, no code blocks, no additional text. Pure JSON only.""",
            context=[
                stable_company_discovery_task,
                financial_stability_task,
                stability_scoring_task,
            ],
            output_file="output/screen_stable_companies.json",
        )

        stability_screening_crew = Crew(
            agents=[stability_screener],
            tasks=[
                stable_company_discovery_task,
                financial_stability_task,
                stability_scoring_task,
                stability_data_structuring_task,
            ],
            verbose=True,
        )

        self.state.stability_scores = stability_screening_crew.kickoff()

    @listen(screen_stable_companies)
    def evaluate_value_potential(self):
        pass
        # self.state.divide_scores = ..

    @listen(or_(evaluate_growth_potential, evaluate_value_potential))
    def synthesize_portfolio(self):
        pass

    @listen(synthesize_portfolio)
    def finalize_investment_recommendation(self):
        pass
        return self.state.portfolio


flow = FundManagerFlow()
flow.kickoff(
    inputs={
        "investment_goal": "AI 같은 첨단 기술주에 투자하고 싶습니다.",
        "risk_preference": "공격적",
        "budget": 20000.0,
    }
)

# flow.kickoff(
#     inputs={
#         "investment_goal": "은퇴 자금을 위해 안정적인 배당을 원합니다. ",
#         "risk_preference": "보수적",
#         "budget": 50000.0,
#     }
# )


# flow.plot()