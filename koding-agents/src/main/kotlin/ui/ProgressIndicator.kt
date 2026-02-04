package org.example.ui

import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.NonCancellable.isActive
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import org.example.ui.ColorScheme.BRIGHT_CYAN
import org.example.ui.ColorScheme.RESET

class ProgressIndicator(
    private val message: String = "Thinking"
) {
    private var job: Job? = null
    private val frames = listOf("⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏")
    private var currentFrame = 0
    fun start() {
        job = CoroutineScope(Dispatchers.Default).launch {
            while (isActive) {
                val frame = frames[currentFrame % frames.size]
                print("\r$BRIGHT_CYAN$frame$RESET $message...")
                currentFrame++
                delay(100)
            }
        }
    }

    fun stop() {
        job?.cancel()
        print("\r${" ".repeat(message.length + 10)}\r")
    }
}