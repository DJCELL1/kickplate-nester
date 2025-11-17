from io import StringIO
import streamlit as st
import pandas as pd
import requests
from requests.auth import HTTPBasicAuth
from data_loader import load_plate_csv
from nesting_engine import nest_plates, Sheet
from visualiser import draw_sheet
from label_generator import generate_labels_pdf

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------
st.set_page_config(page_title="Kickplate Nester", layout="wide")
st.title("Kickplate Nester – Clean Modern UI")


# ---------------------------------------------------
# DOWNLOAD TEMPLATE CSV
# ---------------------------------------------------
st.subheader("📄 Download CSV Template")

template_df = pd.DataFrame({
    "q_reference": ["Q12345"],
    "door": ["D01"],
    "width": [300],
    "height": [800],
    "grain": ["TRUE"]
})

template_bytes = template_df.to_csv(index=False).encode()

st.download_button(
    label="Download Kickplate Template CSV",
    data=template_bytes,
    file_name="kickplate_template.csv",
    mime="text/csv"
)


# ---------------------------------------------------
# UPLOAD CSV
# ---------------------------------------------------
st.subheader("📤 Upload CSV File")
uploaded = st.file_uploader("Upload kickplate CSV", type=["csv"])

uploaded_df = None

if uploaded:
    try:
        uploaded_df = pd.read_csv(uploaded)
        st.success("Uploaded CSV Preview:")
        st.dataframe(uploaded_df, height=250)
    except Exception as e:
        st.error(f"CSV load error: {e}")


# ---------------------------------------------------
# MANUAL ENTRY TABLE
# ---------------------------------------------------
st.subheader("✍️ Manual Kickplate Entry (Optional)")

empty_df = pd.DataFrame({
    "q_reference": [""] * 20,
    "door": [""] * 20,
    "width": [0] * 20,
    "height": [0] * 20,
    "grain": [False] * 20
})

manual_df = st.data_editor(
    empty_df,
    num_rows="dynamic",
    key="manual",
    height=350
)

manual_clean = manual_df[
    (manual_df["door"] != "") &
    (manual_df["width"] > 0) &
    (manual_df["height"] > 0)
]

if len(manual_clean) > 0:
    st.success("Manual Entries Preview:")
    st.dataframe(manual_clean, height=250)


# ---------------------------------------------------
# MERGE CSV + MANUAL DATA
# ---------------------------------------------------
st.subheader("🔄 Combine Data")

combined_df = pd.DataFrame()

if uploaded_df is not None:
    combined_df = pd.concat([combined_df, uploaded_df], ignore_index=True)

if len(manual_clean) > 0:
    combined_df = pd.concat([combined_df, manual_clean], ignore_index=True)

if len(combined_df) == 0:
    st.info("Upload a CSV or enter manual data to continue.")
else:
    st.success("Combined Data:")
    st.dataframe(combined_df, height=300)


# ---------------------------------------------------
# CIN7 API LOOKUP BASED ON Q REFERENCE
# ---------------------------------------------------
def fetch_job_details(q_ref):
    try:
        url = f"https://api.cin7.com/api/v1/SalesOrders?where=OrderNumber='{q_ref}'"

        r = requests.get(
            url,
            auth=HTTPBasicAuth(
                st.secrets["cin7"]["username"],
                st.secrets["cin7"]["api_key"]
            )
        )

        data = r.json()

        if isinstance(data, dict) and "message" in data:
            return None

        if len(data) == 0:
            return None

        job = data[0]
        return {
            "company": job.get("company"),
            "projectName": job.get("firstName"),
            "accountNumber": job.get("accountNumber")
        }
    except:
        return None


st.subheader("🔍 API Job Lookup from Q Reference")

if st.button("Fetch Job Info (Optional)"):
    if "q_reference" in combined_df.columns:
        job_info_results = []

        for _, row in combined_df.iterrows():
            q = str(row.get("q_reference", "")).strip()
            details = fetch_job_details(q) if q else None
            job_info_results.append(details)

        combined_df["job_details"] = job_info_results

        st.success("Job info fetched!")
        st.dataframe(combined_df, height=300)
    else:
        st.error("No 'q_reference' column found.")


# ---------------------------------------------------
# STOCK INPUTS
# ---------------------------------------------------
st.subheader("📦 Stock Available")

full_sheets = st.number_input(
    "How many full sheets (1200×2400) available?",
    min_value=0, value=2
)

offcuts_num = st.number_input(
    "How many offcuts do you want to enter?",
    min_value=0, value=0
)

offcuts = []
for i in range(offcuts_num):
    col1, col2 = st.columns(2)
    w = col1.number_input(f"Offcut {i+1} width", value=300)
    h = col2.number_input(f"Offcut {i+1} height", value=900)
    offcuts.append((w, h))


# ---------------------------------------------------
# ---------------------------------------------------
# RUN NESTING
# ---------------------------------------------------
st.subheader("🧩 Run Nesting")

if st.button("Nest Kickplates Now"):

    if len(combined_df) == 0:
        st.error("No kickplates to nest.")
        st.stop()

    # Convert combined_df → Plate objects safely using StringIO
    csv_buffer = StringIO(combined_df.to_csv(index=False))
    plates = load_plate_csv(csv_buffer)

    # Build sheet list
    sheets = []

    # Add offcuts first
    for i, (w, h) in enumerate(offcuts):
        sheets.append(Sheet(w, h, f"Offcut-{i+1}"))

    # Add full sheets
    for i in range(full_sheets):
        sheets.append(Sheet(1200, 2400, f"Sheet-{i+1}"))

    # Run the nesting engine
    sheets, unplaced = nest_nest(plates, sheets)

    # Out of stock message
    if unplaced:
        st.error("🛑 Bruv… you're out of metal. These wouldn't fit:")
        for p in unplaced:
            st.write(f"- {p.door} ({p.width}×{p.height})")

        st.write(f"You need **{len(unplaced)} extra sheets**.")

    # Display sheet diagrams
    st.subheader("📊 Sheet Layouts")

    for s in sheets:
        if s.placements:
            fig = draw_sheet(s)
            st.pyplot(fig)

    # Labels
    st.subheader("🏷 Generate Labels")

    if st.button("Download Labels PDF"):
        filename = generate_labels_pdf([p for s in sheets for p in s.placements])
        with open(filename, "rb") as f:
            st.download_button(
                "Download Labels",
                f,
                file_name="Kickplate_Labels.pdf"
            )
