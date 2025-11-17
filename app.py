import streamlit as st
import pandas as pd
from io import StringIO
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
st.title("Kickplate Nester – Auto Q Detection + Contacts API")


# ---------------------------------------------------
# DOWNLOAD TEMPLATE CSV
# ---------------------------------------------------
st.subheader("📄 Download CSV Template")

template_df = pd.DataFrame({
    "door": ["D01"],
    "width": [300],
    "height": [800],
    "grain": ["TRUE"],
    "company": ["Murrays Bay Intermediate School"]  # optional
})

st.download_button(
    "Download Kickplate CSV Template",
    data=template_df.to_csv(index=False).encode(),
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
        st.success("Uploaded CSV Preview")
        st.dataframe(uploaded_df, height=250)
    except Exception as e:
        st.error(f"CSV load error: {e}")


# ---------------------------------------------------
# MANUAL ENTRY TABLE
# ---------------------------------------------------
st.subheader("✍️ Manual Kickplate Entry")

empty_df = pd.DataFrame({
    "door": [""] * 20,
    "width": [0] * 20,
    "height": [0] * 20,
    "grain": [False] * 20,
    "company": [""] * 20  # optional for lookup
})

manual_df = st.data_editor(
    empty_df,
    num_rows="dynamic",
    height=350,
    key="manual"
)

manual_clean = manual_df[
    (manual_df["door"] != "") &
    (manual_df["width"] > 0) &
    (manual_df["height"] > 0)
]

if len(manual_clean) > 0:
    st.success("Manual Entries Preview")
    st.dataframe(manual_clean, height=250)


# ---------------------------------------------------
# MERGE CSV + MANUAL
# ---------------------------------------------------
st.subheader("🔄 Combined Data")

combined_df = pd.DataFrame()

if uploaded_df is not None:
    combined_df = pd.concat([combined_df, uploaded_df], ignore_index=True)

if len(manual_clean) > 0:
    combined_df = pd.concat([combined_df, manual_clean], ignore_index=True)

if len(combined_df) == 0:
    st.info("Upload a CSV or enter manual entries to continue.")
else:
    st.success("Combined Data Ready")
    st.dataframe(combined_df, height=300)


# ---------------------------------------------------
# CIN7 CONTACTS API LOOKUP
# ---------------------------------------------------
def fetch_job_details(search_term):
    """
    Search Cin7 Contacts API by company name or partial project,
    automatically extract:
      - Q reference
      - Project name
      - Company
      - Account number
    """
    if not search_term:
        return None

    url = (
        "https://api.cin7.com/api/v1/Contacts?"
        f"where=FirstName~%27%25{search_term}%25%27"
    )

    try:
        r = requests.get(
            url,
            auth=HTTPBasicAuth(
                st.secrets["cin7"]["username"],
                st.secrets["cin7"]["api_key"]
            )
        )
        data = r.json()

        if not isinstance(data, list) or len(data) == 0:
            return None

        contact = data[0]

        fullname = contact.get("firstName", "")
        company = contact.get("company")
        account = contact.get("accountNumber")

        # Extract Q ref (before space or dash)
        if " " in fullname:
            q_ref = fullname.split(" ")[0].split("-")[0].strip()
        elif "-" in fullname:
            q_ref = fullname.split("-")[0].strip()
        else:
            q_ref = fullname.strip()

        # Extract project name (after dash)
        if "-" in fullname:
            project = fullname.split("-", 1)[1].strip()
        else:
            project = ""

        return {
            "q_reference": q_ref,
            "projectName": project,
            "company": company,
            "accountNumber": account
        }

    except Exception:
        return None


# ---------------------------------------------------
# FETCH JOB DETAILS
# ---------------------------------------------------
st.subheader("🔍 Fetch Job Info From Contacts API")

if st.button("Fetch Job Info"):
    job_info_results = []

    # Determine lookup method
    if "company" in combined_df.columns:
        lookup_col = "company"
    else:
        lookup_col = "door"  # worst-case fallback

    for _, row in combined_df.iterrows():
        key = str(row.get(lookup_col, "")).strip()
        info = fetch_job_details(key)
        job_info_results.append(info)

    combined_df["job_details"] = job_info_results

    st.success("Job info loaded from Contacts API!")
    st.dataframe(combined_df, height=300)


# ---------------------------------------------------
# STOCK & OFFCUTS
# ---------------------------------------------------
st.subheader("📦 Stock Available")

full_sheets = st.number_input(
    "Full sheets (1200×2400)",
    min_value=0, value=2
)

offcuts_num = st.number_input("How many offcuts?", 0, 10)

offcuts = []
for i in range(offcuts_num):
    w = st.number_input(f"Offcut {i+1} width", 0, 2400)
    h = st.number_input(f"Offcut {i+1} height", 0, 2400)
    offcuts.append((w, h))


# ---------------------------------------------------
# RUN NESTING
# ---------------------------------------------------
st.subheader("🧩 Run Nesting")

if st.button("Start Nesting"):

    if len(combined_df) == 0:
        st.error("No kickplates to nest!")
        st.stop()

    csv_buffer = StringIO(combined_df.to_csv(index=False))
    plates = load_plate_csv(csv_buffer)

    # Build sheets
    sheets = []
    for i, (w, h) in enumerate(offcuts):
        sheets.append(Sheet(w, h, f"Offcut-{i+1}"))

    for i in range(full_sheets):
        sheets.append(Sheet(1200, 2400, f"Sheet-{i+1}"))

    # Run optimiser
    sheets, unplaced = nest_plates(plates, sheets)

    if unplaced:
        st.error("Some plates could not fit:")
        for p in unplaced:
            st.write(f"- {p.door} ({p.width}×{p.height})")

    st.subheader("📊 Layouts")

    for s in sheets:
        if s.placements:
            fig = draw_sheet(s)
            st.pyplot(fig)

    # Labels
    st.subheader("🏷 Generate Labels")

    if st.button("Download Labels PDF"):
        filename = generate_labels_pdf([p for s in sheets for p in s.placements])
        with open(filename, "rb") as f:
            st.download_button("Download Labels", f, file_name="Kickplate_Labels.pdf")
