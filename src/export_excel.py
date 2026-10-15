"""Professional Excel Workbook Generator for Retail Sales Analytics.

Builds a polished 10-sheet financial workbook adhering to corporate FP&A
and BI design standards using openpyxl.
"""

import logging
from pathlib import Path
from typing import Dict, Any, List
import numpy as np
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
import pandas as pd

from src.config import EXCEL_OUTPUT_FILE
from src.metrics import (
    calculate_kpi_summary,
    calculate_monthly_summary,
    calculate_category_summary,
    calculate_discount_sensitivity,
    calculate_sales_traps,
    calculate_rfm_metrics,
    calculate_regional_summary,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Design Palette
FONT_FAMILY = "Segoe UI"
COLOR_NAVY_DARK = "1B365D"       # Primary Headers
COLOR_NAVY_LIGHT = "2563EB"      # Accent Blue
COLOR_SLATE_HEADER = "334155"    # Secondary Headers
COLOR_LIGHT_BG = "F8FAFC"        # Card background
COLOR_EMERALD_BG = "ECFDF5"      # Positive KPI
COLOR_EMERALD_TEXT = "065F46"
COLOR_ROSE_BG = "FEF2F2"         # Negative KPI
COLOR_ROSE_TEXT = "991B1B"
COLOR_ZEBRA = "F1F5F9"           # Alternating row fill

# Style primitives
FONT_TITLE = Font(name=FONT_FAMILY, size=16, bold=True, color="FFFFFF")
FONT_SUBTITLE = Font(name=FONT_FAMILY, size=11, italic=True, color="E2E8F0")
FONT_SECTION = Font(name=FONT_FAMILY, size=12, bold=True, color=COLOR_NAVY_DARK)
FONT_HEADER = Font(name=FONT_FAMILY, size=10, bold=True, color="FFFFFF")
FONT_REGULAR = Font(name=FONT_FAMILY, size=10)
FONT_BOLD = Font(name=FONT_FAMILY, size=10, bold=True)
FONT_KPI_VAL = Font(name=FONT_FAMILY, size=18, bold=True, color=COLOR_NAVY_DARK)
FONT_KPI_LBL = Font(name=FONT_FAMILY, size=9, bold=True, color="64748B")

FILL_TITLE = PatternFill(start_color=COLOR_NAVY_DARK, end_color=COLOR_NAVY_DARK, fill_type="solid")
FILL_HEADER = PatternFill(start_color=COLOR_SLATE_HEADER, end_color=COLOR_SLATE_HEADER, fill_type="solid")
FILL_CARD = PatternFill(start_color=COLOR_LIGHT_BG, end_color=COLOR_LIGHT_BG, fill_type="solid")
FILL_ZEBRA = PatternFill(start_color=COLOR_ZEBRA, end_color=COLOR_ZEBRA, fill_type="solid")
FILL_PROFIT_POS = PatternFill(start_color=COLOR_EMERALD_BG, end_color=COLOR_EMERALD_BG, fill_type="solid")
FILL_PROFIT_NEG = PatternFill(start_color=COLOR_ROSE_BG, end_color=COLOR_ROSE_BG, fill_type="solid")

THIN_BORDER_SIDE = Side(style="thin", color="CBD5E1")
BORDER_BOX = Border(left=THIN_BORDER_SIDE, right=THIN_BORDER_SIDE, top=THIN_BORDER_SIDE, bottom=THIN_BORDER_SIDE)
BORDER_TOP_BOTTOM = Border(top=THIN_BORDER_SIDE, bottom=Side(style="double", color="334155"))

ALIGN_CENTER = Alignment(horizontal="center", vertical="center")
ALIGN_LEFT = Alignment(horizontal="left", vertical="center")
ALIGN_RIGHT = Alignment(horizontal="right", vertical="center")


def auto_fit_columns(ws, min_width: int = 12, max_width: int = 40):
    """Auto-fit column widths with safety bounds to prevent clipped text."""
    ws.views.sheetView[0].showGridLines = True
    for col in ws.columns:
        col_letter = get_column_letter(col[0].column)
        max_len = 0
        for cell in col:
            # Skip title merged banner rows
            if cell.row in [1, 2]:
                continue
            val_str = str(cell.value or "")
            if len(val_str) > max_len:
                max_len = len(val_str)
        adjusted_width = max(min_width, min(max_len + 4, max_width))
        ws.column_dimensions[col_letter].width = adjusted_width


def add_sheet_banner(ws, title: str, subtitle: str, max_col: int = 8):
    """Add a polished corporate banner header across the top of a worksheet."""
    ws.row_dimensions[1].height = 32
    ws.row_dimensions[2].height = 20
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=max_col)
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=max_col)

    cell_title = ws.cell(row=1, column=1, value=title)
    cell_title.font = FONT_TITLE
    cell_title.fill = FILL_TITLE
    cell_title.alignment = Alignment(horizontal="left", vertical="center", indent=1)

    cell_sub = ws.cell(row=2, column=1, value=subtitle)
    cell_sub.font = FONT_SUBTITLE
    cell_sub.fill = FILL_TITLE
    cell_sub.alignment = Alignment(horizontal="left", vertical="center", indent=1)


def create_executive_dashboard(wb: openpyxl.Workbook, df: pd.DataFrame):
    """Build Sheet 1: Executive Dashboard with KPI Scorecards and high-level summaries."""
    ws = wb.create_sheet(title="Executive Dashboard", index=0)
    add_sheet_banner(
        ws,
        "RETAIL SALES & PROFITABILITY EXECUTIVE DASHBOARD",
        "Enterprise commercial performance scorecard (2014 - 2017) | Data-driven decision support",
        max_col=10,
    )

    kpis = calculate_kpi_summary(df)

    # 1. KPI Cards Setup
    kpi_cards = [
        ("TOTAL REVENUE", f"${kpis['total_revenue']:,.2f}", "$#,##0.00", kpis['total_revenue']),
        ("NET PROFIT", f"${kpis['total_profit']:,.2f}", "$#,##0.00", kpis['total_profit']),
        ("PROFIT MARGIN", f"{kpis['profit_margin_pct']:.2f}%", "0.00%", kpis['profit_margin_pct'] / 100.0),
        ("TOTAL ORDERS", f"{kpis['total_orders']:,}", "#,##0", kpis['total_orders']),
        ("TOTAL UNITS SOLD", f"{kpis['total_units_sold']:,}", "#,##0", kpis['total_units_sold']),
        ("AVG ORDER VALUE", f"${kpis['average_order_value']:,.2f}", "$#,##0.00", kpis['average_order_value']),
    ]

    ws.row_dimensions[4].height = 18
    ws.row_dimensions[5].height = 28

    col_idx = 1
    for title, display_val, num_fmt, raw_val in kpi_cards:
        # Header cell
        c_lbl = ws.cell(row=4, column=col_idx, value=title)
        c_lbl.font = FONT_KPI_LBL
        c_lbl.fill = FILL_CARD
        c_lbl.alignment = ALIGN_CENTER
        c_lbl.border = Border(left=THIN_BORDER_SIDE, right=THIN_BORDER_SIDE, top=THIN_BORDER_SIDE)

        # Value cell
        c_val = ws.cell(row=5, column=col_idx, value=raw_val)
        c_val.font = FONT_KPI_VAL
        c_val.fill = FILL_CARD
        c_val.alignment = ALIGN_CENTER
        c_val.number_format = num_fmt
        c_val.border = Border(left=THIN_BORDER_SIDE, right=THIN_BORDER_SIDE, bottom=THIN_BORDER_SIDE)

        ws.column_dimensions[get_column_letter(col_idx)].width = 18
        col_idx += 1

    # 2. Executive Highlights Table (Annual Progression)
    ws.cell(row=8, column=1, value="ANNUAL COMMERCIAL PERFORMANCE TRAJECTORY").font = FONT_SECTION

    annual_summary = (
        df.groupby("order_year", as_index=False)
        .agg(
            total_orders=("order_id", "nunique"),
            total_sales=("sales", "sum"),
            total_profit=("profit", "sum"),
            units_sold=("quantity", "sum"),
            avg_discount=("discount", "mean"),
        )
        .sort_values("order_year")
    )
    annual_summary["profit_margin"] = annual_summary["total_profit"] / annual_summary["total_sales"]
    annual_summary["aov"] = annual_summary["total_sales"] / annual_summary["total_orders"]

    headers = ["Fiscal Year", "Orders", "Units Sold", "Total Revenue", "Net Profit", "Profit Margin", "Avg Discount", "AOV"]
    for j, h in enumerate(headers, start=1):
        c = ws.cell(row=9, column=j, value=h)
        c.font = FONT_HEADER
        c.fill = FILL_HEADER
        c.alignment = ALIGN_CENTER
        c.border = BORDER_BOX

    for i, row in annual_summary.iterrows():
        r = 10 + i
        ws.cell(row=r, column=1, value=int(row["order_year"])).alignment = ALIGN_CENTER
        ws.cell(row=r, column=2, value=int(row["total_orders"])).number_format = "#,##0"
        ws.cell(row=r, column=3, value=int(row["units_sold"])).number_format = "#,##0"
        ws.cell(row=r, column=4, value=float(row["total_sales"])).number_format = "$#,##0.00"
        
        cp = ws.cell(row=r, column=5, value=float(row["total_profit"]))
        cp.number_format = "$#,##0.00"
        cp.fill = FILL_PROFIT_POS if row["total_profit"] >= 0 else FILL_PROFIT_NEG

        cm = ws.cell(row=r, column=6, value=float(row["profit_margin"]))
        cm.number_format = "0.00%"
        cm.fill = FILL_PROFIT_POS if row["profit_margin"] >= 0 else FILL_PROFIT_NEG

        ws.cell(row=r, column=7, value=float(row["avg_discount"])).number_format = "0.0%"
        ws.cell(row=r, column=8, value=float(row["aov"])).number_format = "$#,##0.00"

        for col_j in range(1, 9):
            ws.cell(row=r, column=col_j).border = BORDER_BOX
            ws.cell(row=r, column=col_j).font = FONT_REGULAR

    # Summary Totals Row via Formula
    tot_r = 10 + len(annual_summary)
    ws.cell(row=tot_r, column=1, value="Total / Enterprise").font = FONT_BOLD
    ws.cell(row=tot_r, column=2, value=f"=SUM(B10:B{tot_r-1})").number_format = "#,##0"
    ws.cell(row=tot_r, column=3, value=f"=SUM(C10:C{tot_r-1})").number_format = "#,##0"
    ws.cell(row=tot_r, column=4, value=f"=SUM(D10:D{tot_r-1})").number_format = "$#,##0.00"
    ws.cell(row=tot_r, column=5, value=f"=SUM(E10:E{tot_r-1})").number_format = "$#,##0.00"
    ws.cell(row=tot_r, column=6, value=f"=E{tot_r}/D{tot_r}").number_format = "0.00%"
    ws.cell(row=tot_r, column=7, value=f"=AVERAGE(G10:G{tot_r-1})").number_format = "0.0%"
    ws.cell(row=tot_r, column=8, value=f"=D{tot_r}/B{tot_r}").number_format = "$#,##0.00"

    for col_j in range(1, 9):
        c = ws.cell(row=tot_r, column=col_j)
        c.font = FONT_BOLD
        c.border = BORDER_TOP_BOTTOM
        if col_j >= 2:
            c.alignment = ALIGN_RIGHT
        else:
            c.alignment = ALIGN_CENTER

    # 3. Key Management Callouts Box
    ws.cell(row=16, column=1, value="STRATEGIC OBSERVATIONS & EXECUTIVE CALLOUTS").font = FONT_SECTION
    callouts = [
        "1. Revenue Velocity: Enterprise revenue expanded steadily from 2014 to 2017, with peak monthly surges concentrated in Q4 holiday cycles.",
        "2. Margin Compression Warning: Heavy discounting (>20%) systematically converts profitable volume into net losses, particularly in Furniture and Supplies.",
        "3. Value Destroyers: Subcategories such as Tables (-$17.7K net loss) and Bookcases suffer chronic negative margins requiring immediate pricing intervention.",
        "4. Technology Outperformance: Technology maintains the highest net profit contribution (~$145.5K) led by Phones, Copiers, and Accessories.",
    ]
    for idx, text in enumerate(callouts, start=17):
        c = ws.cell(row=idx, column=1, value=text)
        c.font = FONT_REGULAR
        ws.merge_cells(start_row=idx, start_column=1, end_row=idx, end_column=8)

    auto_fit_columns(ws)


