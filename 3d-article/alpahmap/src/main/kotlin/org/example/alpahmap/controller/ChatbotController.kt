package org.example.alpahmap.controller

import org.example.alpahmap.dto.MessageDto
import org.example.alpahmap.service.ChatbotService
import org.springframework.web.bind.annotation.PostMapping
import org.springframework.web.bind.annotation.RequestBody
import org.springframework.web.bind.annotation.RequestMapping
import org.springframework.web.bind.annotation.RestController

@RestController
@RequestMapping("/chatbot")
class ChatbotController(
    private val chatbotService: ChatbotService,
) {

    @PostMapping
    fun getChatbot(
        @RequestBody req: MessageDto
    ): MessageDto {
        return chatbotService.getChatbotMessage(req)
    }
}