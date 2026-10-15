-- Authoritative queries are maintained at sql/business_analysis.sql
-- This copy is provided for the database/ directory structure requirements.

-- QUERY 1: Executive KPI Performance Overview
SELECT
    ROUND(SUM(sales), 2) AS total_revenue,
    ROUND(SUM(profit), 2) AS total_profit,
    ROUND((SUM(profit) / SUM(sales)) * 100.0, 2) AS overall_profit_margin_pct,
    SUM(quantity) AS total_units_sold,
    COUNT(DISTINCT order_id) AS total_orders,
    COUNT(DISTINCT customer_id) AS total_customers,
    ROUND(SUM(sales) / COUNT(DISTINCT order_id), 2) AS average_order_value
FROM retail_orders;

-- QUERY 2: Monthly Revenue, Profit, and Margin Trajectory
SELECT
    order_year_month,
    order_year,
    order_month,
    ROUND(SUM(sales), 2) AS total_revenue,
    ROUND(SUM(profit), 2) AS total_profit,
    ROUND((SUM(profit) / SUM(sales)) * 100.0, 2) AS profit_margin_pct,
    COUNT(DISTINCT order_id) AS total_orders,
    SUM(quantity) AS units_sold
FROM retail_orders
GROUP BY order_year_month, order_year, order_month
ORDER BY order_year_month ASC;

-- QUERY 3: Month-over-Month (MoM) Growth Rates Using Window Functions
WITH monthly_agg AS (
    SELECT
        order_year_month,
        ROUND(SUM(sales), 2) AS monthly_sales,
        ROUND(SUM(profit), 2) AS monthly_profit
    FROM retail_orders
    GROUP BY order_year_month
)
SELECT
    order_year_month,
    monthly_sales AS current_month_sales,
    LAG(monthly_sales) OVER (ORDER BY order_year_month) AS prior_month_sales,
    ROUND(
        ((monthly_sales - LAG(monthly_sales) OVER (ORDER BY order_year_month)) /
        LAG(monthly_sales) OVER (ORDER BY order_year_month)) * 100.0, 2
    ) AS mom_sales_growth_pct,
    monthly_profit AS current_month_profit,
    LAG(monthly_profit) OVER (ORDER BY order_year_month) AS prior_month_profit,
    ROUND(
        ((monthly_profit - LAG(monthly_profit) OVER (ORDER BY order_year_month)) /
        ABS(LAG(monthly_profit) OVER (ORDER BY order_year_month))) * 100.0, 2
    ) AS mom_profit_growth_pct
FROM monthly_agg
ORDER BY order_year_month ASC;

-- QUERY 4: Quarterly Performance and Seasonal Trajectory
SELECT
    order_year,
    order_quarter,
    ROUND(SUM(sales), 2) AS total_revenue,
    ROUND(SUM(profit), 2) AS total_profit,
    ROUND((SUM(profit) / SUM(sales)) * 100.0, 2) AS profit_margin_pct,
    COUNT(DISTINCT order_id) AS order_count
FROM retail_orders
GROUP BY order_year, order_quarter
ORDER BY order_year ASC, order_quarter ASC;

-- QUERY 5: Year-over-Year (YoY) Revenue & Profitability Expansion
WITH annual_summary AS (
    SELECT
        order_year,
        ROUND(SUM(sales), 2) AS annual_revenue,
        ROUND(SUM(profit), 2) AS annual_profit,
        COUNT(DISTINCT order_id) AS annual_orders
    FROM retail_orders
    GROUP BY order_year
)
SELECT
    order_year,
    annual_revenue,
    LAG(annual_revenue) OVER (ORDER BY order_year) AS prior_year_revenue,
    ROUND(
        ((annual_revenue - LAG(annual_revenue) OVER (ORDER BY order_year)) /
        LAG(annual_revenue) OVER (ORDER BY order_year)) * 100.0, 2
    ) AS yoy_revenue_growth_pct,
    annual_profit,
    LAG(annual_profit) OVER (ORDER BY order_year) AS prior_year_profit,
    ROUND(
        ((annual_profit - LAG(annual_profit) OVER (ORDER BY order_year)) /
        LAG(annual_profit) OVER (ORDER BY order_year)) * 100.0, 2
    ) AS yoy_profit_growth_pct,
    annual_orders
FROM annual_summary
ORDER BY order_year ASC;

-- QUERY 6: Category and Subcategory Profitability Breakdown
SELECT
    category,
    sub_category,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit,
    ROUND((SUM(profit) / SUM(sales)) * 100.0, 2) AS profit_margin_pct,
    SUM(quantity) AS units_sold,
    SUM(CASE WHEN profit < 0 THEN 1 ELSE 0 END) AS loss_order_count,
    ROUND(100.0 * SUM(CASE WHEN profit < 0 THEN 1 ELSE 0 END) / COUNT(*), 2) AS loss_rate_pct
FROM retail_orders
GROUP BY category, sub_category
ORDER BY category ASC, total_profit DESC;

