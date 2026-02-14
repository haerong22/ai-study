package org.example.gourmetbot.tools

import org.example.gourmetbot.dto.BookingDtos
import org.example.gourmetbot.service.ReservationService
import org.springframework.ai.tool.annotation.Tool
import org.springframework.stereotype.Component
import java.time.LocalDateTime

@Component
class ReservationTools(
    private val reservationService: ReservationService,
) {

    @Tool(description = "고객의 연락처로 방문 이력을 조회합니다.")
    fun checkCustomerHistory(req: BookingDtos.CustomerCheckRequest): String {
        return reservationService.checkCustomer(req.phoneNumber)
    }

    @Tool(description = "날짜, 인원, 선호 좌석에 맞춰 '예약 가능한 테이블 목록'을 조회합니다.")
    fun searchTables(req: BookingDtos.TableSearchRequest): String {
        return try {
            reservationService.findAvailableTables(LocalDateTime.parse(req.dateTime), req.partySize, req.preferredType)
        } catch (e: Exception) {
            "오류: 날짜 형식이 올바르지 않습니다."
        }
    }

    @Tool(description = "최종적으로 예약을 생성합니다.")
    fun bookTable(req: BookingDtos.CreateReservationRequest): String {
        return reservationService.createReservation(
            req.customerName,
            req.phoneNumber,
            LocalDateTime.parse(req.dateTime),
            req.tableId,
            req.partySize,
            req.allergies,
            req.specialRequests
        )
    }

    @Tool(description = "예정된 예약을 취소합니다.")
    fun cancelReservation(req: BookingDtos.CancelReservationRequest): String {
        return reservationService.cancelReservation(req.phoneNumber, req.reservationId)
    }

    @Tool(description = "나의 에약 목록을 조회합니다.")
    fun checkMyBookings(req: BookingDtos.MyBookingRequest): String {
        return reservationService.getMyBookings(req.phoneNumber)
    }
}