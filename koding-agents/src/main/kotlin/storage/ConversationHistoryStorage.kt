package org.example.storage

import ai.koog.prompt.message.Message
import kotlinx.datetime.Instant
import kotlinx.serialization.Serializable

interface ConversationHistoryStorage {
    suspend fun addConversation(userMessage: String, assistantMessage: String)
    suspend fun getHistory(): List<Message>
}

@Serializable
data class JsonlEntry(
    val timestamp: Instant,
    val message: Message
)