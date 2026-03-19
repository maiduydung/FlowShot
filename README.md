# FlowShot

Turn codebases into branded workflow diagrams using LLMs. Built for engineers who ship, not designers.

You point it at one or more repos. An LLM reads the code, understands the business flow, and generates a clean, professional SVG/PNG diagram — branded with your colors and logo, ready for LinkedIn or client presentations.

## Install

```bash
pip install flowshot
```

## Quick Start

```bash
# Set your LLM API key
export ANTHROPIC_API_KEY="sk-..."
# or
export OPENAI_API_KEY="sk-..."

# Point it at your repos
flowshot ./backend ./frontend -o workflow.png

# Use OpenAI instead
flowshot ./my-project -o workflow.png --provider openai

# Custom logo
flowshot ./backend ./frontend -o workflow.png --logo ./my-logo.png

# Custom brand color
flowshot ./my-project -o workflow.svg --primary-color "#FF6B00"
```

## Python API

```python
from flowshot import generate

generate(
    repos=["./backend", "./frontend"],
    output="workflow.png",
    provider="anthropic",  # or "openai"
)
```

### Custom Theme

```python
from flowshot import generate
from flowshot.theme import Theme

theme = Theme(
    primary="#FF6B00",       # your brand color
    primaryLight="#FFF3E8",   # light variant
    primaryBg="#FFFAF5",      # section background
)

generate(
    repos=["./my-project"],
    output="workflow.png",
    theme=theme,
    logo_path="./my-logo.png",
)
```

## How It Works

```
Repos --> Scanner --> LLM Analyzer --> Renderer --> SVG/PNG
          reads       understands      draws        ready for
          code        business flow    branded      LinkedIn
```

1. **Scanner** — walks your repos, reads READMEs, source files, configs. Builds a context string.
2. **Analyzer** — sends context to an LLM (Anthropic or OpenAI). The LLM returns a structured JSON workflow with before/after sections, metrics, and a tagline.
3. **Renderer** — converts the JSON into a hand-crafted SVG with your brand colors, proper typography, shadows, and layout.
4. **Converter** — exports to PNG at 2x resolution for crisp display on LinkedIn.

## Output Structure

Every diagram follows the same proven layout:

- **Left: BEFORE** — the painful manual process (gray/muted tones)
- **Right: AFTER** — the automated solution (brand colors, split into logical lanes)
- **Metrics bar** — 3-5 key results with punchy numbers
- **Tagline** — one clean sentence
- **Footer** — your logo

## Design System

Default theme (Pathfinder Softworks brand):

| Token | Value | Usage |
|-------|-------|-------|
| `primary` | `#1273FF` | Action nodes, arrows, badges |
| `primaryLight` | `#E8F0FE` | Input node fills |
| `primaryBg` | `#F0F7FF` | After section background |
| `background` | `#FFFFFF` | Canvas |
| `warningStroke` | `#FB923C` | Problem nodes in Before |
| `dangerStroke` | `#F87171` | Worst-outcome nodes in Before |

## Supported LLM Providers

| Provider | Default Model | Env Var |
|----------|--------------|---------|
| Anthropic | `claude-sonnet-4-20250514` | `ANTHROPIC_API_KEY` |
| OpenAI | `gpt-4o` | `OPENAI_API_KEY` |

Override with `--model`:
```bash
flowshot ./repo -o out.png --provider anthropic --model claude-opus-4-20250514
```

## Project Structure

```
flowshot/
├── __init__.py      # Public API: generate()
├── cli.py           # Click CLI entry point
├── scanner.py       # Repo walker, reads key files
├── analyzer.py      # LLM integration (Anthropic/OpenAI)
├── schema.py        # JSON schema the LLM must follow
├── renderer.py      # Workflow JSON -> branded SVG
├── converter.py     # SVG -> PNG via cairosvg
├── theme.py         # Design system tokens
└── assets/
    └── logo.png     # Default footer logo
```
