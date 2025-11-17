import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import numpy as np

# Pastel colour palette
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
    """Assign consistent color based on plate size."""
    key = (plate.width, plate.height)
    idx = (hash(key) % len(PASTEL_COLORS))
    return PASTEL_COLORS[idx]


def draw_sheet(sheet):
    """Draw a clean, modern, pastel coloured sheet layout with grain hatching."""

    fig, ax = plt.subplots(figsize=(6, 10))

    # Margin around the sheet
    margin = 20
    ax.set_xlim(-margin, sheet.width + margin)
    ax.set_ylim(-margin, sheet.height + margin)
    ax.invert_yaxis()

    # Clean theme
    ax.set_facecolor("#FAFAFA")
    plt.rcParams["font.family"] = "DejaVu Sans"
    plt.rcParams["font.size"] = 9

    # Sheet title bar
    ax.text(
        sheet.width / 2,
        -margin + 5,
        f"{sheet.name}   ({sheet.width} × {sheet.height})",
        ha="center",
        va="top",
        fontsize=12,
        weight="bold",
        color="#333",
        bbox=dict(
            boxstyle="round,pad=0.4",
            facecolor="#E8E8E8",
            edgecolor="#BBBBBB"
        ),
    )

    # Draw each plate
    for p in sheet.placements:
        color = get_color_for_plate(p)

        # Rounded rectangle for the plate
        rect = FancyBboxPatch(
            (p.x, p.y),
            p.width,
            p.height,
            boxstyle="round,pad=0.3",
            linewidth=1.2,
            edgecolor="#555",
            facecolor=color,
        )
        ax.add_patch(rect)

        # Grain hatch if required
        if p.grain:
            # Hatch angle depends on orientation
            if p.height > p.width:
                hatch = "//"   # vertical plates
            else:
                hatch = "\\\\"  # horizontal plates

            hatch_rect = FancyBboxPatch(
                (p.x, p.y),
                p.width,
                p.height,
                boxstyle="round,pad=0.3",
                linewidth=0,
                facecolor="none",
                hatch=hatch,
                edgecolor="none"
            )
            ax.add_patch(hatch_rect)

        # Label text inside plate
        label = f"{p.door}\n{p.width} × {p.height}"

        ax.text(
            p.x + p.width / 2,
            p.y + p.height / 2,
            label,
            ha="center",
            va="center",
            fontsize=9,
            color="#333",
            weight="bold"
        )

    # Hide axis lines
    ax.axis("off")

    return fig
