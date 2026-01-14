package org.example.agentwebhook.service

import org.springframework.http.HttpHeaders
import org.springframework.stereotype.Service
import org.springframework.web.client.RestClient

@Service
class GithubService(
    private val githubClient: RestClient,
) {

    fun getPrDiff(owner: String, repo: String, prNumber: Int): String {
        return githubClient.get()
            .uri("/repos/$owner/$repo/pulls/$prNumber")
            .header(HttpHeaders.ACCEPT, "application/vnd.github.v3.diff")
            .retrieve()
            .body(String::class.java)!!
    }

    fun commentOnPr(owner: String, repo: String, prNumber: Int, comment: String) {
        githubClient.post()
            .uri("/repos/$owner/$repo/issues/$prNumber/comments")
            .header(HttpHeaders.ACCEPT, "application/vnd.github+json")
            .body(mapOf("body" to comment))
            .retrieve()
            .toBodilessEntity()
    }
}