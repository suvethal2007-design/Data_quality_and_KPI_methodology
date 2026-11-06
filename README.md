# Retail KPI Interactive Dashboard

## Files
- `app.py` — Streamlit interactive dashboard
- `retail-orders-raw.csv` — source order data
- `requirements.txt` — Python dependencies
- `dashboard_summary.pdf` — static KPI snapshot and methodology

## Run locally
1. Install Python 3.10 or later.
2. Open a terminal in this folder.
3. Install packages: `pip install -r requirements.txt`
4. Run: `streamlit run app.py`
5. Open the local URL shown in the terminal (usually http://localhost:8501).

## Publish online (Streamlit Community Cloud)
1. Create a GitHub repository and upload all files in this folder.
2. Visit https://share.streamlit.io/ and sign in with GitHub.
3. Select **Create app**, choose your repository, branch, and `app.py`.
4. Deploy. Copy the public app URL for your project submission.

## Data quality decisions
- Exact duplicate rows are removed.
- Invalid dates, missing required city/category values, non-numeric or non-positive quantities, and discounts outside 0–100% are excluded from KPI calculations.
- Missing discount is assumed to be 0% for this demonstration and is flagged in the dashboard. Confirm with the data owner before production use.
- Net revenue includes Paid orders only. Pending, Failed and Refunded orders contribute zero to net revenue.
- Churn and customer acquisition cost cannot be computed from this dataset because customer-level history and acquisition spend are not present.
