# Retail Sales & Profitability Analytics: Enterprise Decision Support System

[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![Database](https://img.shields.io/badge/SQL-SQLite%203-003B57.svg)](https://www.sqlite.org/)
[![Tests](https://img.shields.io/badge/pytest-17%20Passed%20(100%25)-brightgreen.svg)](https://pytest.org/)
[![License](https://img.shields.io/badge/License-Public%20Domain-lightgrey.svg)](data/README.md)
[![Status](https://img.shields.io/badge/Status-Portfolio%20Ready-success.svg)](#)

A complete, production-grade, reproducible data engineering and analytics solution built to diagnose enterprise retail profitability, evaluate discount elasticity, identify product value destroyers, and provide evidence-based commercial recommendations.

Developed as a **Final-Year B.Tech Computer Science & Engineering Placement Portfolio Project** demonstrating skills in Data Analytics, Analytics Engineering, Python development, Relational SQL, Financial Modeling in Excel, and Automated Testing.

---

## 📑 Table of Contents
1. [Project Overview & Business Problem](#1-project-overview--business-problem)
2. [Key Questions Answered](#2-key-questions-answered)
3. [Technology Stack](#3-technology-stack)
4. [Architecture & Pipeline Flow](#4-architecture--pipeline-flow)
5. [Dataset Provenance & Quality Assurance](#5-dataset-provenance--quality-assurance)
6. [Key Empirical Findings](#6-key-empirical-findings)
7. [Visualizations & Screenshots](#7-visualizations--screenshots)
8. [SQL Analytics Library](#8-sql-analytics-library)
9. [Excel Deliverable Overview](#9-excel-deliverable-overview)
10. [Installation & Reproduction Guide](#10-installation--reproduction-guide)
11. [Automated Testing & Reconciliation](#11-automated-testing--reconciliation)
12. [Interactive Streamlit Web Application](#12-interactive-streamlit-web-application)
13. [Limitations & Future Enhancements](#13-limitations--future-enhancements)
14. [What I Learned](#14-what-i-learned)

---

## 1. Project Overview & Business Problem

### The Business Dilemma
In modern multi-channel retail, executive leadership often celebrates top-line gross revenue expansion while overlooking the erosion of net contribution margins. Between 2014 and 2017, the enterprise achieved **$2,297,200.86 in gross revenue** across **5,009 orders**, yet net profit lagged at **$286,397.02 (12.47% margin)**. 

Crucially, **18.7% of all transaction line items operated at a net loss**. Without granular visibility into product-level unit economics, discount sensitivity, and regional cost dynamics, management risked continuing to scale unprofitable volume.

### The Objective
Build a modular, verified data analytics solution that:
- Audits and cleans 9,994 multi-year retail transactions with zero data loss via an automated quarantine pattern.
- Ingests data into an indexed SQLite relational database with pre-aggregated analytical views.
- Delivers a curated library of 21 business SQL queries with advanced window functions.
- Generates a polished, 10-sheet corporate Excel workbook (`excel/retail_sales_analytics.xlsx`) adhering to FP&A standards.
- Reconciles Python vectorized calculations and SQL queries with 100% precision down to the cent.
- Formulates evidence-based commercial strategies to eliminate a $21.2K catalog deficit and protect gross margins.

---

## 2. Key Questions Answered

1. **Revenue & Profit Dynamics:** How do sales, net profit, order volume, and Average Order Value (AOV) evolve across months and fiscal quarters?
2. **Category & Subcategory Breakdown:** Which product categories generate strong cash flow, and which suffer chronic negative profitability?
3. **Discount Elasticity & Value Destruction:** What is the exact mathematical relationship between promotional discount depth and transaction margins?
4. **Product "Sales Traps":** Which high-sales items appear successful on the surface but destroy enterprise profit?
5. **Geographic Asymmetry:** Why do California and New York produce massive profits (+$150K combined) while Texas and Illinois bleed red ink (-$38K combined)?
6. **Customer RFM Segmentation:** How are customer lifetime value (CLV) and repeat purchase patterns distributed across market segments?

---

## 3. Technology Stack

- **Core Analytics & Data Engineering:** Python 3.12, pandas 2.2+, NumPy 1.26+
- **Relational Database Engine:** SQLite 3.x (Zero-config, embedded, ACID-compliant)
- **Financial Modeling & Excel Reporting:** openpyxl 3.1+, xlsxwriter 3.2+
- **Data Visualization:** Matplotlib 3.10+, Seaborn 0.13+, Plotly 6.3+
- **Interactive Web Portal:** Streamlit 1.51+
- **Quality Assurance & Automated Testing:** pytest 8.3+

---

## 4. Architecture & Pipeline Flow

```mermaid
flowchart LR
    A["Raw Data Ingestion<br/>(sample_superstore.csv)"] --> B["Data Cleaning & Validation<br/>(src/data_cleaning.py)"]
    B -->|Cleaned (100%)| C["Feature Engineering<br/>(src/feature_engineering.py)"]
    B -->|Quarantined| Q["Quarantined Audit CSV<br/>(retail_sales_rejected.csv)"]
    C --> D["SQLite Database<br/>(database/retail_analytics.db)"]
    D --> E["SQL Query Library<br/>(21 Business Queries)"]
    C --> F["Vectorized Python Metrics<br/>(src/metrics.py)"]
    E & F --> G["Reconciliation Engine<br/>(Dollar-for-Dollar Audit)"]
    G --> H["10-Sheet Excel Workbook<br/>(excel/*.xlsx)"]
    G --> I["High-Res Visualizations<br/>(screenshots/*.png)"]
    G --> J["Streamlit Interactive Web App<br/>(app/streamlit_app.py)"]
```

---

## 5. Dataset Provenance & Quality Assurance

- **Dataset Name:** Tableau Sample Superstore Benchmark Dataset
- **Verified Record Count:** 9,994 transaction line items | 21 raw columns
- **Date Range:** January 3, 2014 – December 30, 2017 (4 continuous operating years)
- **SHA-256 Checksum:** `58fb59c63089e564d6c41b80d0d829497e7cf20689b0d6682701d51ab4ce3e58`
- **Source Repository:** [sumit0072/Superstore-Data-Analysis](https://github.com/sumit0072/Superstore-Data-Analysis)
- **License:** Public Domain / Tableau Sample Data provided for educational and benchmarking purposes.
- **Detailed Data Dictionary:** Documented in [data/README.md](data/README.md) and inside the generated Excel workbook.

### Cleaning & Validation Policies
1. **Schema Standardization:** All raw column headers converted from mixed casing to standard SQL `snake_case`.
2. **Quarantine Pattern:** Records violating business rules are routed to `data/processed/retail_sales_rejected.csv` with a descriptive error string rather than being silently dropped.
3. **Data Quality Audit:** Passed with 100% clean record validation (0 nulls in mandatory fields, 0 negative shipping paradoxes, 100% positive sales and valid quantities).

---

## 6. Key Empirical Findings

All findings are computed directly from the verified dataset:

1. **The 20% Discount Cliff:**
   - **0% Discount:** Generates **$1.08M sales** and **$320.98K profit** (**29.79% margin**; 0% loss transactions).
   - **1%–20% Discount:** Generates **$667.6K sales** and **$107.5K profit** (**13.5%–16.5% margin**).
   - **> 20% Discount:** Catastrophic margin collapse. Discounts between 21% and 40% yield **-$13.8K in losses** (-14.3% margin; 83.1% loss rate), while discounts >40% yield **-$84.3K in losses** (-83.4% margin; 84.1% loss rate).
2. **Subcategory Value Destroyers:**
   - **Tables:** Generated **-$17,725.48 net loss** on $207.0K revenue (-8.56% margin).
   - **Bookcases:** Generated **-$3,472.55 net loss** on $114.9K revenue (-3.02% margin).
3. **Department Outperformance:**
   - **Technology:** Delivered **$145.5K profit** (**17.39% margin**), led by Copiers ($55.6K profit, 37.2% margin) and Phones ($44.5K profit).
   - **Office Supplies:** Delivered **$122.5K profit** (**17.03% margin**), led by Paper ($34.1K profit, 43.4% margin).
4. **Geographic Divergence:**
   - **West & East:** Drive **69.8% of total profit** ($199.9K combined).
   - **Central:** Lags at **7.92% margin**, penalized by **Texas (-$25.7K deficit)** and **Illinois (-$12.6K deficit)** due to excessive local discounting (averaging 37%–39%).
5. **Customer Basket Health:**
   - While the **Consumer** segment drives volume ($1.16M sales), **Home Office** generates the **highest basket size ($474.75 AOV)** and the **highest margin (14.03%)**.

---

## 7. Visualizations & Screenshots

High-resolution charts generated automatically by `src/visualizations.py` and saved to `screenshots/`:

| Visualization | Description | File Path |
| :--- | :--- | :--- |
| **Monthly Commercial Trajectory** | 48-month trend tracking sales, net profit, and margin % | [screenshots/monthly_sales_profit_trend.png](screenshots/monthly_sales_profit_trend.png) |
| **Subcategory Profit Breakdown** | Horizontal bar chart highlighting positive stars vs loss centers | [screenshots/category_subcategory_performance.png](screenshots/category_subcategory_performance.png) |
| **Discount Margin Erosion** | Dual-axis graph proving the 20% discount tipping point | [screenshots/discount_profit_margin_erosion.png](screenshots/discount_profit_margin_erosion.png) |
| **Regional Sales vs Profit** | Macro-region financial comparison (West, East, Central, South) | [screenshots/regional_profitability_summary.png](screenshots/regional_profitability_summary.png) |

---

## 8. SQL Analytics Library

The project includes an authoritative library of **21 curated business queries** in `sql/business_analysis.sql` and `database/analysis_queries.sql`, covering:
- Executive baseline scorecard
- Sequential Month-over-Month (MoM) growth using `LAG()` window functions
- Intra-category profitability ranking via `DENSE_RANK()`
- Product catalog "Sales Traps" isolation
- Deep promotional sensitivity analysis
- State-level rankings using `UNION ALL` with CTEs
- Customer RFM (Recency, Frequency, Monetary) profile modeling
- Cumulative running totals using `SUM() OVER (ORDER BY order_year_month)`

### Example: Identifying Product Sales Traps
```sql
SELECT
    product_name,
    category,
    sub_category,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS net_loss,
    ROUND((SUM(profit) / SUM(sales)) * 100.0, 2) AS profit_margin_pct,
    ROUND(AVG(discount) * 100.0, 1) AS avg_discount_pct
FROM retail_orders
GROUP BY product_id, product_name, category, sub_category
HAVING SUM(sales) >= 2500.0 AND SUM(profit) < 0
ORDER BY net_loss ASC;
```

---

## 9. Excel Deliverable Overview

The generated workbook at `excel/retail_sales_analytics.xlsx` contains **10 meticulously formatted worksheets**:

1. **Executive Dashboard:** Corporate Navy banner, KPI cards ($2.30M sales, $286.4K profit, 12.47% margin, 5,009 orders), annual progression table, and executive takeaways.
2. **Monthly Trends:** 48-month sequential financial summary with MoM growth rates.
3. **Category Analysis:** 17 subcategories benchmarked with conditional formatting.
4. **Product Analysis:** Top 15 Profit Stars vs Catalog Sales Traps.
5. **Regional Analysis:** Macro-regions and Top 5 / Bottom 5 state rankings.
6. **Discount & Profitability:** Empirical discount tier sensitivity matrix.
7. **Customer Analysis:** Segment performance and Top 15 accounts by lifetime profit.
8. **Cleaned Data:** 1,000-row standardized data extract with Excel auto-filters.
9. **Data Dictionary:** Schema specifications, data types, business semantics, and constraints.
10. **Methodology & KPI Definitions:** Exact formulas, denominator rules, and edge case specifications.

---

## 10. Installation & Reproduction Guide

### Prerequisites
- Python 3.10+ (Tested on Python 3.12)
- Git

### Step-by-Step Setup
```bash
# 1. Clone repository
git clone https://github.com/your-username/retail-sales-analytics.git
cd retail-sales-analytics

# 2. Create and activate a virtual environment
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Execute the complete end-to-end pipeline
python -m src.main
```

Upon execution, the pipeline automatically:
- Loads and validates the raw CSV.
- Quarantines any invalid rows into `data/processed/retail_sales_rejected.csv`.
- Enriches the dataset with 10 derived analytical features.
- Initializes `database/retail_analytics.db` with indexes and views.
- Executes Python-SQL reconciliation.
- Exports all high-resolution charts into `screenshots/`.
- Generates the 10-sheet workbook at `excel/retail_sales_analytics.xlsx`.

---

## 11. Automated Testing & Reconciliation

Run the test suite using `pytest`:
```bash
pytest -v
```

### Verified Test Results
```text
============================= test session starts =============================
platform win32 -- Python 3.12.6, pytest-8.3.4
collected 17 items

tests/test_cleaning.py::test_clean_retail_data_valid PASSED              [  5%]
tests/test_cleaning.py::test_quarantine_negative_sales PASSED            [ 11%]
tests/test_cleaning.py::test_quarantine_invalid_discount PASSED          [ 17%]
tests/test_cleaning.py::test_quarantine_ship_date_preceding_order_date PASSED [ 23%]
tests/test_cleaning.py::test_feature_engineering_derivatives PASSED      [ 29%]
tests/test_excel.py::test_excel_file_exists PASSED                       [ 35%]
tests/test_excel.py::test_excel_ten_sheets_exist PASSED                  [ 41%]
tests/test_excel.py::test_executive_dashboard_kpis_populated PASSED      [ 47%]
tests/test_excel.py::test_cleaned_data_sheet_structure PASSED            [ 52%]
tests/test_metrics.py::test_kpi_metrics_exact_values PASSED              [ 58%]
tests/test_metrics.py::test_empty_dataframe_edge_cases PASSED            [ 64%]
tests/test_metrics.py::test_zero_sales_margin_safe_division PASSED       [ 70%]
tests/test_metrics.py::test_rfm_metrics_structure PASSED                 [ 76%]
tests/test_reconciliation.py::test_python_and_sql_reconciliation PASSED  [ 82%]
tests/test_sql.py::test_database_exists_and_table_populated PASSED       [ 88%]
tests/test_sql.py::test_database_views_exist PASSED                      [ 94%]
tests/test_sql.py::test_all_21_business_analysis_queries PASSED          [100%]

============================= 17 passed in 2.95s ==============================
```

### Python-SQL Reconciliation Summary

| Metric | Python Value | SQL Database Value | Delta | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Total Revenue** | $2,297,200.86 | $2,297,200.86 | $0.00 | **MATCH (PASS)** |
| **Net Profit** | $286,397.02 | $286,397.02 | $0.00 | **MATCH (PASS)** |
| **Total Quantity** | 37,873 units | 37,873 units | 0 units | **MATCH (PASS)** |
| **Unique Orders** | 5,009 orders | 5,009 orders | 0 orders | **MATCH (PASS)** |
| **Unique Customers** | 793 customers | 793 customers | 0 customers | **MATCH (PASS)** |

---

## 12. Interactive Streamlit Web Application

Launch the interactive executive decision-support portal:
```bash
streamlit run app/streamlit_app.py
```

### Key Interactive Features:
- **Date & Geography Slicers:** Dynamic sidebar date range picker, region multi-selector, and department filters.
- **Visual Analytics Tabs:** Revenue trajectories, subcategory horizontal bars, and discount sensitivity curves.
- **SQL Query Sandbox:** Interactive editor allowing users to run custom queries directly against `database/retail_analytics.db`.

---

## 13. Limitations & Future Enhancements

### Known Limitations
1. **Operating Expenses (OpEx) Excluded:** Profit measures gross contribution after merchandise costs and discounts, but does not capture fixed warehouse overhead or corporate marketing costs.
2. **Absence of Return Logs:** Return/refund statuses are not tracked, meaning return rates cannot be isolated.

### Future Improvements
1. **Machine Learning Forecaster:** Implement ARIMA / Prophet time-series models to forecast Q4 monthly demand.
2. **Dynamic Price Elasticity Engine:** Train an econometric regression model to estimate product-level price elasticity of demand ($\epsilon$).
3. **Cloud Data Warehouse Migration:** Transition SQLite pipeline to dbt + Snowflake or BigQuery.

---

## 14. What I Learned

Building this placement portfolio project strengthened my technical and analytical abilities:
- **Defensive Data Engineering:** Implemented quarantine patterns rather than silently discarding bad data.
- **Advanced SQL Patterns:** Mastered multi-table CTEs, partitioned window functions (`DENSE_RANK`), and sequential lag operators (`LAG`).
- **Precision Reconciliation:** Learned how slight differences in rounding or denominator rules can derail executive trust, and how automated reconciliation tests resolve discrepancies.
- **Translating Data to Strategy:** Developed the ability to communicate findings through an executive lens, linking data evidence to business action.

---

## 📬 Placement & Interview Preparation

For an in-depth interview walkthrough, 20+ technical Q&A, and resume bullet points, see [docs/interview_guide.md](docs/interview_guide.md).
