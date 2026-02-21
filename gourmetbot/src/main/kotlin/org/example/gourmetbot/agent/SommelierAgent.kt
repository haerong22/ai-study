package org.example.gourmetbot.agent

import org.example.gourmetbot.tools.SommelierTools
import org.springframework.ai.chat.client.ChatClient
import org.springframework.ai.chat.client.advisor.MessageChatMemoryAdvisor
import org.springframework.ai.chat.memory.ChatMemory
import org.springframework.ai.chat.prompt.SystemPromptTemplate
import org.springframework.stereotype.Component
import java.time.LocalDate
import java.time.format.DateTimeFormatter
import java.util.Locale

@Component
class SommelierAgent(
    private val chatClientBuilder: ChatClient.Builder,
    private val workerPrompts: Map<String, String>,
    private val chatMemory: ChatMemory,
    private val sommelierTools: SommelierTools,
) {
    private val chatClient = chatClientBuilder.build()


    fun process(userMessage: String, conversationId: String): String? {
        val currentDate = LocalDate.now().format(DateTimeFormatter.ofPattern("yyyy-MM-dd (E요일)", Locale.KOREAN))
        val systemPrompt = SystemPromptTemplate(workerPrompts["sommelier"])
            .create(mapOf("current_date" to currentDate)).contents

        return chatClient.prompt()
            .system(systemPrompt)
            .user(userMessage)
            .advisors(MessageChatMemoryAdvisor.builder(chatMemory).build())
            .advisors { it.param(ChatMemory.CONVERSATION_ID, conversationId) }
            .tools(sommelierTools)
            .call()
            .content()
    }
}