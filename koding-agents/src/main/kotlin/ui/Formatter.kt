package org.example.ui

import org.example.ui.ColorScheme.BOLD
import org.example.ui.ColorScheme.BRIGHT_CYAN
import org.example.ui.ColorScheme.MUTED
import org.example.ui.ColorScheme.RESET
import org.example.ui.ColorScheme.SUCCESS

object Formatter {
    fun userPrompt(text: String = ""): String {
        return "${BOLD}${BRIGHT_CYAN}User >${RESET} $text"
    }

    fun assistantPrompt(): String {
        return "${BOLD}${SUCCESS}Assistant >${RESET}"
    }

    fun divider(char: String = "─", length: Int = 60): String {
        return "$MUTED${char.repeat(length)}$RESET"
    }

    fun errorBox(message: String): String {
        return buildString {
            appendLine("${ColorScheme.ERROR}╭─ ERROR ─╮${RESET}")
            appendLine("${ColorScheme.ERROR}│ $message${RESET}")
            appendLine("${ColorScheme.ERROR}╰──────────╯${RESET}")
        }
    }
}