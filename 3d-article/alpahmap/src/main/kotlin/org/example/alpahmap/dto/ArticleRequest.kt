package org.example.alpahmap.dto

data class ArticleRequest(
    val title: String,
    val content: String,
    val imageUrl: String,
    val modelId: Long,
)
