package org.example.agentwebhook.controller

import org.example.agentwebhook.dto.GithubWebhookPayload
import org.example.agentwebhook.service.PullRequestService
import org.slf4j.LoggerFactory
import org.springframework.web.bind.annotation.PostMapping
import org.springframework.web.bind.annotation.RequestBody
import org.springframework.web.bind.annotation.RequestHeader
import org.springframework.web.bind.annotation.RestController

@RestController
class WebhookController(
    private val pullRequestService: PullRequestService,
) {
    private val logger = LoggerFactory.getLogger(javaClass)

    @PostMapping("/webhook")
    fun handleGithubEvent(
        @RequestHeader(value = "X-GitHub-Event", defaultValue = "unknown") eventType: String,
        @RequestBody payload: GithubWebhookPayload,
    ) {
        if (eventType != "pull_request") return
        if (payload.action !in listOf("opened", "synchronize")) return

        logger.info("🚀 PR 이벤트 감지! 데이터 분석 시작...")

        val pr = payload.pullRequest ?: run {
            logger.warn("pull_request 정보가 없습니다")
            return
        }
        val repo = payload.repository ?: run {
            logger.warn("repository 정보가 없습니다")
            return
        }

        logger.info("🔔 과제: {} / 학생: {} / PR 번호: #{}", repo.name, pr.user.login, pr.number)

        runCatching {
            pullRequestService.processPullRequest(
                repoOwner = repo.owner.login,
                repoName = repo.name,
                prNumber = pr.number,
                studentName = pr.user.login,
                solutionCode = SOLUTION_CODE
            )
        }.onFailure { e ->
            logger.error("❌ PR 처리 중 오류 발생: {}", e.message, e)
        }
    }

    companion object {
        private val SOLUTION_CODE = """
            public int add(int a, int b) {
                return a + b;
            }
        """.trimIndent()
    }
}
