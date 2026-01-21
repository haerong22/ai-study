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
        system("당신은 코딩 에이전트 입니다.")
        user(userPrompt)
    }

    val response = executor.execute(
        prompt = prompt,
        model = OpenAIModels.Chat.GPT5Mini
    )

    println("Assistant: ${response.last().content}")
}