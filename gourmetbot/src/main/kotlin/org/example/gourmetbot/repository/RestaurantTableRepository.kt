package org.example.gourmetbot.repository

import org.example.gourmetbot.domain.TableType
import org.example.gourmetbot.entity.RestaurantTable
import org.springframework.data.jpa.repository.JpaRepository

interface RestaurantTableRepository: JpaRepository<RestaurantTable, Long> {

    fun findByCapacityGreaterThanEqual(capacity: Int): List<RestaurantTable>

    fun findByCapacityGreaterThanEqualAndType(capacity: Int, type: TableType): List<RestaurantTable>
}