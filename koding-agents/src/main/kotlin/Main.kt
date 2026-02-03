package org.example

suspend fun main() {
    val apiKey = System.getenv("OPENAI_API_KEY") ?: error("Missing OPENAI_API_KEY")

    var codingAgent = CodingAgent(apiKey)

    while (true) {
        print("User: ")
        val userPrompt = readln()

        when {
            userPrompt == "/clear" -> {
                codingAgent = CodingAgent(apiKey)
                println("새로운 대화가 시작되었습니다.")
                continue
            }

            userPrompt == "/exit" -> {
                println("종료합니다.")
                break
            }

            userPrompt.startsWith("/memory add") -> {
                val content = userPrompt.removePrefix("/memory add ").trim()
                codingAgent.addMemory(content)
                println("메모리에 저장했습니다: $content")
            }

            else -> {
                val response = codingAgent.chat(userPrompt)

                println("Assistant: $response")
            }
        }
    }
}