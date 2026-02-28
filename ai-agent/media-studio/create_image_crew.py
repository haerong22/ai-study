import os
from datetime import datetime
import requests
from crewai import Crew, Agent, Task
from crewai.project import CrewBase, task, agent, crew
import replicate
from env import GEMINI_API_KEY


os.environ["GEMINI_API_KEY"] = GEMINI_API_KEY


@CrewBase
class PromptMakerCrew:

    @agent
    def prompt_maker_agent(self) -> Agent:
        return Agent(
            role="최고의 이미지 프롬프트 엔지니어",
            goal="사용자가 만들고 싶어하는 이미지의 의도를 철저하게 분석해서 이미지 생성 AI가 가장 잘 만들 수 있도록 하는 최고의 prompt를 만들어준다. 사용자가 한글로 작성해도 prompt는 영어로 하는게 더 좋기에 영어로 prompt를 만들어줘야 함 ",
            backstory="""
            당신은 10년 이상의 경험을 가진 최고의 이미지 프롬프트 엔지니어입니다.
            Midjourney, DALL-E, Stable Diffusion, Imagen 등 다양한 AI 이미지 생성 도구들의 특성을 완벽하게 이해하고 있으며,
            특히 Google Imagen-4의 특성과 최적화된 프롬프트 패턴을 숙지하고 있습니다.

            당신은 사용자의 모호한 요청이라도 세밀한 시각적 디테일로 구체화시키는 능력이 뛰어나며,
            색감, 조명, 구도, 스타일, 분위기 등 모든 시각적 요소를 고려하여 완벽한 프롬프트를 작성합니다.
            한국어로 된 요청을 받더라도 항상 영어로 최적화된 프롬프트를 생성합니다.
            """,
            llm="gemini/gemini-2.0-flash",
            verbose=True,
        )

    @task
    def make_prompt_task(self) -> Task:
        return Task(
            agent=self.prompt_maker_agent(),
            description="""
            사용자로부터 받은 메시지('{message}')를 단계별로 분석하여 최고 품질의 이미지 생성 프롬프트를 작성합니다.

            분석 단계:
            1. 핵심 주제 및 객체 식별 - 사용자가 생성하고 싶은 주요 요소들을 파악
            2. 시각적 스타일 결정 - 사진, 일러스트, 디지털 아트, 회화 등 적합한 스타일 선택
            3. 구체적 디테일 추가 - 색감, 조명, 각도, 구도, 분위기 등 세부 사항 보완
            4. 기술적 파라미터 최적화 - 해상도, 품질, 아스펙트 비율 등 고려
            5. Imagen-4에 최적화된 영어 프롬프트로 변환

            특히 다음 요소들을 반드시 고려해야 합니다:
            - 주요 객체의 위치와 크기
            - 조명 방향과 강도 (natural lighting, soft lighting, dramatic lighting 등)
            - 색상 팔레트와 톤 (vibrant, muted, monochromatic 등)
            - 카메라 각도 (close-up, wide shot, bird's eye view 등)
            - 예술적 스타일 (photorealistic, impressionistic, minimalist 등)
            - 감정과 분위기 (serene, energetic, mysterious 등)
            """,
            expected_output="""
            Google Imagen-4에 최적화된 고품질 영어 프롬프트를 생성합니다.

            출력 형식:
            - 명확하고 구체적인 영어 프롬프트 (50-150 단어)
            - 불필요한 수식어나 모호한 표현 제거
            - 시각적 요소를 우선순위별로 배치
            - 기술적 품질 키워드 포함 (high quality, detailed, professional 등)

            프롬프트 구조 예시:
            "[주요 객체 및 행동] in [환경/배경], [스타일 설명], [조명 조건], [색상 정보], [카메라 설정], [품질 키워드]"

            예: "A serene mountain lake at sunrise, crystal clear water reflecting snow-capped peaks, soft golden lighting, vibrant blue and orange sky, wide landscape shot, photorealistic, high quality, detailed, 4K resolution"

            주의사항:
            - 일관성 있는 스타일과 톤 유지
            - 구체적이지만 과도하게 복잡하지 않은 수준 유지
            """,
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=[self.prompt_maker_agent()],
            tasks=[self.make_prompt_task()],
            verbose=True,
        )


def create_image(message: str, model: str = "google/imagen-4-fast"):
    prompt_maker_crew = PromptMakerCrew().crew()

    prompt = prompt_maker_crew.kickoff(inputs={"message": message}).raw

    output = replicate.run(
        "google/imagen-4-fast",
        input={
            "prompt": prompt,
            "aspect_ratio": "4:3",
            "output_format": "jpg",
            "safety_filter_level": "block_only_high",
        },
    )

    print(output)

    if output:
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"generated_image_{current_time}.jpg"

        try:
            response = requests.get(str(output))

            with open(filename, "wb") as f:
                f.write(response.content)

            print(f"이미지가 저장되었습니다: {filename}")

        except Exception as e:
            print(f"이미지 저장 중 오류 발생: {e}")

    else:
        print("이미지 생성에 실패했습니다.")


create_image("해변에 앉아있는 밀집모자 해적단")