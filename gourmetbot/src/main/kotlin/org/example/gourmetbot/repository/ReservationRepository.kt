package org.example.gourmetbot.repository

import org.example.gourmetbot.entity.Reservation
import org.springframework.data.jpa.repository.JpaRepository
import org.springframework.data.jpa.repository.Query
import org.springframework.data.repository.query.Param
import java.time.LocalDateTime

interface ReservationRepository : JpaRepository<Reservation, Long> {

    @Query("""
        SELECT r.restaurantTable.id
          FROM Reservation r
         WHERE r.reservationTime < :endTime
           AND r.reservationTime > :startTimeMinus2Hours
           AND r.status = 'CONFIRMED'
    """)
    fun findBookedTableIds(
        @Param("startTimeMinus2Hours") startTimeMinus2Hours: LocalDateTime,
        @Param("endTime") endTime: LocalDateTime,
    ): List<Long>

    @Query("""
        SELECT r 
          FROM Reservation r
         WHERE r.customer.phoneNumber = :phoneNumber
           AND r.reservationTime > CURRENT_TIMESTAMP
           AND r.status = 'CONFIRMED'
    """)
    fun findUpcomingReservations(@Param("phoneNumber") phoneNumber: String): List<Reservation>

}