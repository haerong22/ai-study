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
    val json = Json { ignoreUnknownKeys = true }
    val model = OpenAIModels.Chat.GPT5Mini
    var iteration = 0
    val maxIteration = 10

    val conversationHistory = mutableListOf<Pair<String, String>>()

    val systemPrompt = """
        # 역할
        당신은 코딩 에이전트 입니다.
        
        ## 도구
        ### 사용 가능한 도구
        - readFile(path: String): String : 주어진 파일 경로를 받고 파일 내용을 응답하는 도구 입니다.
        
        ### 도구 사용 규칙
        - 도구를 사용하려면 반드시 다음 JSON 형식으로 응답하세요:
          {"tool": "readFile", "args": {"path": "파일경로"}}
        - 도구 사용 시 다른 텍스트를 절대 포함하지 마세요. 오직 JSON만 응답하세요.
        - 도구가 필요하지 않은 일반 대화는 그냥 텍스트로 응답하세요   
    """.trimIndent()

    fun parseToolCall(response: String): ToolCall? {
        return try {
            json.decodeFromString<ToolCall>(response)
        } catch (e: Exception) {
            null
        }
    }

    print("User: ")
    val userPrompt = readln()

    while (maxIteration > iteration) {

        val currentPrompt = prompt(id = "agent-loop") {
            system(systemPrompt)
            user(userPrompt)
            conversationHistory.forEach { (assistantMsg, userMsg) ->
                assistant(assistantMsg)
                user(userMsg)
            }
        }

        val response = executor.execute(currentPrompt, model)
        val llmResponse = response.first().content

        val toolCall = parseToolCall(llmResponse)

        if (toolCall != null) {
            val toolResult = when (toolCall.tool) {
                "readFile" -> readFile(toolCall.args.path)
                else -> "알 수 없는 Tool입니다: ${toolCall.tool}"
            }
            println("Tool 결과: ${toolResult.take(100)}...")
            conversationHistory.add(llmResponse to toolResult)
            iteration++
        } else {
            println("Assistant: $llmResponse")
            break
        }
    }
}