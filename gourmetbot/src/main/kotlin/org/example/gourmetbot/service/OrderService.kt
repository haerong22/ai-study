package org.example.gourmetbot.service

import org.example.gourmetbot.dto.BookingDtos.OrderItemRequest
import org.example.gourmetbot.entity.OrderItem
import org.example.gourmetbot.repository.MenuRepository
import org.example.gourmetbot.repository.OrderItemRepository
import org.example.gourmetbot.repository.ReservationRepository
import org.springframework.data.repository.findByIdOrNull
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional
import java.text.NumberFormat

@Service
class OrderService(
    private val menuRepository: MenuRepository,
    private val orderItemRepository: OrderItemRepository,
    private val reservationRepository: ReservationRepository,
) {
    private val numberFormat = NumberFormat.getInstance()

    @Transactional(readOnly = true)
    fun getMenuBoard(): String {
        val menus = menuRepository.findAll()
        if (menus.isEmpty()) return "현재 준비된 메뉴가 없습니다."

        return menus
            .groupBy { it.category }
            .entries.joinToString("\n\n") { (category, items) ->
                val itemLines = items.joinToString("\n") { "- ${it.name}: ${formatPrice(it.price)}원" }
                "[${category}]\n${itemLines}"
            }
    }

    @Transactional(readOnly = true)
    fun calculateEstimate(orderItems: List<OrderItemRequest>): String {
        var totalAmount = 0

        val lines = orderItems.map { item ->
            val menu = menuRepository.findByName(item.menuName)
                ?: return@map "- [X] ${item.menuName}: 메뉴 정보 없음"

            val itemTotal = menu.price * item.quantity
            totalAmount += itemTotal
            "- ${item.menuName} ${item.quantity}개: ${formatPrice(itemTotal)}원"
        }

        return buildString {
            appendLine("요청하신 메뉴의 견적입니다:")
            appendLine(lines.joinToString("\n"))
            appendLine("--------------------------------")
            append("총 예상 금액: ${formatPrice(totalAmount)}원")
        }
    }

    @Transactional
    fun addOrderToReservation(reservationId: Long, items: List<OrderItemRequest>): String {
        val reservation = findReservationOrThrow(reservationId)

        var totalAmount = 0
        val savedOrders = items.mapNotNull { item ->
            val menu = menuRepository.findByName(item.menuName) ?: return@mapNotNull null

            totalAmount += menu.price * item.quantity
            orderItemRepository.save(
                OrderItem(
                    reservation = reservation,
                    menu = menu,
                    quantity = item.quantity,
                    request = item.request,
                )
            )
        }

        return "예약(#${reservationId})에 메뉴 ${savedOrders.size}건이 정상적으로 추가되었습니다.\n" +
                "현재 추가된 주문의 총 금액은 [${formatPrice(totalAmount)}원]입니다."
    }

    @Transactional(readOnly = true)
    fun getOrderHistory(reservationId: Long): String {
        validateReservationExists(reservationId)

        val orders = orderItemRepository.findByReservationId(reservationId)
        if (orders.isEmpty()) return "예약번호 #${reservationId}에 등록된 주문 내역이 없습니다."

        var total = 0
        return buildString {
            appendLine("예약번호 #${reservationId}의 주문내역 입니다.")
            appendLine("--------------------------------")
            for (item in orders) {
                val price = item.menu.price * item.quantity
                total += price
                appendLine("- ${item.menu.name} ${item.quantity}개: ${formatPrice(price)}원")
            }
            appendLine("--------------------------------")
            appendLine("총 합계: ${formatPrice(total)}원")
        }
    }

    @Transactional
    fun cancelOrder(reservationId: Long): String {
        validateReservationExists(reservationId)
        orderItemRepository.deleteByReservationId(reservationId)

        return "예약번호 #${reservationId}의 모든 선주문 내역이 정상적으로 취소되었습니다. (예약은 유지됩니다)"
    }

    @Transactional
    fun removeMenuItem(reservationId: Long, menuName: String): String {
        val items = orderItemRepository.findByReservationIdAndMenu_Name(reservationId, menuName)
        if (items.isEmpty()) return "예약(${reservationId})에 주문된 '${menuName}'메뉴가 없습니다."

        orderItemRepository.deleteAll(items)

        return "예약(${reservationId})에서 '${menuName}'메뉴(총 ${items.size}건)를 정상적으로 취소했습니다."
    }

    private fun findReservationOrThrow(reservationId: Long) =
        reservationRepository.findByIdOrNull(reservationId)
            ?: throw IllegalArgumentException("예약 정보를 찾을 수 없습니다.")

    private fun validateReservationExists(reservationId: Long) {
        require(reservationRepository.existsById(reservationId)) { "존재하지 않는 예약 번호입니다." }
    }

    private fun formatPrice(price: Int): String = numberFormat.format(price)
}
