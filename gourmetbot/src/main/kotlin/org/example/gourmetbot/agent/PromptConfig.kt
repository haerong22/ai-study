package org.example.gourmetbot.agent

import org.springframework.beans.factory.annotation.Value
import org.springframework.context.annotation.Bean
import org.springframework.context.annotation.Configuration
import org.springframework.core.io.Resource
import org.springframework.util.StreamUtils
import java.nio.charset.StandardCharsets

@Configuration
class PromptConfig(
    @Value("classpath:prompts/router-system.md")
    private val routerResource: Resource,
    @Value("classpath:prompts/worker-reservation.md")
    private val reservationResource: Resource,
    @Value("classpath:prompts/worker-sommelier.md")
    private val sommelierResource: Resource,
    @Value("classpath:prompts/worker-concierge.md")
    private val conciergeResource: Resource,
) {

    private fun loadPrompt(resource: Resource): String {
        return StreamUtils.copyToString(resource.inputStream, StandardCharsets.UTF_8)
    }

    @Bean(name = ["routerSystemPrompt"])
    fun routerSystemPrompt(): String {
        return loadPrompt(routerResource)
    }

    @Bean(name = ["workerPrompts"])
    fun workerPrompts(): Map<String, String> {
        return mapOf(
            "reservation" to loadPrompt(reservationResource),
            "sommelier" to loadPrompt(sommelierResource),
            "concierge" to loadPrompt(conciergeResource),
        )
    }
}