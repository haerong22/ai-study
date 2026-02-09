package org.example.gourmetbot.entity

import jakarta.persistence.Entity
import jakarta.persistence.EnumType
import jakarta.persistence.Enumerated
import jakarta.persistence.FetchType
import jakarta.persistence.GeneratedValue
import jakarta.persistence.GenerationType
import jakarta.persistence.Id
import jakarta.persistence.ManyToOne
import org.example.gourmetbot.domain.ReservationStatus
import java.time.LocalDateTime

@Entity
class Reservation(
    val reservationTime: LocalDateTime,
    @ManyToOne(fetch = FetchType.LAZY)
    val customer: Customer,
    @ManyToOne(fetch = FetchType.LAZY)
    val restaurantTable: RestaurantTable,
    val partySize: Int,
    val allergies: String,
    @Enumerated(EnumType.STRING)
    val status: ReservationStatus,
    val specialRequests: String,
) {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long? = null
}