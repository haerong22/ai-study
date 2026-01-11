package org.example.agentwebhook.config

import org.springframework.beans.factory.annotation.Value
import org.springframework.context.annotation.Bean
import org.springframework.context.annotation.Configuration
import org.springframework.http.HttpHeaders
import org.springframework.web.client.RestClient

@Configuration
class RestClientConfig(
    @param:Value("\${github.token}")
    private val token: String,
) {

    @Bean
    fun githubClient(): RestClient {
        return RestClient.builder()
            .baseUrl("https://api.github.com")
            .defaultHeader(HttpHeaders.AUTHORIZATION, "Bearer $token")
            .build()
    }
}