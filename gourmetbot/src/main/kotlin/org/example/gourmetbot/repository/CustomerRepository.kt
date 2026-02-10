package org.example.gourmetbot.repository

import org.example.gourmetbot.entity.Customer
import org.springframework.data.jpa.repository.JpaRepository

interface CustomerRepository: JpaRepository<Customer, Long> {

    fun findByPhoneNumber(phoneNumber: String): Customer?
}