\# Supply Chain Insights (EDA • Segmentation • Forecasting)

git add README.md
git commit -m "Add polished README with screenshots and sections"
git pull --rebase origin main
git push



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

