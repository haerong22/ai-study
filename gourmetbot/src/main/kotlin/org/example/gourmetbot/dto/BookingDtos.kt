package org.example.gourmetbot.dto

object BookingDtos {

    data class CustomerCheckRequest(
        val phoneNumber: String,
    )

    data class TableSearchRequest(
        val dateTime: String,
        val partySize: Int,
        val preferredType: String,
    )

    data class CreateReservationRequest(
        val customerName: String,
        val phoneNumber: String,
        val dateTime: String,
        val tableId: Long,
        val partySize: Int,
        val allergies: String,
        val specialRequests: String,
    )

    data class CancelReservationRequest(
        val phoneNumber: String,
        val reservationId: Long,
    )

    data class MyBookingRequest(
        val phoneNumber: String,
    )

    data class OrderItemRequest(
        val menuName: String,
        val quantity: Int,
        val request: String,
    )

    data class EstimateRequest(
        val orderItems: List<OrderItemRequest>,
    )

    data class AddOrderRequest(
        val reservationId: Long,
        val orderItems: List<OrderItemRequest>,
    )

    data class OrderHistoryRequest(
        val reservationId: Long,
    )

    data class CancelOrderRequest(
        val reservationId: Long,
    )

    data class CancelMenuItemRequest(
        val reservationId: Long,
        val menuName: String,
    )
}
