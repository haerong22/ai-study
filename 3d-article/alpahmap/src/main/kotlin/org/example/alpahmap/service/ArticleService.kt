package org.example.alpahmap.service

import org.example.alpahmap.dto.ArticleRequest
import org.example.alpahmap.dto.ArticleResponse
import org.example.alpahmap.entity.Article
import org.example.alpahmap.repository.ArticleRepository
import org.example.alpahmap.repository.ModelRepository
import org.springframework.stereotype.Service

@Service
class ArticleService(
    val articleRepository: ArticleRepository,
    val modelRepository: ModelRepository,
) {

    fun createArticle(request: ArticleRequest): ArticleResponse {
        val model = modelRepository.findById(request.modelId).orElseThrow()

        val article = Article(
            title = request.title,
            content = request.content,
            imageUrl = request.imageUrl,
            model = model,
        )
        val saved = articleRepository.save(article)

        return ArticleResponse(saved)
    }

    fun findAll(): List<ArticleResponse> {
        return articleRepository.findAll().map { ArticleResponse(it) }
    }
}