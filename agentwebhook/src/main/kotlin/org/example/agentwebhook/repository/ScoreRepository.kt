package org.example.agentwebhook.repository

import org.example.agentwebhook.entity.AssignmentScore
import org.springframework.data.jpa.repository.JpaRepository

interface ScoreRepository: JpaRepository<AssignmentScore, Long> {

    // 특정 학생의 점수 기록을 '채점 일시' 내림차순으로 조회
    fun findByStudentNameOrderByGradedAtDesc(studentName: String): List<AssignmentScore>
}