package org.example.agentwebhook.dto

import com.fasterxml.jackson.annotation.JsonIgnoreProperties
import com.fasterxml.jackson.annotation.JsonProperty

@JsonIgnoreProperties(ignoreUnknown = true)
data class GithubWebhookPayload(
    val action: String?,
    @JsonProperty("pull_request") val pullRequest: PullRequestInfo?,
    val repository: RepositoryInfo?,
)

@JsonIgnoreProperties(ignoreUnknown = true)
data class PullRequestInfo(
    val number: Int,
    val user: GithubUser,
)

@JsonIgnoreProperties(ignoreUnknown = true)
data class RepositoryInfo(
    val name: String,
    val owner: GithubUser,
)

@JsonIgnoreProperties(ignoreUnknown = true)
data class GithubUser(
    val login: String,
)
