package org.example.gourmetbot.controller

import org.example.gourmetbot.agent.GourmetOrchestrator
import org.springframework.web.bind.annotation.CrossOrigin
import org.springframework.web.bind.annotation.PostMapping
import org.springframework.web.bind.annotation.RequestBody
import org.springframework.web.bind.annotation.RequestHeader
import org.springframework.web.bind.annotation.RequestMapping
import org.springframework.web.bind.annotation.RestController
import java.util.UUID

@RestController
@RequestMapping("/api/v1/chat")
@CrossOrigin("http://localhost:5173")
class AiController(
    private val gourmetOrchestrator: GourmetOrchestrator,
) {

    @PostMapping
    fun chat(
        @RequestBody requestBody: Map<String, String>,
        @RequestHeader("ConversationId", required = false) conversationId: String?,
    ): String? {
        val userMessage = requestBody["message"] ?: ""
        val currentConversationId = conversationId ?: UUID.randomUUID().toString()
        return gourmetOrchestrator.chat(userMessage, currentConversationId)
    }
}