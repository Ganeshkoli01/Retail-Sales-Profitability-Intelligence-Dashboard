"""Visualizations generator for Retail Sales Analytics.

Produces publication-quality charts using Matplotlib and Seaborn, saved to screenshots/
for inclusion in reports, GitHub README, and interview presentations.
"""

import logging
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import pandas as pd
import seaborn as sns

from src.config import SCREENSHOTS_DIR

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Aesthetic styling
plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
plt.rcParams["font.sans-serif"] = ["Segoe UI", "DejaVu Sans", "Arial"]
plt.rcParams["axes.edgecolor"] = "#CBD5E1"
plt.rcParams["axes.linewidth"] = 0.8


def plot_monthly_trend(monthly_df: pd.DataFrame, output_dir: Path = SCREENSHOTS_DIR) -> Path:
    """Plot 4-year monthly revenue and profit trend with margin trajectory."""
    output_dir.mkdir(parents=True, exist_ok=True)
    out_file = output_dir / "monthly_sales_profit_trend.png"

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8), sharex=True, gridspec_kw={"height_ratios": [2.5, 1.2]})

    x = np.arange(len(monthly_df))
    labels = monthly_df["order_year_month"].tolist()

    # Upper subplot: Revenue and Profit Bars/Lines
    ax1.plot(x, monthly_df["total_sales"] / 1000.0, marker="o", color="#1E3A8A", linewidth=2.2, label="Monthly Sales ($K)")
    ax1.plot(x, monthly_df["total_profit"] / 1000.0, marker="s", color="#059669", linewidth=2.0, label="Monthly Profit ($K)")
    ax1.axhline(0, color="#DC2626", linestyle="--", linewidth=1.0, alpha=0.7)
    ax1.set_title("Enterprise Monthly Revenue and Profit Trend (2014 - 2017)", fontsize=14, weight="bold", pad=12)
    ax1.set_ylabel("Amount ($ Thousands)", fontsize=11, weight="bold")
    ax1.yaxis.set_major_formatter(ticker.StrMethodFormatter("${x:,.0f}K"))
    ax1.legend(loc="upper left", frameon=True)
    ax1.grid(True, linestyle=":", alpha=0.6)

    # Lower subplot: Profit Margin %
    colors = ["#059669" if m >= 0 else "#DC2626" for m in monthly_df["profit_margin_pct"]]
    ax2.bar(x, monthly_df["profit_margin_pct"], color=colors, width=0.6, alpha=0.85)
    ax2.axhline(0, color="#475569", linewidth=0.8)
    ax2.set_title("Realized Monthly Profit Margin (%)", fontsize=11, weight="bold", pad=8)
    ax2.set_ylabel("Margin (%)", fontsize=10, weight="bold")
    ax2.yaxis.set_major_formatter(ticker.StrMethodFormatter("{x:.0f}%"))
    ax2.set_xticks(x[::2])
    ax2.set_xticklabels(labels[::2], rotation=45, ha="right", fontsize=9)
    ax2.grid(True, linestyle=":", alpha=0.6)

    plt.tight_layout()
    plt.savefig(out_file, dpi=300, bbox_inches="tight")
    plt.close()
    logger.info(f"Saved: {out_file}")
    return out_file


def plot_category_profitability(cat_df: pd.DataFrame, output_dir: Path = SCREENSHOTS_DIR) -> Path:
    """Plot subcategory profitability and sales comparison highlighting loss-makers."""
    output_dir.mkdir(parents=True, exist_ok=True)
    out_file = output_dir / "category_subcategory_performance.png"

    sorted_df = cat_df.sort_values("total_profit", ascending=True).copy()

    fig, ax = plt.subplots(figsize=(12, 8))
    colors = ["#DC2626" if p < 0 else "#0D9488" for p in sorted_df["total_profit"]]

    bars = ax.barh(sorted_df["sub_category"], sorted_df["total_profit"] / 1000.0, color=colors, height=0.65)
    ax.axvline(0, color="#1E293B", linewidth=1.0)

    # Annotate labels
    for bar in bars:
        width = bar.get_width()
        ha = "left" if width >= 0 else "right"
        offset = 0.5 if width >= 0 else -0.5
        ax.text(
            width + offset,
            bar.get_y() + bar.get_height() / 2,
            f"${width:,.1f}K",
            va="center",
            ha=ha,
            fontsize=9,
            weight="bold",
            color="#1E293B",
        )

    ax.set_title("Subcategory Net Profit Contribution ($K) - Identifying Value Destroyers", fontsize=14, weight="bold", pad=14)
    ax.set_xlabel("Net Profit ($ Thousands)", fontsize=11, weight="bold")
    ax.xaxis.set_major_formatter(ticker.StrMethodFormatter("${x:,.0f}K"))
    ax.grid(True, axis="x", linestyle=":", alpha=0.6)

    plt.tight_layout()
    plt.savefig(out_file, dpi=300, bbox_inches="tight")
    plt.close()
    logger.info(f"Saved: {out_file}")
    return out_file


