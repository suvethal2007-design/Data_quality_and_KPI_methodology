import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(page_title="Retail KPI Dashboard", page_icon="📊", layout="wide")

@st.cache_data
def load_data():
    file_path = Path(__file__).parent / "retail-orders-raw.csv"
    df = pd.read_csv(file_path)
    df["order_id"] = df["order_id"].astype("string").str.strip()
    df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
    df["customer_segment"] = df["customer_segment"].astype("string").str.strip().str.title()
    df["city"] = df["city"].astype("string").str.strip()
    df["category"] = df["category"].astype("string").str.strip()
    df["payment_status"] = df["payment_status"].astype("string").str.strip().str.title()
    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")
    df["unit_price"] = pd.to_numeric(df["unit_price"], errors="coerce")
    df["discount_pct"] = pd.to_numeric(df["discount_pct"], errors="coerce")

    # Exact duplicate rows are removed before KPI calculations.
    df = df.drop_duplicates()
    # Blank discounts are treated as 0% for this demo, and are disclosed in the data-quality panel.
    df["discount_was_missing"] = df["discount_pct"].isna()
    df["discount_pct"] = df["discount_pct"].fillna(0)

    required_ok = (
        df["order_id"].notna() & df["order_date"].notna() &
        df["city"].notna() & df["city"].ne("") &
        df["category"].notna() & df["quantity"].notna() &
        df["unit_price"].notna() & df["quantity"].gt(0) &
        df["unit_price"].ge(0) & df["discount_pct"].between(0, 100)
    )
    clean = df.loc[required_ok].copy()
    clean["revenue"] = clean["quantity"] * clean["unit_price"] * (1 - clean["discount_pct"] / 100)
    clean["revenue"] = clean["revenue"].where(clean["payment_status"].eq("Paid"), 0)
    return df, clean

raw, data = load_data()

st.title("🛍️ Retail Sales & KPI Dashboard")
st.caption("Interactive business intelligence dashboard | Retail Orders | INR")
st.markdown("Track revenue, orders, product performance, customer segments and payment outcomes.")

# Sidebar filters
st.sidebar.header("Dashboard Filters")
date_min, date_max = data["order_date"].min().date(), data["order_date"].max().date()
date_range = st.sidebar.date_input("Order date range", value=(date_min, date_max), min_value=date_min, max_value=date_max)
segments = st.sidebar.multiselect("Customer segment", sorted(data["customer_segment"].dropna().unique()), default=sorted(data["customer_segment"].dropna().unique()))
cities = st.sidebar.multiselect("City", sorted(data["city"].dropna().unique()), default=sorted(data["city"].dropna().unique()))
categories = st.sidebar.multiselect("Product category", sorted(data["category"].dropna().unique()), default=sorted(data["category"].dropna().unique()))
statuses = st.sidebar.multiselect("Payment status", sorted(data["payment_status"].dropna().unique()), default=sorted(data["payment_status"].dropna().unique()))

filtered = data.copy()
if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
    filtered = filtered[filtered["order_date"].dt.date.between(date_range[0], date_range[1])]
filtered = filtered[
    filtered["customer_segment"].isin(segments) &
    filtered["city"].isin(cities) &
    filtered["category"].isin(categories) &
    filtered["payment_status"].isin(statuses)
]

total_orders = filtered["order_id"].nunique()
paid = filtered[filtered["payment_status"].eq("Paid")]
paid_orders = paid["order_id"].nunique()
revenue = paid["revenue"].sum()
aov = revenue / paid_orders if paid_orders else 0
quantity = filtered["quantity"].sum()
success_rate = paid_orders / total_orders * 100 if total_orders else 0
pending = filtered.loc[filtered["payment_status"].eq("Pending"), "order_id"].nunique()

def inr(x):
    return f"₹{x:,.2f}"

c1,c2,c3,c4,c5 = st.columns(5)
c1.metric("Net Revenue (Paid)", inr(revenue))
c2.metric("Valid Orders", f"{total_orders:,}")
c3.metric("Avg. Order Value", inr(aov))
c4.metric("Units Ordered", f"{quantity:,.0f}")
c5.metric("Payment Success", f"{success_rate:.1f}%")

