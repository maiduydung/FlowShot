"""Convert SVG to PNG using cairosvg."""


def svg_to_png(svgPath: str, pngPath: str, scale: int = 2) -> str:
    """Convert SVG file to high-res PNG.

    Args:
        svgPath: Path to input SVG file.
        pngPath: Path for output PNG file.
        scale: Resolution multiplier (2 = retina/LinkedIn quality).

    Returns:
        Path to the generated PNG.
    """
    import cairosvg

    # Read SVG to get dimensions
    with open(svgPath, "r") as f:
        svgContent = f.read()

    # Extract width from viewBox or width attribute
    width = 1200  # default
    if 'width="' in svgContent:
        try:
            widthStr = svgContent.split('width="')[1].split('"')[0]
            width = int(widthStr)
        except (ValueError, IndexError):
            pass

    cairosvg.svg2png(
        url=svgPath,
        write_to=pngPath,
        output_width=width * scale,
    )

    return pngPath
