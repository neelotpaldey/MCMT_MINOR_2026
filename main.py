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

# -------------------------------------------------------
# GOOGLE SHEET DETAILS
# -------------------------------------------------------

SHEET_ID = "15qpNNgSRDENU_vDnHWwccJCC_u85EASZrV4zTWI7M00"
SHEET_NAME = "Minor Project"

sheet_name = SHEET_NAME.replace(" ", "%20")

url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_name}"

# -------------------------------------------------------
# LOAD DATA
# -------------------------------------------------------

try:
    response = requests.get(url)

    if response.status_code != 200:
        st.error("Unable to access Google Sheet.")
        st.stop()

    df = pd.read_csv(
        io.StringIO(response.text),
        dtype=str,
        keep_default_na=False
    )

except Exception as e:
    st.error(e)
    st.stop()

# -------------------------------------------------------
# CLEAN COLUMN NAMES
# -------------------------------------------------------

df.columns = [
    unicodedata.normalize("NFKC", c).strip()
    for c in df.columns
]

# Remove extra spaces from all text
for col in df.columns:
    df[col] = df[col].astype(str).str.strip()

# -------------------------------------------------------
# REQUIRED COLUMNS
# -------------------------------------------------------

required = [
    "Faculty",
    "University",
    "Student_1_Name",
    "Student_2_Name",
    "Topic",
    "Language"
]

for col in required:
    if col not in df.columns:
        st.error(f"Column '{col}' not found.")
        st.write(df.columns.tolist())
        st.stop()

# -------------------------------------------------------
# TITLE
# -------------------------------------------------------

st.title("📚 Project Dashboard 2026")

# -------------------------------------------------------
# KPI
# -------------------------------------------------------

total_projects = len(df)

total_faculty = df["Faculty"].replace("", pd.NA).dropna().nunique()

total_languages = df["Language"].replace("", pd.NA).dropna().nunique()

total_university = df["University"].replace("", pd.NA).dropna().nunique()

student1 = df["Student_1_Name"].replace("", pd.NA).dropna().shape[0]

student2 = (
    df["Student_2_Name"]
    .replace(["", "N/A", "nan"], pd.NA)
    .dropna()
    .shape[0]
)

total_students = student1 + student2

c1, c2, c3, c4, c5 = st.columns(5)

c1.metric("Projects", total_projects)
c2.metric("Faculty", total_faculty)
c3.metric("Students", total_students)
c4.metric("Languages", total_languages)
c5.metric("Universities", total_university)

st.divider()

# -------------------------------------------------------
# SEARCH
# -------------------------------------------------------

search = st.text_input("🔍 Search Project")

if search:

    result = df[
        df["Topic"].str.contains(search, case=False, na=False)
    ]

    st.dataframe(result, use_container_width=True)

    st.divider()

# -------------------------------------------------------
# TABS
# -------------------------------------------------------

tab1, tab2, tab3 = st.tabs(
    [
        "Faculty",
        "Language",
        "University"
    ]
)

# =======================================================
# FACULTY
# =======================================================

with tab1:

    st.subheader("Faculty Wise Projects")

    faculty_counts = (
        df.groupby("Faculty")
        .size()
        .sort_values(ascending=False)
    )

    for faculty, count in faculty_counts.items():

        if faculty == "":
            continue

        with st.expander(f"👨‍🏫 {faculty} ({count} Projects)"):

            temp = df[df["Faculty"] == faculty]

            for _, row in temp.iterrows():

                with st.expander(f"📁 {row['Topic']}"):

                    st.write("### Students")

                    st.write("**Student 1:**", row["Student_1_Name"])

                    if row["Student_2_Name"] not in ["", "N/A", "nan"]:
                        st.write("**Student 2:**", row["Student_2_Name"])
                    else:
                        st.write("**Student 2:** N/A")

# =======================================================
# LANGUAGE
# =======================================================

with tab2:

    st.subheader("Language Wise Projects")

    language_counts = (
        df.groupby("Language")
        .size()
        .sort_values(ascending=False)
    )

    for language, count in language_counts.items():

        if language == "":
            continue

        with st.expander(f"💻 {language} ({count} Projects)"):

            temp = df[df["Language"] == language]

            for _, row in temp.iterrows():

                with st.expander(f"📁 {row['Topic']}"):

                    st.write("**Student 1:**", row["Student_1_Name"])

                    if row["Student_2_Name"] not in ["", "N/A", "nan"]:
                        st.write("**Student 2:**", row["Student_2_Name"])
                    else:
                        st.write("**Student 2:** N/A")

# =======================================================
# UNIVERSITY
# =======================================================

with tab3:

    st.subheader("University Wise Projects")

    university_counts = (
        df.groupby("University")
        .size()
        .sort_values(ascending=False)
    )

    for university, count in university_counts.items():

        if university == "":
            continue

        with st.expander(f"🏛️ {university} ({count} Projects)"):

            temp = df[df["University"] == university]

            for _, row in temp.iterrows():

                with st.expander(f"📁 {row['Topic']}"):

                    st.write("**Student 1:**", row["Student_1_Name"])

                    if row["Student_2_Name"] not in ["", "N/A", "nan"]:
                        st.write("**Student 2:**", row["Student_2_Name"])
                    else:
                        st.write("**Student 2:** N/A")

# -------------------------------------------------------
# DOWNLOAD
# -------------------------------------------------------

st.divider()

st.download_button(
    "⬇ Download CSV",
    data=df.to_csv(index=False),
    file_name="Projects.csv",
    mime="text/csv"
)
