package org.example.alpahmap.service

import org.example.alpahmap.dto.ModelDto
import org.example.alpahmap.entity.Model
import org.example.alpahmap.repository.ModelRepository
import org.springframework.core.io.InputStreamResource
import org.springframework.stereotype.Service
import org.springframework.web.multipart.MultipartFile
import java.io.File
import java.util.UUID

@Service
class ModelService(
    private val modelRepository: ModelRepository,
) {

    fun createModel(file: MultipartFile, latitude: Double, longitude: Double, height: Int): ModelDto {

        val uploadDir = File(System.getProperty("user.dir"), "models")

        if (!uploadDir.exists()) {
            uploadDir.mkdirs()
        }

        val filename = file.originalFilename ?: "${UUID.randomUUID()}.glb"
        val destFile = File(uploadDir, filename)

        file.transferTo(destFile)

        val model = Model(
            filename = filename,
            filepath = destFile.absolutePath,
            latitude = latitude,
            longitude = longitude,
            height = height
        )

        val modelEntity = modelRepository.save(model)

        return ModelDto(
            id = modelEntity.id!!,
            filename = modelEntity.filename,
            filepath = modelEntity.filepath,
            latitude = modelEntity.latitude,
            longitude = modelEntity.longitude,
            height = modelEntity.height
        )
    }

    fun getModelResource(modelId: Long): InputStreamResource {
        val model = modelRepository.findById(modelId).orElseThrow()

        val file = File(model.filepath)

        if (!file.exists()) throw RuntimeException("File does not exist: ${model.filepath}")

        return InputStreamResource(file.inputStream())
    }
}