from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.graphics.barcode import qr
from reportlab.lib.utils import ImageReader
import os

def generate_labels_pdf(plates, layout="4x3", job_name="", company=""):
    """
    Creates professional manufacturing labels with:
    - QR code encoding door + dimensions + Q-ref
    - Big door number
    - Job name
    - Company name
    - Order count
    - Grid label layout (4x2 or 4x3)
    - Avery sheet compatibility
    - Thumbnail placeholder
    """

    filename = "/tmp/labels.pdf"

    if layout == "4x2":
        cols = 4
        rows = 2
    else:
        cols = 4
        rows = 3

    page_w, page_h = A4
    label_w = page_w / cols
    label_h = page_h / rows

    c = canvas.Canvas(filename, pagesize=A4)

    order_count = len(plates)

    for i, p in enumerate(plates):

        col = i % cols
        row = rows - 1 - ((i // cols) % rows)
        page = i // (cols * rows)

        if i > 0 and col == 0 and row == rows - 1:
            c.showPage()

        x0 = col * label_w
        y0 = row * label_h

        # DRAW BORDER
        c.setLineWidth(0.5)
        c.rect(x0 + 2*mm, y0 + 2*mm, label_w - 4*mm, label_h - 4*mm)

        # DOOR NUMBER (big + centered)
        c.setFont("Helvetica-Bold", 26)
        c.drawCentredString(x0 + label_w / 2, y0 + label_h - 18*mm, str(p.door))

        # JOB NAME
        c.setFont("Helvetica-Bold", 10)
        c.drawString(x0 + 6*mm, y0 + label_h - 30*mm, f"{job_name}")

        # COMPANY
        c.setFont("Helvetica", 9)
        c.drawString(x0 + 6*mm, y0 + label_h - 36*mm, f"{company}")

        # ORDER COUNT
        c.drawString(x0 + 6*mm, y0 + label_h - 43*mm, f"Item {i+1} of {order_count}")

        # DIMENSIONS + Q REF
        details = f"{p.width} × {p.height}"
        if hasattr(p, "q_reference"):
            details += f" | {p.q_reference}"

        c.setFont("Helvetica-Bold", 12)
        c.drawString(x0 + 6*mm, y0 + 14*mm, details)

        # THUMBNAIL (placeholder for now)
        c.setFont("Helvetica-Oblique", 8)
        c.drawString(x0 + 6*mm, y0 + 8*mm, "[THUMBNAIL COMING SOON]")

        # QR CODE (bottom right)
        qr_data = f"{p.door}|{p.width}x{p.height}|{getattr(p, 'q_reference', '')}"
        qr_code = qr.QrCodeWidget(qr_data)
        bounds = qr_code.getBounds()
        qr_size = 22 * mm
        d = qr_size / max(bounds[2] - bounds[0], bounds[3] - bounds[1])

        qr_x = x0 + label_w - qr_size - 6*mm
        qr_y = y0 + 6*mm

        c.saveState()
        c.translate(qr_x, qr_y)
        c.scale(d, d)
        qr_code.drawOn(c, 0, 0)
        c.restoreState()

    c.save()
    return filename
