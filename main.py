import streamlit as st
import pandas as pd
import requests
import io
import unicodedata
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="Project Dashboard",
    page_icon="📚",
    layout="wide"
)

# =====================================================
# GOOGLE SHEET DETAILS
# =====================================================
SHEET_ID = "15I6HYYZhIKJaBdp3PU6_eimLuOcPj3BN3-fgy_3WwTA"
SHEET_NAME = "Minor Project"

sheet_name = SHEET_NAME.replace(" ", "%20")

url = (
    f"https://docs.google.com/spreadsheets/d/"
    f"{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
)

# =====================================================
# LOAD DATA
# =====================================================

@st.cache_data(ttl=60)
def load_data():

    response = requests.get(url)

    if response.status_code != 200:
        st.error("Unable to access Google Sheet.")
        st.stop()

    df = pd.read_csv(
        io.StringIO(response.text),
        dtype=str,
        keep_default_na=False
    )

    # Clean column names
    df.columns = [
        unicodedata.normalize("NFKC", c).strip()
        for c in df.columns
    ]

    # Remove extra spaces
    for col in df.columns:
        df[col] = df[col].astype(str).str.strip()

    return df


df = load_data()

# =====================================================
# REQUIRED COLUMNS
# =====================================================

required_columns = [
    "Faculty",
    "University",
    "Language",
    "Topic",
    "Student_1_Name",
    "Student_2_Name",
    "Reserved_On"
]

missing = [
    c for c in required_columns
    if c not in df.columns
]

if missing:
    st.error(f"Missing Columns : {missing}")
    st.write(df.columns.tolist())
    st.stop()

# =====================================================
# DATE COLUMN
# =====================================================

df["Reserved_On"] = pd.to_datetime(
    df["Reserved_On"],
    errors="coerce",
    dayfirst=True
)

today = pd.Timestamp.now().normalize()

week_start = today - pd.Timedelta(days=today.weekday())

today_projects = (
    df["Reserved_On"].dt.normalize() == today
).sum()

week_projects = (
    df["Reserved_On"] >= week_start
).sum()

month_projects = (
    (
        df["Reserved_On"].dt.month == today.month
    )
    &
    (
        df["Reserved_On"].dt.year == today.year
    )
).sum()


# =====================================================
# TITLE
# =====================================================

st.title("📚 Minor Project Dashboard 2026")

st.caption(
    "Live data from Google Sheets"
)

# =====================================================
# KPI
# =====================================================

student1 = (
    df["Student_1_Name"]
    .replace("", pd.NA)
    .dropna()
    .shape[0]
)

student2 = (
    df["Student_2_Name"]
    .replace(["", "N/A"], pd.NA)
    .dropna()
    .shape[0]
)

total_students = student1 + student2

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "📚 Projects",
    len(df)
)

c2.metric(
    "👨‍🎓 Students",
    total_students
)

c3.metric(
    "👨‍🏫 Faculty",
    df["Faculty"].nunique()
)

c4.metric(
    "💻 Languages",
    df["Language"].nunique()
)

st.divider()

# =====================================================
# RESERVATION STATISTICS
# =====================================================

st.subheader("📈 Reservation Statistics")

today = pd.Timestamp.now().normalize()

yesterday = today - pd.Timedelta(days=1)

week_start = today - pd.Timedelta(days=today.weekday())

month_start = today.replace(day=1)

# Current counts
today_projects = (
    df["Reserved_On"].dt.normalize() == today
).sum()

yesterday_projects = (
    df["Reserved_On"].dt.normalize() == yesterday
).sum()

week_projects = (
    df["Reserved_On"] >= week_start
).sum()

month_projects = (
    (df["Reserved_On"].dt.month == today.month)
    &
    (df["Reserved_On"].dt.year == today.year)
).sum()

# Previous counts
last_week_start = week_start - pd.Timedelta(days=7)

last_week_end = week_start

last_week_projects = (
    (
        df["Reserved_On"] >= last_week_start
    )
    &
    (
        df["Reserved_On"] < last_week_end
    )
).sum()

previous_month = (
    month_start - pd.DateOffset(days=1)
)

last_month_projects = (
    (
        df["Reserved_On"].dt.month == previous_month.month
    )
    &
    (
        df["Reserved_On"].dt.year == previous_month.year
    )
).sum()

# Metrics
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric(
        "🆕 Today",
        today_projects,
        delta=today_projects - yesterday_projects
    )

with c2:
    st.metric(
        "📅 Yesterday",
        yesterday_projects
    )

with c3:
    st.metric(
        "📆 This Week",
        week_projects,
        delta=week_projects - last_week_projects
    )

with c4:
    st.metric(
        "🗓 This Month",
        month_projects,
        delta=month_projects - last_month_projects
    )

st.divider()

