"""Render a workflow JSON into a branded SVG. The heart of the package."""

import base64
import os
from pathlib import Path

from flowshot.theme import Theme

DEFAULT_LOGO = Path(__file__).parent / "assets" / "logo.png"


def render_svg(workflow: dict, theme: Theme | None = None, logo_path: str | None = None) -> str:
    """Render workflow JSON to SVG string."""
    t = theme or Theme()
    ctx = _LayoutContext(workflow, t)
    ctx.compute()

    parts = [
        _svgHeader(t, ctx),
        _svgDefs(t),
        _svgBackground(t),
        _svgTitle(workflow, t),
        _svgBeforeSection(workflow["before"], t, ctx),
        _svgTransitionArrow(t, ctx),
        _svgAfterSection(workflow["after"], t, ctx),
        _svgMetricsBar(workflow.get("metrics", []), t, ctx),
        _svgTagline(workflow.get("tagline", ""), t, ctx),
        _svgFooter(t, ctx, logo_path),
        "</svg>",
    ]
    return "\n".join(parts)


class _LayoutContext:
    """Pre-compute layout positions for all elements."""

    def __init__(self, workflow: dict, theme: Theme):
        self.workflow = workflow
        self.t = theme
        # Dimensions computed in compute()
        self.beforeX = 30
        self.beforeY = 70
        self.beforeW = 0
        self.beforeH = 0
        self.afterX = 0
        self.afterY = 70
        self.afterW = 0
        self.afterH = 0
        self.arrowX = 0
        self.metricsY = 0
        self.taglineY = 0
        self.footerY = 0
        self.canvasH = 0

    def compute(self):
        beforeNodes = self.workflow["before"]["nodes"]
        afterSections = self.workflow["after"]["sections"]
        metrics = self.workflow.get("metrics", [])

        # Before section: fixed width, height based on node count
        self.beforeW = 280
        nodeH = 56
        gapH = 26
        self.beforeH = len(beforeNodes) * nodeH + (len(beforeNodes) - 1) * gapH + 80

        # Arrow zone
        arrowZone = 50

        # After section
        self.afterX = self.beforeX + self.beforeW + arrowZone
        sectionH = 0
        for section in afterSections:
            nodeCount = len(section["nodes"])
            rows = (nodeCount + 3) // 4  # up to 4 nodes per row
            sectionH += rows * nodeH + 80
        self.afterW = self.t.canvasWidth - self.afterX - 30
        self.afterH = max(sectionH + (len(afterSections) - 1) * 20, self.beforeH)

        # Make before match after height
        self.beforeH = max(self.beforeH, self.afterH)

        self.arrowX = self.beforeX + self.beforeW + arrowZone // 2

        # Metrics bar below sections
        sectionBottom = self.beforeY + max(self.beforeH, self.afterH) + 20
        self.metricsY = sectionBottom
        self.taglineY = self.metricsY + 60
        self.footerY = self.taglineY + 50

        # Total canvas height
        self.canvasH = self.footerY + 50


def _svgHeader(t: Theme, ctx: _LayoutContext) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'xmlns:xlink="http://www.w3.org/1999/xlink" '
        f'viewBox="0 0 {t.canvasWidth} {ctx.canvasH}" '
        f'width="{t.canvasWidth}" height="{ctx.canvasH}">'
    )


def _svgDefs(t: Theme) -> str:
    return f"""  <defs>
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&amp;display=swap');
      text {{ font-family: {t.fontFamily}; }}
    </style>
    <marker id="arrow-blue" viewBox="0 0 10 7" refX="10" refY="3.5"
            markerWidth="10" markerHeight="7" orient="auto-start-reverse">
      <polygon points="0 0, 10 3.5, 0 7" fill="{t.primary}"/>
    </marker>
    <marker id="arrow-gray" viewBox="0 0 10 7" refX="10" refY="3.5"
            markerWidth="10" markerHeight="7" orient="auto-start-reverse">
      <polygon points="0 0, 10 3.5, 0 7" fill="{t.textLight}"/>
    </marker>
    <filter id="shadow-blue" x="-4%" y="-4%" width="108%" height="116%">
      <feDropShadow dx="0" dy="2" stdDeviation="4"
                    flood-color="{t.shadowColor}" flood-opacity="{t.shadowOpacity}"/>
    </filter>
    <filter id="shadow-gray" x="-4%" y="-4%" width="108%" height="116%">
      <feDropShadow dx="0" dy="2" stdDeviation="4"
                    flood-color="#000" flood-opacity="{t.shadowGrayOpacity}"/>
    </filter>
  </defs>"""


