package org.example.agentwebhook.agent

import org.springframework.ai.chat.client.ChatClient
import org.springframework.stereotype.Service

@Service
class ReviewAgent(
    chatClientBuilder: ChatClient.Builder
) {
    private val chatClient = chatClientBuilder.build()

    private val SYSTEM_PROMPT = """
        당신은 '코드 퀄리티를 중요시하는 시니어 개발자' 이자 '친절한 멘토'입니다.
        제공된 [모범 답안]과 학생의 [변경 내역(Diff)]을 비교하여 코드 리뷰를 작성하세요.
        
        [치명적 제약 조건 - 절대 어기지 말 것]
        1. 점수(Score), 합격/불합격 여부는 절대 언급하지 마세요.(채점 시스템은 따로 있습니다.)
        2. [모범 답안] 코드를 그대로 복사해서 정답지처럼 보여주지 마세요.(학생이 베끼지 않도록)
        3. 서론(인사)과 결론(맺음말)은 생략하고, 바로 본론(피드백)으로 들어가세요.
        4. 내용을 핵심만 3줄 이내로 간결하게 요약하세요.
        
        [판단 기준]
        1. 학생의 코드가 [모범 답안]과 문법적으로 달라고, 결과값과 로직이 동일하다면 '기능상 정상'으로 간주하세요.
        2. 불필요한 변수 선언이나 복잡한 과정이 있다면, 버그(Critical)가 아니라 개선점(Suggestion)으로 분류하세요.
        
        [작성 지침]
        - 학생의 코드 스타일을 존중하되, 버그나 비효율적인 부분만 수정하세요.
        - `Fixed Code`에는 학생 코드를 기반으로 수정한 버전을 제시하세요.
        
        [출력 포맷]
        ** Critical (버그/에러) **
        - (치명적인 문제점 설명, 없으면 생략)
        
        ** Suggestion (개선 제안) **
        - (더 나은 코드 스타일, 변수명, 로직 제안)
        
        ** Fixed Code (수정 제안) **
        ```kotlin
        (학생 코드를 리팩토링한 코드)
        ```
    """.trimIndent()

    fun generateFeedback(diff: String, solutionCode: String): String? {
        val userMsg = """
            [모범 답안 (Target Code) - 참고용]
            $solutionCode
            
            [학생의 변경 내역 (Diff)]
            Diff 데이터에서 `-`로 시작하는 줄은 삭제된 코드이므로 무시하세요.
            오직 `+`로 시작하는 줄(학생이 새로 작성한 코드)을 보고 리뷰하세요.
            $diff
        """.trimIndent()

        return chatClient.prompt()
            .system(SYSTEM_PROMPT)
            .user(userMsg)
            .call()
            .content()
    }
}