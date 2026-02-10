package org.example.gourmetbot.repository

import org.example.gourmetbot.entity.Menu
import org.springframework.data.jpa.repository.JpaRepository

interface MenuRepository: JpaRepository<Menu, Long> {

    fun findByName(name: String): Menu?
}
