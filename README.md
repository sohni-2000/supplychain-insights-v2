# 📊 Supply Chain Insights Dashboard

An interactive Streamlit dashboard for **EDA, Forecasting, and Customer Segmentation**.  
Built with **Python, Pandas, Plotly, and Streamlit** — recruiter-ready, business-friendly.

---

## 🚀 Features
- **EDA (Exploratory Data Analysis)**  
  Sales by category, region, and month with interactive charts.  

- **Forecasting**  
  Next 3-month sales forecast using Prophet (or fallback rolling average).  

- **Customer Segmentation**  
  K-Means clustering to group customers (Platinum/Gold/Silver/Bronze).  

- **Interactive Dashboard**  
  Tabs for Overview, Customers, Profiles, EDA, Forecasting, and Help.  

---

## 📂 Project Structure
sc_fresh/
│
├── app/ # Streamlit app
│ └── app.py
├── data/ # Local datasets (not tracked in Git)
│ ├── README.md
│ └── sample_data.csv
├── outputs/ # Saved analysis outputs
│ ├── customer_segments.csv
│ ├── segment_profile.csv
│ ├── forecast_prophet.csv
│ └── ...
├── screenshots/ # Dashboard screenshots for README
│ ├── overview.png
│ ├── customers.png
│ ├── profiles.png
│ ├── eda.png
│ └── forecasting.png
├── requirements.txt
└── README.md

yaml
Copy code

---

## 🛠️ Installation
Clone the repo and create a virtual environment:

```bash
git clone https://github.com/sohni-2000/supplychain-insights-v2.git
cd supplychain-insights-v2

python -m venv .venv
.\.venv\Scripts\activate

pip install -r requirements.txt
▶️ Run locally
bash
Copy code
streamlit run app/app.py
The app will start at http://localhost:8501

📑 Data setup
Place your full dataset as data/train.csv (kept local / not in Git).

A tiny demo dataset (data/sample_data.csv) is included.
To run without real data, copy it to train.csv:

bash
Copy code
copy data\sample_data.csv data\train.csv
📸 Dashboard Preview
Overview	Customers	Profiles
		

EDA	Forecasting
	

📜 License
MIT License. Free to use and adapt.

yaml
Copy code

---

✅ Steps for you:  
1. Open `C:\dev\sc_fresh\README.md`.  
2. Replace everything with the above code.  
3. Save.  
4. Run:

```bash
git add README.md
git commit -m "Finalize README with full project description"
git push