package org.example

suspend fun main() {
    val apiKey = System.getenv("OPENAI_API_KEY") ?: error("Missing OPENAI_API_KEY")

    val codingAgent = CodingAgent(apiKey)

    while (true) {
        print("User: ")
        val userPrompt = readln()

        val response = codingAgent.chat(userPrompt)

        println("Assistant: $response")
    }
}