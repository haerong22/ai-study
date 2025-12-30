package org.example.alpahmap.service

import org.example.alpahmap.dto.MessageDto
import org.springframework.ai.chat.prompt.Prompt
import org.springframework.ai.openai.OpenAiChatModel
import org.springframework.stereotype.Service

@Service
class ChatbotService(
    private val openAiChatModel: OpenAiChatModel,
) {

    fun getChatbotMessage(message: MessageDto): MessageDto {
        val prompt = Prompt(
            "너는 사회문제를 잘 알고있는 사회문제 전문가야. " +
                    "사용자가 너한테 사회 문제에 관련해서 질문을 하면 너는 전문가처럼 답변을 진행해줘야해. " +
                    "사용자의 질문은" + message.message + "이야."
        )
        return MessageDto(openAiChatModel.call(prompt).result.output.text ?: "")
    }
}