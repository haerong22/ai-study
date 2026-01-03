package org.example.alpahmap.dto

import org.example.alpahmap.entity.Article

data class ArticleResponse(
    val id: Long,
    val title: String,
    val content: String,
    val imageUrl: String,
    val model: ModelDto,
) {

    constructor(article: Article) : this(
        article.id!!,
        article.title,
        article.content,
        article.imageUrl,
        ModelDto(
            article.model.id!!,
            article.model.filename,
            article.model.filepath,
            article.model.latitude,
            article.model.longitude,
            article.model.height,
            article.model.scale,
        )
    )
}
