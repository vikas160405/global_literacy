#streamlit_app.py

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import sqlite3
import os

st.set_page_config(
    page_title="Global Literacy Dashboard",
    layout="wide",
    page_icon="📊"
)

# ─────────────────────────────────────────
# PATHS
# ─────────────────────────────────────────
BASE = os.path.dirname(os.path.abspath(__file__))

def find(filename):
    for p in [os.path.join(BASE, filename), filename]:
        if os.path.exists(p):
            return p
    return None

# ─────────────────────────────────────────
# LOAD DATA FROM CSVs
# ─────────────────────────────────────────
@st.cache_data
def load_all():
    lr = pd.read_csv(find("cleaned_literacy_rates.csv"))
    ip = pd.read_csv(find("cleaned_illiteracy_population.csv"))
    gs = pd.read_csv(find("cleaned_gdp_schooling.csv"))

    # Standardise literacy_rates columns
    lr = lr.rename(columns={
        "iso_code_x": "iso_code",
        "adult_literacy": "adult_literacy_rate",
        "owid_region": "region",
    })

    lr.drop(columns=["iso_code_y"], errors="ignore", inplace=True)

    # Derived features
    lr["literacy_gender_gap"] = (
        lr["youth_literacy_male"] -
        lr["youth_literacy_female"]
    )

    lr["youth_literacy_avg"] = (
        lr["youth_literacy_male"] +
        lr["youth_literacy_female"]
    ) / 2

    # Standardise illiteracy_population
    ip = ip.rename(columns={
        "illiteracy_rate": "illiteracy_pct"
    })

    # Numeric conversion
    skip = {"country", "iso_code", "region"}

    for df in [lr, ip, gs]:
        for col in df.columns:
            if col not in skip:
                df[col] = pd.to_numeric(
                    df[col],
                    errors="coerce"
                )

    return lr, ip, gs

lr_df, ip_df, gs_df = load_all()

countries = sorted(
    lr_df["country"].dropna().unique()
)

# ─────────────────────────────────────────
# DATABASE
# ─────────────────────────────────────────
@st.cache_resource
def get_conn():
    path = find("global_literacy.db")

    if path is None:
        return None

    return sqlite3.connect(
        path,
        check_same_thread=False
    )

conn = get_conn()

# ─────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────
st.sidebar.markdown("## 📊 Global Literacy App")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigate to",
    [
        "🏠 Overview Dashboard",
        "🛢️ SQL Query Executor",
        "📈 EDA Visualizations",
        "🌍 Country Profile"
    ]
)

st.sidebar.markdown("---")
st.sidebar.caption(
    "Global Literacy & Education Trends"
)

# ════════════════════════════════════════
# OVERVIEW DASHBOARD
# ════════════════════════════════════════
if page == "🏠 Overview Dashboard":

    st.title("📊 Global Literacy & Education Dashboard")
    st.markdown("### Analytical Study (1990–2023)")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "🌐 Countries",
        lr_df["country"].nunique()
    )

    c2.metric(
        "📖 Avg Adult Literacy",
        f"{lr_df['adult_literacy_rate'].mean():.1f}%"
    )

    c3.metric(
        "💰 Avg GDP/Capita",
        f"${gs_df['gdp_per_capita'].mean():,.0f}"
    )

    c4.metric(
        "🎓 Avg Schooling Idx",
        f"{gs_df['avg_years_schooling'].mean():.1f}"
    )

    st.markdown("---")

    valid_years = sorted(
        lr_df.dropna(
            subset=["iso_code", "adult_literacy_rate"]
        )["year"].unique().astype(int)
    )

    if valid_years:

        year_sel = st.select_slider(
            "Select Year for Map",
            options=valid_years,
            value=valid_years[-1]
        )

        map_df = lr_df[
            (lr_df["year"] == year_sel) &
            lr_df["iso_code"].notna() &
            lr_df["adult_literacy_rate"].notna()
        ]

        st.subheader(
            f"🌍 Global Literacy Map — {year_sel}"
        )

        if not map_df.empty:

            fig = px.choropleth(
                map_df,
                locations="iso_code",
                color="adult_literacy_rate",
                hover_name="country",
                color_continuous_scale="RdYlGn",
                range_color=[20, 100],
                labels={
                    "adult_literacy_rate":
                    "Adult Literacy %"
                }
            )

            fig.update_layout(
                margin=dict(l=0, r=0, t=0, b=0)
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        else:
            st.warning("No data available.")

# ════════════════════════════════════════
# SQL QUERY EXECUTOR
# ════════════════════════════════════════
elif page == "🛢️ SQL Query Executor":

    st.title("🛢️ SQL Query Executor")

    if conn is None:
        st.error(
            "global_literacy.db not found."
        )
        st.stop()

    query = st.text_area(
        "Write SQL Query",
        "SELECT * FROM literacy_rates LIMIT 10;",
        height=150
    )

    run = st.button("▶ Run Query")

    if run:

        try:

            result = pd.read_sql_query(
                query,
                conn
            )

            st.success(
                f"{len(result)} rows returned"
            )

            st.dataframe(
                result,
                use_container_width=True
            )

            st.download_button(
                "⬇ Download CSV",
                result.to_csv(index=False).encode(),
                "query_result.csv",
                "text/csv"
            )

        except Exception as e:
            st.error(f"SQL Error: {e}")

# ════════════════════════════════════════
# EDA VISUALIZATIONS
# ════════════════════════════════════════
elif page == "📈 EDA Visualizations":

    st.title("📈 EDA Visualizations")

    st.subheader(
        "Adult Literacy Rate Distribution"
    )

    fig1 = px.histogram(
        lr_df.dropna(
            subset=["adult_literacy_rate"]
        ),
        x="adult_literacy_rate",
        nbins=30,
        title="Histogram"
    )

    st.plotly_chart(
        fig1,
        use_container_width=True
    )

    st.subheader(
        "GDP vs Literacy"
    )

    merged = gs_df.merge(
        lr_df[
            ["country", "year",
             "adult_literacy_rate"]
        ],
        on=["country", "year"]
    )

    merged = merged.dropna(
        subset=[
            "gdp_per_capita",
            "adult_literacy_rate"
        ]
    )

    fig2 = px.scatter(
        merged,
        x="gdp_per_capita",
        y="adult_literacy_rate",
        hover_name="country",
        log_x=True,
        trendline="ols",
        title="GDP vs Literacy"
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )

# ════════════════════════════════════════
# COUNTRY PROFILE
# ════════════════════════════════════════
elif page == "🌍 Country Profile":

    st.title("🌍 Country Profile")

    sel_country = st.selectbox(
        "Select Country",
        countries
    )

    country_df = lr_df[
        lr_df["country"] == sel_country
    ]

    st.subheader(
        f"Adult Literacy Trend — {sel_country}"
    )

    fig = px.line(
        country_df,
        x="year",
        y="adult_literacy_rate",
        markers=True
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.subheader(
        f"Youth Literacy Gender Comparison"
    )

    fig2 = go.Figure()

    fig2.add_trace(
        go.Scatter(
            x=country_df["year"],
            y=country_df["youth_literacy_male"],
            mode="lines+markers",
            name="Male"
        )
    )

    fig2.add_trace(
        go.Scatter(
            x=country_df["year"],
            y=country_df["youth_literacy_female"],
            mode="lines+markers",
            name="Female"
        )
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )
