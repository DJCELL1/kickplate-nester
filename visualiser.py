import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import numpy as np

# Pastel colour palette for the cuts
PASTEL_COLORS = [
    "#A7D2CB",  # mint
    "#F4BFBF",  # pastel red
    "#E5E5E5",  # light grey
    "#95D1CC",  # teal mint
    "#F7E6C4",  # cream yellow
    "#E8FFD9",  # pale green
    "#C7D3FF",  # blue pastel
    "#FFD6A5",  # peach pastel
]


def get_color_for_plate(plate):
    """Consistent colour assignment per plate size."""
    key = (plate.width, plate.height)
    return PASTEL_COLORS[hash(key) % len(PASTEL_COLORS)]


def draw_sheet(sheet):
    """Draw a landscape, ultra-clean, proportional layout with stock border and pastel cuts."""

    # ---------- FIGURE SETUP ----------
    # Landscape size (smaller but readable)
    fig, ax = plt.subplots(figsize=(10, 5))

    # Neutral background
    ax.set_facecolor("#FAFAFA")
    plt.rcParams["font.family"] = "DejaVu Sans"
    plt.rcParams["font.size"] = 9

    # ---------- PROPORTIONAL SCALING ----------
    # Fit the sheet proportionally into the figure
    target_width = 800
    scale = target_width / sheet.width
    scaled_width = sheet.width * scale
    scaled_height = sheet.height * scale

    # Margin around the sheet for breathing room
    margin = 30

    ax.set_xlim(-margin, scaled_width + margin)
    ax.set_ylim(-margin, scaled_height + margin)
    ax.invert_yaxis()

    # ---------- DRAW STOCK SHEET BORDER ----------
    sheet_border = FancyBboxPatch(
        (0, 0),
        scaled_width,
        scaled_height,
        boxstyle="round,pad=0.5",
        linewidth=1.6,
        edgecolor="#222",
        facecolor="none"
    )
    ax.add_patch(sheet_border)

    # ---------- SHEET TITLE HEADER ----------
    ax.text(
        scaled_width / 2,
        -20,
        f"{sheet.name}   ({sheet.width} × {sheet.height})",
        ha="center",
        va="bottom",
        fontsize=12,
        weight="bold",
        color="#222",
        bbox=dict(
            boxstyle="round,pad=0.3",
            facecolor="#E8E8E8",
            edgecolor="#BBBBBB"
        )
    )

    # ---------- DRAW EACH CUT INSIDE THE SHEET ----------
    for p in sheet.placements:
        color = get_color_for_plate(p)

        # Scale positions and sizes
        x = p.x * scale
        y = p.y * scale
        w = p.width * scale
        h = p.height * scale

        # Rounded pastel rectangle for the cut
        rect = FancyBboxPatch(
            (x, y),
            w,
            h,
            boxstyle="round,pad=0.3",
            linewidth=1.2,
            edgecolor="#444",
            facecolor=color,
        )
        ax.add_patch(rect)

        # ---------- GRAIN HATCH ----------
        if p.grain:
            if p.height > p.width:
                hatch_style = "//"   # vertical grain feel
            else:
                hatch_style = "\\\\"  # horizontal grain feel

            hatch_rect = FancyBboxPatch(
                (x, y),
                w,
                h,
                boxstyle="round,pad=0.3",
                linewidth=0,
                facecolor="none",
                hatch=hatch_style,
                edgecolor="none"
            )
            ax.add_patch(hatch_rect)

        # ---------- LABEL ON EACH CUT ----------
        label = f"{p.door}\n{p.width} × {p.height}"

        ax.text(
            x + w / 2,
            y + h / 2,
            label,
            ha="center",
            va="center",
            fontsize=8.5,
            weight="bold",
            color="#222"
        )

    # ---------- CLEAN LOOK ----------
    ax.axis("off")

    return fig
