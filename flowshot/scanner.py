"""Scan repositories and extract context for LLM analysis."""

import os
from pathlib import Path

# Files to prioritize (in order)
PRIORITY_FILES = [
    "README.md",
    "CLAUDE.md",
    "CHANGELOG.md",
    "package.json",
    "pyproject.toml",
    "requirements.txt",
    "Cargo.toml",
    "go.mod",
]

# Directories likely to contain key source files
SOURCE_DIRS = ["src", "app", "lib", "pkg", "cmd", "api", "services", "routes", "pages"]

# Extensions to scan
CODE_EXTENSIONS = {
    ".py", ".ts", ".tsx", ".js", ".jsx", ".go", ".rs", ".java",
    ".svelte", ".vue", ".rb", ".php", ".cs", ".swift", ".kt",
}

SKIP_DIRS = {
    "node_modules", ".git", "__pycache__", ".venv", "venv",
    "dist", "build", ".next", ".svelte-kit", "target",
}

MAX_FILE_SIZE = 50_000  # chars per file
MAX_TOTAL_CONTEXT = 200_000  # total chars sent to LLM


def scan_repos(repoPaths: list[str]) -> str:
    """Scan one or more repos and return a structured context string."""
    sections = []

    for repoPath in repoPaths:
        repoPath = os.path.expanduser(repoPath)
        repoName = os.path.basename(os.path.abspath(repoPath))
        sections.append(f"\n{'='*60}\nREPOSITORY: {repoName}\nPath: {repoPath}\n{'='*60}\n")

        # 1. Priority files first
        for filename in PRIORITY_FILES:
            filePath = os.path.join(repoPath, filename)
            if os.path.isfile(filePath):
                content = _readFile(filePath)
                if content:
                    sections.append(f"\n--- {filename} ---\n{content}\n")

        # 2. Directory structure
        tree = _getDirectoryTree(repoPath, maxDepth=3)
        sections.append(f"\n--- Directory Structure ---\n{tree}\n")

        # 3. Key source files
        sourceFiles = _findSourceFiles(repoPath)
        for filePath in sourceFiles:
            relPath = os.path.relpath(filePath, repoPath)
            content = _readFile(filePath)
            if content:
                sections.append(f"\n--- {relPath} ---\n{content}\n")

    fullContext = "\n".join(sections)

    # Truncate if too long
    if len(fullContext) > MAX_TOTAL_CONTEXT:
        fullContext = fullContext[:MAX_TOTAL_CONTEXT] + "\n\n[...truncated...]"

    return fullContext


def _readFile(filePath: str) -> str | None:
    """Read a file, return None if too large or binary."""
    try:
        size = os.path.getsize(filePath)
        if size > MAX_FILE_SIZE:
            return f"[File too large: {size} bytes, skipped]"
        with open(filePath, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    except (OSError, UnicodeDecodeError):
        return None


def _getDirectoryTree(rootPath: str, maxDepth: int = 3) -> str:
    """Generate a compact directory tree."""
    lines = []
    rootPath = Path(rootPath)

    def _walk(dirPath: Path, prefix: str, depth: int):
        if depth > maxDepth:
            return
        try:
            entries = sorted(dirPath.iterdir(), key=lambda e: (not e.is_dir(), e.name))
        except PermissionError:
            return

        dirs = [e for e in entries if e.is_dir() and e.name not in SKIP_DIRS]
        files = [e for e in entries if e.is_file()]

        for f in files[:15]:  # cap files per dir
            lines.append(f"{prefix}{f.name}")
        if len(files) > 15:
            lines.append(f"{prefix}... and {len(files) - 15} more files")

        for d in dirs[:10]:
            lines.append(f"{prefix}{d.name}/")
            _walk(d, prefix + "  ", depth + 1)

    _walk(rootPath, "", 0)
    return "\n".join(lines[:100])  # cap total lines


def _findSourceFiles(repoPath: str) -> list[str]:
    """Find key source files: entry points, configs, main modules."""
    found = []

    for sourceDir in SOURCE_DIRS:
        dirPath = os.path.join(repoPath, sourceDir)
        if not os.path.isdir(dirPath):
            continue

        for root, dirs, files in os.walk(dirPath):
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS]

            for fname in sorted(files):
                ext = os.path.splitext(fname)[1]
                if ext not in CODE_EXTENSIONS:
                    continue
                # Prioritize entry points and key files
                fullPath = os.path.join(root, fname)
                found.append(fullPath)

            if len(found) > 40:
                break

    return found[:40]
