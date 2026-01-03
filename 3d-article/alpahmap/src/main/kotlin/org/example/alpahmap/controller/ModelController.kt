package org.example.alpahmap.controller

import org.example.alpahmap.dto.ModelDto
import org.example.alpahmap.service.ModelService
import org.springframework.core.io.InputStreamResource
import org.springframework.http.MediaType
import org.springframework.http.ResponseEntity
import org.springframework.web.bind.annotation.GetMapping
import org.springframework.web.bind.annotation.PathVariable
import org.springframework.web.bind.annotation.PostMapping
import org.springframework.web.bind.annotation.RequestMapping
import org.springframework.web.bind.annotation.RequestParam
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
        @RequestParam latitude: Double,
        @RequestParam longitude: Double,
        @RequestParam height: Int,
        @RequestParam scale: Int,
    ): ModelDto {
        return modelService.createModel(file, latitude, longitude, height, scale)
    }

    @GetMapping("/{modelId}")
    fun getModel(
        @PathVariable modelId: Long,
    ): ResponseEntity<InputStreamResource> {
        val modelResource = modelService.getModelResource(modelId)
        return ResponseEntity.ok()
            .header("Content-Disposition", "attachment; filename=\"${modelResource.filename}\"")
            .contentType(MediaType.parseMediaType("model/gltf-binary"))
            .body(modelResource)
    }
}