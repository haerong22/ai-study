package org.example.gourmetbot.config

import org.example.gourmetbot.domain.TableType
import org.example.gourmetbot.entity.Customer
import org.example.gourmetbot.entity.Menu
import org.example.gourmetbot.entity.RestaurantTable
import org.example.gourmetbot.repository.CustomerRepository
import org.example.gourmetbot.repository.MenuRepository
import org.example.gourmetbot.repository.RestaurantTableRepository
import org.slf4j.LoggerFactory
import org.springframework.boot.CommandLineRunner
import org.springframework.stereotype.Component

@Component
class DataLoader(
    private val restaurantTableRepository: RestaurantTableRepository,
    private val customerRepository: CustomerRepository,
    private val menuRepository: MenuRepository,
) : CommandLineRunner {

    private val log = LoggerFactory.getLogger(javaClass)

    override fun run(vararg args: String?) {
        initTables()
        initMenus()
        initCustomers()
    }

    private fun initTables() {
        if (restaurantTableRepository.count() > 0) return
        restaurantTableRepository.saveAll(
            listOf(
                RestaurantTable(4, TableType.WINDOW),
                RestaurantTable(4, TableType.WINDOW),
                RestaurantTable(4, TableType.HALL),
                RestaurantTable(6, TableType.HALL),
                RestaurantTable(8, TableType.ROOM),
            )
        )
        log.info("[Init] 레스토랑 테이블 5개 생성 완료")
    }

    private fun initMenus() {
        if (menuRepository.count() > 0) return
        menuRepository.saveAll(
            listOf(
                Menu("티본 스테이크", 150000, "MAIN"),
                Menu("봉골레 파스타", 28000, "MAIN"),
                Menu("트러플 리조또", 35000, "MAIN"),
                Menu("카베르네 소비뇽", 80000, "WINE"),
                Menu("샴페인", 120000, "WINE"),
                Menu("수제 티라미수", 12000, "DESSERT"),
            )
        )
        log.info("[Init] 메뉴 데이터 생성 완료")
    }

    private fun initCustomers() {
        if (customerRepository.count() > 0) return
        customerRepository.save(
            Customer("홍길동", "010-1234-5678", 10, "레드 와인을 선호하심")
        )
        log.info("[Init] VIP 고객(홍길동) 생성 완료")
    }
}