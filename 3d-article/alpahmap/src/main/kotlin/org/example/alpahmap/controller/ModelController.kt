package org.example.alpahmap.controller

import org.example.alpahmap.dto.ModelDto
import org.example.alpahmap.service.ModelService
import org.springframework.web.bind.annotation.PostMapping
import org.springframework.web.bind.annotation.RequestMapping
import org.springframework.web.bind.annotation.RequestPart
import org.springframework.web.bind.annotation.RestController
import org.springframework.web.multipart.MultipartFile

@RestController
@RequestMapping("/article/model")
class ModelController(
    private val modelService: ModelService
) {

    @PostMapping
    fun createModel(
        @RequestPart file: MultipartFile,
        @RequestPart latitude: Double,
        @RequestPart longitude: Double,
        @RequestPart height: Int,
    ): ModelDto {
        return modelService.createModel(file, latitude, longitude, height)
    }
}