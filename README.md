# AI Insurance Claim Automation — DS-03 KPI Dashboard

---

![Status](https://img.shields.io/badge/Status-Week%205%20Complete-16a34a?style=flat-square)
![Week](https://img.shields.io/badge/Sprint-W1%20%7C%20W2%20%7C%20W3%20%7C%20W4%20%7C%20W5-1a3a6b?style=flat-square)
![Python](https://img.shields.io/badge/Python-3.13-1a3a6b?style=flat-square&logo=python&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-Latest-636EFA?style=flat-square&logo=plotly&logoColor=white)
![Dash](https://img.shields.io/badge/Dash-Latest-00CC96?style=flat-square&logo=plotly&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-D71F00?style=flat-square)
![Pandas](https://img.shields.io/badge/Pandas-Latest-150458?style=flat-square&logo=pandas&logoColor=white)

---

## Overview

This repository contains all five weekly deliverables for the **DS-03 KPI Dashboard** workstream, part of the AI Insurance Claim Automation system built for a UK Healthcare demo.

The goal of this workstream is to define, compute, visualise, and serve real-time KPI metrics measuring the performance of the AI claim processing pipeline — from approval rates and fraud detection through to cost savings and automation efficiency.

---

## Project Context

| Field | Detail |
|---|---|
| **Project** | AI Insurance Claim Automation — UK Healthcare Demo |
| **Squad** | Data Science & Analytics |
| **Role** | KPI Dashboard Intern (DS-03) |
| **Primary Dataset** | `claim_data.csv` — 1,000 synthetic UK insurance claims, 15 columns |
| **Date Range** | May 2024 → September 2024 |
| **Demo Deadline** | 3 June 2025 |

---

## Repository Structure

```
├── W1_kpi.ipynb                       # Week 1 — KPI definition & computation
├── DS03_W1_KPI_Specification.docx     # Week 1 — Formal KPI specification document
├── W2_Dashboard.ipynb                 # Week 2 — Static Plotly dashboard prototype
├── DS03_W2_Dashboard_Prototype.html   # Week 2 — Self-contained browser dashboard
├── app.py                             # Week 3 → W5 — Live Dash dashboard (updated each week)
├── claim_data.csv                     # Primary dataset (1,000 records, 15 columns)
├── claim_data_w4.csv                  # W4 dataset — includes synthetic Trust column
├── claims_demo.csv                    # DS-01 demo dataset (500 records, 6 columns)
├── requirements.txt                   # Python dependencies
└── README.md
```

---

## KPIs Tracked

Defined in W1, visualised in W2, served live in W3, filtered in W4, demo-ready in W5.

| # | KPI | Value | Status | Notes |
|---|---|---|---|---|
| 1 | **Approval Rate** | 33.4% | ✅ Live | `Claim Status == Paid` / Total |
| 2 | **Avg Days to Decision** | — | ❌ Blocked | Requires `decision_date` column from FS-06 |
| 3 | **Fraud Flag Rate** | 25.5% | ⚠️ Proxy | Reason code proxy — replaced by ML-03 `fraud_score` when available |
| 4 | **Auto-Decision Rate** | 11.6% | ⚠️ Proxy | Outcome proxy — replaced by ML-04 `auto_decision_flag` when available |
| 5 | **£ Saved** | £96,437 | ✅ Live | `SUM(Billed Amount − Paid Amount)` — avg £96.44/claim |

---

## Weekly Deliverables

### Week 1 — KPI Specification & Computation [`W1_kpi.ipynb`]

- Loaded and validated `claim_data.csv` — 1,000 records, 15 columns
- Formally defined all 5 KPIs with business logic, formulas, and column mappings
- Computed KPI values using Pandas with structured console output
- Identified and documented upstream blockers for KPI 2 and KPI 4
- Produced formal KPI specification Word document (`DS03_W1_KPI_Specification.docx`)

**Output:** `W1_kpi.ipynb` + `DS03_W1_KPI_Specification.docx`

---

### Week 2 — Static Dashboard Prototype [`W2_Dashboard.ipynb`]

Built a fully static interactive dashboard using Plotly and exported as a self-contained HTML file.

- **KPI Indicator Cards** — 5-panel row, colour coded, with inline Blocked and Proxy warnings
- **Monthly Trend Lines** — approval rate, fraud flag rate, and £ saved across May–Sep 2024
- **Claim Breakdown Charts** — by insurance type, claim status distribution, monthly volume
- **Auto-Decision Donut** — 11.6% auto-decided vs 88.4% human review with proxy label
- Fixed Plotly blank chart issue — moved CDN script to `<head>` so all charts render

**Output:** `W2_Dashboard.ipynb` + `DS03_W2_Dashboard_Prototype.html`

---

### Week 3 — Live Dashboard with SQLAlchemy + Auto-Refresh [`app.py`]

Converted the W2 static prototype into a live Dash application with database connectivity.

- Replaced static `pd.read_csv()` with SQLAlchemy abstraction layer
- Added `dcc.Interval` for 30-second auto-refresh — re-queries data on every tick
- Built `USE_DATABASE` toggle — one line switches between CSV and PostgreSQL
- All chart logic moved into Dash callbacks so data is always live

**How to run:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```
Open browser → `http://localhost:8050`

**Switch to PostgreSQL (when FS-06 provides credentials):**
```python
# In app.py, change:
USE_DATABASE = False   # current — CSV mode

# To:
USE_DATABASE = True    # connects to PostgreSQL

# And update:
engine = create_engine("postgresql://user:password@host:5432/dbname")
```

**W3 Deliverable Status:**
- [x] SQLAlchemy DB connection layer
- [x] 30-second auto-refresh via `dcc.Interval`
- [x] CSV / PostgreSQL toggle
- [ ] PostgreSQL live connection — pending FS-06 credentials

---

### Week 4 — Filters + Drill-Down + Smart Column Detection [`app.py`]

Extended the W3 dashboard with interactive filters, individual claim drill-down, and a smart dataset detection system.

- **Top bar filters** — Trust, Insurance Type, and Date Range — all charts respond instantly
- **Individual claim drill-down table** — sortable, filterable, colour-coded by status
- **Smart column detection** — dashboard adapts to any dataset automatically:
  - No Trust column → filter disabled, banner shows blocker
  - No `decision_date` → KPI 2 shows Blocked label
  - No `fraud_score` → falls back to reason code proxy
  - No `auto_decision_flag` → falls back to outcome proxy
- Added synthetic Trust column to `claim_data_w4.csv` with 8 UK provider trusts
- Dataset auto-detection priority: `claim_data_w4.csv` → `claim_data.csv` → `claims_demo.csv`

**W4 Deliverable Status:**
- [x] Trust filter
- [x] Date range filter
- [x] Insurance type filter
- [x] Individual claim drill-down table
- [x] Smart adaptive column detection
- [ ] Integration testing with FS-05 — pending Full Stack availability

---

### Week 5 — Demo-Ready Dashboard [`app.py`]

Final polish sprint — performance optimisation and demo preparation.

- **Data caching** — dataset loaded once into memory, serves instantly on every 30s refresh
- **Load time display** — millisecond timer shown next to last refresh timestamp
- **Demo talking points panel** built into dashboard UI:
  - Real-time visibility — live claim processing view every 30 seconds
  - Cost savings — £96,437 saved across 1,000 claims, avg £96 per claim
  - Fraud detection — 25.5% flagged, upgrades to ML-03 real-time score when live
- `debug=False` set for demo day — removes debug overhead for faster load
- All charts confirmed loading within 2 seconds on local dataset

**W5 Deliverable Status:**
- [x] 3 demo talking points prepared and embedded in dashboard
- [x] Charts load within 2 seconds
- [x] Data caching implemented
- [x] debug=False for demo

---

## How to Run

```bash
# 1. Create virtual environment (required on Linux Mint / Ubuntu)
python3 -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run dashboard
python app.py

# 4. Open browser
# http://localhost:8050
```

---

## Tech Stack

| Tool | Purpose |
|---|---|
| Python 3.13 | Core language |
| Pandas | Data loading, aggregation, KPI computation |
| Plotly | All chart rendering |
| Dash | Live web dashboard framework (W3+) |
| SQLAlchemy | Database abstraction layer (W3+) |
| Jupyter Notebook | W1 and W2 development environment |

---

## Dependencies & Blockers

| KPI | Blocker | Blocked By | Status |
|---|---|---|---|
| Avg Days to Decision | `decision_date` column missing from DB schema | FS-06 | Pending |
| Fraud Flag Rate | `fraud_score` not yet in `/predict` API output | ML-03 | Proxy in use |
| Auto-Decision Rate | `auto_decision_flag` not yet from rules engine | ML-04 | Proxy in use |
| Trust filter | `Trust` column not in original dataset | DS-01 | Synthetic data used |
| PostgreSQL connection | DB credentials not yet provided | FS-06 | CSV mode active |

---

## Design System

Dashboard theme matched to project Figma design:

| Token | Value | Usage |
|---|---|---|
| Primary | `#1a3a6b` | Header, sidebar, table headers |
| Blue | `#2563eb` | Active elements, links, record count |
| Green | `#16a34a` | Approved status, success states |
| Red | `#dc2626` | Denied status, fraud alerts |
| Orange | `#f59e0b` | Pending, blocked, proxy warnings |
| Background | `#f1f5f9` | Page background |
| Font | Arial | All text |

---

## Commit History

| Week | Commit Message |
|---|---|
| W1 | `DS-03 W1 - KPI specification document` |
| W2 | `DS-03 W2 - Static dashboard prototype` |
| W3 | `DS-03 W3 - Live dashboard SQLAlchemy + 30s refresh` |
| W4 | `DS-03 W4 - Filters + drill-down + smart column detection` |
| W5 | `DS-03 W5 - Demo ready dashboard with talking points and performance optimisation` |

---

*AI Insurance Claim Automation | UK Healthcare Demo | DS-03 | Confidential — Internal Use Only*