# =====================================================
# RECENT RESERVATIONS
# =====================================================

st.subheader("🕒 Recent Reservations")

recent = (
    df.sort_values(
        "Reserved_On",
        ascending=False
    )
    .head(10)
)

show_cols = [
    "Topic",
    "Faculty",
    "Student_1_Name",
    "Student_2_Name",
    "Language",
    "University",
    "Reserved_On"
]

show_cols = [
    c for c in show_cols
    if c in recent.columns
]

st.dataframe(
    recent[show_cols],
    use_container_width=True,
    hide_index=True
)

st.divider()

# =====================================================
# ANALYTICS
# =====================================================

st.header("📊 Analytics")


# ---------- Function to show Count + Percentage ----------
def make_autopct(values):
    def my_autopct(pct):
        total = sum(values)
        count = int(round(pct * total / 100.0))
        return f"{count}\n({pct:.1f}%)"
    return my_autopct


# ---------- Pie Chart Function ----------
def draw_pie_chart(data, title):

    fig, ax = plt.subplots(figsize=(4, 4))

    ax.pie(
        data.values,
        labels=data.index,
        autopct=make_autopct(data.values),
        startangle=90,
        radius=0.85,
        labeldistance=1.08,
        pctdistance=0.65,
        textprops={
            "fontsize":7
        },
        wedgeprops={
            "edgecolor":"white",
            "linewidth":1
        }
    )

    ax.set_title(
        title,
        fontsize=13,
        fontweight="bold",
        pad=12
    )

    ax.set_aspect("equal")

    fig.tight_layout()

    st.pyplot(fig, use_container_width=True)

    plt.close(fig)


# =====================================================
# PREPARE DATA
# =====================================================

faculty_chart = (
    df.groupby("Faculty")
      .size()
      .sort_values(ascending=False)
)

language_chart = (
    df.groupby("Language")
      .size()
      .sort_values(ascending=False)
)

university_chart = (
    df.groupby("University")
      .size()
      .sort_values(ascending=False)
)


# =====================================================
# DISPLAY CHARTS
# =====================================================

col1, col2, col3 = st.columns(3)

with col1:
    draw_pie_chart(
        faculty_chart,
        "👨‍🏫 Faculty"
    )

with col2:
    draw_pie_chart(
        language_chart,
        "💻 Language"
    )

with col3:
    draw_pie_chart(
        university_chart,
        "🏛 University"
    )

st.divider()

# =====================================================
# EXPANDABLE TREE VIEW
# =====================================================

tab1, tab2, tab3 = st.tabs(
    [
        "👨‍🏫 Faculty",
        "💻 Language",
        "🏛 University"
    ]
)

# =====================================================
# FACULTY
# =====================================================

with tab1:
    st.subheader("Faculty → Project → Students")
    MAX_PROJECTS = 10
    faculty_list = sorted(
        df["Faculty"]
        .dropna()
        .unique()
    )
    for faculty in faculty_list:
        if faculty == "":
            continue
        faculty_df = df[
            df["Faculty"] == faculty
        ]
# ----------------------------
# Count University-wise
# ----------------------------
        vbspu_df = faculty_df[
            faculty_df["University"]
            .str.upper()
            .str.contains("VBSPU", na=False)
        ]
        mgkvp_df = faculty_df[
            faculty_df["University"]
            .str.upper()
            .str.contains("MGKVP", na=False)
        ]
        vbspu_count = len(vbspu_df)
        mgkvp_count = len(mgkvp_df)

# ----------------------------
# Status
# ----------------------------
        if vbspu_count >= MAX_PROJECTS:
            vbspu_status = "        ✅ Reserved"
        else:
            vbspu_status = f"       🟢 {vbspu_count}/{MAX_PROJECTS} Available"

        if mgkvp_count >= MAX_PROJECTS:
            mgkvp_status = "✅ Reserved"
        else:
            mgkvp_status = f"       🟢 {mgkvp_count}/{MAX_PROJECTS} Available"

        # ----------------------------
        # Faculty Expander
        # ----------------------------

        with st.expander(
            f"👨‍🏫 {faculty}"
            f" | VBSPU : {vbspu_status}"
            f" | MGKVP : {mgkvp_status}",
            expanded=False
        ):
            faculty_df = faculty_df.sort_values(
                ["University", "Topic"]
            )
            current_university = ""
            for _, row in faculty_df.iterrows():
                # -----------------------------------
                # University Heading
                # -----------------------------------
                if row["University"] != current_university:
                    current_university = row["University"]
                    st.markdown(
                        f"## 🏛 {current_university}"
                    )
                # -----------------------------------
                # Project
                # -----------------------------------

                with st.expander(
                    f"📁 {row['Topic']}"
                ):
                    c1, c2 = st.columns(2)
                    with c1:
                        st.write(
                            "**Student 1**"
                        )
                        st.success(
                            row["Student_1_Name"]
                        )
                    with c2:
                        st.write(
                            "**Student 2**"
                        )
                        if row["Student_2_Name"] not in ["", "N/A", "nan"]:
                            st.success(
                                row["Student_2_Name"]
                            )
                        else:
                            st.info(
                                "Not Assigned"
                            )
                    st.divider()
                    info1, info2 = st.columns(2)
                    with info1:
                        st.write(
                            f"**Language :** {row['Language']}"
                        )
                    with info2:
                        st.write(
                            f"**University :** {row['University']}"
                        )
