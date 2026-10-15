-- Authoritative schema is maintained at sql/schema.sql
-- This copy is provided for the database/ directory structure requirements.

DROP TABLE IF EXISTS retail_orders;

CREATE TABLE retail_orders (
    row_id                  INTEGER PRIMARY KEY,
    order_id                TEXT NOT NULL,
    order_date              TEXT NOT NULL,
    ship_date               TEXT NOT NULL,
    ship_mode               TEXT NOT NULL,
    customer_id             TEXT NOT NULL,
    customer_name           TEXT NOT NULL,
    segment                 TEXT NOT NULL,
    country                 TEXT NOT NULL,
    city                    TEXT NOT NULL,
    state                   TEXT NOT NULL,
    postal_code             TEXT NOT NULL,
    region                  TEXT NOT NULL,
    product_id              TEXT NOT NULL,
    category                TEXT NOT NULL,
    sub_category            TEXT NOT NULL,
    product_name            TEXT NOT NULL,
    sales                   REAL NOT NULL,
    quantity                INTEGER NOT NULL,
    discount                REAL NOT NULL,
    profit                  REAL NOT NULL,
    order_year              INTEGER NOT NULL,
    order_month             INTEGER NOT NULL,
    order_quarter           TEXT NOT NULL,
    order_year_month        TEXT NOT NULL,
    shipping_duration_days  INTEGER NOT NULL,
    profit_margin           REAL NOT NULL,
    unit_price              REAL NOT NULL,
    unit_cost               REAL NOT NULL,
    is_profitable           INTEGER NOT NULL,
    discount_tier           TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_orders_order_date ON retail_orders(order_date);
CREATE INDEX IF NOT EXISTS idx_orders_customer_id ON retail_orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_orders_category ON retail_orders(category);
CREATE INDEX IF NOT EXISTS idx_orders_sub_category ON retail_orders(sub_category);
CREATE INDEX IF NOT EXISTS idx_orders_region ON retail_orders(region);
CREATE INDEX IF NOT EXISTS idx_orders_state ON retail_orders(state);
CREATE INDEX IF NOT EXISTS idx_orders_year_month ON retail_orders(order_year_month);

DROP VIEW IF EXISTS v_monthly_summary;
CREATE VIEW v_monthly_summary AS
SELECT
    order_year_month,
    order_year,
    order_month,
    COUNT(DISTINCT order_id) AS total_orders,
    COUNT(*) AS total_line_items,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit,
    SUM(quantity) AS total_quantity,
    ROUND(AVG(discount), 4) AS avg_discount,
    ROUND(SUM(profit) / SUM(sales), 4) AS overall_profit_margin,
    ROUND(SUM(sales) / COUNT(DISTINCT order_id), 2) AS average_order_value
FROM retail_orders
GROUP BY order_year_month, order_year, order_month
ORDER BY order_year_month ASC;

DROP VIEW IF EXISTS v_category_performance;
CREATE VIEW v_category_performance AS
SELECT
    category,
    sub_category,
    COUNT(DISTINCT order_id) AS total_orders,
    SUM(quantity) AS total_units_sold,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit,
    ROUND(SUM(profit) / SUM(sales), 4) AS profit_margin,
    ROUND(AVG(discount), 4) AS avg_discount,
    SUM(CASE WHEN profit < 0 THEN 1 ELSE 0 END) AS loss_making_orders,
    ROUND(100.0 * SUM(CASE WHEN profit < 0 THEN 1 ELSE 0 END) / COUNT(*), 2) AS loss_order_rate_pct
FROM retail_orders
GROUP BY category, sub_category
ORDER BY category ASC, total_profit DESC;

DROP VIEW IF EXISTS v_customer_rfm;
CREATE VIEW v_customer_rfm AS
SELECT
    customer_id,
    customer_name,
    segment,
    COUNT(DISTINCT order_id) AS frequency,
    ROUND(SUM(sales), 2) AS monetary_sales,
    ROUND(SUM(profit), 2) AS monetary_profit,
    ROUND(SUM(profit) / SUM(sales), 4) AS customer_profit_margin,
    MAX(order_date) AS last_order_date,
    MIN(order_date) AS first_order_date
FROM retail_orders
GROUP BY customer_id, customer_name, segment;
