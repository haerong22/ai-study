package org.example.ui

object ColorScheme {
    // 기본 ANSI 색상 코드
    const val RESET = "\u001B[0m"
    const val BOLD = "\u001B[1m"
    const val DIM = "\u001B[2m"
    const val ITALIC = "\u001B[3m"
    // 밝은 전경색
    const val BRIGHT_BLACK = "\u001B[90m"
    const val BRIGHT_RED = "\u001B[91m"
    const val BRIGHT_GREEN = "\u001B[92m"
    const val BRIGHT_YELLOW = "\u001B[93m"
    const val BRIGHT_BLUE = "\u001B[94m"
    const val BRIGHT_MAGENTA = "\u001B[95m"
    const val BRIGHT_CYAN = "\u001B[96m"
    // 시맨틱 색상
    const val PRIMARY = BRIGHT_CYAN
    const val SUCCESS = BRIGHT_GREEN
    const val WARNING = BRIGHT_YELLOW
    const val ERROR = BRIGHT_RED
    const val INFO = BRIGHT_MAGENTA
    const val MUTED = BRIGHT_BLACK
    fun success(text: String): String = "${SUCCESS}✓ $text$RESET"
    fun error(text: String): String = "${ERROR}✗ $text$RESET"
    fun warning(text: String): String = "${WARNING}⚠ $text$RESET"
    fun info(text: String): String = "${INFO}ℹ $text$RESET"
}