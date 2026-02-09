package org.example.gourmetbot.entity

import jakarta.persistence.Entity
import jakarta.persistence.FetchType
import jakarta.persistence.GeneratedValue
import jakarta.persistence.GenerationType
import jakarta.persistence.Id
import jakarta.persistence.JoinColumn
import jakarta.persistence.ManyToOne

@Entity
class OrderItem(
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "reservation_id")
    val reservation: Reservation,

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "menu_id")
    val menu: Menu,

    val quantity: Int,
    val request: String,
) {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long? = null
}