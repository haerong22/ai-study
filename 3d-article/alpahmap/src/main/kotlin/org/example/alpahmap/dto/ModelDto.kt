package org.example.alpahmap.dto

data class ModelDto(
    val id: Long,
    val filename: String,
    val filepath: String,
    val latitude: Double,
    val longitude: Double,
    val height: Int,
    val scale: Int,
)
