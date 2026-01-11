package org.example.agentwebhook.dto

data class SaveScoreRequest(
    val studentName: String,
    val repoName: String,
    val prNumber: Int,
    val score: Int,
    val feedback: String,
)