def create_monthly_trends_sheet(wb: openpyxl.Workbook, df: pd.DataFrame):
    """Build Sheet 2: Monthly Trends with MoM growth and margin metrics."""
    ws = wb.create_sheet(title="Monthly Trends")
    add_sheet_banner(ws, "MONTHLY COMMERCIAL PERFORMANCE & MOM TRAJECTORY", "Sequential 48-month time series tracking sales, profit, orders, and MoM velocity", max_col=10)

    monthly_df = calculate_monthly_summary(df)

    headers = [
        "Month (YYYY-MM)", "Year", "Month", "Orders", "Units Sold",
        "Revenue", "Net Profit", "Margin %", "AOV", "MoM Sales Growth %"
    ]
    for j, h in enumerate(headers, start=1):
        c = ws.cell(row=4, column=j, value=h)
        c.font = FONT_HEADER
        c.fill = FILL_HEADER
        c.alignment = ALIGN_CENTER
        c.border = BORDER_BOX

    for i, row in monthly_df.iterrows():
        r = 5 + i
        ws.cell(row=r, column=1, value=row["order_year_month"]).alignment = ALIGN_CENTER
        ws.cell(row=r, column=2, value=int(row["order_year"])).alignment = ALIGN_CENTER
        ws.cell(row=r, column=3, value=int(row["order_month"])).alignment = ALIGN_CENTER
        ws.cell(row=r, column=4, value=int(row["total_orders"])).number_format = "#,##0"
        ws.cell(row=r, column=5, value=int(row["total_quantity"])).number_format = "#,##0"
        ws.cell(row=r, column=6, value=float(row["total_sales"])).number_format = "$#,##0.00"

        cp = ws.cell(row=r, column=7, value=float(row["total_profit"]))
        cp.number_format = "$#,##0.00"
        cp.fill = FILL_PROFIT_POS if row["total_profit"] >= 0 else FILL_PROFIT_NEG

        cm = ws.cell(row=r, column=8, value=float(row["profit_margin_pct"]) / 100.0)
        cm.number_format = "0.00%"
        cm.fill = FILL_PROFIT_POS if row["profit_margin_pct"] >= 0 else FILL_PROFIT_NEG

        ws.cell(row=r, column=9, value=float(row["average_order_value"])).number_format = "$#,##0.00"

        c_mom = ws.cell(
            row=r,
            column=10,
            value=(float(row["mom_sales_growth_pct"]) / 100.0) if pd.notna(row["mom_sales_growth_pct"]) else "",
        )
        if pd.notna(row["mom_sales_growth_pct"]):
            c_mom.number_format = "0.00%"

        for col_j in range(1, 11):
            ws.cell(row=r, column=col_j).border = BORDER_BOX
            ws.cell(row=r, column=col_j).font = FONT_REGULAR

    ws.freeze_panes = "A5"
    auto_fit_columns(ws)


def create_category_analysis_sheet(wb: openpyxl.Workbook, df: pd.DataFrame):
    """Build Sheet 3: Category & Subcategory Profitability Breakdown."""
    ws = wb.create_sheet(title="Category Analysis")
    add_sheet_banner(ws, "DEPARTMENT & SUBCATEGORY PROFITABILITY ANALYSIS", "Evaluation of 17 product subcategories highlighting winners and loss-makers", max_col=10)

    cat_df = calculate_category_summary(df)

    headers = [
        "Category", "Sub-Category", "Orders", "Units Sold", "Total Revenue",
        "Net Profit", "Profit Margin", "Avg Discount", "Loss Order Lines", "Loss Line Rate %"
    ]
    for j, h in enumerate(headers, start=1):
        c = ws.cell(row=4, column=j, value=h)
        c.font = FONT_HEADER
        c.fill = FILL_HEADER
        c.alignment = ALIGN_CENTER
        c.border = BORDER_BOX

    for i, row in cat_df.iterrows():
        r = 5 + i
        ws.cell(row=r, column=1, value=row["category"]).alignment = ALIGN_LEFT
        ws.cell(row=r, column=2, value=row["sub_category"]).alignment = ALIGN_LEFT
        ws.cell(row=r, column=3, value=int(row["total_orders"])).number_format = "#,##0"
        ws.cell(row=r, column=4, value=int(row["units_sold"])).number_format = "#,##0"
        ws.cell(row=r, column=5, value=float(row["total_sales"])).number_format = "$#,##0.00"

        cp = ws.cell(row=r, column=6, value=float(row["total_profit"]))
        cp.number_format = "$#,##0.00"
        cp.fill = FILL_PROFIT_POS if row["total_profit"] >= 0 else FILL_PROFIT_NEG

        cm = ws.cell(row=r, column=7, value=float(row["profit_margin_pct"]) / 100.0)
        cm.number_format = "0.00%"
        cm.fill = FILL_PROFIT_POS if row["profit_margin_pct"] >= 0 else FILL_PROFIT_NEG

        ws.cell(row=r, column=8, value=float(row["avg_discount_pct"]) / 100.0).number_format = "0.0%"
        ws.cell(row=r, column=9, value=int(row["loss_orders"])).number_format = "#,##0"
        ws.cell(row=r, column=10, value=float(row["loss_rate_pct"]) / 100.0).number_format = "0.00%"

        for col_j in range(1, 11):
            ws.cell(row=r, column=col_j).border = BORDER_BOX
            ws.cell(row=r, column=col_j).font = FONT_REGULAR

    ws.freeze_panes = "A5"
    auto_fit_columns(ws)


