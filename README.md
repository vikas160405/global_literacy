# 🌍 Global Literacy & Education Analysis Dashboard

## 📌 Project Overview

This project presents a data-driven analysis of global literacy, education, and economic indicators (1990–2023) using interactive visualizations and statistical insights.

It explores:

- 📚 Literacy trends across countries
- ⚖️ Gender disparities in education
- 💰 Relationship between education and economic growth

---

## 📊 Project Presentation (PPT)

📥 View / Download PowerPoint Presentation:  
👉 https://drive.google.com/file/d/1E6w1rYTOsUbyxyyWaj84MtwJaDbOoCZu/view?usp=sharing

### 📌 The presentation includes:

- Introduction & Problem Statement
- Dataset Explanation
- Visual Analysis
- Key Insights
- Conclusion

---

## 🚀 Key Features

- 🌍 Interactive Global Literacy Map
- 📈 GDP vs Literacy Correlation Analysis
- 🎓 Schooling vs Literacy Comparison
- 📅 Country-wise Literacy Trends
- 🏆 Top & Bottom Countries Analysis

### 📊 Advanced Visualizations

- Gender Gap Analysis
- Correlation Heatmap
- GDP Distribution
- Literacy Distribution

---

## 📸 Visualizations

- Youth Literacy Gender Gap
- Correlation Matrix
- Top Countries by Schooling
- GDP Distribution
- Adult Literacy Distribution

---

## 🧠 Key Insights

- 📉 Higher gender gap leads to lower literacy rates
- 📈 Strong positive correlation between Literacy & Schooling (~0.94+)
- 📉 Gender gap negatively impacts literacy
- 💰 GDP has moderate influence on literacy
- 🌍 Developed countries show near 100% literacy

---

## 🛠️ Tech Stack

- Python
- Pandas, NumPy – Data Processing
- Matplotlib, Seaborn, Plotly – Visualization
- SQLite – Database Management
- Streamlit – Interactive Dashboard

---

## 🛢️ SQL Queries Used in the Project

### 1️⃣ Top 5 countries with highest adult literacy in 2020

```sql
SELECT country, adult_literacy_rate
FROM literacy_rates
WHERE year = 2020
AND adult_literacy_rate IS NOT NULL
ORDER BY adult_literacy_rate DESC
LIMIT 5;
```

### 2️⃣ Countries where female youth literacy < 80%

```sql
SELECT country, year, youth_literacy_female
FROM literacy_rates
WHERE youth_literacy_female < 80
ORDER BY youth_literacy_female ASC;
```

### 3️⃣ Average adult literacy by country

```sql
SELECT country,
ROUND(AVG(adult_literacy_rate), 2) AS avg_adult_literacy
FROM literacy_rates
GROUP BY country
ORDER BY avg_adult_literacy DESC;
```

### 4️⃣ Countries with illiteracy % > 20% in 2000

```sql
SELECT country, illiteracy_pct
FROM illiteracy_population
WHERE year = 2000
AND illiteracy_pct > 20
ORDER BY illiteracy_pct DESC;
```

### 5️⃣ Trend of illiteracy % for India (2000–2020)

```sql
SELECT year, illiteracy_pct
FROM illiteracy_population
WHERE country = 'India'
AND year BETWEEN 2000 AND 2020
ORDER BY year;
```

### 6️⃣ Top 10 countries with largest illiterate population

```sql
SELECT country, year, illiterate_total
FROM illiteracy_population
WHERE year = (
    SELECT MAX(year)
    FROM illiteracy_population
)
ORDER BY illiterate_total DESC
LIMIT 10;
```

### 7️⃣ Countries with schooling > 7 and GDP < 5000

```sql
SELECT country, year,
avg_years_schooling,
gdp_per_capita
FROM gdp_schooling
WHERE avg_years_schooling > 7
AND gdp_per_capita < 5000
ORDER BY gdp_per_capita ASC;
```

### 8️⃣ Rank countries by GDP per schooling year in 2020

```sql
SELECT country,
gdp_per_schooling_year,
gdp_per_capita,
avg_years_schooling
FROM gdp_schooling
WHERE year = 2020
ORDER BY gdp_per_schooling_year DESC;
```

### 9️⃣ Global average schooling years per year

```sql
SELECT year,
ROUND(AVG(avg_years_schooling), 2)
AS global_avg_schooling
FROM gdp_schooling
GROUP BY year
ORDER BY year;
```

### 🔟 Highest GDP but schooling less than 6

```sql
SELECT country,
gdp_per_capita,
avg_years_schooling
FROM gdp_schooling
WHERE year = 2020
AND avg_years_schooling < 6
ORDER BY gdp_per_capita DESC
LIMIT 10;
```

### 1️⃣1️⃣ High illiteracy despite schooling > 10

```sql
SELECT i.country,
i.year,
i.illiteracy_pct,
g.avg_years_schooling
FROM illiteracy_population i
JOIN gdp_schooling g
ON i.country = g.country
AND i.year = g.year
WHERE g.avg_years_schooling > 10
AND i.illiteracy_pct > 10
ORDER BY i.illiteracy_pct DESC;
```

### 1️⃣2️⃣ Literacy rates and GDP growth for India

```sql
SELECT l.year,
l.adult_literacy_rate,
g.gdp_per_capita
FROM literacy_rates l
JOIN gdp_schooling g
ON l.country = g.country
AND l.year = g.year
WHERE l.country = 'India'
AND l.year >= 2003
ORDER BY l.year;
```

### 1️⃣3️⃣ Gender literacy gap for countries with GDP > 30000

```sql
SELECT l.country,
l.youth_literacy_male,
l.youth_literacy_female,
l.literacy_gender_gap,
g.gdp_per_capita
FROM literacy_rates l
JOIN gdp_schooling g
ON l.country = g.country
AND l.year = g.year
WHERE l.year = 2020
AND g.gdp_per_capita > 30000
ORDER BY l.literacy_gender_gap DESC;
```

---

## 📂 Project Structure

```text
├── streamlit_app.py
├── Global_Literacy_Project.ipynb
├── cleaned_datasets/
│   ├── cleaned_gdp_schooling.csv
│   ├── cleaned_literacy_rates.csv
│   ├── cleaned_illiteracy_population.csv
├── global_literacy.db
├── images/
│   ├── gender_gap.png
│   ├── correlation_heatmap.png
│   ├── top20_schooling.png
│   ├── gdp_dist.png
│   ├── adult_literacy_dist.png
└── README.md
```

---

## ⚙️ Installation & Setup

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/your-username/global-literacy-dashboard.git
cd global-literacy-dashboard
```

### 2️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 3️⃣ Run the Application

```bash
streamlit run streamlit_app.py
```

---

## 📊 Data Sources

- Our World in Data (OWID)
- World Bank

---

## 📈 Future Improvements

- 🔮 Add Machine Learning Predictions
- 🌐 Deploy Dashboard Online
- 🔄 Real-time Data Updates
- 🎨 Enhanced UI/UX
