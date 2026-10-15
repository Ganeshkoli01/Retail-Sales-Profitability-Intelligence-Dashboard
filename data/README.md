# Retail Sales & Profitability Dataset Documentation

## 1. Overview & Provenance
This project utilizes the canonical **Retail Superstore Sales & Profitability Dataset**, widely recognized as the industry benchmark for retail business intelligence, operations analytics, and financial performance modeling.

- **Dataset Name:** Tableau Sample Superstore Dataset
- **Acquisition Date:** 2026-10-15
- **Source Repository:** [sumit0072/Superstore-Data-Analysis](https://github.com/sumit0072/Superstore-Data-Analysis)
- **Direct Raw URL:** `https://raw.githubusercontent.com/sumit0072/Superstore-Data-Analysis/main/Sample%20-%20Superstore.csv`
- **File Format:** CSV (`windows-1252` encoding)
- **Raw File Size:** 2,287,806 bytes (2.18 MB)
- **SHA-256 Checksum:** `58fb59c63089e564d6c41b80d0d829497e7cf20689b0d6682701d51ab4ce3e58`
- **License / Terms of Use:** Public Domain / Tableau Educational Dataset provided for analytics evaluation, portfolio benchmarking, and statistical modeling.

## 2. Dataset Structure

| Column Name | Raw Type | Standardized Name | Target Type | Description & Business Meaning | Quality Validation Rules |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `Row ID` | int64 | `row_id` | INTEGER PRIMARY KEY | Unique sequential row identifier | Unique, non-null, > 0 |
| `Order ID` | object | `order_id` | VARCHAR(25) | Unique alphanumeric order transaction ID | Non-null, formatted `[A-Z]{2}-\d{4}-\d{6}` |
| `Order Date` | object | `order_date` | DATE | Date the order was placed by the customer | Valid date between 2014-01-01 and 2017-12-31 |
| `Ship Date` | object | `ship_date` | DATE | Date the order was dispatched | Valid date, must be >= `order_date` |
| `Ship Mode` | object | `ship_mode` | VARCHAR(25) | Fulfillment transit class (Standard, Second, First, Same Day) | In allowed set of shipping classes |
| `Customer ID` | object | `customer_id` | VARCHAR(20) | Unique customer alphanumeric identifier | Non-null, formatted `[A-Z]{2}-\d{5}` |
| `Customer Name` | object | `customer_name` | VARCHAR(100) | Customer's full name | Non-null string |
| `Segment` | object | `segment` | VARCHAR(25) | Market segment (`Consumer`, `Corporate`, `Home Office`) | Allowed categorical values only |
| `Country` | object | `country` | VARCHAR(50) | Country of purchase (`United States`) | Non-null |
| `City` | object | `city` | VARCHAR(50) | Delivery city name | Non-null string |
| `State` | object | `state` | VARCHAR(50) | US state | Valid US state name |
| `Postal Code` | int64 | `postal_code` | VARCHAR(10) | 5-digit postal zip code (zero-padded string) | Padded to 5 digits |
| `Region` | object | `region` | VARCHAR(20) | Geographic macro-region (`East`, `West`, `Central`, `South`) | Allowed categorical values |
| `Product ID` | object | `product_id` | VARCHAR(25) | Unique SKU / product identifier | Non-null alphanumeric string |
| `Category` | object | `category` | VARCHAR(30) | High-level merchandise category (`Furniture`, `Office Supplies`, `Technology`) | Allowed categorical values |
| `Sub-Category` | object | `sub_category` | VARCHAR(30) | Detailed merchandise grouping (e.g., `Chairs`, `Binders`, `Phones`) | Non-null string |
| `Product Name` | object | `product_name` | VARCHAR(255) | Full descriptive commercial name of the item | Non-null string |
| `Sales` | float64 | `sales` | NUMERIC(10,2) | Gross transaction revenue after discount | Float > 0.00 |
| `Quantity` | int64 | `quantity` | INTEGER | Units purchased in transaction | Integer >= 1 |
| `Discount` | float64 | `discount` | NUMERIC(4,2) | Discount percentage applied as a decimal (0.00 to 0.80) | Float between 0.00 and 1.00 |
| `Profit` | float64 | `profit` | NUMERIC(10,2) | Net contribution profit (can be negative for loss-making items) | Float, validated against margin |

## 3. Engineered Features (Processed Dataset)

| Field Name | Type | Formula / Origin | Business Purpose |
| :--- | :--- | :--- | :--- |
| `order_year` | INTEGER | `order_date.year` | Annual aggregation & YoY analysis |
| `order_month` | INTEGER | `order_date.month` | Monthly seasonality analysis (1-12) |
| `order_quarter` | VARCHAR(5) | `Q1`, `Q2`, `Q3`, `Q4` | Quarterly financial reporting |
| `order_year_month`| VARCHAR(7) | `YYYY-MM` | Continuous time-series indexing |
| `shipping_duration_days` | INTEGER | `(ship_date - order_date).days` | Fulfillment latency and logistics performance |
| `profit_margin` | NUMERIC(6,4) | `profit / sales` | Profitability efficiency ratio per line item |
| `discount_tier` | VARCHAR(25) | `Case when discount = 0 then 'None' ...` | Discount sensitivity segmentation |
| `unit_price` | NUMERIC(10,2) | `sales / quantity` | Realized price per unit |
| `unit_cost` | NUMERIC(10,2) | `(sales - profit) / quantity` | Implied cost of goods sold per unit |
| `is_profitable` | INTEGER (0/1) | `1 if profit > 0 else 0` | Loss-making transaction flag |

## 4. Quality Rules & Handling Policy
1. **Rejection Policy:** Rather than silently discarding questionable records, any record failing core constraints (e.g., `sales <= 0`, `quantity <= 0`, `ship_date < order_date`, invalid `discount` range) is routed to `data/processed/retail_sales_rejected.csv` with a detailed `rejection_reason`.
2. **Postal Code Formatting:** Postal codes stored as integers are converted to strings and zero-padded to 5 digits (e.g., `05408` instead of `5408`) to preserve valid US zip code standards.
3. **Encoding & Text Cleanliness:** Trim whitespace from text fields, normalize string casing for categories, and ensure UTF-8 compatibility throughout pipeline storage.