# =====================================================
# LANGUAGE
# =====================================================

with tab2:
    st.subheader("Language → Project → Students")
    language_list = sorted(
        df["Language"]
        .dropna()
        .unique()
    )
    for language in language_list:
        if language == "":
            continue
        language_df = df[
            df["Language"] == language
        ]
        with st.expander(
            f"💻 {language} ({len(language_df)})"
        ):
            language_df = language_df.sort_values("Topic")
            for _, row in language_df.iterrows():
                with st.expander(
                    f"📁 {row['Topic']}"
                ):
                    st.write(
                        f"**Student 1 :** {row['Student_1_Name']}"
                    )
                    if (
                        row["Student_2_Name"]
                        not in ["", "N/A", "nan"]
                    ):
                        st.write(
                            f"**Student 2 :** {row['Student_2_Name']}"
                        )
                    st.write("---")
                    st.write(
                        f"**Faculty :** {row['Faculty']}"
                    )
                    st.write(
                        f"**University :** {row['University']}"
                    )
# =====================================================
# UNIVERSITY
# =====================================================

with tab3:

    st.subheader("University → Project → Students")

    university_list = sorted(
        df["University"]
        .dropna()
        .unique()
    )

    for university in university_list:
        if university == "":
            continue
        university_df = df[
            df["University"] == university
        ]
        with st.expander(
            f"🏛 {university} ({len(university_df)})"
        ):
            university_df = university_df.sort_values("Topic")
            for _, row in university_df.iterrows():
                with st.expander(
                    f"📁 {row['Topic']}"
                ):
                    st.write(
                        f"**Student 1 :** {row['Student_1_Name']}"
                    )
                    if (
                        row["Student_2_Name"]
                        not in ["", "N/A", "nan"]
                    ):
                        st.write(
                            f"**Student 2 :** {row['Student_2_Name']}"
                        )
                    st.write("---")
                    st.write(
                        f"**Faculty :** {row['Faculty']}"
                    )
                    st.write(
                        f"**Language :** {row['Language']}"
                    )
st.divider()
# =====================================================
# SEARCH
# =====================================================
st.header("🔍 Search")
search = st.text_input(
    "Search by Project, Student, Faculty, Language or University"
)
if search.strip():
    mask = (
        df["Topic"].str.contains(search, case=False, na=False)
        |
        df["Student_1_Name"].str.contains(search, case=False, na=False)
        |
        df["Student_2_Name"].str.contains(search, case=False, na=False)
        |
        df["Faculty"].str.contains(search, case=False, na=False)
        |
        df["Language"].str.contains(search, case=False, na=False)
        |
        df["University"].str.contains(search, case=False, na=False)
    )
    result = df[mask]
    if len(result):
        st.success(f"{len(result)} Result(s) Found")
        display = result.drop(
            columns=[
                "Student_1_Number",
                "Student_2_Number"
            ],
            errors="ignore"
        )
        st.dataframe(
            display,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.warning("No matching records found.")
st.divider()

# =====================================================
# DOWNLOAD CSV
# =====================================================

download_df = df.drop(
    columns=[
        "Student_1_Number",
        "Student_2_Number"
    ],
    errors="ignore"
)

st.download_button(
    label="⬇ Download Project List (CSV)",
    data=download_df.to_csv(index=False),
    file_name="MCMT_Project_List.csv",
    mime="text/csv"
)

st.caption(
    "Phone numbers are intentionally excluded from the downloaded file."
)

st.divider()

# =====================================================
# MANUAL REFRESH
# =====================================================

col1, col2 = st.columns([1, 4])

with col1:

    if st.button("🔄 Refresh"):

        st.cache_data.clear()
        st.rerun()

with col2:

    st.info(
        "Dashboard automatically refreshes every 60 seconds (cached). "
        "Click Refresh to load the latest data immediately."
    )

st.divider()

# =====================================================
# FOOTER
# =====================================================

st.markdown("---")

st.caption(
    "© 2026 Microtek College of Management & Technology | "
    "Department of Computer Science"
)

st.caption(
    "Developed by HOD CS | Project Monitoring Dashboard"
)
