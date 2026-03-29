"""Design system tokens. White + blue, clean, transparent, professional."""

from dataclasses import dataclass


@dataclass
class Theme:
    # Core palette
    primary: str = "#1273FF"
    primaryLight: str = "#E8F0FE"
    primaryBg: str = "#F0F7FF"
    white: str = "#FFFFFF"
    background: str = "#FFFFFF"

    # Text
    textDark: str = "#0F172A"
    textBody: str = "#475569"
    textMuted: str = "#64748B"
    textLight: str = "#94A3B8"

    # Semantic
    warningFill: str = "#FFF7ED"
    warningStroke: str = "#FB923C"
    warningText: str = "#C2410C"
    dangerFill: str = "#FEF2F2"
    dangerStroke: str = "#F87171"
    dangerText: str = "#DC2626"
    successText: str = "#22C55E"

    # Borders
    border: str = "#E2E8F0"
    borderLight: str = "#CBD5E1"

    # Before section (muted/gray)
    beforeBg: str = "#F8FAFC"
    beforeBadgeBg: str = "#FEE2E2"
    beforeBadgeText: str = "#DC2626"

    # Layout
    canvasWidth: int = 1200
    canvasHeight: int = 680
    nodeRadius: int = 10
    nodeHeight: int = 52
    nodePadding: int = 16
    sectionRadius: int = 16
    arrowWidth: float = 1.5
    fontSize: int = 13
    fontFamily: str = "'Inter', -apple-system, BlinkMacSystemFont, sans-serif"

    # Shadow
    shadowColor: str = "#1273FF"
    shadowOpacity: float = 0.08
    shadowGrayOpacity: float = 0.06
