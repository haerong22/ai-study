package org.example.alpahmap.repository

import org.example.alpahmap.entity.Model
import org.springframework.data.repository.CrudRepository

interface ModelRepository : CrudRepository<Model, Long> {
}