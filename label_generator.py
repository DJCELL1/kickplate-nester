from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

def generate_labels_pdf(plates, filename="labels.pdf"):
    c = canvas.Canvas(filename, pagesize=A4)

    cols = 3
    rows = 7
    label_w = A4[0] / cols
    label_h = A4[1] / rows

    x = 0
    y = A4[1] - label_h

    for i, p in enumerate(plates):
        text = f"Door: {p.door}\nSize: {p.width}x{p.height}\nArea: {p.area}\nSheet: {p.sheet}"
        c.rect(x + 5, y + 5, label_w - 10, label_h - 10)

        for offset, line in enumerate(text.split("\n")):
            c.drawString(x + 10, y + label_h - 20 - (offset * 12), line)

        x += label_w
        if (i + 1) % cols == 0:
            x = 0
            y -= label_h
        if (i + 1) % (cols * rows) == 0:
            c.showPage()
            x = 0
            y = A4[1] - label_h

    c.save()
    return filename
