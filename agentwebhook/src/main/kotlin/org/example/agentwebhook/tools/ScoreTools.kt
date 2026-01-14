package org.example.agentwebhook.tools

import org.example.agentwebhook.dto.SaveScoreRequest
import org.example.agentwebhook.entity.AssignmentScore
import org.example.agentwebhook.repository.ScoreRepository
import org.springframework.ai.tool.annotation.Tool
import org.springframework.stereotype.Component

@Component
class ScoreTools(
    private val scoreRepository: ScoreRepository,
) {

    @Tool(
        description = "채점 결과를 DB에 저장하는 도구입니다. 점수(0~100)와 피드백을 반드시 저장해야 합니다."
    )
    fun saveScore(request: SaveScoreRequest): String {
        println("[Tool] AI가 DB 저장을 요청했습니다. ${request.score}점")

        val assignmentScore = AssignmentScore(
            request.studentName,
            request.repoName,
            request.prNumber,
            request.score,
            request.feedback,
        )

        scoreRepository.save(assignmentScore)

        return "DB 저장 완료! (학생: ${request.studentName}, 점수: ${request.score})"
    }
}