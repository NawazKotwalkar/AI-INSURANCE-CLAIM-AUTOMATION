# AI Insurance Claim Automation (Healthcare)

## About the Project
This project focuses on automating the analysis of healthcare insurance claims using Python and Data Science.
The goal is to identify claim patterns, detect fraud, and understand why claims get denied —
helping insurance companies process claims faster and more accurately.

## Dataset
- **File:** `claim_data.csv`
- **Rows:** 1000 claims
- **Columns:** 15 (Claim ID, Provider ID, Patient ID, Billed Amount, Paid Amount, Claim Status, Outcome, Reason Code, Insurance Type, and more)

## What We Did

### Day 1 — Data Understanding & EDA
- Loaded the dataset using Pandas
- Cleaned data (duplicates, null values, data types)
- Calculated mean and median of claim amounts
- Found denial rates and revenue leakage
- Plotted distribution of Billed, Allowed, and Paid amounts

### Day 2 — Visualizations & Insights
- Bar chart of claim outcomes (Paid, Denied, Partially Paid)
- Bar chart of top denial reasons
- Comparison of average Billed vs Paid amounts

### Day 3 — Final Cleaning & Export
- Final data cleaning pass
- Added new columns: Claim Gap and Recovery Rate
- Exported cleaned data as `clean_claim_data.csv`

## Tools Used
- Python
- Pandas
- Matplotlib
- Jupyter Notebook