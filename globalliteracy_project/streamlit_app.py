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
        st.error("global_literacy.db not found.")
        st.stop()

    # ==========================================
    # CUSTOM QUERY SECTION
    # ==========================================

    st.subheader("✍ Custom SQL Query")

    query = st.text_area(
        "Write SQL Query",
        "SELECT * FROM literacy_rates LIMIT 10;",
        height=150
    )

    if st.button("▶ Run Custom Query"):

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
                "custom_query_result.csv",
                "text/csv"
            )

        except Exception as e:
            st.error(f"SQL Error: {e}")

    st.markdown("---")

    # ==========================================
    # PROJECT QUERIES SECTION
    # ==========================================

    st.subheader("📜 Project SQL Queries")

    sql_queries = {

        "Q1 - Top 5 countries with highest adult literacy in 2020":
        """
        SELECT country, adult_literacy_rate
        FROM literacy_rates
        WHERE year = 2020
        AND adult_literacy_rate IS NOT NULL
        ORDER BY adult_literacy_rate DESC
        LIMIT 5;
        """,

        "Q2 - Countries where female youth literacy < 80%":
        """
        SELECT DISTINCT country, year, youth_literacy_female
        FROM literacy_rates
        WHERE youth_literacy_female < 80
        ORDER BY youth_literacy_female ASC;
        """,

        "Q3 - Average adult literacy per continent/region":
        """
        SELECT
            CASE
                WHEN iso_code LIKE 'A%' THEN 'Africa/Asia'
                WHEN iso_code LIKE 'E%' THEN 'Europe'
                WHEN iso_code LIKE 'N%' OR iso_code LIKE 'U%' THEN 'Americas'
                WHEN iso_code LIKE 'O%' THEN 'Oceania'
                ELSE 'Other'
            END AS region,
            ROUND(AVG(adult_literacy_rate), 2) AS avg_adult_literacy
        FROM literacy_rates
        WHERE adult_literacy_rate IS NOT NULL
        GROUP BY region
        ORDER BY avg_adult_literacy DESC;
        """,

        "Q4 - Countries with illiteracy % > 20% in 2000":
        """
        SELECT country,
               ROUND(illiteracy_pct,2) AS illiteracy_pct
        FROM illiteracy_population
        WHERE year = 2000
        AND illiteracy_pct > 20
        ORDER BY illiteracy_pct DESC;
        """,

        "Q5 - Trend of illiteracy % for India (2000–2020)":
        """
        SELECT year,
               ROUND(illiteracy_pct,2) AS illiteracy_pct
        FROM illiteracy_population
        WHERE country = 'India'
        AND year BETWEEN 2000 AND 2020
        ORDER BY year;
        """,

        "Q6 - Top 10 countries with largest illiterate population":
        """
        WITH latest AS (
            SELECT country,
                   MAX(year) AS max_year
            FROM illiteracy_population
            GROUP BY country
        )
        SELECT ip.country,
               ip.year,
               ROUND(ip.illiterate_total) AS illiterate_total
        FROM illiteracy_population ip
        JOIN latest l
        ON ip.country = l.country
        AND ip.year = l.max_year
        ORDER BY illiterate_total DESC
        LIMIT 10;
        """,

        "Q7 - Countries with avg schooling > 7 and GDP < 5000":
        """
        SELECT country,
               year,
               ROUND(avg_years_schooling,2) AS avg_years_schooling,
               ROUND(gdp_per_capita,2) AS gdp_per_capita
        FROM gdp_schooling
        WHERE avg_years_schooling > 7
        AND gdp_per_capita < 5000
        ORDER BY avg_years_schooling DESC;
        """,

        "Q8 - Rank countries by GDP per schooling year (2020)":
        """
        SELECT country,
               ROUND(gdp_per_capita,2) AS gdp_per_capita,
               ROUND(avg_years_schooling,2) AS avg_years_schooling,
               ROUND(gdp_per_schooling_year,2) AS gdp_per_schooling_year,
               RANK() OVER (
                   ORDER BY gdp_per_schooling_year DESC
               ) AS rank
        FROM gdp_schooling
        WHERE year = 2020
        AND gdp_per_schooling_year IS NOT NULL
        ORDER BY rank
        LIMIT 20;
        """,

        "Q9 - Global average schooling years per year":
        """
        SELECT year,
               ROUND(AVG(avg_years_schooling),2)
               AS global_avg_schooling
        FROM gdp_schooling
        WHERE avg_years_schooling IS NOT NULL
        GROUP BY year
        ORDER BY year;
        """,

        "Q10 - Highest GDP but lowest schooling (<6 years)":
        """
        SELECT country,
               ROUND(gdp_per_capita,2) AS gdp_per_capita,
               ROUND(avg_years_schooling,2) AS avg_years_schooling
        FROM gdp_schooling
        WHERE year = 2020
        AND avg_years_schooling < 6
        ORDER BY gdp_per_capita DESC
        LIMIT 10;
        """,

        "Q11 - High illiteracy despite >10 schooling years":
        """
        SELECT ip.country,
               ip.year,
               ROUND(ip.illiteracy_pct,2) AS illiteracy_pct,
               ROUND(gs.avg_years_schooling,2) AS avg_years_schooling
        FROM illiteracy_population ip
        JOIN gdp_schooling gs
        ON ip.country = gs.country
        AND ip.year = gs.year
        WHERE gs.avg_years_schooling > 10
        ORDER BY ip.illiteracy_pct DESC
        LIMIT 20;
        """,

        "Q12 - India literacy and GDP growth":
        """
        SELECT lr.country,
               lr.year,
               ROUND(lr.adult_literacy_rate,2) AS adult_literacy_rate,
               ROUND(gs.gdp_per_capita,2) AS gdp_per_capita
        FROM literacy_rates lr
        LEFT JOIN gdp_schooling gs
        ON lr.country = gs.country
        AND lr.year = gs.year
        WHERE lr.country = 'India'
        AND lr.year >= 2000
        ORDER BY lr.year;
        """,

        "Q13 - Gender gap for GDP > $30,000 countries":
        """
        SELECT lr.country,
               ROUND(lr.youth_literacy_male,2) AS youth_literacy_male,
               ROUND(lr.youth_literacy_female,2) AS youth_literacy_female,
               ROUND(lr.literacy_gender_gap,2) AS gender_gap,
               ROUND(gs.gdp_per_capita,2) AS gdp_per_capita
        FROM literacy_rates lr
        JOIN gdp_schooling gs
        ON lr.country = gs.country
        AND lr.year = gs.year
        WHERE gs.year = 2020
        AND gs.gdp_per_capita > 30000
        ORDER BY ABS(gender_gap) DESC;
        """
    }

    selected_query = st.selectbox(
        "Select Project SQL Query",
        list(sql_queries.keys())
    )

    st.code(
        sql_queries[selected_query],
        language="sql"
    )

    if st.button("▶ Execute Selected Query"):

        try:

            result = pd.read_sql_query(
                sql_queries[selected_query],
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
                "⬇ Download Result CSV",
                result.to_csv(index=False).encode(),
                "project_query_result.csv",
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