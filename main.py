import streamlit as st
import pandas as pd
import requests
import io
import unicodedata

st.set_page_config(
    page_title="Project Dashboard 2026",
    page_icon="📚",
    layout="wide"
)

# ============================
# GOOGLE SHEET DETAILS
# ============================

SHEET_ID = "15qpNNgSRDENU_vDnHWwccJCC_u85EASZrV4zTWI7M00"

# CHANGE THIS IF REQUIRED
SHEET_NAME = "Minor Project"

sheet_name = SHEET_NAME.replace(" ", "%20")

url = (
    f"https://docs.google.com/spreadsheets/d/"
    f"{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
)

# ============================
# LOAD DATA
# ============================

try:
    response = requests.get(url)

    if response.status_code != 200:
        st.error("Unable to access Google Sheet.")
        st.stop()

    df = pd.read_csv(io.StringIO(response.text))

except Exception as e:
    st.error(e)
    st.stop()

# Clean column names
df.columns = [
    unicodedata.normalize("NFKC", c).strip()
    for c in df.columns
]

df.fillna("N/A", inplace=True)

# ============================
# TITLE
# ============================

st.title("📚 Minor/Major Project Dashboard")

# ============================
# KPI
# ============================

total_students = len(df)

if "Student_2_Name" in df.columns:
    total_students += len(df[df["Student_2_Name"] != "N/A"])

c1, c2, c3, c4, c5 = st.columns(5)

c1.metric("Projects", len(df))
c2.metric("Faculty", df["Faculty"].nunique())
c3.metric("Students", total_students)
c4.metric("Languages", df["Language"].nunique())
c5.metric("Universities", df["University"].nunique())

st.divider()

# ============================
# SEARCH
# ============================

search = st.text_input("🔍 Search Project")

if search:
    result = df[df["Topic"].str.contains(search, case=False, na=False)]

    st.dataframe(result, use_container_width=True)

    st.divider()

# ============================
# TABS
# ============================

tab1, tab2, tab3 = st.tabs(
    [
        "Faculty",
        "Language",
        "University"
    ]
)

# ==========================================================
# FACULTY
# ==========================================================

with tab1:

    st.subheader("Faculty Wise Projects")

    faculty_counts = (
        df.groupby("Faculty")
        .size()
        .sort_values(ascending=False)
    )

    for faculty, count in faculty_counts.items():

        with st.expander(f"👨‍🏫 {faculty} ({count} Projects)"):

            faculty_df = df[df["Faculty"] == faculty]

            for _, row in faculty_df.iterrows():

                with st.expander(f"📁 {row['Topic']}"):

                    st.write("### Students")

                    st.write("**Student 1:**", row["Student_1_Name"])

                    if row["Student_2_Name"] != "N/A":
                        st.write("**Student 2:**", row["Student_2_Name"])

                    else:
                        st.write("**Student 2:** N/A")

# ==========================================================
# LANGUAGE
# ==========================================================

with tab2:

    st.subheader("Language Wise Projects")

    language_counts = (
        df.groupby("Language")
        .size()
        .sort_values(ascending=False)
    )

    for language, count in language_counts.items():

        with st.expander(f"💻 {language} ({count} Projects)"):

            language_df = df[df["Language"] == language]

            for _, row in language_df.iterrows():

                with st.expander(f"📁 {row['Topic']}"):

                    st.write("### Students")

                    st.write("**Student 1:**", row["Student_1_Name"])

                    if row["Student_2_Name"] != "N/A":
                        st.write("**Student 2:**", row["Student_2_Name"])

                    else:
                        st.write("**Student 2:** N/A")

# ==========================================================
# UNIVERSITY
# ==========================================================

with tab3:

    st.subheader("University Wise Projects")

    university_counts = (
        df.groupby("University")
        .size()
        .sort_values(ascending=False)
    )

    for university, count in university_counts.items():

        with st.expander(f"🏛️ {university} ({count} Projects)"):

            university_df = df[df["University"] == university]

            for _, row in university_df.iterrows():

                with st.expander(f"📁 {row['Topic']}"):

                    st.write("### Students")

                    st.write("**Student 1:**", row["Student_1_Name"])

                    if row["Student_2_Name"] != "N/A":
                        st.write("**Student 2:**", row["Student_2_Name"])

                    else:
                        st.write("**Student 2:** N/A")

# ============================
# DOWNLOAD
# ============================

st.divider()

st.download_button(
    label="⬇ Download CSV",
    data=df.to_csv(index=False),
    file_name="Projects.csv",
    mime="text/csv"
)
