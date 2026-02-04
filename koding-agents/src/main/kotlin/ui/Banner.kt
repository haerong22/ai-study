package org.example.ui

import org.example.ui.ColorScheme.BOLD
import org.example.ui.ColorScheme.BRIGHT_CYAN
import org.example.ui.ColorScheme.BRIGHT_GREEN
import org.example.ui.ColorScheme.MUTED
import org.example.ui.ColorScheme.PRIMARY
import org.example.ui.ColorScheme.RESET

object Banner {
    private const val VERSION = "1.0.0"

    private val asciiArt = """
$BRIGHT_CYAN
██╗ ██╗ ██████╗ ██████╗  ██╗███╗   ██╗ ██████╗
██║ ██╔╝██╔═══██╗██╔══██╗██║████╗  ██║██╔════╝
█████╔╝ ██║   ██║██║  ██║██║██╔██╗ ██║██║  ███╗
██╔═██╗ ██║   ██║██║  ██║██║██║╚██╗██║██║   ██║
██║ ██╗╚██████╔╝██████╔╝ ██║██║ ╚████║╚██████╔╝
╚═╝ ╚═╝ ╚═════╝ ╚═════╝  ╚═╝╚═╝  ╚═══╝ ╚═════╝
 █████╗ ██████╗  ███████╗███╗   ██╗████████╗
██╔══██╗██╔════╝ ██╔════╝████╗  ██║╚══██╔══╝
███████║██║  ███╗█████╗  ██╔██╗ ██║   ██║
██╔══██║██║   ██║██╔══╝  ██║╚██╗██║   ██║
██║  ██║╚██████╔╝███████╗██║ ╚████║   ██║
╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═══╝   ╚═╝
$RESET
    """.trimIndent()

    fun printWelcome() {
        println()
        println(asciiArt)
        println()
        println("${BOLD}${PRIMARY}╔═══════════════════════════════════════════════════════╗$RESET")
        println("${BOLD}${PRIMARY}║        AI-Powered Coding Assistant for Kotlin         ║$RESET")
        println("${BOLD}${PRIMARY}║                     Version $VERSION                  ║$RESET")
        println("${BOLD}${PRIMARY}╚═══════════════════════════════════════════════════════╝$RESET")
        println()
        println("${MUTED} Type ${BRIGHT_CYAN}/help$MUTED for commands or start coding!$RESET")
        println("${MUTED} Type ${BRIGHT_CYAN}/quit$MUTED or ${BRIGHT_CYAN}/exit$MUTED to leave.$RESET")
        println()
    }

    fun printGoodbye() {
        println()
        println("${BRIGHT_GREEN}╔═══════════════════════════════════════╗$RESET")
        println("${BRIGHT_GREEN}║ ${BOLD}Happy Coding! See you!$RESET$BRIGHT_GREEN║$RESET")
        println("${BRIGHT_GREEN}╚═══════════════════════════════════════╝$RESET")
        println()
    }
}