def create_product_analysis_sheet(wb: openpyxl.Workbook, df: pd.DataFrame):
    """Build Sheet 4: Product Analysis (Top Profitable vs Sales Traps)."""
    ws = wb.create_sheet(title="Product Analysis")
    add_sheet_banner(ws, "PRODUCT PROFITABILITY & SALES TRAP AUDIT", "Catalog performance: Top 15 Profit Stars vs High-Revenue Value Destroyers", max_col=8)

    # Top 15 Profitable Products
    prod_summary = (
        df.groupby(["product_id", "product_name", "category", "sub_category"], as_index=False)
        .agg(
            total_sales=("sales", "sum"),
            total_profit=("profit", "sum"),
            units_sold=("quantity", "sum"),
            avg_discount=("discount", "mean"),
        )
    )
    prod_summary["profit_margin"] = prod_summary["total_profit"] / prod_summary["total_sales"]

    top_15 = prod_summary.sort_values("total_profit", ascending=False).head(15).reset_index(drop=True)

    ws.cell(row=4, column=1, value="TOP 15 PROFITABLE MERCHANDISE STARS").font = FONT_SECTION
    headers = ["SKU / Product ID", "Product Name", "Category", "Sub-Category", "Units", "Total Revenue", "Net Profit", "Margin %"]
    for j, h in enumerate(headers, start=1):
        c = ws.cell(row=5, column=j, value=h)
        c.font = FONT_HEADER
        c.fill = FILL_HEADER
        c.alignment = ALIGN_CENTER
        c.border = BORDER_BOX

    for i, row in top_15.iterrows():
        r = 6 + i
        ws.cell(row=r, column=1, value=row["product_id"]).alignment = ALIGN_LEFT
        ws.cell(row=r, column=2, value=str(row["product_name"])[:45]).alignment = ALIGN_LEFT
        ws.cell(row=r, column=3, value=row["category"]).alignment = ALIGN_LEFT
        ws.cell(row=r, column=4, value=row["sub_category"]).alignment = ALIGN_LEFT
        ws.cell(row=r, column=5, value=int(row["units_sold"])).number_format = "#,##0"
        ws.cell(row=r, column=6, value=float(row["total_sales"])).number_format = "$#,##0.00"
        
        cp = ws.cell(row=r, column=7, value=float(row["total_profit"]))
        cp.number_format = "$#,##0.00"
        cp.fill = FILL_PROFIT_POS

        cm = ws.cell(row=r, column=8, value=float(row["profit_margin"]))
        cm.number_format = "0.00%"
        cm.fill = FILL_PROFIT_POS

        for col_j in range(1, 9):
            ws.cell(row=r, column=col_j).border = BORDER_BOX
            ws.cell(row=r, column=col_j).font = FONT_REGULAR

    # Bottom Loss-Making Products / Sales Traps
    start_r = 23
    ws.cell(row=start_r, column=1, value="PRODUCT 'SALES TRAPS' (High Sales >= $2,500 but Negative Profit)").font = FONT_SECTION
    traps = calculate_sales_traps(df, min_sales=2500.0)

    for j, h in enumerate(headers, start=1):
        c = ws.cell(row=start_r + 1, column=j, value=h)
        c.font = FONT_HEADER
        c.fill = FILL_HEADER
        c.alignment = ALIGN_CENTER
        c.border = BORDER_BOX

    for i, row in traps.iterrows():
        r = start_r + 2 + i
        ws.cell(row=r, column=1, value=row["product_id"]).alignment = ALIGN_LEFT
        ws.cell(row=r, column=2, value=str(row["product_name"])[:45]).alignment = ALIGN_LEFT
        ws.cell(row=r, column=3, value=row["category"]).alignment = ALIGN_LEFT
        ws.cell(row=r, column=4, value=row["sub_category"]).alignment = ALIGN_LEFT
        ws.cell(row=r, column=5, value=int(row["units_sold"])).number_format = "#,##0"
        ws.cell(row=r, column=6, value=float(row["total_sales"])).number_format = "$#,##0.00"

        cp = ws.cell(row=r, column=7, value=float(row["total_profit"]))
        cp.number_format = "$#,##0.00"
        cp.fill = FILL_PROFIT_NEG

        cm = ws.cell(row=r, column=8, value=float(row["profit_margin_pct"]) / 100.0)
        cm.number_format = "0.00%"
        cm.fill = FILL_PROFIT_NEG

        for col_j in range(1, 9):
            ws.cell(row=r, column=col_j).border = BORDER_BOX
            ws.cell(row=r, column=col_j).font = FONT_REGULAR

    ws.freeze_panes = "A6"
    auto_fit_columns(ws)


