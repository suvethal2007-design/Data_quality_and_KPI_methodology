**# Data_quality_and_KPI_methodology
Data quality and KPI methodology
**Exact duplicate rows are removed.
Invalid dates, missing required city/category values, non-numeric or non-positive quantities, and discounts outside 0–100% are excluded from KPI calculations.
Missing discount is assumed to be 0% for this demonstration and is flagged in the dashboard. Confirm with the data owner before production use.
Net revenue includes Paid orders only. Pending, Failed and Refunded orders contribute zero to net revenue.
Churn and customer acquisition cost cannot be computed from this dataset because customer-level history and acquisition spend are not present.
