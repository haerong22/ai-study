package org.example.alpahmap.service

import org.example.alpahmap.dto.ArticleRequest
import org.example.alpahmap.dto.ArticleResponse
import org.example.alpahmap.entity.Article
import org.example.alpahmap.repository.ArticleRepository
import org.example.alpahmap.repository.ModelRepository
import org.springframework.data.repository.findByIdOrNull
import org.springframework.stereotype.Service

@Service
class ArticleService(
    val articleRepository: ArticleRepository,
    val modelRepository: ModelRepository,
) {

    fun createArticle(request: ArticleRequest): ArticleResponse {
        val model = modelRepository.findByIdOrNull(request.modelId)
            ?: throw IllegalArgumentException("not found model: ${request.modelId}")

        val article = Article(
            title = request.title,
            content = request.content,
            imageUrl = request.imageUrl,
            model = model,
        )
        val saved = articleRepository.save(article)

        return ArticleResponse(saved)
    }
}