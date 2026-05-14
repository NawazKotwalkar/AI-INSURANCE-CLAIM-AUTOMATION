# NHS Claims Analytics — KPI Dashboard
### DS-03 | Data Science & Analytics Squad
**AI Insurance Claim Automation — UK NHS & Private Clinic Demo**

---

![Status](https://img.shields.io/badge/Status-Week%202%20Complete-009639?style=flat-square)
![Week](https://img.shields.io/badge/Sprint-W1%20%7C%20W2-003087?style=flat-square)
![Python](https://img.shields.io/badge/Python-3.13-003087?style=flat-square&logo=python&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-6.7.0-636EFA?style=flat-square&logo=plotly&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-Latest-150458?style=flat-square&logo=pandas&logoColor=white)

---

## Overview

This repository contains the Week 1 and Week 2 deliverables for the **DS-03 KPI Dashboard** workstream, part of a larger multi-squad AI Insurance Claim Automation system built for a UK NHS & Private Clinic demonstration.

The goal of this workstream is to define, compute, visualise, and eventually serve real-time KPI metrics that measure the performance of the AI claim processing pipeline — from approval rates and fraud detection through to cost savings and automation efficiency.

---

## Project Context

| Field | Detail |
|---|---|
| **Project** | AI Insurance Claim Automation — UK Healthcare Demo |
| **Squad** | Data Science & Analytics |
| **Role** | KPI Dashboard Intern (DS-03) |
| **Dataset** | `claim_data.csv` — 1,000 synthetic UK insurance claims |
| **Date Range** | May 2024 → September 2024 |
| **Demo Deadline** | 3 June 2025 |

---

## Repository Structure

```
├── W1_kpi.ipynb                      # Week 1 — KPI definition & computation
├── W2_Dashboard.ipynb                # Week 2 — Static Plotly dashboard prototype
├── DS03_W2_Dashboard_Prototype.html  # Week 2 — Exported self-contained dashboard
├── claim_data.csv                    # Source dataset (1,000 records, 17 columns)
└── README.md
```

---

## KPIs Tracked

The following five KPIs were formally defined in Week 1 in alignment with the Full Stack and UI/UX squads, and visualised in Week 2.

| # | KPI | Value | Notes |
|---|---|---|---|
| 1 | **Approval Rate** | 33.4% | Share of claims with `Claim Status == Paid` |
| 2 | **Avg Days to Decision** | — | Pending — requires `decision_date` field from the Database squad |
| 3 | **Fraud Flag Rate** | 25.5% | Claims with reason codes: `Duplicate claim` or `Incorrect billing information` |
| 4 | **Auto-Decision Rate** | 11.6% *(proxy)* | Proxy: `Outcome == Paid AND Claim Status == Paid`. To be replaced by the `auto_decision_flag` field from the AI/ML squad |
| 5 | **£ Saved** | £96,437 | `Billed Amount − Paid Amount`, summed across all claims (avg: £96.44/claim) |

---

## Weekly Deliverables

### Week 1 — KPI Specification & Computation [`W1_kpi.ipynb`]

- Loaded and validated `claim_data.csv` (1,000 records | 17 columns)
- Formally defined all 5 KPIs with business logic and column mappings
- Computed KPI values using Pandas and printed a structured summary
- Identified and documented two upstream dependencies blocking full KPI coverage (see [Dependencies](#dependencies--blockers) below)

**Output:** KPI summary printed to console with clear BLOCKED annotations where data is unavailable.

---

### Week 2 — Static Dashboard Prototype [`W2_Dashboard.ipynb` → `DS03_W2_Dashboard_Prototype.html`]

Built a fully static, NHS-branded interactive dashboard using **Plotly** and exported it as a self-contained HTML file. The dashboard includes four visual sections:

**1. KPI Indicator Cards (5-panel row)**
Top-level metric tiles displaying all five KPIs at a glance, colour-coded to NHS palette standards — green for approval, red for fraud, NHS Blue for automation, with inline warning labels on blocked or proxy metrics.

**2. Monthly Trend Lines**
Line charts plotting the month-over-month movement of approval rate, fraud flag rate, auto-decision rate, and £ saved across the May–September 2024 period. Aggregated at `Month` level using `Date of Service`.

**3. Claim Breakdown Charts**
Segmentation of claims by insurance type (Medicare, Commercial, Self-Pay, etc.), claim status distribution, and reason code frequency — providing context for the top-level KPIs.

**4. Auto-Decision Donut Chart**
Visualises the 11.6% auto-decided vs 88.4% human-review split, with a prominent proxy warning note pending the AI/ML squad's `auto_decision_flag` integration.

**Output:** `DS03_W2_Dashboard_Prototype.html` — a fully self-contained, browser-ready dashboard file with no external dependencies at runtime.

---

## Tech Stack

| Tool | Purpose |
|---|---|
| Python 3.13 | Core language |
| Pandas | Data loading, aggregation, KPI computation |
| NumPy | Numerical support |
| Plotly 6.7.0 | All chart rendering (indicators, line charts, bar charts, donut) |
| Plotly Subplots | Multi-panel KPI card layout |
| Jupyter Notebook | Development environment |
| HTML export | Self-contained dashboard delivery |

---

## Dependencies & Blockers

Two KPIs have upstream dependencies on other squads and are currently incomplete or using proxy logic:

**KPI 2 — Avg Days to Decision**
This metric requires a `decision_date` column in the claims database schema. The column has not yet been added. This KPI will remain **BLOCKED** until the Database squad delivers the updated schema. Once available, this notebook will be updated to compute the delta between `Date of Service` and `decision_date`.

**KPI 4 — Auto-Decision Rate (Proxy)**
The definitive auto-decision flag (`auto_decision_flag`) will be produced by the AI/ML squad's rules engine. Until that field is available in the dataset, the auto-decision rate is approximated using the condition `Outcome == 'Paid' AND Claim Status == 'Paid'`. This proxy will be replaced upon delivery of the ML squad's output. The dashboard clearly labels this metric as a proxy in both the chart title and the blocker banner.

---

## Upcoming Weeks

| Week | Planned Deliverable |
|---|---|
| **W3** | Connect dashboard to live PostgreSQL database via SQLAlchemy; implement auto-refresh every 30 seconds |
| **W4** | Add interactive filters (by trust, date range, claim type); add drill-down on individual claims; integration testing with the Full Stack squad |
| **W5** | Demo preparation — finalise 3 key dashboard talking points; ensure all charts load within 2 seconds for client demo |

---

## Design Notes

The dashboard follows **NHS Identity Guidelines**:
- Primary colour: NHS Blue `#003087`
- Success/approval: NHS Green `#009639`
- Alert/fraud: NHS Red `#DA291C`
- Warning/blocked: Amber `#ED8B00`
- Font: Arial (NHS standard)
- All charts use `paper_bgcolor: white` with clean margins for presentation readability

---

*AI Insurance Claim Automation | UK NHS & Private Clinic Demo | Confidential — Internal Use Only*