def _svgBackground(t: Theme) -> str:
    return f'  <rect width="100%" height="100%" fill="{t.background}"/>'


def _svgTitle(workflow: dict, t: Theme) -> str:
    title = _escapeXml(workflow.get("title", "Workflow"))
    return (
        f'  <text x="{t.canvasWidth // 2}" y="48" text-anchor="middle" '
        f'font-size="22" font-weight="800" fill="{t.textDark}">{title}</text>'
    )


def _svgBeforeSection(before: dict, t: Theme, ctx: _LayoutContext) -> str:
    parts = []
    x, y, w, h = ctx.beforeX, ctx.beforeY, ctx.beforeW, ctx.beforeH

    # Container
    parts.append(
        f'  <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{t.sectionRadius}" '
        f'fill="{t.beforeBg}" stroke="{t.border}" stroke-width="1.5"/>'
    )

    # Badge
    parts.append(
        f'  <rect x="{x}" y="{y}" width="100" height="32" rx="16" fill="{t.beforeBadgeBg}"/>'
    )
    parts.append(
        f'  <text x="{x + 50}" y="{y + 21}" text-anchor="middle" '
        f'font-size="13" font-weight="700" fill="{t.beforeBadgeText}">BEFORE</text>'
    )

    # Nodes (vertical chain)
    nodes = before["nodes"]
    nodeW = w - 60
    nodeH = 52
    startY = y + 50
    centerX = x + w // 2
    gapY = 26

    # Vertically center the nodes
    totalNodesH = len(nodes) * nodeH + (len(nodes) - 1) * gapY
    startY = y + (h - totalNodesH) // 2

    for i, node in enumerate(nodes):
        ny = startY + i * (nodeH + gapY)
        nx = centerX - nodeW // 2

        # Style based on type
        nType = node.get("type", "process")
        if nType == "danger":
            fill, stroke, textFill, fontW = t.dangerFill, t.dangerStroke, t.dangerText, "700"
        elif nType == "warning":
            fill, stroke, textFill, fontW = t.warningFill, t.warningStroke, t.warningText, "600"
        else:
            fill, stroke, textFill, fontW = t.white, t.borderLight, t.textBody, "600"

        parts.append(
            f'  <rect x="{nx}" y="{ny}" width="{nodeW}" height="{nodeH}" rx="{t.nodeRadius}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="1.5" filter="url(#shadow-gray)"/>'
        )

        label = _escapeXml(node["label"])
        sublabel = node.get("sublabel")
        if sublabel:
            parts.append(
                f'  <text x="{centerX}" y="{ny + 22}" text-anchor="middle" '
                f'font-size="14" font-weight="{fontW}" fill="{textFill}">{label}</text>'
            )
            parts.append(
                f'  <text x="{centerX}" y="{ny + 40}" text-anchor="middle" '
                f'font-size="12" font-weight="500" fill="{t.textLight}">{_escapeXml(sublabel)}</text>'
            )
        else:
            parts.append(
                f'  <text x="{centerX}" y="{ny + nodeH // 2 + 5}" text-anchor="middle" '
                f'font-size="14" font-weight="{fontW}" fill="{textFill}">{label}</text>'
            )

        # Arrow to next node
        if i < len(nodes) - 1:
            arrowY1 = ny + nodeH
            arrowY2 = ny + nodeH + gapY - 2
            parts.append(
                f'  <line x1="{centerX}" y1="{arrowY1}" x2="{centerX}" y2="{arrowY2}" '
                f'stroke="{t.textLight}" stroke-width="1.5" marker-end="url(#arrow-gray)"/>'
            )

    return "\n".join(parts)


