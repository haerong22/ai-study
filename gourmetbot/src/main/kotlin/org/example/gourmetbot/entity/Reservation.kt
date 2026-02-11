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
    val allergies: String?,
    val specialRequests: String?,
) {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long? = null

    @Enumerated(EnumType.STRING)
    var status: ReservationStatus = ReservationStatus.CONFIRMED

    val formattedTime: String
        get() = "${reservationTime.toLocalDate()} ${reservationTime.toLocalTime()}"

    fun isCancellableBy(phone: String): Boolean =
        customer.phoneNumber == phone && reservationTime.isAfter(LocalDateTime.now())

    fun cancel() {
        status = ReservationStatus.CANCELLED
    }
}