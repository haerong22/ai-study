package org.example.gourmetbot.config

import jakarta.annotation.PostConstruct
import org.slf4j.LoggerFactory
import org.springframework.ai.document.Document
import org.springframework.ai.transformer.splitter.TokenTextSplitter
import org.springframework.ai.vectorstore.VectorStore
import org.springframework.beans.factory.annotation.Value
import org.springframework.core.io.Resource
import org.springframework.jdbc.core.simple.JdbcClient
import org.springframework.stereotype.Component
import java.lang.Thread.sleep

@Component
class RagLoader(
    private val vectorStore: VectorStore,
    private val jdbcClient: JdbcClient,
    @Value("classpath:menu.txt") private val resource: Resource,
) {
    private val log = LoggerFactory.getLogger(javaClass)

    @PostConstruct
    fun init() {
        try {
            val sql = "select count(*) from vector_store"
            val count = jdbcClient.sql(sql).query(Int::class.java).single()
            if (count == 0) {
                log.info("데이터 로딩을 시작합니다.")

                resource.inputStream.bufferedReader(Charsets.UTF_8).use { br ->
                    val documents = br.lines().map { Document(it) }
                    val splitter = TokenTextSplitter(800, 200, 10, 5000, true)

                    for (doc in documents) {
                        val chunks = splitter.split(doc)
                        vectorStore.accept(chunks)
                        log.info("${chunks.size}개의 청크가 저장되었습니다.")
                        sleep(200)
                    }
                }

                log.info("데이터 로딩 완료.")
            } else {
                log.info("데이터가 이미 로드되어 있습니다.(총 ${count}개)")
            }
        } catch (e: Exception) {
            log.error("데이터 로딩 중 오류 발생", e)
        }
    }
}