def plot_discount_impact(disc_df: pd.DataFrame, output_dir: Path = SCREENSHOTS_DIR) -> Path:
    """Plot relationship between promotional discount tiers, profit margins, and loss rates."""
    output_dir.mkdir(parents=True, exist_ok=True)
    out_file = output_dir / "discount_profit_margin_erosion.png"

    fig, ax1 = plt.subplots(figsize=(10, 6))

    x = np.arange(len(disc_df))
    tiers = disc_df["discount_tier"].tolist()

    # Bar chart: Realized Profit Margin %
    bar_colors = ["#059669" if m > 0 else "#DC2626" for m in disc_df["profit_margin_pct"]]
    bars = ax1.bar(x, disc_df["profit_margin_pct"], color=bar_colors, width=0.45, label="Profit Margin %", alpha=0.85)

    ax1.set_ylabel("Realized Profit Margin (%)", fontsize=11, weight="bold", color="#1E293B")
    ax1.set_xticks(x)
    ax1.set_xticklabels(tiers, rotation=15, ha="right", fontsize=9, weight="bold")
    ax1.yaxis.set_major_formatter(ticker.StrMethodFormatter("{x:.0f}%"))
    ax1.axhline(0, color="#475569", linewidth=0.8)

    # Line chart on secondary axis: Loss Transaction Rate %
    ax2 = ax1.twinx()
    ax2.plot(x, disc_df["loss_rate_pct"], color="#E11D48", marker="o", linewidth=2.5, markersize=8, label="Loss Order Rate %")
    ax2.set_ylabel("Loss-Making Order Lines (%)", fontsize=11, weight="bold", color="#E11D48")
    ax2.yaxis.set_major_formatter(ticker.StrMethodFormatter("{x:.0f}%"))
    ax2.grid(False)

    for bar in bars:
        h = bar.get_height()
        va = "bottom" if h >= 0 else "top"
        ax1.text(
            bar.get_x() + bar.get_width() / 2,
            h + (1.0 if h >= 0 else -3.0),
            f"{h:.1f}%",
            ha="center",
            va=va,
            fontsize=9,
            weight="bold",
        )

    plt.title("Discount Margin Erosion: Steep Losses Occur When Discounts Exceed 20%", fontsize=13, weight="bold", pad=14)
    plt.tight_layout()
    plt.savefig(out_file, dpi=300, bbox_inches="tight")
    plt.close()
    logger.info(f"Saved: {out_file}")
    return out_file


def plot_regional_performance(reg_df: pd.DataFrame, output_dir: Path = SCREENSHOTS_DIR) -> Path:
    """Plot regional sales, profit, and margin performance."""
    output_dir.mkdir(parents=True, exist_ok=True)
    out_file = output_dir / "regional_profitability_summary.png"

    fig, ax = plt.subplots(figsize=(9, 5))
    x = np.arange(len(reg_df))
    width = 0.35

    ax.bar(x - width/2, reg_df["total_sales"] / 1000.0, width, label="Total Sales ($K)", color="#2563EB", alpha=0.9)
    ax.bar(x + width/2, reg_df["total_profit"] / 1000.0, width, label="Total Profit ($K)", color="#059669", alpha=0.9)

    ax.set_title("Regional Sales vs Profit Performance", fontsize=13, weight="bold", pad=12)
    ax.set_xticks(x)
    ax.set_xticklabels(reg_df["region"], fontsize=10, weight="bold")
    ax.yaxis.set_major_formatter(ticker.StrMethodFormatter("${x:,.0f}K"))
    ax.legend(frameon=True)
    ax.grid(True, linestyle=":", alpha=0.6)

    plt.tight_layout()
    plt.savefig(out_file, dpi=300, bbox_inches="tight")
    plt.close()
    logger.info(f"Saved: {out_file}")
    return out_file


def generate_all_visualizations(
    monthly_df: pd.DataFrame,
    cat_df: pd.DataFrame,
    disc_df: pd.DataFrame,
    reg_df: pd.DataFrame,
    output_dir: Path = SCREENSHOTS_DIR,
) -> None:
    """Generate all presentation charts."""
    logger.info("Generating publication-ready analytics charts...")
    plot_monthly_trend(monthly_df, output_dir)
    plot_category_profitability(cat_df, output_dir)
    plot_discount_impact(disc_df, output_dir)
    plot_regional_performance(reg_df, output_dir)
    logger.info("All visualization assets generated successfully.")
