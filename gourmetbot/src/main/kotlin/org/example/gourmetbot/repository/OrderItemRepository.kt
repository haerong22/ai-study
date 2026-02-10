package org.example.gourmetbot.repository

import org.example.gourmetbot.entity.OrderItem
import org.springframework.data.jpa.repository.JpaRepository

interface OrderItemRepository: JpaRepository<OrderItem, Long> {

    fun findByReservationId(reservationId: Long): List<OrderItem>

    fun deleteByReservationId(reservationId: Long)

    fun existsByReservationId(reservationId: Long): Boolean

    fun existsByReservationIdAndMenu_Name(reservationId: Long, menuName: String): Boolean

    fun findByReservationIdAndMenu_Name(reservationId: Long, menuName: String): List<OrderItem>
}