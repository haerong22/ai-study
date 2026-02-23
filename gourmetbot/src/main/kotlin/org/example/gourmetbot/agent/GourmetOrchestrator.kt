package org.example.gourmetbot.agent

import org.springframework.stereotype.Component

@Component
class GourmetOrchestrator(
    private val intentRouter: IntentRouter,
    private val reservationAgent: ReservationAgent,
    private val sommelierAgent: SommelierAgent,
    private val conciergeAgent: ConciergeAgent,
) {

    fun chat(userMessage: String, conversationId: String): String? {
        val workerType = intentRouter.determineWorker(userMessage)
        return when (workerType) {
            "reservation" -> reservationAgent.process(userMessage, conversationId)
            "sommelier" -> sommelierAgent.process(userMessage, conversationId)
            "concierge" -> conciergeAgent.process(userMessage, conversationId)
            else -> conciergeAgent.process(userMessage, conversationId)
        }
    }
}