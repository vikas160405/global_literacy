🌍 Global Literacy & Education Analysis Dashboard
📌 Project Overview

This project presents a data-driven analysis of global literacy, education, and economic indicators (1990–2023) using interactive visualizations and statistical insights.

The goal is to understand:

Literacy trends across countries
Gender disparities in education
Relationship between education and economic growth

A well-written README helps others understand your project, reproduce results, and explore insights effectively

🚀 Live Demo / Project Link

🔗 Google Drive Project Link:
https://drive.google.com/file/d/1E6w1rYTOsUbyxyyWaj84MtwJaDbOoCZu/view?usp=sharing

📊 Key Features
🌍 Interactive Global Literacy Map
📈 GDP vs Literacy correlation analysis
🎓 Schooling vs Literacy relationship
📅 Country-wise literacy trends over time
🏆 Top & Bottom countries comparison
📊 Advanced visualizations:
Gender Gap Analysis
Correlation Heatmap
GDP Distribution
Literacy Distribution
📸 Project Visualizations
🔹 Youth Literacy Gender Gap

🔹 Correlation Matrix

🔹 Top Countries by Schooling

🔹 GDP Distribution

🔹 Adult Literacy Distribution

🧠 Key Insights
📉 Countries with low literacy often show high gender gaps
📈 Strong positive correlation between:
Literacy & Schooling (~0.94+)
📉 Gender gap negatively correlates with literacy
💰 GDP has moderate impact on literacy but not as strong as education
🌍 Developed countries show near 100% literacy rates
🛠️ Tech Stack
Python
Pandas, NumPy – Data Processing
Matplotlib, Seaborn, Plotly – Visualization
Streamlit – Web App Dashboard
📂 Project Structure
├── streamlit_app.py          # Main dashboard app :contentReference[oaicite:1]{index=1}
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
⚙️ Installation & Setup
1️⃣ Clone the repository
git clone https://github.com/your-username/global-literacy-dashboard.git
cd global-literacy-dashboard
2️⃣ Install dependencies
pip install -r requirements.txt
3️⃣ Run the Streamlit app
streamlit run streamlit_app.py
📊 Data Sources
Our World in Data (OWID)
World Bank datasets
📈 Future Improvements
Add Machine Learning predictions 📊
Deploy dashboard online 🌐
Add real-time data updates 🔄
Improve UI/UX design 🎨
