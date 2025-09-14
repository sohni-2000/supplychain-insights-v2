# 📊 Supply Chain Insights Dashboard
*EDA • Segmentation • Forecasting*

![Streamlit](https://img.shields.io/badge/Streamlit-1.37.0-FF4B4B?logo=streamlit&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.10-blue?logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-2.2.2-150458?logo=pandas&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-5.22.0-3F4F75?logo=plotly&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-1.5.1-F7931E?logo=scikit-learn&logoColor=white)

---
## 🌐 Live Demo  
Check out the live app here:  
👉 [Supply Chain Insights Dashboard](https://supplychain-insights-v2-ejm6tu4at6nc79li9khu83.streamlit.app)  

---

## 📌 Project Overview
This is an **interactive Streamlit dashboard** built for supply chain analytics.  
It demonstrates:
- **Exploratory Data Analysis (EDA):** Sales by category, region, and time trends.
- **Customer Segmentation:** RFM-style features with KMeans clustering.
- **Forecasting:** Sales forecasts using Prophet (with fallback to rolling mean).

The project is designed to showcase **data engineering + analytics + ML skills** in a single dashboard.

---

## 🖼️ Screenshots

### 🔎 Overview Tab  
![Overview](screenshots/overview.png)

### 👥 Customers Tab  
![Customers](screenshots/customers.png)

### 🗂️ Profiles Tab  
![Profiles](screenshots/profiles.png)

### 📊 EDA Tab  
![EDA](screenshots/eda.png)

### 📈 Forecasting Tab  
![Forecasting](screenshots/forecasting.png)

---

## ⚙️ Run Locally  

```bash
# 1. Create virtual environment
python -m venv .venv
.\\.venv\\Scripts\\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the app
streamlit run app/app.py
📂 Data setup
Place your full dataset as data/train.csv (kept local / not in Git).

A tiny demo dataset (data/sample_data.csv) is included.
To run without real data, copy it to train.csv:

bash
Copy code
copy data\sample_data.csv data\train.csv

📜 License
MIT License © 2025 Sohni Korrapolu
