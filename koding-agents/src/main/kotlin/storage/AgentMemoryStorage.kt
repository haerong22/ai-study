package org.example.storage

interface AgentMemoryStorage {
    suspend fun addMemory(content: String)
    suspend fun getMemory(): String?
}