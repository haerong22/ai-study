package org.example.gourmetbot.agent

import org.slf4j.LoggerFactory
import org.springframework.ai.chat.client.ChatClient
import org.springframework.stereotype.Component

@Component
class IntentRouter(
    private val chatClientBuilder: ChatClient.Builder,
    private val routerSystemPrompt: String,
) {
    private val chatClient: ChatClient = chatClientBuilder.build()

    private val log = LoggerFactory.getLogger(javaClass)

    data class RoutingResponse(
        val reasoning: String,
        val selection: String,
    )

    fun determineWorker(userMessage: String): String {
        val response = chatClient.prompt()
            .system(routerSystemPrompt)
            .user(userMessage)
            .call()
            .entity(RoutingResponse::class.java)!!

        log.info("라우터 분석: ${response.selection}(${response.reasoning})")
        return response.selection
    }
}