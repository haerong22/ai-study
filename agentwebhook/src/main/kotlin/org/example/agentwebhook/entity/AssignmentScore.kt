package org.example.agentwebhook.entity

import jakarta.persistence.Column
import jakarta.persistence.Entity
import jakarta.persistence.GeneratedValue
import jakarta.persistence.GenerationType
import jakarta.persistence.Id
import java.time.LocalDateTime

@Entity
class AssignmentScore(
    val studentName: String,
    val repoName: String,
    val prNumber: Int,
    val score: Int,
    @Column(length = 1000)
    val feedback: String,
) {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long? = null

    val gradedAt: LocalDateTime = LocalDateTime.now()
}