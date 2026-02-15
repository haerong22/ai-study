package org.example.gourmetbot.tools

import org.example.gourmetbot.dto.BookingDtos
import org.example.gourmetbot.service.OrderService
import org.springframework.ai.tool.annotation.Tool
import org.springframework.ai.vectorstore.SearchRequest
import org.springframework.ai.vectorstore.VectorStore
import org.springframework.stereotype.Component

@Component
class OrderTools(
    private val orderService: OrderService,
    private val vectorStore: VectorStore,
) {

    @Tool(description = "전체 메뉴를 보여줍니다.")
    fun showMenuList(): String {
        return orderService.getMenuBoard()
    }

    @Tool(description = "주문 예상 견적을 계산합니다.")
    fun getPriceEstimate(req: BookingDtos.EstimateRequest): String {
        return orderService.calculateEstimate(req.orderItems)
    }

    @Tool(description = "예약에 메뉴 주문을 추가합니다.")
    fun addOrder(req: BookingDtos.AddOrderRequest): String {
        return orderService.addOrderToReservation(req.reservationId, req.orderItems)
    }

    @Tool(description = "주문 내역을 조회합니다.")
    fun checkOrderedMenu(req: BookingDtos.OrderHistoryRequest): String {
        return orderService.getOrderHistory(req.reservationId)
    }

    @Tool(description = "특정 메뉴 하나를 취소합니다.")
    fun removeMenuItem(req: BookingDtos.CancelMenuItemRequest): String {
        return orderService.removeMenuItem(req.reservationId, req.menuName)
    }

    @Tool(description = "전체 주문을 취소합니다.")
    fun cancelOrder(req: BookingDtos.CancelOrderRequest): String {
        return orderService.cancelOrder(req.reservationId)
    }

    @Tool(description = "고객이 '메뉴 추천'을 원하건, 특정 맛/재료를 찾을 때 상세 정보를 검색합니다.")
    fun searchMenuDescriptions(query: String): String {
        val results = vectorStore.similaritySearch(SearchRequest.builder().query(query).build())

        if (results.isEmpty()) return "관련 정보를 찾을 수 없습니다."

        return results.joinToString("\n") { it.text.toString() }
    }
}