def create_regional_analysis_sheet(wb: openpyxl.Workbook, df: pd.DataFrame):
    """Build Sheet 5: Regional Analysis with State rankings."""
    ws = wb.create_sheet(title="Regional Analysis")
    add_sheet_banner(ws, "GEOGRAPHIC & REGIONAL PROFITABILITY PERFORMANCE", "Macro-region comparison and state-level profit contribution audit", max_col=8)

    reg_df = calculate_regional_summary(df)

    ws.cell(row=4, column=1, value="MACRO-REGIONAL PERFORMANCE SUMMARY").font = FONT_SECTION
    headers = ["Region", "Orders", "Units Sold", "Total Revenue", "Net Profit", "Profit Margin", "Share of Profit", "Avg Discount"]
    for j, h in enumerate(headers, start=1):
        c = ws.cell(row=5, column=j, value=h)
        c.font = FONT_HEADER
        c.fill = FILL_HEADER
        c.alignment = ALIGN_CENTER
        c.border = BORDER_BOX

    for i, row in reg_df.iterrows():
        r = 6 + i
        ws.cell(row=r, column=1, value=row["region"]).alignment = ALIGN_CENTER
        ws.cell(row=r, column=2, value=int(row["total_orders"])).number_format = "#,##0"
        ws.cell(row=r, column=3, value=int(row["units_sold"])).number_format = "#,##0"
        ws.cell(row=r, column=4, value=float(row["total_sales"])).number_format = "$#,##0.00"

        cp = ws.cell(row=r, column=5, value=float(row["total_profit"]))
        cp.number_format = "$#,##0.00"
        cp.fill = FILL_PROFIT_POS if row["total_profit"] >= 0 else FILL_PROFIT_NEG

        cm = ws.cell(row=r, column=6, value=float(row["profit_margin_pct"]) / 100.0)
        cm.number_format = "0.00%"
        cm.fill = FILL_PROFIT_POS if row["profit_margin_pct"] >= 0 else FILL_PROFIT_NEG

        ws.cell(row=r, column=7, value=float(row["profit_share_pct"]) / 100.0).number_format = "0.00%"
        ws.cell(row=r, column=8, value=float(row["avg_discount_pct"]) / 100.0).number_format = "0.0%"

        for col_j in range(1, 9):
            ws.cell(row=r, column=col_j).border = BORDER_BOX
            ws.cell(row=r, column=col_j).font = FONT_REGULAR

    # State Performance
    state_summary = (
        df.groupby("state", as_index=False)
        .agg(
            total_orders=("order_id", "nunique"),
            total_sales=("sales", "sum"),
            total_profit=("profit", "sum"),
            avg_discount=("discount", "mean"),
        )
    )
    state_summary["margin"] = state_summary["total_profit"] / state_summary["total_sales"]

    # Top 5 States
    start_r = 13
    ws.cell(row=start_r, column=1, value="TOP 5 MOST PROFITABLE STATES").font = FONT_SECTION
    top_states = state_summary.sort_values("total_profit", ascending=False).head(5).reset_index(drop=True)

    headers_st = ["State", "Orders", "Total Revenue", "Net Profit", "Profit Margin", "Avg Discount"]
    for j, h in enumerate(headers_st, start=1):
        c = ws.cell(row=start_r + 1, column=j, value=h)
        c.font = FONT_HEADER
        c.fill = FILL_HEADER
        c.alignment = ALIGN_CENTER
        c.border = BORDER_BOX

    for i, row in top_states.iterrows():
        r = start_r + 2 + i
        ws.cell(row=r, column=1, value=row["state"]).alignment = ALIGN_LEFT
        ws.cell(row=r, column=2, value=int(row["total_orders"])).number_format = "#,##0"
        ws.cell(row=r, column=3, value=float(row["total_sales"])).number_format = "$#,##0.00"
        
        cp = ws.cell(row=r, column=4, value=float(row["total_profit"]))
        cp.number_format = "$#,##0.00"
        cp.fill = FILL_PROFIT_POS

        cm = ws.cell(row=r, column=5, value=float(row["margin"]))
        cm.number_format = "0.00%"
        cm.fill = FILL_PROFIT_POS

        ws.cell(row=r, column=6, value=float(row["avg_discount"])).number_format = "0.0%"

        for col_j in range(1, 7):
            ws.cell(row=r, column=col_j).border = BORDER_BOX
            ws.cell(row=r, column=col_j).font = FONT_REGULAR

    # Bottom 5 States
    start_r2 = 21
    ws.cell(row=start_r2, column=1, value="BOTTOM 5 LOSS-MAKING STATES").font = FONT_SECTION
    bot_states = state_summary.sort_values("total_profit", ascending=True).head(5).reset_index(drop=True)

    for j, h in enumerate(headers_st, start=1):
        c = ws.cell(row=start_r2 + 1, column=j, value=h)
        c.font = FONT_HEADER
        c.fill = FILL_HEADER
        c.alignment = ALIGN_CENTER
        c.border = BORDER_BOX

    for i, row in bot_states.iterrows():
        r = start_r2 + 2 + i
        ws.cell(row=r, column=1, value=row["state"]).alignment = ALIGN_LEFT
        ws.cell(row=r, column=2, value=int(row["total_orders"])).number_format = "#,##0"
        ws.cell(row=r, column=3, value=float(row["total_sales"])).number_format = "$#,##0.00"

        cp = ws.cell(row=r, column=4, value=float(row["total_profit"]))
        cp.number_format = "$#,##0.00"
        cp.fill = FILL_PROFIT_NEG

        cm = ws.cell(row=r, column=5, value=float(row["margin"]))
        cm.number_format = "0.00%"
        cm.fill = FILL_PROFIT_NEG

        ws.cell(row=r, column=6, value=float(row["avg_discount"])).number_format = "0.0%"

        for col_j in range(1, 7):
            ws.cell(row=r, column=col_j).border = BORDER_BOX
            ws.cell(row=r, column=col_j).font = FONT_REGULAR

    ws.freeze_panes = "A6"
    auto_fit_columns(ws)


def create_discount_profitability_sheet(wb: openpyxl.Workbook, df: pd.DataFrame):
    """Build Sheet 6: Discount & Profitability Sensitivity Matrix."""
    ws = wb.create_sheet(title="Discount & Profitability")
    add_sheet_banner(ws, "PROMOTIONAL DISCOUNTING & MARGIN EROSION AUDIT", "Evidence-based analysis revealing catastrophic losses when discounts exceed 20%", max_col=7)

    disc_df = calculate_discount_sensitivity(df)

    headers = [
        "Discount Tier", "Line Item Count", "Total Revenue", "Net Profit",
        "Realized Margin %", "Average Discount", "Loss Line Rate %"
    ]
    for j, h in enumerate(headers, start=1):
        c = ws.cell(row=4, column=j, value=h)
        c.font = FONT_HEADER
        c.fill = FILL_HEADER
        c.alignment = ALIGN_CENTER
        c.border = BORDER_BOX

    for i, row in disc_df.iterrows():
        r = 5 + i
        ws.cell(row=r, column=1, value=row["discount_tier"]).alignment = ALIGN_LEFT
        ws.cell(row=r, column=2, value=int(row["transaction_count"])).number_format = "#,##0"
        ws.cell(row=r, column=3, value=float(row["total_sales"])).number_format = "$#,##0.00"

        cp = ws.cell(row=r, column=4, value=float(row["total_profit"]))
        cp.number_format = "$#,##0.00"
        cp.fill = FILL_PROFIT_POS if row["total_profit"] >= 0 else FILL_PROFIT_NEG

        cm = ws.cell(row=r, column=5, value=float(row["profit_margin_pct"]) / 100.0)
        cm.number_format = "0.00%"
        cm.fill = FILL_PROFIT_POS if row["profit_margin_pct"] >= 0 else FILL_PROFIT_NEG

        ws.cell(row=r, column=6, value=float(row["avg_discount_pct"]) / 100.0).number_format = "0.0%"
        ws.cell(row=r, column=7, value=float(row["loss_rate_pct"]) / 100.0).number_format = "0.00%"

        for col_j in range(1, 8):
            ws.cell(row=r, column=col_j).border = BORDER_BOX
            ws.cell(row=r, column=col_j).font = FONT_REGULAR

    # Policy Recommendation Note
    note_r = 12
    ws.cell(row=note_r, column=1, value="POLICY RECOMMENDATION: HARD DISCOUNT CEILING AT 20%").font = FONT_SECTION
    bullets = [
        "• Orders with 0% discount generate healthy ~30% profit margins with near-zero loss transactions.",
        "• Modest discounts of 10-20% still yield positive returns (+13% to +20% margins).",
        "• Discounts > 20% experience catastrophic margin collapse (-14% to -83% negative margin), with over 80% of lines unprofitable.",
        "• Strategic Mandate: Eliminate discretionary sales discounts above 20% unless authorized by executive management with offset bundling.",
    ]
    for idx, b in enumerate(bullets, start=note_r + 1):
        c = ws.cell(row=idx, column=1, value=b)
        c.font = FONT_REGULAR
        ws.merge_cells(start_row=idx, start_column=1, end_row=idx, end_column=7)

    ws.freeze_panes = "A5"
    auto_fit_columns(ws)


