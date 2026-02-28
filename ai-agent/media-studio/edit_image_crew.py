import os
import replicate
import requests
from crewai import Crew, Agent, Task
from crewai.project import CrewBase, task, agent, crew
from env import GEMINI_API_KEY


os.environ["GEMINI_API_KEY"] = GEMINI_API_KEY


@CrewBase
class EditImagePromptMakerCrew:

    @agent
    def image_edit_prompt_maker_agent(self) -> Agent:
        return Agent(
            role="최고의 이미지 편집 프롬프트 엔지니어",
            goal="사용자가 원하는 이미지 편집 의도를 정확히 파악하고 Google Nano Banana 모델이 최상의 결과를 만들 수 있도록 하는 최적화된 편집 프롬프트를 만들어준다. 사용자가 한글로 작성해도 prompt는 영어로 하는게 더 좋기에 영어로 prompt를 만들어줘야 함",
            backstory="""
            당신은 10년 이상의 경험을 가진 최고의 이미지 편집 프롬프트 엔지니어입니다.
            Photoshop, GIMP, Canva 등 다양한 이미지 편집 도구들과 AI 기반 이미지 편집 모델들의 특성을 완벽하게 이해하고 있으며,
            특히 Google Nano Banana 모델의 image-to-image 편집 기능에 최적화된 프롬프트 작성에 특화되어 있습니다.

            당신은 사용자가 원하는 편집 의도를 정확히 파악하여:
            - 기존 이미지의 어떤 부분을 유지해야 하는지
            - 어떤 부분을 변경해야 하는지
            - 변경할 요소들의 구체적인 특징들 (색상, 스타일, 크기, 위치 등)
            을 명확하게 구분하여 최적의 편집 프롬프트를 생성합니다.

            한국어로 된 요청을 받더라도 항상 영어로 최적화된 편집 프롬프트를 생성합니다.
            """,
            llm="openai/o4-mini",
            verbose=True,
        )

    @task
    def make_edit_prompt_task(self) -> Task:
        return Task(
            agent=self.image_edit_prompt_maker_agent(),
            description="""
            사용자로부터 받은 편집 요청('{edit_request}')을 분석하여 Google Nano Banana 모델에 최적화된 이미지 편집 프롬프트를 작성합니다.

            편집 분석 단계:
            1. 편집 목적 파악 - 사용자가 무엇을 변경하고 싶어하는지 명확히 이해
            2. 유지 요소 식별 - 기존 이미지에서 보존되어야 할 부분들 파악
            3. 변경 요소 정의 - 수정되어야 할 구체적인 요소들과 원하는 변경 사항
            4. 편집 강도 조절 - 자연스러운 편집을 위한 적절한 변경 정도 설정
            5. Nano Banana에 최적화된 영어 편집 프롬프트로 변환

            특히 다음 요소들을 고려해야 합니다:
            - 편집의 구체적인 목표 (색상 변경, 객체 추가/제거, 스타일 변경 등)
            - 편집 범위 (전체 이미지 vs 특정 부분)
            - 편집 강도 (subtle changes vs dramatic transformation)
            - 일관성 유지 (기존 이미지의 전반적인 스타일과 조화)
            - 자연스러운 결과를 위한 세부 지침
            """,
            expected_output="""
            Google Nano Banana 모델에 최적화된 영어 편집 프롬프트만을 출력합니다.

            출력 형식:
            - 명확하고 구체적인 영어 편집 프롬프트 (30-100 단어)
            - 편집 목표를 정확히 표현
            - 불필요한 설명 제거
            - 자연스러운 편집을 위한 적절한 키워드 포함

            편집 프롬프트 구조:
            "[편집 동작] [대상 객체/영역] to [원하는 결과], keep original [보존할 요소들], [스타일/품질 조건], [자연스러운 통합을 위한 지침]"

            예시:
            - "Change the sky to sunset colors with warm orange and pink tones, keep original composition and lighting style"
            - "Transform person's outfit to tank top, keep original pose, facial features, and background unchanged"
            - "Add flowers in the foreground, colorful wildflowers, keep original background and main subject intact"

            주의사항:
            - 편집 프롬프트만 출력하고 다른 설명은 포함하지 않음
            - 원본 이미지의 주요 특징(인물, 포즈, 배경 등)을 반드시 보존하도록 명시
            - "keep original", "maintain", "preserve" 같은 보존 키워드 적극 사용
            - 미세한 편집을 통한 자연스러운 결과 추구
            """,
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=[self.image_edit_prompt_maker_agent()],
            tasks=[self.make_edit_prompt_task()],
            verbose=True,
        )


def edit_image_from_url(image_url, edit_requet):

    try:

        edit_prompt_crew = EditImagePromptMakerCrew().crew()
        enhanced_prompt = edit_prompt_crew.kickoff(
            inputs={"edit_request": edit_requet}
        ).raw

        output = replicate.run(
            "google/nano-banana",
            input={
                "prompt": enhanced_prompt,
                "image_input": [image_url],
                "output_format": "png",
            },
        )

        print(output)

    except Exception as e:
        print(f"Error editing image from URL: {str(e)}")
        raise e


edit_image_from_url(
    "https://replicate.delivery/xezq/qSpb5y13EY56IdlhbuV7SaJBssYLOXGHK7Tfk5nPFfbsLNgVA/tmpso4k6npg.jpg",
    "이미지의 바다색을 노란색으로 변경해줘",
)