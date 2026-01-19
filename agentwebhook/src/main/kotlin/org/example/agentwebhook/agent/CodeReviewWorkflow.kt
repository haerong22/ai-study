package org.example.agentwebhook.agent

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.async
import kotlinx.coroutines.runBlocking
import org.springframework.stereotype.Component

@Component
class CodeReviewWorkflow(
    private val reviewAgent: ReviewAgent,
    private val gradingAgent: GradingAgent,
) {

    fun execute(diff: String, solutionCode: String, prNumber: Int, studentName: String, repoName: String): String =
        runBlocking(Dispatchers.IO) {
            val startTime = System.currentTimeMillis()

            val reviewDeferred = async {
                println("📝 [Async] 리뷰 에이전트가 분석을 시작했습니다...")
                reviewAgent.generateFeedback(diff, solutionCode)
            }

            val gradingDeferred = async {
                println("⚖️ [Async] 채점 에이전트가 채점 중입니다...")
                gradingAgent.gradeAndSave(diff, solutionCode, prNumber, studentName, repoName)
            }

            val reviewResult = reviewDeferred.await()
            val gradingLog = gradingDeferred.await()

            println("⏱️ [Performance] 전체 처리 시간: ${System.currentTimeMillis() - startTime}ms")
            println("🔍 [System Log] $gradingLog")

            "## 🤖 AI 코드 리뷰!\n\n$reviewResult"
        }
}