-- QUERY 7: Intra-Category Subcategory Profit Ranking (Window Functions)
WITH subcat_metrics AS (
    SELECT
        category,
        sub_category,
        ROUND(SUM(sales), 2) AS total_sales,
        ROUND(SUM(profit), 2) AS total_profit,
        ROUND((SUM(profit) / SUM(sales)) * 100.0, 2) AS profit_margin_pct
    FROM retail_orders
    GROUP BY category, sub_category
)
SELECT
    category,
    sub_category,
    DENSE_RANK() OVER (PARTITION BY category ORDER BY total_profit DESC) AS category_profit_rank,
    total_profit,
    DENSE_RANK() OVER (PARTITION BY category ORDER BY total_sales DESC) AS category_sales_rank,
    total_sales,
    profit_margin_pct
FROM subcat_metrics
ORDER BY category, category_profit_rank ASC;

-- QUERY 8: "Sales Traps" - High Revenue but Negative Profit Items
SELECT
    product_id,
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

-- QUERY 9: Top 10 Most Profitable Products
SELECT
    product_id,
    product_name,
    category,
    sub_category,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS net_profit,
    ROUND((SUM(profit) / SUM(sales)) * 100.0, 2) AS profit_margin_pct,
    SUM(quantity) AS units_sold
FROM retail_orders
GROUP BY product_id, product_name, category, sub_category
ORDER BY net_profit DESC
LIMIT 10;

-- QUERY 10: Top 10 Biggest Loss-Making Products
SELECT
    product_id,
    product_name,
    category,
    sub_category,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS net_loss,
    ROUND((SUM(profit) / SUM(sales)) * 100.0, 2) AS profit_margin_pct,
    ROUND(AVG(discount) * 100.0, 1) AS avg_discount_pct
FROM retail_orders
GROUP BY product_id, product_name, category, sub_category
ORDER BY net_loss ASC
LIMIT 10;

-- QUERY 11: Discount Tier Sensitivity & Margin Erosion Analysis
SELECT
    discount_tier,
    COUNT(*) AS transaction_count,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit,
    ROUND((SUM(profit) / SUM(sales)) * 100.0, 2) AS realized_profit_margin_pct,
    ROUND(100.0 * SUM(CASE WHEN profit < 0 THEN 1 ELSE 0 END) / COUNT(*), 2) AS loss_transaction_rate_pct
FROM retail_orders
GROUP BY discount_tier
ORDER BY MIN(discount) ASC;

-- QUERY 12: Promotional Threshold Impact (Discounts < 20% vs >= 20%)
SELECT
    CASE
        WHEN discount = 0 THEN '1. Full Price (0%)'
        WHEN discount > 0 AND discount < 0.20 THEN '2. Mild Discount (1-19%)'
        WHEN discount >= 0.20 AND discount < 0.40 THEN '3. Heavy Discount (20-39%)'
        ELSE '4. Extreme Discount (40%+)'
    END AS discount_policy_group,
    COUNT(*) AS order_lines,
    ROUND(SUM(sales), 2) AS total_revenue,
    ROUND(SUM(profit), 2) AS total_profit,
    ROUND((SUM(profit) / SUM(sales)) * 100.0, 2) AS profit_margin_pct,
    ROUND(AVG(discount) * 100.0, 1) AS avg_discount_pct
FROM retail_orders
GROUP BY discount_policy_group
ORDER BY discount_policy_group ASC;

-- QUERY 13: Regional Performance & Profit Contribution Breakdown
WITH enterprise_totals AS (
    SELECT SUM(profit) AS grand_total_profit FROM retail_orders
)
SELECT
    r.region,
    ROUND(SUM(r.sales), 2) AS total_sales,
    ROUND(SUM(r.profit), 2) AS total_profit,
    ROUND((SUM(r.profit) / SUM(r.sales)) * 100.0, 2) AS profit_margin_pct,
    COUNT(DISTINCT r.order_id) AS total_orders,
    ROUND((SUM(r.profit) / et.grand_total_profit) * 100.0, 2) AS profit_share_pct
FROM retail_orders r
CROSS JOIN enterprise_totals et
GROUP BY r.region, et.grand_total_profit
ORDER BY total_profit DESC;

-- QUERY 14: State Profitability Extremes (Top 5 and Bottom 5 States)
WITH state_profits AS (
    SELECT
        state,
        ROUND(SUM(sales), 2) AS total_sales,
        ROUND(SUM(profit), 2) AS total_profit,
        ROUND((SUM(profit) / SUM(sales)) * 100.0, 2) AS profit_margin_pct,
        ROW_NUMBER() OVER (ORDER BY SUM(profit) DESC) AS top_rank,
        ROW_NUMBER() OVER (ORDER BY SUM(profit) ASC) AS bottom_rank
    FROM retail_orders
    GROUP BY state
)
SELECT 'Top 5 Most Profitable' AS state_tier, state, total_sales, total_profit, profit_margin_pct
FROM state_profits WHERE top_rank <= 5
UNION ALL
SELECT 'Bottom 5 Loss-Making' AS state_tier, state, total_sales, total_profit, profit_margin_pct
FROM state_profits WHERE bottom_rank <= 5
ORDER BY state_tier DESC, total_profit DESC;

