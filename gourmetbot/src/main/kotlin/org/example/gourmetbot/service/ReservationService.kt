package org.example.gourmetbot.service

import org.example.gourmetbot.domain.TableType
import org.example.gourmetbot.entity.Customer
import org.example.gourmetbot.entity.Reservation
import org.example.gourmetbot.repository.CustomerRepository
import org.example.gourmetbot.repository.OrderItemRepository
import org.example.gourmetbot.repository.ReservationRepository
import org.example.gourmetbot.repository.RestaurantTableRepository
import org.springframework.data.repository.findByIdOrNull
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional
import java.time.LocalDateTime

@Service
class ReservationService(
    private val restaurantTableRepository: RestaurantTableRepository,
    private val reservationRepository: ReservationRepository,
    private val customerRepository: CustomerRepository,
    private val orderItemRepository: OrderItemRepository,
) {

    @Transactional(readOnly = true)
    fun findAvailableTables(time: LocalDateTime, size: Int, typeStr: String?): String {
        val type = typeStr?.let {
            runCatching { TableType.valueOf(it) }.getOrNull()
                ?: return "잘못된 좌석 타입입니다. WINDOW, ROOM, HALL 중 하나여야 합니다."
        }

        val candidates = if (type != null) {
            restaurantTableRepository.findByCapacityGreaterThanEqualAndType(size, type)
        } else {
            restaurantTableRepository.findByCapacityGreaterThanEqual(size)
        }

        val bookedIds = reservationRepository.findBookedTableIds(
            time.minusHours(2), time.plusHours(2)
        )
        val availableTables = candidates.filter { it.id !in bookedIds }

        if (availableTables.isEmpty()) {
            return "죄송합니다. 해당 조건에 맞는 빈 테이블이 없습니다."
        }

        return availableTables.joinToString(
            separator = "\n",
            prefix = "예약 가능 테이블 목록: \n"
        ) { "- [ID:${it.id}] ${it.type}타입 (${it.capacity}인석)" }
    }

    @Transactional
    fun createReservation(
        name: String,
        phone: String,
        time: LocalDateTime,
        tableId: Long,
        size: Int,
        allergies: String?,
        specialRequests: String?
    ): String {
        val table = restaurantTableRepository.findByIdOrNull(tableId)
            ?: throw IllegalArgumentException("존재하지 않는 테이블 입니다.")

        val allergyMemo = allergies
            ?.takeUnless { it in listOf("없음", "None") }
            ?.let { "주의: $it" }
            ?: "신규등록"

        val customer = customerRepository.findByPhoneNumber(phone)
            ?: customerRepository.save(
                Customer(
                    name = name,
                    phoneNumber = phone,
                    memo = allergyMemo,
                    visitCount = 0,
                )
            )
        customer.visit()

        val reservation = reservationRepository.save(
            Reservation(
                customer = customer,
                restaurantTable = table,
                reservationTime = time,
                partySize = size,
                allergies = allergies,
                specialRequests = specialRequests,
            )
        )

        return "예약이 확정되었습니다! \n예약번호 [#${reservation.id}]. ${name}님을 ${table.id}테이블(${table.type})로 모시겠습니다."
    }

    @Transactional(readOnly = true)
    fun checkCustomer(phone: String): String {
        return customerRepository.findByPhoneNumber(phone)
            ?.let { "기존 고객입니다. 이름: ${it.name}, 방문횟수: ${it.visitCount}회. (VIP 여부 확인 필요)" }
            ?: "신규 고객입니다."
    }

    @Transactional
    fun cancelReservation(phone: String, reservationId: Long): String {
        val reservation = reservationRepository.findByIdOrNull(reservationId)
            ?: return "해당 예약 번호의 예약 내역이 없습니다."

        if (!reservation.isCancellableBy(phone)) {
            return "예약을 취소할 수 없습니다. 예약 정보를 다시 확인해 주세요."
        }

        orderItemRepository.deleteByReservationId(reservationId)
        reservation.cancel()

        return buildString {
            appendLine("예약이 정상적으로 취소되었습니다.")
            appendLine("(함께 주문하신 메뉴 내역도 모두 삭제되었습니다.)")
            append("[취소내역] 날짜: ${reservation.formattedTime}")
            append(", 인원: ${reservation.partySize}")
        }
    }

    @Transactional(readOnly = true)
    fun getMyBookings(phone: String): String {
        val bookings = reservationRepository.findUpcomingReservations(phone)

        if (bookings.isEmpty()) {
            return "해당 번호로 잡혀있는 예정된 예약이 없습니다."
        }

        return bookings.joinToString(
            separator = "\n",
            prefix = "고객님의 예약 내역입니다.\n"
        ) { "- ${it.formattedTime}, ${it.partySize}명, ${it.restaurantTable.type}타입 테이블 (예약번호 #${it.id})" }
    }
}
