import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.io as pio

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="Netflix Dashboard",
    page_icon="🎬",
    layout="wide"
)

pio.templates.default = "plotly_dark"

# =========================
# CUSTOM CSS
# =========================
st.markdown("""
<style>

.main {
    background-color: #0B0B0B;
}

section[data-testid="stSidebar"] {
    background-color: #141414;
}

h1, h2, h3 {
    color: white;
}

.card {
    background-color: #161616;
    padding: 20px;
    border-radius: 15px;
    border-left: 5px solid #E50914;
    text-align: center;
}

.card h3{
    color:white;
}

.card h1{
    color:#E50914;
}

</style>
""", unsafe_allow_html=True)

# =========================
# LOAD DATA
# =========================
df = pd.read_csv("netflix_titles.csv")

df["country"] = df["country"].fillna("Unknown")
df["listed_in"] = df["listed_in"].fillna("")

df["date_added"] = pd.to_datetime(df["date_added"], errors="coerce")
df["year_added"] = df["date_added"].dt.year

# =========================
# SIDEBAR FILTERS
# =========================
st.sidebar.title("🎬 Netflix Filters")
st.sidebar.markdown("---")

content_type = st.sidebar.multiselect(
    "Content Type",
    options=df["type"].dropna().unique(),
    default=df["type"].dropna().unique()
)

year_range = st.sidebar.slider(
    "Release Year",
    int(df["release_year"].min()),
    int(df["release_year"].max()),
    (int(df["release_year"].min()), int(df["release_year"].max()))
)

country_filter = st.sidebar.multiselect(
    "Country",
    options=sorted(df["country"].unique())
)

genres = sorted(
    df["listed_in"].str.split(", ").explode().unique()
)

selected_genres = st.sidebar.multiselect(
    "Genre",
    genres
)

# =========================
# FILTER DATA
# =========================
filtered_df = df.copy()

filtered_df = filtered_df[
    filtered_df["type"].isin(content_type)
]

filtered_df = filtered_df[
    (filtered_df["release_year"] >= year_range[0]) &
    (filtered_df["release_year"] <= year_range[1])
]

if country_filter:
    filtered_df = filtered_df[
        filtered_df["country"].isin(country_filter)
    ]

if selected_genres:
    filtered_df = filtered_df[
        filtered_df["listed_in"].apply(
            lambda x: any(g in x for g in selected_genres)
        )
    ]

# =========================
# SAFETY CHECK
# =========================
if filtered_df.empty:
    st.warning("No data available for selected filters")
    st.stop()

# =========================
# HEADER
# =========================
st.markdown("""
<div style="
background: linear-gradient(90deg,#E50914,#B20710);
padding:25px;
border-radius:15px;
text-align:center;
margin-bottom:20px;
">
<h1 style="color:white;">🎬 Netflix Content Analytics Dashboard</h1>
<p style="color:white;font-size:18px;">
Interactive Analysis of Netflix Movies & TV Shows
</p>
</div>
""", unsafe_allow_html=True)

# =========================
# KPI CARDS
# =========================
movies = len(filtered_df[filtered_df["type"] == "Movie"])
tvshows = len(filtered_df[filtered_df["type"] == "TV Show"])
total = len(filtered_df)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
    <div class="card">
        <h3>Total Titles</h3>
        <h1>{total}</h1>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="card">
        <h3>Movies</h3>
        <h1>{movies}</h1>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="card">
        <h3>TV Shows</h3>
        <h1>{tvshows}</h1>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# =========================
# CHART 1: TYPE
# =========================
type_count = filtered_df["type"].value_counts().reset_index()
type_count.columns = ["type", "count"]

fig1 = px.pie(
    type_count,
    names="type",
    values="count",
    hole=0.5,
    title="Movies vs TV Shows",
    color_discrete_sequence=["#E50914", "#B81D24"]
)

# =========================
# CHART 2: COUNTRIES
# =========================
top_countries = df["country"].value_counts().head(10).reset_index()
top_countries.columns = ["country", "count"]

fig2 = px.bar(
    top_countries,
    x="country",
    y="count",
    title="Top 10 Content Producing Countries",
    color_discrete_sequence=["#E50914"]
)

# =========================
# DISPLAY CHARTS
# =========================
col1, col2 = st.columns(2)

with col1:
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.plotly_chart(fig2, use_container_width=True)

# =========================
# CHART 3: YEAR TREND
# =========================
content_year = filtered_df["year_added"].value_counts().sort_index().reset_index()
content_year.columns = ["year_added", "count"]

fig3 = px.line(
    content_year,
    x="year_added",
    y="count",
    title="Content Added Over Time",
    markers=True
)

st.plotly_chart(fig3, use_container_width=True)

# =========================
# CHART 4: GENRES
# =========================
genre_df = filtered_df["listed_in"].str.split(", ").explode().value_counts().head(10).reset_index()
genre_df.columns = ["listed_in", "count"]

fig4 = px.bar(
    genre_df,
    x="count",
    y="listed_in",
    orientation="h",
    title="Top 10 Genres",
    color_discrete_sequence=["#E50914"]
)

st.plotly_chart(fig4, use_container_width=True)

# =========================
# INSIGHTS
# =========================
st.subheader("Business Insights")

st.markdown("""
<div style="
background-color:#161616;
padding:20px;
border-radius:15px;
border-left:5px solid #E50914;
">

<b>1.</b> Movies represent the majority of Netflix content.<br><br>
<b>2.</b> Netflix experienced strong growth after 2015.<br><br>
<b>3.</b> A small number of countries dominate content production.<br><br>
<b>4.</b> Drama and International content are most common genres.

</div>
""", unsafe_allow_html=True)

# =========================
# FOOTER
# =========================
st.markdown("---")
st.caption("Prepared by Aseel Sultan | Data Analysis Bootcamp Project")