-- QUERY 15: Customer Segment Commercial Performance
SELECT
    segment,
    COUNT(DISTINCT customer_id) AS customer_count,
    COUNT(DISTINCT order_id) AS total_orders,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit,
    ROUND((SUM(profit) / SUM(sales)) * 100.0, 2) AS profit_margin_pct,
    ROUND(SUM(sales) / COUNT(DISTINCT order_id), 2) AS average_order_value
FROM retail_orders
GROUP BY segment
ORDER BY total_sales DESC;

-- QUERY 16: Average Order Value (AOV) by Region and Segment
SELECT
    region,
    segment,
    COUNT(DISTINCT order_id) AS order_count,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(sales) / COUNT(DISTINCT order_id), 2) AS average_order_value,
    ROUND(SUM(profit) / COUNT(DISTINCT order_id), 2) AS average_profit_per_order
FROM retail_orders
GROUP BY region, segment
ORDER BY region ASC, average_order_value DESC;

-- QUERY 17: Customer-Level RFM Baseline Analysis
WITH dataset_max_date AS (
    SELECT MAX(order_date) AS max_date FROM retail_orders
)
SELECT
    r.customer_id,
    r.customer_name,
    r.segment,
    COUNT(DISTINCT r.order_id) AS order_frequency,
    ROUND(SUM(r.sales), 2) AS total_spend,
    ROUND(SUM(r.profit), 2) AS total_profit,
    ROUND((SUM(r.profit) / SUM(r.sales)) * 100.0, 2) AS profit_margin_pct,
    CAST(ROUND(JULIANDAY(d.max_date) - JULIANDAY(MAX(r.order_date))) AS INTEGER) AS days_since_last_order
FROM retail_orders r
CROSS JOIN dataset_max_date d
GROUP BY r.customer_id, r.customer_name, r.segment, d.max_date
ORDER BY total_spend DESC
LIMIT 20;

-- QUERY 18: Top 15 Customer Accounts by Lifetime Profit Contribution
SELECT
    customer_id,
    customer_name,
    segment,
    COUNT(DISTINCT order_id) AS total_orders,
    ROUND(SUM(sales), 2) AS total_spend,
    ROUND(SUM(profit), 2) AS net_profit_contribution,
    ROUND((SUM(profit) / SUM(sales)) * 100.0, 2) AS profit_margin_pct
FROM retail_orders
GROUP BY customer_id, customer_name, segment
ORDER BY net_profit_contribution DESC
LIMIT 15;

-- QUERY 19: Customer Loyalty & Repeat Order Frequency Distribution
WITH customer_orders AS (
    SELECT
        customer_id,
        COUNT(DISTINCT order_id) AS order_count,
        SUM(sales) AS customer_sales,
        SUM(profit) AS customer_profit
    FROM retail_orders
    GROUP BY customer_id
),
customer_buckets AS (
    SELECT
        customer_id,
        order_count,
        customer_sales,
        customer_profit,
        CASE
            WHEN order_count = 1 THEN '1 Single Order'
            WHEN order_count BETWEEN 2 AND 4 THEN '2 - 4 Orders (Low Repeat)'
            WHEN order_count BETWEEN 5 AND 9 THEN '5 - 9 Orders (Medium Repeat)'
            ELSE '10+ Orders (High Loyalty)'
        END AS purchase_frequency_tier
    FROM customer_orders
)
SELECT
    purchase_frequency_tier,
    COUNT(customer_id) AS customer_count,
    ROUND(SUM(customer_sales), 2) AS total_revenue,
    ROUND(SUM(customer_profit), 2) AS total_profit,
    ROUND(AVG(customer_sales), 2) AS avg_revenue_per_customer
FROM customer_buckets
GROUP BY purchase_frequency_tier
ORDER BY MIN(order_count) ASC;

-- QUERY 20: Shipping Mode Logistics Efficiency and Profit Margins
SELECT
    ship_mode,
    COUNT(*) AS line_items,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit,
    ROUND((SUM(profit) / SUM(sales)) * 100.0, 2) AS profit_margin_pct,
    ROUND(AVG(shipping_duration_days), 1) AS avg_shipping_days
FROM retail_orders
GROUP BY ship_mode
ORDER BY total_sales DESC;

-- QUERY 21: Cumulative Running Totals of Revenue and Profit across Time
WITH monthly_financials AS (
    SELECT
        order_year_month,
        ROUND(SUM(sales), 2) AS monthly_sales,
        ROUND(SUM(profit), 2) AS monthly_profit
    FROM retail_orders
    GROUP BY order_year_month
)
SELECT
    order_year_month,
    monthly_sales,
    ROUND(SUM(monthly_sales) OVER (ORDER BY order_year_month ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW), 2) AS cumulative_sales,
    monthly_profit,
    ROUND(SUM(monthly_profit) OVER (ORDER BY order_year_month ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW), 2) AS cumulative_profit
FROM monthly_financials
ORDER BY order_year_month ASC;