def create_customer_analysis_sheet(wb: openpyxl.Workbook, df: pd.DataFrame):
    """Build Sheet 7: Customer Segment & RFM Profiling."""
    ws = wb.create_sheet(title="Customer Analysis")
    add_sheet_banner(ws, "CUSTOMER SEGMENTATION & RFM VALUE CONTRIBUTION", "Market segment benchmarking and top customer lifetime profitability profiles", max_col=8)

    # 1. Segment Overview
    ws.cell(row=4, column=1, value="CUSTOMER MARKET SEGMENTS").font = FONT_SECTION
    seg_summary = (
        df.groupby("segment", as_index=False)
        .agg(
            customer_count=("customer_id", "nunique"),
            total_orders=("order_id", "nunique"),
            total_sales=("sales", "sum"),
            total_profit=("profit", "sum"),
            units_sold=("quantity", "sum"),
        )
    )
    seg_summary["profit_margin"] = seg_summary["total_profit"] / seg_summary["total_sales"]
    seg_summary["aov"] = seg_summary["total_sales"] / seg_summary["total_orders"]

    headers_seg = ["Segment", "Customers", "Orders", "Units", "Total Revenue", "Net Profit", "Margin %", "AOV"]
    for j, h in enumerate(headers_seg, start=1):
        c = ws.cell(row=5, column=j, value=h)
        c.font = FONT_HEADER
        c.fill = FILL_HEADER
        c.alignment = ALIGN_CENTER
        c.border = BORDER_BOX

    for i, row in seg_summary.iterrows():
        r = 6 + i
        ws.cell(row=r, column=1, value=row["segment"]).alignment = ALIGN_LEFT
        ws.cell(row=r, column=2, value=int(row["customer_count"])).number_format = "#,##0"
        ws.cell(row=r, column=3, value=int(row["total_orders"])).number_format = "#,##0"
        ws.cell(row=r, column=4, value=int(row["units_sold"])).number_format = "#,##0"
        ws.cell(row=r, column=5, value=float(row["total_sales"])).number_format = "$#,##0.00"

        cp = ws.cell(row=r, column=6, value=float(row["total_profit"]))
        cp.number_format = "$#,##0.00"
        cp.fill = FILL_PROFIT_POS

        cm = ws.cell(row=r, column=7, value=float(row["profit_margin"]))
        cm.number_format = "0.00%"
        cm.fill = FILL_PROFIT_POS

        ws.cell(row=r, column=8, value=float(row["aov"])).number_format = "$#,##0.00"

        for col_j in range(1, 9):
            ws.cell(row=r, column=col_j).border = BORDER_BOX
            ws.cell(row=r, column=col_j).font = FONT_REGULAR

    # 2. Top 15 Customer Accounts by Lifetime Profit
    rfm = calculate_rfm_metrics(df).sort_values("total_profit", ascending=False).head(15).reset_index(drop=True)
    start_r = 12
    ws.cell(row=start_r, column=1, value="TOP 15 HIGH-VALUE CLIENT ACCOUNTS BY NET PROFIT").font = FONT_SECTION

    headers_rfm = ["Customer ID", "Customer Name", "Segment", "Order Frequency", "Total Spend", "Net Profit Contribution", "Margin %", "AOV"]
    for j, h in enumerate(headers_rfm, start=1):
        c = ws.cell(row=start_r + 1, column=j, value=h)
        c.font = FONT_HEADER
        c.fill = FILL_HEADER
        c.alignment = ALIGN_CENTER
        c.border = BORDER_BOX

    for i, row in rfm.iterrows():
        r = start_r + 2 + i
        ws.cell(row=r, column=1, value=row["customer_id"]).alignment = ALIGN_CENTER
        ws.cell(row=r, column=2, value=row["customer_name"]).alignment = ALIGN_LEFT
        ws.cell(row=r, column=3, value=row["segment"]).alignment = ALIGN_LEFT
        ws.cell(row=r, column=4, value=int(row["order_frequency"])).number_format = "#,##0"
        ws.cell(row=r, column=5, value=float(row["total_spend"])).number_format = "$#,##0.00"

        cp = ws.cell(row=r, column=6, value=float(row["total_profit"]))
        cp.number_format = "$#,##0.00"
        cp.fill = FILL_PROFIT_POS

        cm = ws.cell(row=r, column=7, value=float(row["profit_margin_pct"]) / 100.0)
        cm.number_format = "0.00%"
        cm.fill = FILL_PROFIT_POS

        ws.cell(row=r, column=8, value=float(row["average_order_value"])).number_format = "$#,##0.00"

        for col_j in range(1, 9):
            ws.cell(row=r, column=col_j).border = BORDER_BOX
            ws.cell(row=r, column=col_j).font = FONT_REGULAR

    ws.freeze_panes = "A6"
    auto_fit_columns(ws)


