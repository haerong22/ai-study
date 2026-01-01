package org.example.alpahmap.entity

import jakarta.persistence.Entity
import jakarta.persistence.GeneratedValue
import jakarta.persistence.GenerationType
import jakarta.persistence.Id

@Entity
class Model(
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long? = null,
    val filename: String,
    val filepath: String,
    val latitude: Double,
    val longitude: Double,
    val height: Int,
) {
}