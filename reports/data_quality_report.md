# Data Quality, Ingestion & Audit Report

**Project:** Retail Sales & Profitability Analytics  
**Pipeline Run Timestamp:** 2026-10-15  
**Data Engineer:** Senior Analytics Engineer & QA Specialist  
**Database File:** `database/retail_analytics.db`  
**Processed Dataset:** `data/processed/retail_sales_cleaned.csv`  

---

## 1. Executive Data Quality Scorecard

| Quality Dimension | Metric Evaluated | Target Standard | Measured Value | Audit Status |
| :--- | :--- | :--- | :--- | :--- |
| **Completeness** | Mandatory field null rate | 0.00% | 0.00% (0 missing values) | **PASS** |
| **Uniqueness** | Exact duplicate transaction rows | 0 rows | 0 rows detected | **PASS** |
| **Validity** | Sales > 0.00 & Quantity >= 1 | 100.00% | 100.00% compliant | **PASS** |
| **Chronology** | Fulfillment latency (`ship_date >= order_date`) | 100.00% | 100.00% (0 paradoxes) | **PASS** |
| **Boundedness** | Discount between 0.00 and 1.00 | 100.00% | 100.00% (range 0.00–0.80) | **PASS** |
| **Referential Integrity**| Order, Customer & Product IDs populated | 100.00% | 100.00% compliant | **PASS** |
| **Overall Health** | Clean Record Pass Rate | > 99.00% | **100.00% (9,994 / 9,994)** | **OPTIMAL** |

---

## 2. Ingestion & Transformation Audit

### Ingestion Metrics
- **Raw File Source:** `data/raw/sample_superstore.csv` (SHA-256: `58fb59c63089e564d6c41b80d0d829497e7cf20689b0d6682701d51ab4ce3e58`)
- **Raw Record Count:** 9,994 rows
- **Raw Attribute Count:** 21 columns
- **Encoding Verified:** `windows-1252` successfully decoded and normalized to standard UTF-8.

### Data Cleaning Actions Applied
1. **Schema Standardization:** Column headers converted from mixed whitespace casing (e.g., `Sub-Category`, `Order Date`, `Ship Mode`) to standard SQL `snake_case` (`sub_category`, `order_date`, `ship_mode`).
2. **Text Normalization:** Stripped leading and trailing whitespaces from customer names, city names, states, categories, and product names.
3. **Postal Code Sanitization:** Postal codes originally parsed as numeric floats/integers were zero-padded to 5-digit strings (`str.zfill(5)`) to preserve valid US zip code formatting (e.g., `05408` for Vermont zip codes rather than `5408`).
4. **Date Parsing:** Explicit ISO parsing of `order_date` and `ship_date` into `YYYY-MM-DD` strings for SQLite database compatibility.

---

## 3. Statistical Distribution & Boundary Profiling

| Numerical Field | Minimum | 25th Percentile | Median (50th) | 75th Percentile | Maximum | Mean | Std Dev |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Sales ($)** | $0.44 | $17.28 | $54.49 | $209.94 | $22,638.48 | $229.86 | $623.25 |
| **Profit ($)** | -$6,599.98 | $1.73 | $8.67 | $29.36 | $8,399.98 | $28.66 | $234.26 |
| **Quantity** | 1 unit | 2 units | 3 units | 5 units | 14 units | 3.79 units | 2.23 units |
| **Discount** | 0.00 (0%) | 0.00 (0%) | 0.20 (20%) | 0.20 (20%) | 0.80 (80%) | 0.156 (15.6%) | 0.206 |
| **Ship Latency** | 0 days | 3 days | 4 days | 5 days | 7 days | 3.96 days | 1.75 days |

### Analytical Observations
- **High Sales Skewness:** Mean sales ($229.86) is substantially higher than median sales ($54.49), driven by capital equipment purchases (e.g., copiers, servers, conference tables).
- **Extreme Profit Variance:** The distribution of profit ranges from -$6,599.98 to +$8,399.98. The severe negative tail indicates aggressive promotional discounting and high unit costs on specific commercial items.
- **Discount Clumping:** Discounts cluster around discrete promotional tiers: 0% (full price), 20% (standard promotional tier), and 70–80% (clearance/liquidation).

---

## 4. Rejection Policy & Quarantine Mechanics
Our pipeline implements a robust quarantine pattern in `src/data_cleaning.py`:
- Records that violate required schema boundaries are **not silently dropped**.
- Instead, each problematic record is flagged with a detailed, human-readable `rejection_reason` string (e.g., `"Sales must be positive numerical value; Ship date precedes order date;"`) and routed to `data/processed/retail_sales_rejected.csv`.
- This ensures data lineage is preserved and allows operational teams to audit rejected transactions directly.
- In the active Tableau Sample Superstore dataset, all 9,994 records successfully passed all sanity checks, yielding 0 quarantined records.

---

## 5. Automated Unit & Integration Testing Coverage
The pipeline is verified through an automated test suite executed via `pytest`:
- `tests/test_cleaning.py`: Schema validation, null handling, intentional negative sales rejection tests.
- `tests/test_metrics.py`: Vectorized math verification against known test fixtures and zero-division edge cases.
- `tests/test_sql.py`: Database connection, view existence, and execution of all 21 SQL business queries.
- `tests/test_excel.py`: Workbook existence, sheet count (10 sheets), cell values, and auto-filters.
- `tests/test_reconciliation.py`: Exact dollar-for-dollar reconciliation between Python and SQL.

**Test Results:** **17 passed, 0 failed in 2.95s (100% PASS rate)**.
