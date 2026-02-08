package org.example.gourmetbot.entity

import jakarta.persistence.Entity
import jakarta.persistence.EnumType
import jakarta.persistence.Enumerated
import jakarta.persistence.GeneratedValue
import jakarta.persistence.GenerationType
import jakarta.persistence.Id
import org.example.gourmetbot.domain.TableType

@Entity
class RestaurantTable(
    val capacity: Int,
    @Enumerated(EnumType.STRING)
    val type: TableType,
) {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long? = null
}