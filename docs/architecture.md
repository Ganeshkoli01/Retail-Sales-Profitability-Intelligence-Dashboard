# System Architecture & Technical Design

**Project:** Retail Sales & Profitability Analytics  
**Architecture Style:** Modular, Reproducible Batch Analytics & Business Intelligence Pipeline  
**Core Technologies:** Python 3, pandas, NumPy, SQLite 3, openpyxl, Matplotlib, Streamlit, pytest  

---

## 1. End-to-End Pipeline Architecture

The following Mermaid diagram illustrates the end-to-end data flow from raw data ingestion through validation, feature engineering, relational loading, automated testing, Excel reporting, and web visualization:

```mermaid
flowchart TD
    subgraph Data_Ingestion ["1. Ingestion Layer"]
        RAW["data/raw/sample_superstore.csv<br/>(9,994 records, SHA-256 verified)"] --> LOAD["src/data_ingestion.py<br/>(Schema validation, encoding resolution)"]
    end

    subgraph Data_Engineering ["2. Data Engineering & Validation"]
        LOAD --> CLEAN["src/data_cleaning.py<br/>(Boundary checks, ISO date parsing, 0-padding)"]
        CLEAN -->|Valid Records (100%)| FEAT["src/feature_engineering.py<br/>(Vectorized features: margin, AOV, discount tier)"]
        CLEAN -->|Quarantined Records| REJECT["data/processed/retail_sales_rejected.csv<br/>(Preserves lineage with rejection_reason)"]
        FEAT --> PROCESSED["data/processed/retail_sales_cleaned.csv"]
    end

    subgraph Storage ["3. Storage & Relational Database Layer"]
        FEAT --> DBLOAD["src/database.py<br/>(Idempotent truncate & append)"]
        DBLOAD --> SQLITE[("database/retail_analytics.db<br/>(SQLite 3 Engine)")]
        SQLITE --> VIEWS["Analytical Views<br/>v_monthly_summary<br/>v_category_performance<br/>v_customer_rfm"]
    end

    subgraph Analytics ["4. Analytics & Reconciliation Engine"]
        SQLITE --> SQL_LIB["sql/business_analysis.sql<br/>(21 Curated Business Queries)"]
        FEAT --> PY_METRICS["src/metrics.py<br/>(Vectorized NumPy & pandas metrics)"]
        SQL_LIB & PY_METRICS --> RECON["src/analysis.py<br/>(Strict dollar-for-dollar reconciliation)"]
    end

    subgraph Deliverables ["5. Business Deliverables & Interfaces"]
        RECON --> EXCEL["excel/retail_sales_analytics.xlsx<br/>(10-Sheet Executive FP&A Workbook)"]
        RECON --> CHARTS["screenshots/*.png<br/>(High-res Matplotlib/Seaborn visuals)"]
        RECON --> REPORTS["reports/*.md<br/>(Executive summary & business findings)"]
        SQLITE & PROCESSED --> APP["app/streamlit_app.py<br/>(Interactive Web Dashboard Demo)"]
    end

    subgraph QA ["6. Quality Assurance & Testing"]
        TESTS["tests/test_*.py<br/>(17 automated pytest test cases)"] -.->|Verifies| CLEAN
        TESTS -.->|Verifies| PY_METRICS
        TESTS -.->|Verifies| SQLITE
        TESTS -.->|Verifies| EXCEL
        TESTS -.->|Verifies| RECON
    end
```

---

## 2. Directory Structure & Component Responsibilities

