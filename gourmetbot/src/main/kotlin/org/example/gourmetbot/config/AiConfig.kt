package org.example.gourmetbot.config

import org.springframework.ai.chat.client.ChatClient
import org.springframework.ai.chat.client.advisor.SimpleLoggerAdvisor
import org.springframework.ai.chat.memory.ChatMemory
import org.springframework.ai.chat.memory.MessageWindowChatMemory
import org.springframework.ai.chat.memory.repository.jdbc.JdbcChatMemoryRepository
import org.springframework.ai.chat.model.ChatModel
import org.springframework.ai.tool.ToolCallbackProvider
import org.springframework.context.annotation.Bean
import org.springframework.context.annotation.Configuration

@Configuration
class AiConfig {

    @Bean
    fun chatMemory(jdbcChatMemoryRepository: JdbcChatMemoryRepository): ChatMemory {
        return MessageWindowChatMemory.builder()
            .chatMemoryRepository(jdbcChatMemoryRepository)
            .maxMessages(15)
            .build()
    }

    @Bean
    fun chatClientBuilder(chatModel: ChatModel, tools: ToolCallbackProvider): ChatClient.Builder {
        return ChatClient.builder(chatModel)
            .defaultToolCallbacks(tools)
            .defaultAdvisors(SimpleLoggerAdvisor())
    }
}