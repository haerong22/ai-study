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

class CodingAgent(
    private val apiKey: String,
) {
    private val executor = simpleOpenAIExecutor(apiKey)
    private val model = OpenAIModels.Chat.GPT5Mini
    private val systemPrompt = "당신은 코딩 에이전트 입니다."
    val toolRegistry = ToolRegistry {
        tool(::readFile)
        tool(::listFiles)
        tool(::editFile)
        tool(::bash)
        tool(::codeSearch)
    }

    suspend fun chat(userMessage: String): String {
        val agent = AIAgent(
            promptExecutor = executor,
            systemPrompt = systemPrompt,
            toolRegistry = toolRegistry,
            maxIterations = 50,
            llmModel = model,
        )

        return agent.run(userMessage)
    }

}