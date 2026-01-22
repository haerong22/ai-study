package org.example.utils

import java.io.File

fun resolveFilePath(path: String): File {
    val workingDir = File(System.getProperty("user.dir"))

    val directFile = File(path)
    if (directFile.exists()) return directFile.canonicalFile

    val trimmedPath = path.trimStart('/')
    if (trimmedPath != path) {
        val relativePath = File(workingDir, trimmedPath)
        if (relativePath.exists()) return relativePath.canonicalFile
    }

    return File(workingDir, path).canonicalFile
}