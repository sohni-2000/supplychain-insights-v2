\# Supply Chain Insights (EDA • Segmentation • Forecasting)



Interactive Streamlit app:

\- EDA: Category, Region, Monthly trends

\- Customer Segmentation: RFM-style features + KMeans

\- Forecasting: Prophet (if provided) or rolling-mean fallback



\## Run locally

```bash

python -m venv .venv

.\\.venv\\Scripts\\activate

pip install -r requirements.txt

streamlit run app/app.py