def create_cleaned_data_sheet(wb: openpyxl.Workbook, df: pd.DataFrame):
    """Build Sheet 8: Cleaned Data Transaction Extract (first 1,000 rows with headers and filters)."""
    ws = wb.create_sheet(title="Cleaned Data")
    add_sheet_banner(ws, "STANDARDIZED & CLEANED TRANSACTION REPOSITORY", "First 1,000 verified order records (Complete 9,994-row dataset available in SQLite database)", max_col=14)

    display_cols = [
        "order_id", "order_date", "ship_date", "ship_mode", "customer_name",
        "segment", "city", "state", "region", "category", "sub_category",
        "sales", "quantity", "discount", "profit"
    ]
    sub_df = df[display_cols].head(1000).copy()

    headers = [c.replace("_", " ").title() for c in display_cols]
    for j, h in enumerate(headers, start=1):
        c = ws.cell(row=4, column=j, value=h)
        c.font = FONT_HEADER
        c.fill = FILL_HEADER
        c.alignment = ALIGN_CENTER
        c.border = BORDER_BOX

    for i, row in sub_df.iterrows():
        r = 5 + i
        ws.cell(row=r, column=1, value=str(row["order_id"])).alignment = ALIGN_CENTER
        ws.cell(row=r, column=2, value=str(row["order_date"])[:10]).alignment = ALIGN_CENTER
        ws.cell(row=r, column=3, value=str(row["ship_date"])[:10]).alignment = ALIGN_CENTER
        ws.cell(row=r, column=4, value=str(row["ship_mode"])).alignment = ALIGN_LEFT
        ws.cell(row=r, column=5, value=str(row["customer_name"])).alignment = ALIGN_LEFT
        ws.cell(row=r, column=6, value=str(row["segment"])).alignment = ALIGN_LEFT
        ws.cell(row=r, column=7, value=str(row["city"])).alignment = ALIGN_LEFT
        ws.cell(row=r, column=8, value=str(row["state"])).alignment = ALIGN_LEFT
        ws.cell(row=r, column=9, value=str(row["region"])).alignment = ALIGN_LEFT
        ws.cell(row=r, column=10, value=str(row["category"])).alignment = ALIGN_LEFT
        ws.cell(row=r, column=11, value=str(row["sub_category"])).alignment = ALIGN_LEFT
        ws.cell(row=r, column=12, value=float(row["sales"])).number_format = "$#,##0.00"
        ws.cell(row=r, column=13, value=int(row["quantity"])).number_format = "#,##0"
        ws.cell(row=r, column=14, value=float(row["discount"])).number_format = "0.0%"
        
        cp = ws.cell(row=r, column=15, value=float(row["profit"]))
        cp.number_format = "$#,##0.00"
        cp.fill = FILL_PROFIT_POS if row["profit"] >= 0 else FILL_PROFIT_NEG

        for col_j in range(1, 16):
            ws.cell(row=r, column=col_j).border = BORDER_BOX
            ws.cell(row=r, column=col_j).font = FONT_REGULAR

    ws.freeze_panes = "A5"
    ws.auto_filter.ref = f"A4:O{len(sub_df)+4}"
    auto_fit_columns(ws)


def create_data_dictionary_sheet(wb: openpyxl.Workbook):
    """Build Sheet 9: Data Dictionary explaining schema and business constraints."""
    ws = wb.create_sheet(title="Data Dictionary")
    add_sheet_banner(ws, "DATA DICTIONARY & FIELD SPECIFICATIONS", "Comprehensive documentation of columns, data types, business semantics, and quality rules", max_col=6)

    headers = ["Field Name", "Data Type", "Standardized Format", "Description & Business Meaning", "Allowed Domain / Values", "Validation Rule"]
    for j, h in enumerate(headers, start=1):
        c = ws.cell(row=4, column=j, value=h)
        c.font = FONT_HEADER
        c.fill = FILL_HEADER
        c.alignment = ALIGN_CENTER
        c.border = BORDER_BOX

    dict_rows = [
        ("row_id", "INTEGER", "Sequential #", "Unique transactional row identifier", "1 to 9994", "Primary Key, non-null, > 0"),
        ("order_id", "VARCHAR(25)", "XX-YYYY-######", "Unique customer transaction code", "Alphanumeric", "Non-null format validation"),
        ("order_date", "DATE", "YYYY-MM-DD", "Date on which the purchase was authorized", "2014-01-01 to 2017-12-31", "Valid date format"),
        ("ship_date", "DATE", "YYYY-MM-DD", "Date on which logistics fulfilled the order", "2014-01-05 to 2018-01-05", "Must be >= order_date"),
        ("ship_mode", "VARCHAR(25)", "Title Case", "Logistics transit tier", "Standard, Second, First, Same Day", "Allowed categorical enum"),
        ("customer_id", "VARCHAR(20)", "XX-#####", "Unique customer identifier", "Alphanumeric", "Non-null"),
        ("customer_name", "VARCHAR(100)", "Full Name", "Customer legal or business name", "Text string", "Non-null"),
        ("segment", "VARCHAR(25)", "Category", "Customer market grouping", "Consumer, Corporate, Home Office", "Allowed categorical enum"),
        ("country", "VARCHAR(50)", "Country Name", "Sovereign jurisdiction of delivery", "United States", "Non-null string"),
        ("city", "VARCHAR(50)", "City Name", "Municipality of order destination", "US Cities", "Non-null string"),
        ("state", "VARCHAR(50)", "State Name", "US State of order destination", "49 US States + DC", "Valid US state name"),
        ("postal_code", "VARCHAR(10)", "5-digit string", "US Postal Zip Code zero-padded", "01001 to 99950", "Padded string preservation"),
        ("region", "VARCHAR(20)", "Macro Region", "Geographic corporate territory", "East, West, Central, South", "Allowed categorical enum"),
        ("product_id", "VARCHAR(25)", "XX-XX-########", "Unique SKU merchandise code", "Alphanumeric", "Non-null SKU"),
        ("category", "VARCHAR(30)", "Department", "Primary merchandise department", "Furniture, Office Supplies, Technology", "Allowed categorical enum"),
        ("sub_category", "VARCHAR(30)", "Sub-Department", "Granular merchandise category", "17 discrete subcategories", "Non-null category"),
        ("product_name", "VARCHAR(255)", "Commercial Name", "Full catalog name of the item", "Text string", "Non-null description"),
        ("sales", "NUMERIC(10,2)", "$#,##0.00", "Gross realized revenue after discount", "Positive float", "Must be > $0.00"),
        ("quantity", "INTEGER", "#,##0", "Number of merchandise units purchased", "Integer >= 1", "Positive integer"),
        ("discount", "NUMERIC(4,2)", "0.0%", "Promotional price concession percentage", "0.00 to 0.80", "Between 0.00 and 1.00"),
        ("profit", "NUMERIC(10,2)", "$#,##0.00", "Net bottom-line contribution profit/loss", "Real number", "Finite float, reconciles with margin"),
        ("profit_margin", "NUMERIC(6,4)", "0.00%", "Profit divided by Sales ratio", "-100% to +100%", "Safe division, rounded to 4 decimals"),
        ("shipping_duration_days", "INTEGER", "# days", "Transit elapsed latency", "0 to 7 days", "ship_date - order_date >= 0"),
        ("discount_tier", "VARCHAR(25)", "Tier Name", "Categorical discount bracket", "0%, 1-10%, 11-20%, 21-40%, >40%", "Explicit boundary binning"),
    ]

    for i, row in enumerate(dict_rows):
        r = 5 + i
        for col_j, val in enumerate(row, start=1):
            c = ws.cell(row=r, column=col_j, value=val)
            c.border = BORDER_BOX
            c.font = FONT_REGULAR
            if col_j in [1, 2, 3]:
                c.alignment = ALIGN_CENTER
            else:
                c.alignment = ALIGN_LEFT

    ws.freeze_panes = "A5"
    auto_fit_columns(ws)


