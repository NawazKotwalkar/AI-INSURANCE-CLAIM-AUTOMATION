# AI Insurance Claim Automation — UK

---

![Status](https://img.shields.io/badge/Status-Week%203%20Complete-009639?style=flat-square)
![Week](https://img.shields.io/badge/Sprint-W1%20%7C%20W2%20%7C%20W3-003087?style=flat-square)
![Python](https://img.shields.io/badge/Python-3.13-003087?style=flat-square&logo=python&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-6.7.0-636EFA?style=flat-square&logo=plotly&logoColor=white)
![Dash](https://img.shields.io/badge/Dash-2.17.0-00CC96?style=flat-square&logo=plotly&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-D71F00?style=flat-square)
![Pandas](https://img.shields.io/badge/Pandas-Latest-150458?style=flat-square&logo=pandas&logoColor=white)

---

## Overview

This repository contains the Week 1, Week 2, and Week 3 deliverables for the **DS-03 KPI Dashboard** workstream, part of a larger multi-squad AI Insurance Claim Automation system built for a UK NHS & Private Clinic demonstration.

The goal of this workstream is to define, compute, visualise, and serve real-time KPI metrics that measure the performance of the AI claim processing pipeline — from approval rates and fraud detection through to cost savings and automation efficiency.

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
├── app.py                            # Week 3 — Live Dash dashboard (SQLAlchemy + 30s refresh)
├── requirements.txt                  # Python dependencies
├── claim_data.csv                    # Source dataset (1,000 records, 15 columns)
├── claims_demo.csv                   # Demo dataset (500 records, 6 columns) — DS-01
└── README.md
```

---

## KPIs Tracked

Formally defined in Week 1 in alignment with the Full Stack and UI/UX squads, visualised in Week 2, and served live via database in Week 3.

| # | KPI | Value | Status | Notes |
|---|---|---|---|---|
| 1 | **Approval Rate** | 33.4% | ✅ Live | `Claim Status == Paid` / Total |
| 2 | **Avg Days to Decision** | — | ❌ Blocked | Requires `decision_date` from FS-06 |
| 3 | **Fraud Flag Rate** | 25.5% | ⚠️ Proxy | Reason codes: Duplicate / Incorrect billing. Replaced by ML-03 `fraud_score` in W3 |
| 4 | **Auto-Decision Rate** | 11.6% | ⚠️ Proxy | `Outcome == Paid AND Claim Status == Paid`. Replaced by ML-04 `auto_decision_flag` in W4 |
| 5 | **£ Saved** | £96,437 | ✅ Live | `SUM(Billed Amount − Paid Amount)` — avg £96.44/claim |

---

## Weekly Deliverables

### Week 1 — KPI Specification & Computation [`W1_kpi.ipynb`]

- Loaded and validated `claim_data.csv` (1,000 records, 15 columns)
- Formally defined all 5 KPIs with business logic and column mappings
- Computed KPI values using Pandas and printed a structured summary
- Identified and documented two upstream dependencies blocking full KPI coverage

**Output:** KPI summary printed to console with BLOCKED annotations where data is unavailable.

---

### Week 2 — Static Dashboard Prototype [`W2_Dashboard.ipynb` → `DS03_W2_Dashboard_Prototype.html`]

Built a fully static, NHS-branded interactive dashboard using Plotly and exported as a self-contained HTML file. Includes:

- **KPI Indicator Cards** — 5-panel row, colour-coded to NHS palette, with inline warnings on blocked/proxy metrics
- **Monthly Trend Lines** — approval rate, fraud flag rate, auto-decision rate, and £ saved across May–September 2024
- **Claim Breakdown Charts** — by insurance type, claim status, and reason code frequency
- **Auto-Decision Donut Chart** — 11.6% auto-decided vs 88.4% human review, with proxy warning

**Output:** `DS03_W2_Dashboard_Prototype.html` — fully self-contained, browser-ready, no external dependencies.

---

### Week 3 — Live Dashboard with SQLAlchemy + Auto-Refresh [`app.py`]

Converted the static prototype into a live Dash application connected to a database backend with real-time refresh.

**Key changes from W2:**
- Replaced static `pd.read_csv()` with SQLAlchemy database connection
- Added `dcc.Interval` component for 30-second auto-refresh — dashboard re-queries DB on every tick
- Built `USE_DATABASE` toggle — switch between CSV and PostgreSQL with one line
- All chart logic moved into a Dash callback so data stays live

**How to run:**
```bash
pip install -r requirements.txt
python app.py
```
Open browser → `http://localhost:8050`

**Switch to PostgreSQL (when FS-06 provides credentials):**

In `app.py`, change:
```python
USE_DATABASE = False   # current — runs on CSV/SQLite
```
to:
```python
USE_DATABASE = True    # connects to PostgreSQL
```
Then update the connection string:
```python
engine = create_engine("postgresql://user:password@host:5432/dbname")
```

**Output:** Live Dash dashboard at `localhost:8050` — auto-refreshes every 30 seconds.

**W3 Deliverable Status:**
- [x] SQLAlchemy DB connection layer
- [x] 30-second auto-refresh via `dcc.Interval`
- [x] CSV / PostgreSQL toggle via single flag
- [ ] PostgreSQL live connection — pending FS-06 credentials

---

## Tech Stack

| Tool | Purpose |
|---|---|
| Python 3.13 | Core language |
| Pandas | Data loading, aggregation, KPI computation |
| Plotly 6.7.0 | All chart rendering |
| Dash 2.17.0 | Live web dashboard framework (W3+) |
| SQLAlchemy 2.0 | Database abstraction layer (W3+) |
| SQLite | Local database (W3 — PostgreSQL-ready) |
| Jupyter Notebook | W1 & W2 development environment |

---

## Dependencies & Blockers

| KPI | Blocker | Blocked By | Expected In |
|---|---|---|---|
| Avg Days to Decision | `decision_date` column missing from DB schema | FS-06 | W3 schema update |
| Fraud Flag Rate (proxy) | `fraud_score` field not yet in `/predict` API output | ML-03 | W3 |
| Auto-Decision Rate (proxy) | `auto_decision_flag` not yet produced by rules engine | ML-04 | W4 |

---

## Upcoming Weeks

| Week | Planned Deliverable |
|---|---|
| **W4** | Add filters — by trust, date range, claim type. Add drill-down on individual claims. Integration testing with Full Stack squad (FS-05) |
| **W5** | Demo preparation — finalise 3 key talking points, ensure all charts load within 2 seconds for client demo |

---

## Design Notes

Dashboard follows **NHS Identity Guidelines**:

| Token | Value | Usage |
|---|---|---|
| NHS Blue | `#003087` | Primary colour, headings |
| NHS Green | `#009639` | Approval / success states |
| NHS Red | `#DA291C` | Fraud / denial alerts |
| Amber | `#ED8B00` | Warnings, blocked/proxy labels |
| Font | Arial | NHS standard |

---

*AI Insurance Claim Automation | UK NHS & Private Clinic Demo | Confidential — Internal Use Only*