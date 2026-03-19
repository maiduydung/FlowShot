# AI Assistant Context — FlowShot

## What This Is

FlowShot is a Python CLI/library that turns codebases into branded workflow diagrams. It scans repos, sends context to an LLM (Anthropic or OpenAI), gets back a structured JSON workflow, and renders it as a polished SVG/PNG.

Target user: engineers who want to show their work to business people and on LinkedIn without touching Figma.

## Architecture

```
flowshot/
├── __init__.py      # Public API: generate() — orchestrates the pipeline
├── cli.py           # Click CLI: flowshot ./repo -o output.png
├── scanner.py       # Walks repos, reads README/CLAUDE.md/source files
├── analyzer.py      # Calls LLM API, returns structured workflow JSON
├── schema.py        # JSON schema definition the LLM must follow
├── renderer.py      # Workflow JSON -> SVG (hand-crafted, no libraries)
├── converter.py     # SVG -> PNG via cairosvg
├── theme.py         # Design tokens (colors, fonts, spacing)
└── assets/
    └── logo.png     # Default Pathfinder Softworks logo for footer
```

## Pipeline

1. `scanner.scan_repos(paths)` — reads repos, returns context string (max 200K chars)
2. `analyzer.analyze(context, provider, model)` — LLM call, returns workflow dict
3. `renderer.render_svg(workflow, theme, logo_path)` — generates SVG string
4. `converter.svg_to_png(svg_path, png_path)` — 2x PNG for LinkedIn

## Design Philosophy

- **White + #1273FF blue** — clean, transparent, professional
- Before section: gray/muted tones (pain), After section: blue/white (solution)
- Node types control styling: `input` (light blue), `process` (solid blue), `output` (white + blue border), `warning` (orange), `danger` (red)
- Every diagram has: title, before/after, metrics bar, tagline, logo footer
- SVG is hand-written XML — no D3, no charting library, just string concatenation

## Variable Naming

Use **camelCase** for all variables:
```python
nodeWidth = 150
primaryColor = "#1273FF"
```

## Key Design Decisions

- **LLM returns fixed JSON schema** — rendering is deterministic, LLM only decides content
- **Schema defined in schema.py** — single source of truth for what the LLM returns
- **Theme is a dataclass** — easy to override, defaults to Pathfinder brand
- **Logo embedded as base64** — SVG is self-contained, no external dependencies
- **Scanner caps at 200K chars** — keeps LLM costs reasonable
- **Renderer uses no external SVG libs** — full control over output, no bloat

## Commands

```bash
pip install -e "."              # Install in dev mode
flowshot ./repo -o out.png      # Generate diagram
pytest tests/ -v                # Run tests
```

## Environment Variables

- `ANTHROPIC_API_KEY` — for Anthropic provider
- `OPENAI_API_KEY` — for OpenAI provider

## Common Tasks

### Adding a new LLM provider
1. Add default model to `DEFAULT_MODELS` in `analyzer.py`
2. Add `_callNewProvider()` function in `analyzer.py`
3. Add to the `analyze()` dispatch

### Changing the diagram layout
All layout logic is in `renderer.py`:
- `_LayoutContext.compute()` — calculates positions
- `_svgBeforeSection()` — left side (vertical node chain)
- `_svgAfterSection()` — right side (horizontal lanes)
- `_renderSection()` — individual lane within after section

### Adding new node types
1. Add to enum in `schema.py`
2. Add styling branch in `_svgBeforeSection()` or `_renderSection()` in `renderer.py`
3. Add color tokens to `theme.py` if needed