```text
CUSTOMER RETENTION & CHURN ANALYTICS/
│
├── README.md                      # Comprehensive project presentation & documentation
├── requirements.txt               # Pinned Python package dependencies
├── .gitignore                     # Git ignore rules for environments, caches, OS files
├── .env.example                   # Environment configuration template
│
├── data/
│   ├── raw/
│   │   ├── sample_superstore.csv  # Original unmodified source CSV
│   │   └── provenance.json        # Checksum, source URL, license, and access metadata
│   ├── processed/
│   │   ├── retail_sales_cleaned.csv   # Cleaned & feature-engineered dataset
│   │   └── retail_sales_rejected.csv  # Quarantined records with error audit reasons
│   └── README.md                  # Dataset documentation & data dictionary
│
├── database/
│   ├── schema.sql                 # DDL schema definition
│   ├── analysis_queries.sql       # Query library for database operations
│   └── retail_analytics.db        # Portable SQLite embedded database
│
├── sql/
│   ├── schema.sql                 # Authoritative table & view DDL script
│   └── business_analysis.sql      # Curated library of 21 business-analysis SQL queries
│
├── src/
│   ├── __init__.py                # Package initialization
│   ├── config.py                  # Central paths, schema definitions, and constants
│   ├── data_ingestion.py          # Ingestion module with schema & encoding checks
│   ├── data_cleaning.py           # Data quality rules & quarantine logic
│   ├── feature_engineering.py     # Vectorized derived dimensions & unit economics
│   ├── database.py                # SQLite connection, loading, and query manager
│   ├── metrics.py                 # Vectorized KPI and growth rate calculation engine
│   ├── analysis.py                # Analytical engine & Python-SQL reconciliation auditor
│   ├── visualizations.py          # High-resolution Matplotlib/Seaborn charting engine
│   ├── export_excel.py            # Professional 10-sheet openpyxl workbook generator
│   └── main.py                    # Master orchestrator script running end-to-end pipeline
│
├── notebooks/
│   └── exploratory_analysis.ipynb # Interactive EDA narrative notebook with code & visuals
│
├── excel/
│   └── retail_sales_analytics.xlsx # Polished 10-sheet corporate Excel deliverable
│
├── reports/
│   ├── executive_summary.md       # C-level summary of findings & strategic actions
│   ├── data_quality_report.md     # Ingestion audit, schema validation & distributions
│   └── business_findings.md       # In-depth quantitative findings across all dimensions
│
├── tests/
│   ├── __init__.py                # Test package initialization
│   ├── conftest.py                # Pytest fixtures and synthetic mini-datasets
│   ├── test_cleaning.py           # Unit tests for data cleaning & quarantine rules
│   ├── test_metrics.py            # Unit tests for financial formulas & edge cases
│   ├── test_sql.py                # Integration tests for database schema, views & 21 queries
│   ├── test_excel.py              # Integration tests for workbook structure & formatting
│   └── test_reconciliation.py     # Reconciliation tests between Python and SQL
│
├── screenshots/
│   ├── monthly_sales_profit_trend.png
│   ├── category_subcategory_performance.png
│   ├── discount_profit_margin_erosion.png
│   └── regional_profitability_summary.png
│
├── docs/
│   ├── architecture.md            # System architecture, pipeline design & decisions
│   ├── metric_definitions.md      # Mathematical formulas & edge case specifications
│   └── interview_guide.md         # Comprehensive placement interview walkthrough & Q&A
│
└── app/
    └── streamlit_app.py           # Interactive Streamlit dashboard with SQL sandbox
```

---

## 3. Key Design Decisions & Technical Trade-offs

### 1. SQLite for the Analytical Database
- **Rationale:** SQLite requires zero server infrastructure, eliminates Docker/host setup dependencies for recruiters reviewing the repository, and provides native ACID compliance with full support for modern SQL features (Window functions like `LAG()`, `DENSE_RANK()`, CTEs, and indexed views).
- **Alternative Considered:** PostgreSQL / MySQL. While standard in enterprise multi-user environments, requiring a live PostgreSQL instance creates setup friction for portfolio evaluation without adding analytical value for a 10K-row dataset.

### 2. Explicit Quarantine Policy over Silent Dropping
- **Rationale:** In production data engineering, silently dropping records with `.dropna()` or `df[df['sales'] > 0]` hides upstream data corruption. Our pipeline routes non-compliant rows to `data/processed/retail_sales_rejected.csv` with a descriptive `rejection_reason` string.

### 3. OpenPyXL for Native Excel Financial Modeling
- **Rationale:** Rather than outputting plain CSV files or unformatted dumps, `src/export_excel.py` builds a 10-sheet workbook formatted to Wall Street / Corporate FP&A standards: custom palette (`#1B365D` Navy, Slate headers), explicit currency/percent number formats (`$#,##0.00`, `0.0%`), auto-fitted columns, freeze panes, and visible gridlines.

### 4. Vectorized pandas & NumPy over Iteration
- **Rationale:** All derived metrics (margins, unit costs, discount buckets) use vectorized array operations (`np.where`, `pd.cut`), executing in milliseconds with zero row-by-row iteration loops (`iterrows`).
