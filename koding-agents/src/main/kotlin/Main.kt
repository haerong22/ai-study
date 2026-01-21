package org.example

fun main() {
    val apiKey = System.getenv("OPENAI_API_KEY")

    println(apiKey.take(15))
}