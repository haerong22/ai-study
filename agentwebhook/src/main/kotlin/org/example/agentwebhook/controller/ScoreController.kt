package org.example.agentwebhook.controller

import org.example.agentwebhook.entity.AssignmentScore
import org.example.agentwebhook.repository.ScoreRepository
import org.springframework.http.ResponseEntity
import org.springframework.web.bind.annotation.GetMapping
import org.springframework.web.bind.annotation.PathVariable
import org.springframework.web.bind.annotation.RequestMapping
import org.springframework.web.bind.annotation.RestController

@RestController
@RequestMapping("/api/scores")
class ScoreController(
    private val scoreRepository: ScoreRepository
) {

    @GetMapping("/{studentName}")
    fun getStudentScores(
        @PathVariable studentName: String,
    ): ResponseEntity<List<AssignmentScore>> {
        println("🔍 성적 조회 요청: $studentName")

        val scores = scoreRepository.findByStudentNameOrderByGradedAtDesc(studentName)

        if (scores.isEmpty()) {
            println("⚠️ 기록 없음: $studentName")
            return ResponseEntity.noContent().build()
        }

        return ResponseEntity.ok(scores)
    }
}