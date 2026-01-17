package org.example.agentwebhook.agent

import org.example.agentwebhook.tools.ScoreTools
import org.springframework.ai.chat.client.ChatClient
import org.springframework.ai.chat.prompt.PromptTemplate
import org.springframework.ai.chat.prompt.SystemPromptTemplate
import org.springframework.beans.factory.annotation.Value
import org.springframework.core.io.Resource
import org.springframework.stereotype.Service
import java.io.IOException
import java.nio.charset.StandardCharsets

@Service
class GradingAgent(
    chatClientBuilder: ChatClient.Builder,
    private val scoreTools: ScoreTools,
    @Value("classpath:prompts/grading-rubric.md")
    private val rubricResource: Resource,
    @Value("classpath:prompts/system-message.md")
    private val systemPromptResource: Resource
) {
    private val chatClient = chatClientBuilder.build()

    private val USER_PROMPT_TEMPLATE = """
            [메타 정보]
            - 학생: {studentName}
            - 레포지토리: {repoName}
            - PR 번호: {prNumber}
            
            [모범 답안 (Reference Code)]
            - 아래 코드는 교수님이 작성한 정답입니다. 학생의 코드가 이 로직과 일치하는지 확인하세요.
            {referenceCode}
            
            [학생의 제출 코드 변경사항 (Diff)]
            주의: Diff 형식에서 `-`로 시작하는 줄은 삭제된 코드(과거)이고, `+`로 시작하는 줄이 학생이 작성한 코드(현재)입니다.
            **반드시 `-` 라인은 무시하고, `+` 라인만 보고 평가하세요.**
            
            {diff}
            """.trimIndent()

    fun gradeAndSave(diff: String, solutionCode: String, prNumber: Int, studentName: String, repoName: String): String? {
        val rubric = loadResourceToString(rubricResource)

        val systemMessage = SystemPromptTemplate(systemPromptResource).createMessage(mapOf("rubric" to rubric))

        val userMessage = PromptTemplate(USER_PROMPT_TEMPLATE).createMessage(
            mapOf(
                "studentName" to studentName,
                "repoName" to repoName,
                "prNumber" to prNumber,
                "diff" to diff,
                "referenceCode" to solutionCode,
            )
        )

        return chatClient.prompt()
            .messages(systemMessage, userMessage)
            .tools(scoreTools)
            .call()
            .content()
    }

    private fun loadResourceToString(resource: Resource): String {
        try {
            return resource.getContentAsString(StandardCharsets.UTF_8)
        } catch (e: IOException) {
            throw RuntimeException("프롬프트 파일을 읽을 수 없습니다: ${resource.filename}", e)
        }
    }
}