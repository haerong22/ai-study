package org.example.tools

import ai.koog.agents.core.tools.annotations.LLMDescription
import ai.koog.agents.core.tools.annotations.Tool
import org.example.utils.resolveFilePath

@Tool("readFile")
@LLMDescription("주어진 파일 경로를 받고 파일 내용을 응답하는 도구 입니다.")
fun readFile(
    @LLMDescription("읽을 파일의 경로")
    path: String
): String {
    require(path.isNotBlank()) { return "파일 경로가 비어있습니다." }

    val file = resolveFilePath(path)

    if (!file.exists()) return "오류: 파일을 찾을 수 없습니다: $path"
    if (!file.isFile) return "오류: 파일이 아닙니다: $path"
    if (!file.canRead()) return "오류: 읽기 권한이 없습니다: $path"

    return try {
        file.readText()
    } catch (e: Exception) {
        "오류: 파일을 읽을 수 없습니다: $e"
    }
}