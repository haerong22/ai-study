package org.example

import ai.koog.agents.core.agent.AIAgent
import ai.koog.agents.core.tools.ToolRegistry
import ai.koog.agents.core.tools.reflect.tool
import ai.koog.agents.features.eventHandler.feature.EventHandler
import ai.koog.prompt.executor.clients.openai.OpenAIModels
import ai.koog.prompt.executor.llms.all.simpleOpenAIExecutor
import ai.koog.prompt.message.Message
import ai.koog.rag.base.files.JVMFileSystemProvider
import org.example.storage.AgentMemoryStorage
import org.example.storage.ConversationHistoryStorage
import org.example.storage.JsonlConversationHistoryStorage
import org.example.storage.KodingMemoryStorage
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

    val agentMemoryStorage: AgentMemoryStorage = KodingMemoryStorage(
        fs = JVMFileSystemProvider.ReadWrite,
    )

    suspend fun addMemory(content: String) = agentMemoryStorage.addMemory(content)

    suspend fun chat(userMessage: String): String {
        conversationHistoryStorage.compressHistory(executor, model)

        val memory = agentMemoryStorage.getMemory()
        val summary = conversationHistoryStorage.getSummary()
        val history = conversationHistoryStorage.getHistory()
        val system = buildSystemPromptWithHistory(memory, summary, history)

        val agent = AIAgent(
            promptExecutor = executor,
            systemPrompt = system,
            toolRegistry = toolRegistry,
            maxIterations = 50,
            llmModel = model,
            installFeatures = {
                install(EventHandler) {
                    onToolCallStarting {
                        println()
                        println("\u001B[34m🔧 도구 호출중: ${it.toolName}\u001B[0m")
                        println("${it.toolArgs}")
                        it.toolName
                    }

                    onToolCallCompleted {
                        println("\u001B[32m✅ 도구 완료: ${it.toolName}\u001B[0m")
                        it.toolName
                    }

                    onToolCallFailed {
                        println("\u001B[31m❌ 도구 호출 실패: ${it.toolName}\u001B[0m")
                        it.toolName
                    }
                }
            }
        )

        val assistantMessage = agent.run(userMessage)
        conversationHistoryStorage.addConversation(userMessage, assistantMessage)

        return assistantMessage
    }

    private fun buildSystemPromptWithHistory(memory: String?, summary: String?, history: List<Message>): String {
        if (summary == null && history.isEmpty() && memory == null) return systemPrompt

        return buildString {
            appendLine("# System Prompt")
            appendLine(systemPrompt)

            memory?.let {
                appendLine()
                appendLine("# Project Memory")
                appendLine("아래는 이 프로젝트에 대해 기억해야 할 정보입니다.")
                appendLine(it)
            }

            summary?.let {
                appendLine()
                appendLine("# Previous Conversation Summary")
                appendLine(it)
            }

            if (history.isNotEmpty()) {
                appendLine()
                appendLine("# Recent Conversation")

                history.forEach {
                    when (it) {
                        is Message.User -> appendLine("User: ${it.content}")
                        is Message.Assistant -> appendLine("Assistant: ${it.content}")
                        else -> {}
                    }
                }
            }
            appendLine()
            appendLine("위의 맥락을 바탕으로 대화를 이어가 주세요.")
        }
    }

}