"""CLI entry point for flowshot."""

import click


@click.command()
@click.argument("repos", nargs=-1, required=True)
@click.option("--output", "-o", default="workflow.png", help="Output file path (.svg or .png)")
@click.option(
    "--provider", "-p",
    type=click.Choice(["anthropic", "openai"]),
    default="anthropic",
    help="LLM provider",
)
@click.option("--model", "-m", default=None, help="Model override")
@click.option("--logo", "-l", default=None, help="Path to logo PNG for footer")
@click.option("--primary-color", default=None, help="Primary brand color (hex)")
def main(repos, output, provider, model, logo, primary_color):
    """Generate branded workflow diagrams from codebases.

    Pass one or more repository paths:

        flowshot ./backend ./frontend -o workflow.png
    """
    from flowshot import generate
    from flowshot.theme import Theme

    theme = Theme()
    if primary_color:
        theme.primary = primary_color

    click.echo(f"Scanning {len(repos)} repo(s)...")

    try:
        resultPath = generate(
            repos=list(repos),
            output=output,
            provider=provider,
            model=model,
            theme=theme,
            logo_path=logo,
        )
        click.echo(f"Done! Output: {resultPath}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()


if __name__ == "__main__":
    main()