def create_methodology_sheet(wb: openpyxl.Workbook):
    """Build Sheet 10: Methodology & KPI Definitions."""
    ws = wb.create_sheet(title="Methodology & KPI Definitions")
    add_sheet_banner(ws, "ANALYTICS METHODOLOGY & KPI DEFINITIONS", "Technical formulation, calculation formulas, and spreadsheet engine reconciliation rules", max_col=6)

    headers = ["Metric / KPI Name", "Formula / Mathematical Definition", "Business Purpose", "Edge Case & Denominator Rule", "Target Benchmark"]
    for j, h in enumerate(headers, start=1):
        c = ws.cell(row=4, column=j, value=h)
        c.font = FONT_HEADER
        c.fill = FILL_HEADER
        c.alignment = ALIGN_CENTER
        c.border = BORDER_BOX

    method_rows = [
        ("Total Sales Revenue", "SUM(sales)", "Measures enterprise top-line commercial turnover", "Sum of all non-rejected transaction lines", "Steady growth YoY"),
        ("Net Contribution Profit", "SUM(profit)", "Measures net financial return after cost of goods and discounts", "Can be negative for loss-making items", "> 12.0% enterprise margin"),
        ("Overall Profit Margin", "SUM(profit) / SUM(sales)", "Core efficiency ratio; indicates dollar return per revenue dollar", "Denominated by enterprise total sales, not mean of line margins", "> 15.0% target"),
        ("Average Order Value (AOV)", "Total Sales / COUNT(DISTINCT order_id)", "Measures average basket expenditure per checkout", "Denominated by unique orders, NOT line items", "> $450.00"),
        ("Loss Transaction Rate %", "COUNT(lines WHERE profit < 0) / COUNT(*)", "Quantifies prevalence of red-ink line items", "Line-level evaluation of margin health", "< 15.0%"),
        ("MoM Sales Growth %", "(Sales_t - Sales_t-1) / Sales_t-1 * 100", "Tracks monthly revenue velocity and trajectory", "Null for period 1; handles seasonality", "Positive trajectory"),
        ("Customer RFM Score", "Recency (days), Frequency (orders), Monetary ($)", "Customer segmentation and lifetime value modeling", "Recency anchored to max dataset date (2017-12-30)", "Identifies VIPs"),
        ("Unit Cost of Goods Sold", "(Sales - Profit) / Quantity", "Implied per-unit production/acquisition cost", "Derived field to analyze supplier margins", "Benchmarked per SKU"),
    ]

    for i, row in enumerate(method_rows):
        r = 5 + i
        for col_j, val in enumerate(row, start=1):
            c = ws.cell(row=r, column=col_j, value=val)
            c.border = BORDER_BOX
            c.font = FONT_REGULAR
            if col_j == 1:
                c.font = FONT_BOLD
                c.alignment = ALIGN_LEFT
            elif col_j in [2, 5]:
                c.alignment = ALIGN_CENTER
            else:
                c.alignment = ALIGN_LEFT

    ws.freeze_panes = "A5"
    auto_fit_columns(ws)


def export_full_excel_workbook(df: pd.DataFrame, output_path: Path = EXCEL_OUTPUT_FILE) -> Path:
    """Generate the complete 10-sheet corporate Excel workbook."""
    logger.info(f"Generating professional 10-sheet Excel workbook at: {output_path}")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    wb = openpyxl.Workbook()
    # Remove default blank sheet
    default_sheet = wb.active

    # Create the 10 required sheets in exact order
    create_executive_dashboard(wb, df)
    create_monthly_trends_sheet(wb, df)
    create_category_analysis_sheet(wb, df)
    create_product_analysis_sheet(wb, df)
    create_regional_analysis_sheet(wb, df)
    create_discount_profitability_sheet(wb, df)
    create_customer_analysis_sheet(wb, df)
    create_cleaned_data_sheet(wb, df)
    create_data_dictionary_sheet(wb)
    create_methodology_sheet(wb)

    wb.remove(default_sheet)
    wb.save(output_path)
    logger.info(f"Excel workbook exported successfully to: {output_path}")
    return output_path
