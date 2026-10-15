"""Streamlit Interactive Analytics Application for Retail Sales & Profitability.

Run via command:
    streamlit run app/streamlit_app.py
"""

import sys
from pathlib import Path
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.config import DATABASE_FILE, CLEANED_DATA_FILE
from src.database import get_db_connection, execute_query
from src.metrics import calculate_kpi_summary

# Page Configuration
st.set_page_config(
    page_title="Retail Sales & Profitability Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for executive aesthetic
st.markdown("""
<style>
    .main-header {
        font-size: 28px;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 2px;
    }
    .sub-header {
        font-size: 14px;
        color: #64748B;
        margin-bottom: 20px;
    }
    .metric-card {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 15px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data() -> pd.DataFrame:
    """Load cleaned dataset from CSV or SQLite."""
    if CLEANED_DATA_FILE.exists():
        df = pd.read_csv(CLEANED_DATA_FILE)
        df["order_date"] = pd.to_datetime(df["order_date"])
        df["ship_date"] = pd.to_datetime(df["ship_date"])
        return df
    else:
        conn = get_db_connection(DATABASE_FILE)
        df = pd.read_sql_query("SELECT * FROM retail_orders", conn)
        df["order_date"] = pd.to_datetime(df["order_date"])
        df["ship_date"] = pd.to_datetime(df["ship_date"])
        return df


df_raw = load_data()

# Sidebar Controls
st.sidebar.title("🎛️ Analytics Controls")
st.sidebar.markdown("Filter enterprise transaction metrics:")

# Date Range Filter
min_date = df_raw["order_date"].min().date()
max_date = df_raw["order_date"].max().date()

date_range = st.sidebar.date_input(
    "Order Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)

# Region Filter
regions = sorted(df_raw["region"].unique().tolist())
selected_regions = st.sidebar.multiselect("Geographic Regions", options=regions, default=regions)

# Category Filter
categories = sorted(df_raw["category"].unique().tolist())
selected_categories = st.sidebar.multiselect("Merchandise Categories", options=categories, default=categories)

# Apply Filters
start_d, end_d = (date_range[0], date_range[1]) if len(date_range) == 2 else (min_date, max_date)
mask = (
    (df_raw["order_date"].dt.date >= start_d)
    & (df_raw["order_date"].dt.date <= end_d)
    & (df_raw["region"].isin(selected_regions))
    & (df_raw["category"].isin(selected_categories))
)
df = df_raw[mask].copy()

# Header Banner
st.markdown('<div class="main-header">Retail Sales & Profitability Intelligence Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Executive decision-support portal tracking revenue expansion, discount elasticity, and product margins.</div>', unsafe_allow_html=True)

# Top KPI Metric Cards
kpis = calculate_kpi_summary(df)
k1, k2, k3, k4, k5, k6 = st.columns(6)

k1.metric("Total Revenue", f"${kpis['total_revenue']:,.0f}")
k2.metric("Net Profit", f"${kpis['total_profit']:,.0f}")
k3.metric("Profit Margin", f"{kpis['profit_margin_pct']:.1f}%")
k4.metric("Total Orders", f"{kpis['total_orders']:,}")
k5.metric("Units Sold", f"{kpis['total_units_sold']:,}")
k6.metric("Avg Order Value", f"${kpis['average_order_value']:,.2f}")

st.markdown("---")

# Navigation Tabs
tab_exec, tab_cat, tab_disc, tab_geo, tab_sql = st.tabs([
    "📈 Revenue & Monthly Trends",
    "📦 Category & Sales Traps",
    "🏷️ Discount Margin Erosion",
    "🗺️ Regional & Customers",
    "💻 SQL Query Sandbox",
])

# -------------------------------------------------------------
# TAB 1: Revenue & Monthly Trends
# -------------------------------------------------------------
with tab_exec:
    st.subheader("Monthly Revenue and Profit Trajectory")

    monthly = (
        df.groupby("order_year_month", as_index=False)
        .agg(
            sales=("sales", "sum"),
            profit=("profit", "sum"),
            orders=("order_id", "nunique"),
        )
        .sort_values("order_year_month")
    )
    monthly["margin_pct"] = (monthly["profit"] / monthly["sales"]) * 100.0

    fig_month = go.Figure()
    fig_month.add_trace(go.Bar(
        x=monthly["order_year_month"],
        y=monthly["sales"],
        name="Sales Revenue ($)",
        marker_color="#2563EB",
        opacity=0.85,
    ))
    fig_month.add_trace(go.Scatter(
        x=monthly["order_year_month"],
        y=monthly["profit"],
        name="Net Profit ($)",
        marker_color="#059669",
        mode="lines+markers",
        line=dict(width=2.5),
        yaxis="y2",
    ))
    fig_month.update_layout(
        title="Monthly Commercial Trajectory (Sales vs Net Profit)",
        xaxis=dict(title="Billing Month (YYYY-MM)", tickangle=-45),
        yaxis=dict(title="Sales Revenue ($)", side="left"),
        yaxis2=dict(title="Net Profit ($)", side="right", overlaying="y", showgrid=False),
        legend=dict(x=0.01, y=0.99, bgcolor="rgba(255,255,255,0.8)"),
        height=450,
        margin=dict(l=40, r=40, t=50, b=40),
    )
    st.plotly_chart(fig_month, use_container_width=True)

    # Annual comparison
    col_a1, col_a2 = st.columns(2)
    with col_a1:
        st.subheader("Performance by Calendar Year")
        annual = (
            df.groupby("order_year", as_index=False)
            .agg(
                orders=("order_id", "nunique"),
                sales=("sales", "sum"),
                profit=("profit", "sum"),
            )
            .sort_values("order_year")
        )
        annual["margin_pct"] = (annual["profit"] / annual["sales"]) * 100.0
        fig_ann = px.bar(
            annual,
            x="order_year",
            y="sales",
            color="margin_pct",
            color_continuous_scale="Viridis",
            labels={"order_year": "Year", "sales": "Sales ($)", "margin_pct": "Margin %"},
            title="Annual Sales & Realized Profit Margin",
        )
        st.plotly_chart(fig_ann, use_container_width=True)

    with col_a2:
        st.subheader("Seasonality: Orders by Quarter")
        quarterly = (
            df.groupby("order_quarter", as_index=False)
            .agg(sales=("sales", "sum"), profit=("profit", "sum"))
        )
        fig_q = px.pie(
            quarterly,
            values="sales",
            names="order_quarter",
            title="Revenue Distribution by Fiscal Quarter (Q1-Q4)",
            hole=0.4,
            color_discrete_sequence=px.colors.sequential.Blues_r,
        )
        st.plotly_chart(fig_q, use_container_width=True)


# -------------------------------------------------------------
# TAB 2: Category & Sales Traps
# -------------------------------------------------------------
with tab_cat:
    st.subheader("Subcategory Profitability Benchmark")

    sub_df = (
        df.groupby(["category", "sub_category"], as_index=False)
        .agg(
            sales=("sales", "sum"),
            profit=("profit", "sum"),
            orders=("order_id", "nunique"),
        )
        .sort_values("profit", ascending=True)
    )
    sub_df["margin_pct"] = (sub_df["profit"] / sub_df["sales"]) * 100.0
    sub_df["status"] = ["Loss Maker" if p < 0 else "Profitable" for p in sub_df["profit"]]

    fig_sub = px.bar(
        sub_df,
        x="profit",
        y="sub_category",
        color="status",
        color_discrete_map={"Profitable": "#0D9488", "Loss Maker": "#DC2626"},
        orientation="h",
        labels={"profit": "Net Profit ($)", "sub_category": "Subcategory"},
        title="Subcategory Net Profit Contribution (Red Indicates Loss Centers)",
        height=500,
    )
    st.plotly_chart(fig_sub, use_container_width=True)

    st.subheader("⚠️ Catalog 'Sales Traps' (High Revenue, Negative Profit)")
    st.markdown("Products generating substantial sales volume but bleeding cash due to steep discounts or unsustainable unit economics:")

    traps_df = (
        df.groupby(["product_id", "product_name", "category", "sub_category"], as_index=False)
        .agg(
            sales=("sales", "sum"),
            profit=("profit", "sum"),
            avg_discount=("discount", "mean"),
            units=("quantity", "sum"),
        )
    )
    traps = traps_df[(traps_df["sales"] >= 2000.0) & (traps_df["profit"] < 0)].copy()
    traps["margin_pct"] = (traps["profit"] / traps["sales"]) * 100.0
    traps = traps.sort_values("profit", ascending=True)

    st.dataframe(
        traps.style.format({
            "sales": "${:,.2f}",
            "profit": "${:,.2f}",
            "margin_pct": "{:.1f}%",
            "avg_discount": "{:.1%}",
            "units": "{:,}",
        }),
        use_container_width=True,
    )


# -------------------------------------------------------------
# TAB 3: Discount Margin Erosion
# -------------------------------------------------------------
with tab_disc:
    st.subheader("The Danger of Excessive Discounting")
    st.markdown("""
    Analysis clearly proves that **profit margins compress rapidly as discounts increase**.
    Beyond 20% discount, the average transaction produces severe negative returns.
    """)

    disc_summary = (
        df.groupby("discount_tier", as_index=False, observed=False)
        .agg(
            lines=("row_id", "count"),
            sales=("sales", "sum"),
            profit=("profit", "sum"),
            avg_discount=("discount", "mean"),
            loss_lines=("profit", lambda p: (p < 0).sum()),
        )
    )
    disc_summary["margin_pct"] = (disc_summary["profit"] / disc_summary["sales"]) * 100.0
    disc_summary["loss_rate_pct"] = (disc_summary["loss_lines"] / disc_summary["lines"]) * 100.0

    col_d1, col_d2 = st.columns(2)
    with col_d1:
        fig_disc_m = px.bar(
            disc_summary,
            x="discount_tier",
            y="margin_pct",
            color="margin_pct",
            color_continuous_scale="RdYlGn",
            labels={"discount_tier": "Discount Bracket", "margin_pct": "Realized Margin %"},
            title="Realized Profit Margin % Across Discount Tiers",
        )
        st.plotly_chart(fig_disc_m, use_container_width=True)

    with col_d2:
        fig_disc_loss = px.line(
            disc_summary,
            x="discount_tier",
            y="loss_rate_pct",
            markers=True,
            labels={"discount_tier": "Discount Bracket", "loss_rate_pct": "% Loss Transactions"},
            title="Loss Transaction Rate by Discount Tier",
        )
        fig_disc_loss.update_traces(line_color="#E11D48", line_width=3)
        st.plotly_chart(fig_disc_loss, use_container_width=True)

    st.dataframe(
        disc_summary.style.format({
            "sales": "${:,.2f}",
            "profit": "${:,.2f}",
            "margin_pct": "{:.1f}%",
            "loss_rate_pct": "{:.1f}%",
            "avg_discount": "{:.1%}",
            "lines": "{:,}",
        }),
        use_container_width=True,
    )


# -------------------------------------------------------------
# TAB 4: Regional & Customer Deep Dive
# -------------------------------------------------------------
with tab_geo:
    col_g1, col_g2 = st.columns(2)

    with col_g1:
        st.subheader("Regional Performance")
        reg_df = (
            df.groupby("region", as_index=False)
            .agg(sales=("sales", "sum"), profit=("profit", "sum"))
            .sort_values("profit", ascending=False)
        )
        reg_df["margin_pct"] = (reg_df["profit"] / reg_df["sales"]) * 100.0
        fig_reg = px.bar(
            reg_df,
            x="region",
            y=["sales", "profit"],
            barmode="group",
            labels={"value": "Amount ($)", "region": "Region"},
            title="Sales vs Net Profit by Geographic Region",
            color_discrete_sequence=["#3B82F6", "#10B981"],
        )
        st.plotly_chart(fig_reg, use_container_width=True)

    with col_g2:
        st.subheader("Customer Segment Performance")
        seg_df = (
            df.groupby("segment", as_index=False)
            .agg(
                sales=("sales", "sum"),
                profit=("profit", "sum"),
                orders=("order_id", "nunique"),
            )
        )
        seg_df["aov"] = seg_df["sales"] / seg_df["orders"]
        fig_seg = px.pie(
            seg_df,
            values="sales",
            names="segment",
            title="Sales Share by Customer Segment",
            hole=0.4,
            color_discrete_sequence=px.colors.sequential.Teal,
        )
        st.plotly_chart(fig_seg, use_container_width=True)

    st.subheader("Top 15 Most Profitable Customer Accounts")
    top_cust = (
        df.groupby(["customer_id", "customer_name", "segment"], as_index=False)
        .agg(
            orders=("order_id", "nunique"),
            sales=("sales", "sum"),
            profit=("profit", "sum"),
        )
        .sort_values("profit", ascending=False)
        .head(15)
    )
    top_cust["margin_pct"] = (top_cust["profit"] / top_cust["sales"]) * 100.0
    st.dataframe(
        top_cust.style.format({
            "sales": "${:,.2f}",
            "profit": "${:,.2f}",
            "margin_pct": "{:.1f}%",
            "orders": "{:,}",
        }),
        use_container_width=True,
    )


# -------------------------------------------------------------
# TAB 5: SQL Query Sandbox
# -------------------------------------------------------------
with tab_sql:
    st.subheader("Interactive SQL Analytical Query Sandbox")
    st.markdown("Execute SQL queries directly against the `database/retail_analytics.db` SQLite database:")

    predefined_queries = {
        "Executive KPI Overview": "SELECT ROUND(SUM(sales), 2) AS total_revenue, ROUND(SUM(profit), 2) AS total_profit, ROUND((SUM(profit)/SUM(sales))*100, 2) AS margin_pct, COUNT(DISTINCT order_id) AS orders FROM retail_orders;",
        "Top 10 Profitable Products": "SELECT product_name, category, ROUND(SUM(sales), 2) AS sales, ROUND(SUM(profit), 2) AS profit FROM retail_orders GROUP BY product_name, category ORDER BY profit DESC LIMIT 10;",
        "Subcategory Profitability": "SELECT category, sub_category, ROUND(SUM(sales), 2) AS sales, ROUND(SUM(profit), 2) AS profit, ROUND((SUM(profit)/SUM(sales))*100, 2) AS margin_pct FROM retail_orders GROUP BY category, sub_category ORDER BY profit DESC;",
        "Monthly Sales and Profit": "SELECT order_year_month, ROUND(SUM(sales), 2) AS sales, ROUND(SUM(profit), 2) AS profit FROM retail_orders GROUP BY order_year_month ORDER BY order_year_month ASC LIMIT 12;",
    }

    selected_query_title = st.selectbox("Select Pre-configured Business Query", options=list(predefined_queries.keys()))
    default_sql = predefined_queries[selected_query_title]

    custom_sql = st.text_area("SQL Query Editor", value=default_sql, height=120)

    if st.button("Run SQL Query", type="primary"):
        try:
            res_df = execute_query(custom_sql)
            st.success(f"Query returned {len(res_df):,} rows.")
            st.dataframe(res_df, use_container_width=True)
        except Exception as e:
            st.error(f"SQL Execution Error: {e}")
