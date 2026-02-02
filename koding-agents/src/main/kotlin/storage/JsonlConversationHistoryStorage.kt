package org.example.storage

import ai.koog.prompt.dsl.prompt
import ai.koog.prompt.executor.model.PromptExecutor
import ai.koog.prompt.llm.LLModel
import ai.koog.prompt.message.Message
import ai.koog.prompt.message.RequestMetaInfo
import ai.koog.prompt.message.ResponseMetaInfo
import ai.koog.rag.base.files.JVMFileSystemProvider
import ai.koog.rag.base.files.createDirectory
import ai.koog.rag.base.files.readText
import ai.koog.rag.base.files.writeText
import kotlinx.coroutines.runBlocking
import kotlinx.datetime.Clock
import kotlinx.datetime.Clock.System.now
import kotlinx.serialization.json.Json
import java.nio.file.Path

class JsonlConversationHistoryStorage(
    private val fs: JVMFileSystemProvider.ReadWrite,
    private val sessionDir: Path,
    private val json: Json = Json {
        ignoreUnknownKeys = true
        prettyPrint = false
    }
) : ConversationHistoryStorage {

    companion object {
        private const val COMPRESS_THRESHOLD = 4
        private const val KEEP_RECENT = 2
    }

    private val summaryFile: Path
        get() = fs.joinPath(sessionDir, "summary.md")

    private val historyFile: Path
        get() = fs.joinPath(sessionDir, "session.jsonl")

    init {
        runBlocking {
            if (!fs.exists(sessionDir)) {
                fs.createDirectory(sessionDir)
            }
        }
    }

    override suspend fun addConversation(userMessage: String, assistantMessage: String) {
        val existingContent = if (fs.exists(historyFile)) {
            fs.readText(historyFile)
        } else ""

        val userEntry = JsonlEntry(
            timestamp = now(),
            message = Message.User(userMessage, RequestMetaInfo.create(Clock.System))
        )

        val assistantEntry = JsonlEntry(
            timestamp = now(),
            message = Message.Assistant(assistantMessage, ResponseMetaInfo.create(Clock.System))
        )

        val newlines = listOf(userEntry, assistantEntry)
            .joinToString("\n") { entry ->
                json.encodeToString(JsonlEntry.serializer(), entry)
            }

        val updatedContent = if (existingContent.isEmpty()) {
            newlines
        } else {
            existingContent + "\n" + newlines
        }

        fs.writeText(historyFile, updatedContent)
    }

    override suspend fun getHistory(): List<Message> {
        return loadAllMessages().takeLast(KEEP_RECENT)
    }

    override suspend fun getSummary(): String? {
        if (!fs.exists(summaryFile)) return null
        return fs.readText(summaryFile).ifBlank { null }
    }

    override suspend fun compressHistory(
        executor: PromptExecutor,
        model: LLModel
    ) {
        val allMessages = loadAllMessages()

        if (allMessages.size <= COMPRESS_THRESHOLD) return

        val toSummarize = allMessages.dropLast(KEEP_RECENT)

        val conversationText = buildString {
            getSummary()?.let {
                appendLine("이전 요약 내용: $it")
                appendLine()
            }

            toSummarize.forEach { msg ->
                when (msg) {
                    is Message.User -> appendLine("User: ${msg.content}")
                    is Message.Assistant -> appendLine("Assistant: ${msg.content}")
                    else -> {}
                }
            }
        }

        val summarizePrompt = prompt("summarize") {
            system(conversationText)
            user("이 대화를 간결하게 요약하세요:")
        }

        val response = executor.execute(summarizePrompt, model)

        fs.writeText(summaryFile, response.first().content)
    }

    private suspend fun loadAllMessages(): List<Message> {
        if (!fs.exists(historyFile)) {
            return emptyList()
        }

        return fs.readText(historyFile).lines()
            .filter { it.isNotBlank() }
            .mapNotNull {
                try {
                    val entry = json.decodeFromString<JsonlEntry>(it)
                    entry.message
                } catch (e: Exception) {
                    System.err.println("해당 구문 분석하는데 실패했습니다. $it")
                    null
                }
            }
    }
}