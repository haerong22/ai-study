package org.example.alpahmap.repository

import org.example.alpahmap.entity.Article
import org.springframework.data.repository.CrudRepository

interface ArticleRepository: CrudRepository<Article, Long> {
}