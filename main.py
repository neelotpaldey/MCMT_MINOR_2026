import streamlit as st
import pandas as pd

st.set_page_config(page_title="Project Dashboard", layout="wide")

# ----------------------------
# GOOGLE SHEET CSV LINK
# ----------------------------
sheet_id = "15qpNNgSRDENU_vDnHWwccJCC_u85EASZrV4zTWI7M00"
sheet_name = "Minor Project"     # Change if required

url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"

df = pd.read_csv(url)

df.fillna("N/A", inplace=True)

st.title("📚 Project Dashboard 2026")

# ----------------------------
# KPI
# ----------------------------

col1,col2,col3,col4,col5 = st.columns(5)

col1.metric("Projects", len(df))
col2.metric("Faculty", df["Faculty"].nunique())
col3.metric("Students",
            len(df["Student_1_Name"])+
            len(df[df["Student_2_Name"]!="N/A"]))
col4.metric("Languages", df["Language"].nunique())
col5.metric("Universities", df["University"].nunique())

st.divider()

tabs=st.tabs(["Faculty","Language","University"])

# ---------------------------------------------------
# FACULTY
# ---------------------------------------------------

with tabs[0]:

    st.header("Faculty Wise Projects")

    faculty_count=df.groupby("Faculty").size().sort_values(ascending=False)

    for faculty,total in faculty_count.items():

        with st.expander(f"{faculty} ({total} Projects)"):

            temp=df[df["Faculty"]==faculty]

            for _,row in temp.iterrows():

                with st.expander(row["Topic"]):

                    st.write("**Student 1:**",row["Student_1_Name"])

                    if row["Student_2_Name"]!="N/A":
                        st.write("**Student 2:**",row["Student_2_Name"])
                    else:
                        st.write("**Student 2:** N/A")

# ---------------------------------------------------
# LANGUAGE
# ---------------------------------------------------

with tabs[1]:

    st.header("Language Wise Projects")

    language_count=df.groupby("Language").size()

    for language,total in language_count.items():

        with st.expander(f"{language} ({total})"):

            temp=df[df["Language"]==language]

            for _,row in temp.iterrows():

                with st.expander(row["Topic"]):

                    st.write("Student 1 :",row["Student_1_Name"])
                    st.write("Student 2 :",row["Student_2_Name"])

# ---------------------------------------------------
# UNIVERSITY
# ---------------------------------------------------

with tabs[2]:

    st.header("University Wise Projects")

    university_count=df.groupby("University").size()

    for university,total in university_count.items():

        with st.expander(f"{university} ({total})"):

            temp=df[df["University"]==university]

            for _,row in temp.iterrows():

                with st.expander(row["Topic"]):

                    st.write("Student 1 :",row["Student_1_Name"])
                    st.write("Student 2 :",row["Student_2_Name"])

st.divider()

st.subheader("Search Project")

search=st.text_input("Search by Project Name")

if search:

    result=df[df["Topic"].str.contains(search,case=False)]

    st.dataframe(result,use_container_width=True)

st.download_button(
    "Download CSV",
    df.to_csv(index=False),
    "Projects.csv",
    "text/csv"
)
