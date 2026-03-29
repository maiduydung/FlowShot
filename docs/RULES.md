# AI Instance Governance Rules
### These RULES must be followed at all times.

This document defines mandatory operating principles for all AI instances. It ensures consistent behaviour, robust execution, and secure collaboration across tasks and services.

---

## Code Quality Standards

- All modules must implement structured error handling with specific failure modes.
- Every function must include a concise, purpose-driven docstring.
- Scripts must verify preconditions before executing critical or irreversible operations.
- Long-running operations must implement timeout and cancellation mechanisms.
- File and path operations must verify existence and permissions before access.
- Prioritize OOP — use classes and methods for readability.
- No files should be longer than 300 lines. If a file exceeds this, split into multiple classes in separate files.
- CLI commands must validate all user input before processing — fail fast with clear error messages.
- Never hardcode API keys or credentials. Always load from environment variables.
- LLM provider calls (Anthropic, OpenAI) must include timeout, retry, and token limit guards.

---

## Documentation Protocols

- Keep documentation simple and easy to understand.
- Only update documentation in `/docs`, `CHANGELOG.md`, or `README.md` in the project root.
- Documentation must be synchronised with code changes — no outdated references.
- Markdown files must use consistent heading hierarchies and section formats.
- Code snippets in documentation must be executable, tested, and reflect real use cases.
- Each doc must clearly outline: purpose, usage, parameters, and examples.
- Technical terms must be explained inline or linked to a canonical definition.

---

## Package & Distribution Rules

- All public API surface must be explicitly exported in `__init__.py`.
- Version bumps must follow semantic versioning and be reflected in `pyproject.toml`.
- Dependencies must be pinned to minimum versions, not exact — allow flexibility for consumers.
- The CLI entrypoint must handle all exceptions gracefully and return appropriate exit codes.

---

## Process Execution Requirements

- All actions must be logged with appropriate severity (INFO, WARNING, ERROR, etc.).
- Any failed task must include a clear, human-readable error report with traceback.
- Respect system resource limits — especially memory when parsing large codebases.
- LLM API calls must enforce token budget limits to prevent runaway costs.
- Output files (Mermaid, SVG, etc.) must be written atomically — no partial writes on failure.
- Retry logic for LLM providers must include exponential backoff and failure limits.
