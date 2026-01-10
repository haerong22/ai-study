package org.example.agentwebhook.controller

import org.springframework.web.bind.annotation.PostMapping
import org.springframework.web.bind.annotation.RequestBody
import org.springframework.web.bind.annotation.RestController

@RestController
class WebhookController {

    @PostMapping("/webhook")
    fun handleGithubEvent(
        @RequestBody payload: Map<String, Any>
    ) {
        println(payload)
    }
}