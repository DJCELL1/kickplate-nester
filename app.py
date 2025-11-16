import streamlit as st
import pandas as pd
import tempfile
from data_loader import load_plate_csv
from nesting_engine import shelf_nest, Sheet
from visualiser import draw_sheet
from label_generator import generate_labels_pdf

st.set_page_config(page_title="Kickplate Nester", layout="wide")
st.title("Kickplate Nesting Tool (Neutral Light Theme)")

st.markdown("Upload your CSV, enter your stock, and let the magic happen.")

uploaded = st.file_uploader("Upload kickplate CSV", type=["csv"])

full_sheets = st.number_input("How many full sheets (1200×2400) available?", min_value=0, value=2)

offcuts_num = st.number_input("How many offcuts do you want to enter?", min_value=0, value=0)

offcuts = []
for i in range(offcuts_num):
    col1, col2 = st.columns(2)
    w = col1.number_input(f"Offcut {i+1} width", value=300)
    h = col2.number_input(f"Offcut {i+1} height", value=900)
    offcuts.append((w, h))

if uploaded and st.button("Run Nesting"):
    plates = load_plate_csv(uploaded)

    # Build sheet list
    sheets = []
    for i, (w, h) in enumerate(offcuts):
        sheets.append(Sheet(w, h, f"Offcut-{i+1}"))

    for i in range(full_sheets):
        sheets.append(Sheet(1200, 2400, f"Sheet-{i+1}"))

    sheets, unplaced = shelf_nest(plates, sheets)

    if unplaced:
        st.error("🛑 Bruv… you're out of metal.\n\nSome kickplates wouldn't fit:")
        for p in unplaced:
            st.write(f"- {p.door} ({p.width}x{p.height})")

        needed = round(len(unplaced) * 1.0, 1)
        st.write(f"You need **{needed} extra sheets**.")
    else:
        st.success("Nesting successful!")

    for s in sheets:
        if s.placements:
            fig = draw_sheet(s)
            st.pyplot(fig)

    # Labels
    if st.button("Download Labels PDF"):
        filename = generate_labels_pdf([p for s in sheets for p in s.placements])
        with open(filename, "rb") as f:
            st.download_button("Download Labels", f, file_name="labels.pdf")
