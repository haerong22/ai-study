package org.example

import ai.koog.agents.core.agent.AIAgent
import ai.koog.agents.core.tools.ToolRegistry
import ai.koog.agents.core.tools.reflect.tool
import ai.koog.prompt.executor.clients.openai.OpenAIModels
import ai.koog.prompt.executor.llms.all.simpleOpenAIExecutor
import org.example.tools.bash
import org.example.tools.codeSearch
import org.example.tools.editFile
import org.example.tools.listFiles
import org.example.tools.readFile

suspend fun main() {
    val apiKey = System.getenv("OPENAI_API_KEY") ?: error("Missing OPENAI_API_KEY")

    val executor = simpleOpenAIExecutor(apiKey)
    val model = OpenAIModels.Chat.GPT5Mini

    val toolRegistry = ToolRegistry {
        tool(::readFile)
        tool(::listFiles)
        tool(::editFile)
        tool(::bash)
        tool(::codeSearch)
    }

    val systemPrompt = "당신은 코딩 에이전트 입니다."

    val agent = AIAgent(
        promptExecutor = executor,
        systemPrompt = systemPrompt,
        toolRegistry = toolRegistry,
        maxIterations = 50,
        llmModel = model,
    )

    print("User: ")
    val userPrompt = readln()

    val response = agent.run(userPrompt)

    println("Assistant: $response")
}