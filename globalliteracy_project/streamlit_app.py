import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from io import StringIO

# ───────── PAGE CONFIG ─────────
st.set_page_config(page_title="Global Literacy Dashboard", layout="wide")

# ───────── LOAD CSV ─────────
def load_csv(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    return pd.read_csv(StringIO(response.text))

# ───────── LOAD DATA ─────────
@st.cache_data
def load_data():
    adult = load_csv("https://ourworldindata.org/grapher/literacy-rate-adults.csv")
    youth = load_csv("https://ourworldindata.org/grapher/literacy-rate-of-young-men-and-women.csv")
    gdp   = load_csv("https://ourworldindata.org/grapher/gdp-per-capita-worldbank.csv")
    school= load_csv("https://ourworldindata.org/grapher/literacy-rates-vs-average-years-of-schooling.csv")

    def clean(df):
        df = df.rename(columns={"Entity":"country","Code":"iso_code","Year":"year"})
        df = df[(df["year"] >= 1990) & (df["year"] <= 2023)]
        return df.drop_duplicates()

    adult = clean(adult)
    youth = clean(youth)
    gdp   = clean(gdp)
    school= clean(school)

    # Helper function
    def get_value_columns(df):
        ignore = ["country", "iso_code", "year"]
        return [c for c in df.columns if c not in ignore]

    # Adult literacy
    adult_col = get_value_columns(adult)[0]
    adult["adult_literacy"] = pd.to_numeric(adult[adult_col], errors="coerce")

    # Youth
    youth_cols = get_value_columns(youth)
    youth["youth_male"] = pd.to_numeric(youth[youth_cols[0]], errors="coerce")
    youth["youth_female"] = pd.to_numeric(youth[youth_cols[1]], errors="coerce")

    # GDP
    gdp_col = get_value_columns(gdp)[0]
    gdp["gdp"] = pd.to_numeric(gdp[gdp_col], errors="coerce")

    # 🔥 CLEAN SCHOOL DATA (FIXED)
    school_clean = school.copy()
    school_cols = get_value_columns(school_clean)

    # Ensure correct columns
    if len(school_cols) < 2:
        raise ValueError("School dataset does not have enough columns")

    literacy_col = school_cols[0]
    school_col = school_cols[1]

    school_clean["adult_literacy"] = pd.to_numeric(school_clean[literacy_col], errors="coerce")
    school_clean["schooling"] = pd.to_numeric(school_clean[school_col], errors="coerce")

    school_clean = school_clean.dropna(subset=["schooling", "adult_literacy"])

    # Merge (without school to avoid NaN issues)
    KEY = ["country", "iso_code", "year"]
    df = adult.merge(youth, on=KEY, how="outer") \
              .merge(gdp, on=KEY, how="outer")

    df = df.dropna(how="all")

    # Feature
    df["gender_gap"] = df["youth_male"] - df["youth_female"]

    return df, school_clean

df, school_clean = load_data()

# ───────── SIDEBAR ─────────
st.sidebar.title("🔍 Filters")

year = st.sidebar.slider("Select Year", 1990, 2023, 2020)

countries = sorted(df["country"].dropna().unique())

selected_country = st.sidebar.selectbox(
    "🔎 Select Country",
    countries,
    index=countries.index("India") if "India" in countries else 0
)

year_range = st.sidebar.slider("Year Range", 1990, 2023, (2000, 2020))

# ───────── HEADER ─────────
st.title("📊 Global Literacy & Education Dashboard")
st.markdown("### Analytical Study (1990–2023)")

# ───────── KPIs ─────────
col1, col2, col3, col4 = st.columns(4)

col1.metric("Countries", df["country"].nunique())
col2.metric("Avg Literacy", f"{df['adult_literacy'].dropna().mean():.1f}%")
col3.metric("Avg GDP", f"${df['gdp'].dropna().mean():,.0f}")
col4.metric("Avg Schooling", f"{school_clean['schooling'].mean():.1f} yrs")

st.markdown("---")

# ───────── MAP ─────────
st.subheader("🌍 Global Literacy Map")

map_df = df[
    (df["year"] == year) &
    (df["iso_code"].notna()) &
    (df["adult_literacy"].notna())
]

if not map_df.empty:
    fig_map = px.choropleth(
        map_df,
        locations="iso_code",
        color="adult_literacy",
        hover_name="country",
        color_continuous_scale="RdYlGn"
    )
    st.plotly_chart(fig_map, use_container_width=True)
else:
    st.warning("No data for selected year")

st.markdown("---")

# ───────── GDP vs LITERACY ─────────
st.subheader("📈 GDP vs Literacy")

scatter_df = df.dropna(subset=["gdp", "adult_literacy"])

try:
    fig1 = px.scatter(
        scatter_df,
        x="gdp",
        y="adult_literacy",
        hover_name="country",
        log_x=True,
        trendline="ols"
    )
except:
    fig1 = px.scatter(
        scatter_df,
        x="gdp",
        y="adult_literacy",
        hover_name="country",
        log_x=True
    )

st.plotly_chart(fig1, use_container_width=True)

st.markdown("---")

# ───────── SCHOOLING vs LITERACY ─────────
st.subheader("🎓 Schooling vs Literacy")

sv_df = school_clean.sort_values("year").groupby("country").last().reset_index()

try:
    fig2 = px.scatter(
        sv_df,
        x="schooling",
        y="adult_literacy",
        hover_name="country",
        trendline="ols"
    )
except:
    fig2 = px.scatter(
        sv_df,
        x="schooling",
        y="adult_literacy",
        hover_name="country"
    )

st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

# ───────── COUNTRY TREND ─────────
st.subheader("📅 Country Literacy Trend")

cdf = df[
    (df["country"] == selected_country) &
    (df["year"] >= year_range[0]) &
    (df["year"] <= year_range[1])
].dropna(subset=["adult_literacy"])

if not cdf.empty:
    fig3 = px.line(cdf, x="year", y="adult_literacy", markers=True)
    st.plotly_chart(fig3, use_container_width=True)
else:
    st.warning("No data for selected country")

st.markdown("---")

# ───────── TOP & BOTTOM ─────────
st.subheader("🏆 Top & Bottom Countries")

latest = df.sort_values("year").groupby("country").last().reset_index()
latest = latest.dropna(subset=["adult_literacy"])

top10 = latest.nlargest(10, "adult_literacy")
bottom10 = latest.nsmallest(10, "adult_literacy")

combined = pd.concat([top10, bottom10]).sort_values("adult_literacy")

fig4 = px.bar(
    combined,
    x="adult_literacy",
    y="country",
    orientation="h"
)

st.plotly_chart(fig4, use_container_width=True)