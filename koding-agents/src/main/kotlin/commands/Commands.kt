package org.example.commands

import org.example.storage.AgentMemoryStorage
import org.example.ui.ColorScheme

class HelpCommand(private val registry: CommandRegistry) : Command {
    override val name = "help"
    override val aliases = listOf("h", "?")
    override val description = "Show available commands"
    override suspend fun execute(args: List<String>): CommandResult {
        println()
        println("${ColorScheme.BOLD}${ColorScheme.BRIGHT_CYAN}Available Commands:${ColorScheme.RESET}")
        println()
        registry.getAllCommands().sortedBy { it.name }.forEach { cmd ->
            val aliasText = if (cmd.aliases.isNotEmpty()) {
                " ${ColorScheme.MUTED}(${
                    cmd.aliases.joinToString(", ") {
                        "/$it"
                    }
                })${ColorScheme.RESET}"
            } else ""
            println(" ${ColorScheme.BRIGHT_CYAN}${cmd.usage}${ColorScheme.RESET}$aliasText")
            println(" ${ColorScheme.MUTED}${cmd.description}${ColorScheme.RESET}")
        }
        println()
        return CommandResult.Success()
    }
}

class ExitCommand : Command {
    override val name = "exit"
    override val aliases = listOf("quit", "q")
    override val description = "Exit the application"
    override suspend fun execute(args: List<String>): CommandResult {
        return CommandResult.Exit
    }
}

class ClearCommand : Command {
    override val name = "clear"
    override val aliases = listOf("reset")
    override val description = "Clear session and start fresh"
    override suspend fun execute(args: List<String>): CommandResult {
        println(ColorScheme.success("Session cleared. Starting fresh!"))
        return CommandResult.ClearSession
    }
}
class MemoryCommand(
    private val memoryStorage: AgentMemoryStorage
) : Command {
    override val name = "memory"
    override val aliases = listOf("mem")
    override val description = "Add project memory (usage: /memory add <content>)"
    override val usage = "/memory add <content>"
    override suspend fun execute(args: List<String>): CommandResult {
        if (args.isEmpty() || args.first() != "add") {
            println(ColorScheme.warning("Usage: /memory add <content>"))
            return CommandResult.Success()
        }
        val content = args.drop(1).joinToString(" ")
        if (content.isBlank()) {
            println(ColorScheme.warning("Please provide content to remember"))
            return CommandResult.Success()
        }
        memoryStorage.addMemory(content)
        println(ColorScheme.success("Memory saved: $content"))
        return CommandResult.Success()
    }
}