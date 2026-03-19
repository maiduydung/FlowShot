"""FlowShot — Turn codebases into branded workflow diagrams using LLMs."""

from flowshot.scanner import scan_repos
from flowshot.analyzer import analyze
from flowshot.renderer import render_svg
from flowshot.converter import svg_to_png
from flowshot.theme import Theme

__version__ = "0.1.0"


def generate(
    repos: list[str],
    output: str = "workflow.png",
    provider: str = "anthropic",
    model: str | None = None,
    theme: Theme | None = None,
    logo_path: str | None = None,
) -> str:
    """Generate a branded workflow diagram from one or more repos.

    Args:
        repos: List of paths to repositories.
        output: Output file path (.svg or .png).
        provider: LLM provider ("anthropic" or "openai").
        model: Model override. Defaults to claude-sonnet-4-20250514 / gpt-4o.
        theme: Custom Theme object. Defaults to Pathfinder brand.
        logo_path: Path to logo PNG for footer. Uses built-in if None.

    Returns:
        Path to the generated file.
    """
    theme = theme or Theme()
    context = scan_repos(repos)
    workflow = analyze(context, provider=provider, model=model)
    svgContent = render_svg(workflow, theme=theme, logo_path=logo_path)

    if output.endswith(".svg"):
        with open(output, "w") as f:
            f.write(svgContent)
    else:
        svgPath = output.rsplit(".", 1)[0] + ".svg"
        with open(svgPath, "w") as f:
            f.write(svgContent)
        svg_to_png(svgPath, output)

    return output
