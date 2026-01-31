package org.example

suspend fun main() {
    val apiKey = System.getenv("OPENAI_API_KEY") ?: error("Missing OPENAI_API_KEY")

    var codingAgent = CodingAgent(apiKey)

    while (true) {
        print("User: ")
        val userPrompt = readln()

        if (userPrompt == "/exit") {
            println("종료합니다.")
            break
        }

        if (userPrompt == "/clear") {
            codingAgent = CodingAgent(apiKey)
            println("새로운 대화가 시작되었습니다.")
            println()
            continue
        }

        val response = codingAgent.chat(userPrompt)

        println("Assistant: $response")
    }
}