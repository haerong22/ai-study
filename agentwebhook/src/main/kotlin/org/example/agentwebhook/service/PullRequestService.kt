package org.example.agentwebhook.service

import org.example.agentwebhook.agent.CodeReviewWorkflow
import org.springframework.stereotype.Service

@Service
class PullRequestService(
    private val githubService: GithubService,
    private val codeReviewWorkflow: CodeReviewWorkflow,
) {

    fun processPullRequest(
        repoOwner: String,
        repoName: String,
        prNumber: Int,
        studentName: String,
        solutionCode: String,
    ) {
        val diff = githubService.getPrDiff(repoOwner, repoName, prNumber)
        val comment = codeReviewWorkflow.execute(diff, solutionCode, prNumber, studentName, repoOwner)

        githubService.commentOnPr(repoOwner, repoName, prNumber, comment)
        println("✅ [Service] 모든 처리가 완료되었습니다.")
    }
}