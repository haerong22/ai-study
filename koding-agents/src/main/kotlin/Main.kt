package org.example

import ai.koog.prompt.dsl.prompt
import ai.koog.prompt.executor.clients.openai.OpenAIModels
import ai.koog.prompt.executor.llms.all.simpleOpenAIExecutor

suspend fun main() {
    val apiKey = System.getenv("OPENAI_API_KEY") ?: error("Missing OPENAI_API_KEY")

    val executor = simpleOpenAIExecutor(apiKey)

    print("User: ")
    val userPrompt = readln()

    val prompt = prompt(id = "hello-koog") {
        system("""
            # 역할
            당신은 코딩 에이전트 입니다.
            
            ## 도구
            ### 사용 가능한 도구
            - readFile(path: String): String : 주어진 파일 경로를 받고 파일 내용을 응답하는 도구 입니다.
            
            ### 도구 사용 규칙
            - 도구를 사용하려면 반드시 다음 JSON 형식으로 응답하세요:
                `{"tool": "readFile", "args": {"path": "파일경로"}}`
            - 도구가 필요하지 않은 일반 대화는 그냥 텍스트로 응답하세요.   
           
        """.trimIndent())
        user(userPrompt)
    }

    val response = executor.execute(
        prompt = prompt,
        model = OpenAIModels.Chat.GPT5Mini
    )

    println("Assistant: ${response.last().content}")
}