package org.example.alpahmap.controller

import org.example.alpahmap.dto.ArticleRequest
import org.example.alpahmap.dto.ArticleResponse
import org.example.alpahmap.service.ArticleService
import org.springframework.web.bind.annotation.PostMapping
import org.springframework.web.bind.annotation.RequestBody
import org.springframework.web.bind.annotation.RequestMapping
import org.springframework.web.bind.annotation.RestController

@RestController
@RequestMapping("/article")
class ArticleController(
    val articleService: ArticleService,
) {

    @PostMapping
    fun createArticle(
        @RequestBody request: ArticleRequest,
    ): ArticleResponse {
        return articleService.createArticle(request)
    }

}