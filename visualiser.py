import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import numpy as np

# Pastel colour palette
PASTEL_COLORS = [
    "#A7D2CB", "#F4BFBF", "#E5E5E5", "#95D1CC",
    "#F7E6C4", "#E8FFD9", "#C7D3FF", "#FFD6A5"
]

def get_color_for_plate(plate):
    key = (plate.width, plate.height)
    return PASTEL_COLORS[hash(key) % len(PASTEL_COLORS)]

def draw_sheet(sheet):
    """Landscape, proportional, pastel layout with dashed stock border."""
    
    fig, ax = plt.subplots(figsize=(10, 5))

    ax.set_facecolor("#FAFAFA")
    plt.rcParams["font.family"] = "DejaVu Sans"
    plt.rcParams["font.size"] = 9

    # Scale sheet proportionally
    target_width = 850
    scale = target_width / sheet.width
    scaled_width = sheet.width * scale
    scaled_height = sheet.height * scale

    margin = 30
    ax.set_xlim(-margin, scaled_width + margin)
    ax.set_ylim(-margin, scaled_height + margin)
    ax.invert_yaxis()

    # ----- STOCK BORDER (DASHED) -----
    sheet_border = FancyBboxPatch(
        (0, 0),
        scaled_width,
        scaled_height,
        boxstyle="round,pad=0.4",
        linewidth=1.4,
        edgecolor="#444",
        facecolor="none",
        linestyle="--"   # dashed outline
    )
    ax.add_patch(sheet_border)

    # Header
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

    # Draw each nested plate
    for p in sheet.placements:
        x = p.x * scale
        y = p.y * scale
        w = p.width * scale
        h = p.height * scale

        rect = FancyBboxPatch(
            (x, y),
            w,
            h,
            boxstyle="round,pad=0.3",
            linewidth=1.2,
            edgecolor="#444",
            facecolor=get_color_for_plate(p),
        )
        ax.add_patch(rect)

        # Grain hatch
        if p.grain:
            hatch_style = "//" if p.height > p.width else "\\\\"
            hatch_rect = FancyBboxPatch(
                (x, y), w, h,
                boxstyle="round,pad=0.3",
                linewidth=0,
                facecolor="none",
                hatch=hatch_style,
                edgecolor="none",
            )
            ax.add_patch(hatch_rect)

        # Label
        label = f"{p.door}\n{p.width} × {p.height}"
        ax.text(
            x + w/2,
            y + h/2,
            label,
            ha="center",
            va="center",
            fontsize=8.5,
            weight="bold",
            color="#222",
        )

    ax.axis("off")
    return fig