st.divider()
left, right = st.columns(2)
with left:
    st.subheader("Revenue Trend")
    trend = paid.groupby(paid["order_date"].dt.strftime("%d %b"))["revenue"].sum().reset_index()
    trend.columns = ["Order Date", "Revenue"]
    st.plotly_chart(px.area(trend, x="Order Date", y="Revenue", markers=True, title="Paid revenue by order date"), use_container_width=True)
with right:
    st.subheader("Revenue by Category")
    cat = paid.groupby("category", as_index=False)["revenue"].sum().sort_values("revenue", ascending=False)
    st.plotly_chart(px.bar(cat, x="category", y="revenue", color="category", title="Paid revenue by product category"), use_container_width=True)

left, right = st.columns(2)
with left:
    st.subheader("City-wise Revenue")
    city = paid.groupby("city", as_index=False)["revenue"].sum().sort_values("revenue", ascending=False)
    st.plotly_chart(px.bar(city, x="city", y="revenue", color="revenue", title="Paid revenue by city"), use_container_width=True)
with right:
    st.subheader("Customer Segment Analysis")
    seg = filtered.groupby("customer_segment", as_index=False).agg(Orders=("order_id","nunique"), Units=("quantity","sum"))
    st.plotly_chart(px.bar(seg, x="customer_segment", y="Orders", color="customer_segment", title="Valid orders by customer segment"), use_container_width=True)

left, right = st.columns(2)
with left:
    st.subheader("Payment Status")
    pay = filtered.groupby("payment_status", as_index=False)["order_id"].nunique()
    pay.columns = ["Payment Status", "Orders"]
    st.plotly_chart(px.pie(pay, names="Payment Status", values="Orders", hole=.45, title="Order settlement mix"), use_container_width=True)
with right:
    st.subheader("Discount vs Order Value")
    scatter = filtered.copy()
    scatter["gross_value"] = scatter["quantity"] * scatter["unit_price"]
    st.plotly_chart(px.scatter(scatter, x="discount_pct", y="gross_value", color="customer_segment",
                               hover_data=["order_id","city","category","payment_status"],
                               labels={"discount_pct":"Discount (%)","gross_value":"Gross order value (₹)"},
                               title="Discount and gross order value"), use_container_width=True)

st.divider()
st.subheader("Filtered Order Details")
show_cols = ["order_id","order_date","customer_segment","city","category","quantity","unit_price","discount_pct","payment_status","revenue"]
st.dataframe(filtered[show_cols].sort_values("order_date"), use_container_width=True, hide_index=True)
st.download_button("⬇️ Download filtered data (CSV)", filtered[show_cols].to_csv(index=False).encode("utf-8"),
                   file_name="filtered_retail_orders.csv", mime="text/csv")

with st.expander("Data quality & KPI methodology"):
    st.write(f"Raw rows: **{len(raw)}** | Rows after exact-duplicate removal: **{len(raw.drop_duplicates())}** | Valid rows used: **{len(data)}**")
    st.write(f"Excluded rows: **{len(raw.drop_duplicates()) - len(data)}**. Rows are excluded when required dates/cities/categories are missing, quantities are non-numeric or not positive, or discounts are outside 0–100%.")
    st.write(f"Missing discount values treated as 0% for this demonstration: **{int(data['discount_was_missing'].sum())}**. Confirm this assumption with the data owner before production use.")
    st.markdown("""
    - **Net Revenue:** Quantity × Unit Price × (1 − Discount % / 100), counted only for Paid orders.
    - **Valid Orders:** Distinct order IDs among quality-approved rows.
    - **Average Order Value:** Paid revenue ÷ distinct Paid orders.
    - **Payment Success Rate:** Distinct Paid orders ÷ distinct valid orders × 100.
    - Churn rate and customer acquisition cost are not calculated because the dataset has no customer-level history or acquisition-spend fields.
    """)
st.caption("Sample dataset contains a small number of records; treat results as a demonstration, not a statistically representative business report.")
