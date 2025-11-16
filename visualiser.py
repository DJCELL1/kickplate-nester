import matplotlib.pyplot as plt

def draw_sheet(sheet):
    fig, ax = plt.subplots(figsize=(6, 10))
    ax.set_xlim(0, sheet.width)
    ax.set_ylim(0, sheet.height)
    ax.invert_yaxis()

    for p in sheet.placements:
        rect = plt.Rectangle((p.x, p.y), p.width, p.height,
                             fill=False, edgecolor="black", linewidth=1)
        ax.add_patch(rect)
        ax.text(p.x + 5, p.y + 15, f"{p.door}\n{p.width}x{p.height}",
                fontsize=8)

    ax.set_title(f"Sheet {sheet.name}")
    return fig