def _svgTransitionArrow(t: Theme, ctx: _LayoutContext) -> str:
    """Animated triple chevron between before and after."""
    parts = []
    midY = ctx.beforeY + ctx.beforeH // 2
    ax = ctx.arrowX - 20

    for i, opacity in enumerate([0.15, 0.3, 0.6]):
        offset = i * 18
        parts.append(
            f'  <polygon points="{ax + offset},{ midY - 20} {ax + offset + 24},{midY} '
            f'{ax + offset},{midY + 20}" fill="{t.primary}" opacity="{opacity}"/>'
        )

    return "\n".join(parts)


def _svgAfterSection(after: dict, t: Theme, ctx: _LayoutContext) -> str:
    parts = []
    x, y, w, h = ctx.afterX, ctx.afterY, ctx.afterW, ctx.afterH

    # Container
    parts.append(
        f'  <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{t.sectionRadius}" '
        f'fill="{t.primaryBg}" stroke="{t.primary}" stroke-width="1.5" stroke-opacity="0.3"/>'
    )

    # Badge
    parts.append(
        f'  <rect x="{x}" y="{y}" width="88" height="32" rx="16" fill="{t.primary}"/>'
    )
    parts.append(
        f'  <text x="{x + 44}" y="{y + 21}" text-anchor="middle" '
        f'font-size="13" font-weight="700" fill="{t.white}">AFTER</text>'
    )

    sections = after["sections"]
    sectionGap = 20
    availableH = h - 50  # below badge
    sectionH = (availableH - (len(sections) - 1) * sectionGap) // len(sections)
    curY = y + 45

    # Track all node positions for cross-edges
    nodePositions = {}

    for section in sections:
        parts.append(_renderSection(section, x, curY, w, sectionH, t, nodePositions))
        curY += sectionH + sectionGap

    # Cross-edges
    for edge in after.get("crossEdges", []):
        fromPos = nodePositions.get(edge["from"])
        toPos = nodePositions.get(edge["to"])
        if fromPos and toPos:
            style = edge.get("style", "dashed")
            dashAttr = ' stroke-dasharray="5,4"' if style == "dashed" else ""
            fx, fy = fromPos
            tx, ty = toPos
            parts.append(
                f'  <line x1="{fx}" y1="{fy}" x2="{tx}" y2="{ty}" '
                f'stroke="{t.primary}" stroke-width="1.5"{dashAttr} marker-end="url(#arrow-blue)"/>'
            )

    return "\n".join(parts)


