package org.example

import ai.koog.agents.core.agent.AIAgent
import ai.koog.agents.core.tools.ToolRegistry
import ai.koog.agents.core.tools.reflect.tool
import ai.koog.prompt.executor.clients.openai.OpenAIModels
import ai.koog.prompt.executor.llms.all.simpleOpenAIExecutor
import ai.koog.prompt.message.Message
import ai.koog.rag.base.files.JVMFileSystemProvider
import org.example.storage.ConversationHistoryStorage
import org.example.storage.JsonlConversationHistoryStorage
import org.example.tools.bash
import org.example.tools.codeSearch
import org.example.tools.editFile
import org.example.tools.listFiles
import org.example.tools.readFile
import java.nio.file.Path
import java.util.UUID

class CodingAgent(
    private val apiKey: String,
    projectDir: String = "dir",
    sessionId: String = UUID.randomUUID().toString(),
) {
    private val conversationHistoryStorage: ConversationHistoryStorage = JsonlConversationHistoryStorage(
        fs = JVMFileSystemProvider.ReadWrite,
        sessionDir = Path.of(".koding_agent/projects/$projectDir/$sessionId"),
    )

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
        val history = conversationHistoryStorage.getHistory()
        val system = buildSystemPromptWithHistory(history)

        val agent = AIAgent(
            promptExecutor = executor,
            systemPrompt = system,
            toolRegistry = toolRegistry,
            maxIterations = 50,
            llmModel = model,
        )

        val assistantMessage = agent.run(userMessage)
        conversationHistoryStorage.addConversation(userMessage, assistantMessage)

        return assistantMessage
    }

    private fun buildSystemPromptWithHistory(history: List<Message>): String {
        if (history.isEmpty()) {
            return systemPrompt
        }

        return buildString {
            appendLine("# System Prompt")
            appendLine(systemPrompt)
            appendLine()
            appendLine("# Conversation History")
            history.forEach {
                when (it) {
                    is Message.User -> appendLine("User: ${it.content}")
                    is Message.Assistant -> appendLine("Assistant: ${it.content}")
                    else -> {}
                }
            }
            appendLine()
            appendLine("위의 맥락을 바탕으로 대화를 이어가 주세요.")
        }
    }

}