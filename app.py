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
st.title("Kickplate Nester – Q Reference → Contacts API")


# ---------------------------------------------------
# TEMPLATE CSV DOWNLOAD
# ---------------------------------------------------
st.subheader("📄 Download CSV Template")

template_df = pd.DataFrame({
    "q_reference": ["Q33515B"],
    "door": ["D01"],
    "width": [300],
    "height": [800],
    "grain": ["TRUE"]
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
st.subheader("📤 Upload Kickplate CSV")

uploaded = st.file_uploader("Upload CSV", type=["csv"])

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
st.subheader("✍️ Manual Entry (Optional)")

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
    height=350,
    key="manual"
)

manual_clean = manual_df[
    (manual_df["q_reference"] != "") &
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
    st.success("Combined Data")
    st.dataframe(combined_df, height=300)


# ---------------------------------------------------
# CIN7 CONTACTS API (Q LOOKUP)
# ---------------------------------------------------
def fetch_job_details_from_q(q_ref):
    """
    Look up job info in Cin7 Contacts API using Q reference.
    Example Q: Q33515B
    Extracts:
      - Q reference
      - Project name
      - Company
      - Account number
    """
    if not q_ref:
        return None

    search = q_ref.strip()

    url = (
        "https://api.cin7.com/api/v1/Contacts?"
        f"where=FirstName~%27%25{search}%25%27"
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

        # Extract project name (text after dash)
        project = ""
        if "-" in fullname:
            project = fullname.split("-", 1)[1].strip()

        return {
            "q_reference": q_ref,
            "projectName": project,
            "company": company,
            "accountNumber": account
        }

    except Exception:
        return None


# ---------------------------------------------------
# FETCH JOB DETAILS BUTTON
# ---------------------------------------------------
st.subheader("🔍 Fetch Job Info From Contacts API")

if st.button("Fetch Job Info"):
    if "q_reference" not in combined_df.columns:
        st.error("CSV must contain 'q_reference' column.")
        st.stop()

    job_info_results = []

    for _, row in combined_df.iterrows():
        q = str(row["q_reference"]).strip()
        info = fetch_job_details_from_q(q)
        job_info_results.append(info)

    combined_df["job_details"] = job_info_results

    st.success("Job info retrieved from Contacts API!")
    st.dataframe(combined_df, height=300)


# ---------------------------------------------------
# STOCK + OFFCUTS
# ---------------------------------------------------
st.subheader("📦 Stock Available")

full_sheets = st.number_input(
    "Full sheets (1200×2400)",
    min_value=0,
    value=2
)

offcuts_num = st.number_input("Number of Offcuts", 0, 20)

offcuts = []
for i in range(offcuts_num):
    w = st.number_input(f"Offcut {i+1} width", 0, 2400)
    h = st.number_input(f"Offcut {i+1} height", 0, 2400)
    offcuts.append((w, h))


# ---------------------------------------------------
# RUN NESTING
# ---------------------------------------------------
st.subheader("🧩 Run Nesting Optimiser")

if st.button("Start Nesting"):

    if len(combined_df) == 0:
        st.error("No kickplates to nest!")
        st.stop()

    csv_buffer = StringIO(combined_df.to_csv(index=False))
    plates = load_plate_csv(csv_buffer)

    sheets = []

    # Add offcuts
    for i, (w, h) in enumerate(offcuts):
        sheets.append(Sheet(w, h, f"Offcut-{i+1}"))

    # Add full sheets
    for i in range(full_sheets):
        sheets.append(Sheet(1200, 2400, f"Sheet-{i+1}"))

    # Run optimiser
    sheets, unplaced = nest_plates(plates, sheets)

    if unplaced:
        st.error("These plates could not fit:")
        for p in unplaced:
            st.write(f"- {p.door} ({p.width}×{p.height})")
        st.write(f"Total: {len(unplaced)} unplaced items")

    # Visual layouts
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