def _renderSection(
    section: dict, parentX: int, parentY: int, parentW: int, sectionH: int,
    t: Theme, nodePositions: dict,
) -> str:
    parts = []
    padX = 20
    innerX = parentX + padX
    innerW = parentW - padX * 2

    # Section label
    parts.append(
        f'  <text x="{innerX + 10}" y="{parentY + 16}" font-size="11" font-weight="700" '
        f'fill="{t.primary}" letter-spacing="1.5">{_escapeXml(section["label"].upper())}</text>'
    )
    parts.append(
        f'  <line x1="{innerX + 10}" y1="{parentY + 22}" x2="{innerX + innerW - 10}" '
        f'y2="{parentY + 22}" stroke="{t.primary}" stroke-width="0.5" opacity="0.3"/>'
    )

    nodes = section["nodes"]
    nodeCount = len(nodes)

    # Layout: horizontal flow
    nodeW = min(150, (innerW - (nodeCount - 1) * 40) // nodeCount)
    nodeH = 52
    totalW = nodeCount * nodeW + (nodeCount - 1) * 40
    startX = innerX + (innerW - totalW) // 2
    nodeY = parentY + (sectionH - nodeH) // 2 + 8

    for i, node in enumerate(nodes):
        nx = startX + i * (nodeW + 40)
        nType = node.get("type", "process")

        if nType == "process":
            fill, stroke, textFill, strokeW = t.primary, "none", t.white, "0"
            filterAttr = 'filter="url(#shadow-blue)"'
        elif nType == "output":
            fill, stroke, textFill, strokeW = t.white, t.primary, t.primary, "1.5"
            filterAttr = 'filter="url(#shadow-blue)"'
        else:  # input
            fill, stroke, textFill, strokeW = t.white, t.primary, t.primary, "1.2"
            filterAttr = 'filter="url(#shadow-blue)"'

        parts.append(
            f'  <rect x="{nx}" y="{nodeY}" width="{nodeW}" height="{nodeH}" rx="{t.nodeRadius}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{strokeW}" {filterAttr}/>'
        )

        label = _escapeXml(node["label"])
        sublabel = node.get("sublabel")
        if sublabel:
            parts.append(
                f'  <text x="{nx + nodeW // 2}" y="{nodeY + 22}" text-anchor="middle" '
                f'font-size="12" font-weight="700" fill="{textFill}">{label}</text>'
            )
            parts.append(
                f'  <text x="{nx + nodeW // 2}" y="{nodeY + 38}" text-anchor="middle" '
                f'font-size="10" font-weight="500" fill="{textFill}" opacity="0.8">'
                f'{_escapeXml(sublabel)}</text>'
            )
        else:
            parts.append(
                f'  <text x="{nx + nodeW // 2}" y="{nodeY + nodeH // 2 + 5}" text-anchor="middle" '
                f'font-size="12" font-weight="700" fill="{textFill}">{label}</text>'
            )

        # Store position for cross-edges (center-bottom and center-top)
        nodePositions[node["id"]] = (nx + nodeW // 2, nodeY + nodeH // 2)

        # Arrow to next node
        if i < nodeCount - 1:
            ax1 = nx + nodeW
            ax2 = nx + nodeW + 38
            ay = nodeY + nodeH // 2
            parts.append(
                f'  <line x1="{ax1}" y1="{ay}" x2="{ax2}" y2="{ay}" '
                f'stroke="{t.primary}" stroke-width="1.5" marker-end="url(#arrow-blue)"/>'
            )

    return "\n".join(parts)


def _svgMetricsBar(metrics: list, t: Theme, ctx: _LayoutContext) -> str:
    if not metrics:
        return ""

    parts = []
    x = ctx.afterX
    y = ctx.metricsY
    w = ctx.afterW

    # Background bar
    parts.append(
        f'  <rect x="{x}" y="{y}" width="{w}" height="48" rx="10" '
        f'fill="{t.primary}" opacity="0.06"/>'
    )

    # Distribute metrics evenly
    count = len(metrics)
    slotW = w // count

    for i, metric in enumerate(metrics):
        mx = x + i * slotW + slotW // 2
        parts.append(
            f'  <text x="{mx}" y="{y + 20}" text-anchor="middle" '
            f'font-size="20" font-weight="800" fill="{t.primary}">'
            f'{_escapeXml(metric["value"])}</text>'
        )
        parts.append(
            f'  <text x="{mx}" y="{y + 38}" text-anchor="middle" '
            f'font-size="10" font-weight="500" fill="{t.textMuted}">'
            f'{_escapeXml(metric["label"])}</text>'
        )

    return "\n".join(parts)


def _svgTagline(tagline: str, t: Theme, ctx: _LayoutContext) -> str:
    if not tagline:
        return ""

    x = ctx.afterX
    y = ctx.taglineY
    w = ctx.afterW

    parts = [
        f'  <rect x="{x}" y="{y}" width="{w}" height="40" rx="8" '
        f'fill="{t.white}" stroke="{t.primary}" stroke-width="1" stroke-opacity="0.2"/>',
        f'  <text x="{x + w // 2}" y="{y + 25}" text-anchor="middle" '
        f'font-size="12" font-weight="600" fill="{t.textBody}">{_escapeXml(tagline)}</text>',
    ]
    return "\n".join(parts)


def _svgFooter(t: Theme, ctx: _LayoutContext, logo_path: str | None) -> str:
    parts = []
    y = ctx.footerY

    # Divider line
    parts.append(
        f'  <line x1="30" y1="{y}" x2="{t.canvasWidth - 30}" y2="{y}" '
        f'stroke="{t.border}" stroke-width="1"/>'
    )

    # Logo
    logoFile = logo_path or str(DEFAULT_LOGO)
    if os.path.isfile(logoFile):
        with open(logoFile, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        parts.append(
            f'  <image x="30" y="{y + 10}" width="280" height="46" '
            f'href="data:image/png;base64,{b64}"/>'
        )

    return "\n".join(parts)


def _escapeXml(text: str) -> str:
    """Escape XML special characters."""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )
