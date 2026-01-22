package org.example

import ai.koog.prompt.dsl.prompt
import ai.koog.prompt.executor.clients.openai.OpenAIModels
import ai.koog.prompt.executor.llms.all.simpleOpenAIExecutor
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.Json
import org.example.tools.readFile

@Serializable
data class ToolCall(
    val tool: String,
    val args: ToolArgs,
)

@Serializable
data class ToolArgs(
    val path: String,
)

suspend fun main() {
    val apiKey = System.getenv("OPENAI_API_KEY") ?: error("Missing OPENAI_API_KEY")

    val executor = simpleOpenAIExecutor(apiKey)

    print("User: ")
    val userPrompt = readln()
    val systemPrompt = """
            # 역할
            당신은 코딩 에이전트 입니다.
            
            ## 도구
            ### 사용 가능한 도구
            - readFile(path: String): String : 주어진 파일 경로를 받고 파일 내용을 응답하는 도구 입니다.
            
            ### 도구 사용 규칙
            - 도구를 사용하려면 반드시 다음 JSON 형식으로 응답하세요:
                `{"tool": "readFile", "args": {"path": "파일경로"}}`
            - [중요]: 도구를 선택할 때, 순수한 JSON 문자열로 출력하세요. 코드블럭 혹은 다른 요소들은 제거하시오.
            - 도구가 필요하지 않은 일반 대화는 그냥 텍스트로 응답하세요.   
           
        """.trimIndent()

    val prompt = prompt(id = "hello-koog") {
        system(systemPrompt)
        user(userPrompt)
    }

    val response = executor.execute(
        prompt = prompt,
        model = OpenAIModels.Chat.GPT5Mini
    )

    val json = Json { ignoreUnknownKeys = true }
    val toolCall = json.decodeFromString<ToolCall>(response.first().content)

    val toolResult = when (toolCall.tool) {
        "readFile" -> readFile(toolCall.args.path)
        else -> "알 수 없는 Tool입니다: ${toolCall.tool}"
    }

    val secondPrompt = prompt(id = "second-prompt") {
        system(systemPrompt)
        user(userPrompt)
        assistant(response.first().content)
        user(toolResult)
    }

    val finalResult = executor.execute(
        prompt = secondPrompt,
        model = OpenAIModels.Chat.GPT5Mini
    )

    println("=============================")
    println("finalResult: ${finalResult.first().content}")
    println("=============================")
}