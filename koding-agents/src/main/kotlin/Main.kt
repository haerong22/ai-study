package org.example

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import org.example.commands.ClearCommand
import org.example.commands.CommandRegistry
import org.example.commands.CommandResult
import org.example.commands.ExitCommand
import org.example.commands.HelpCommand
import org.example.commands.MemoryCommand
import org.example.ui.Banner
import org.example.ui.ColorScheme
import org.example.ui.Formatter
import org.example.ui.ProgressIndicator
import org.jline.reader.EndOfFileException
import org.jline.reader.LineReaderBuilder
import org.jline.reader.UserInterruptException
import org.jline.terminal.TerminalBuilder

suspend fun main() {
    val apiKey = System.getenv("OPENAI_API_KEY")
        ?: error("OPENAI_API_KEY 환경 변수가 설정되지 않았습니다")
    var agent = CodingAgent(apiKey = apiKey)
    // 명령어 등록
    val commandRegistry = CommandRegistry()
    commandRegistry.registerAll(
        ExitCommand(),
        ClearCommand(),
        MemoryCommand(agent.agentMemoryStorage),
    )
    commandRegistry.register(HelpCommand(commandRegistry))
    // JLine3 터미널 설정
    val terminal = TerminalBuilder.builder().system(true).build()
    val lineReader = LineReaderBuilder.builder().terminal(terminal).build()
    // 웰컴 배너
    Banner.printWelcome()
    // 메인 REPL 루프
    while (true) {
        try {
            val userInput = lineReader.readLine(Formatter.userPrompt()).trim()
            if (userInput.isEmpty()) continue
            // 명령어 처리
            if (userInput.startsWith("/")) {
                when (val result = commandRegistry.execute(userInput)) {
                    is CommandResult.Exit -> {
                        Banner.printGoodbye(); break
                    }

                    is CommandResult.ClearSession -> {
                        agent = CodingAgent(apiKey = apiKey)
                    }

                    is CommandResult.Error -> {
                        println(ColorScheme.error(result.message))
                    }

                    is CommandResult.Success -> {}
                    null -> {
                        println(ColorScheme.error("Unknown command. Type /help"))
                    }
                }
                continue
            }
            // Agent 실행
            val spinner = ProgressIndicator("Thinking")
            spinner.start()
            val result = agent.chat(userInput)
            spinner.stop()
            println(Formatter.assistantPrompt())
            println()
            println(result)
            println()
            println(Formatter.divider())
            println()
        } catch (e: UserInterruptException) {
            println()
            println(ColorScheme.warning("Interrupted. Type /exit to quit."))
        } catch (e: EndOfFileException) {
            Banner.printGoodbye()
            break
        } catch (e: Exception) {
            println(Formatter.errorBox("Error: ${e.message}"))
        }
    }
    withContext(Dispatchers.IO) { terminal.close() }
}