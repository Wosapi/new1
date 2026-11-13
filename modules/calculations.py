"""
Financial & Sales KPI Calculations Module:
Implements strict business rules:
- Achievement % = (Actual / Target) * 100 (only when Target > 0 and Actual is valid)
- Variance = Actual - Target
- Remaining Target = Target - Actual
- Never calculates Achievement % when Target is 0 or NaN.
- Handles incomplete/future zero months cleanly.
"""

from typing import Dict, Any
import numpy as np
import pandas as pd
from config import MONTHS_ORDER, THRESHOLD_GREEN, THRESHOLD_ORANGE


def compute_metrics(df: pd.DataFrame, target_col: str = "Target", actual_col: str = "Actual") -> pd.DataFrame:
    """Safely append Variance, Remaining Target, Achievement %, and Performance Status."""
    out = df.copy()
    t = out[target_col]
    a = out[actual_col]

    out["Variance"] = np.where(t.notna() & a.notna(), a - t, np.nan)
    out["Remaining_Target"] = np.where(t.notna() & a.notna(), t - a, np.where(t.notna(), t, np.nan))
    out["Achievement_Pct"] = np.where(
        t.notna() & (t > 0) & a.notna(),
        (a / t) * 100.0,
        np.nan,
    )

    conditions = [
        out["Achievement_Pct"].isna(),
        out["Achievement_Pct"] >= THRESHOLD_GREEN,
        out["Achievement_Pct"] >= THRESHOLD_ORANGE,
    ]
    choices = ["na", "achieved", "warning"]
    out["Perf_Code"] = np.select(conditions, choices, default="low")
    return out


def filter_monthly_data(
    monthly_df: pd.DataFrame,
    selected_years: list,
    selected_months: list,
    selected_products: list,
    exclude_future_zeros: bool = True,
) -> pd.DataFrame:
    """Apply interactive sidebar filters and optionally exclude future all-zero months from KPI ratios."""
    df = monthly_df.copy()
    if selected_years:
        df = df[df["Year"].isin(selected_years)]
    if selected_months:
        df = df[df["Month"].isin(selected_months)]
    if selected_products:
        df = df[df["Product"].isin(selected_products)]

    if exclude_future_zeros:
        # Treat all-zero future months (e.g., Apr 2026 & Dec 2026) as unrecorded Actual (NaN) for accurate YTD/Achievement
        df.loc[df["Is_All_Zero_Actual"], "Actual"] = np.nan

    return compute_metrics(df)


def calculate_kpis(filtered_df: pd.DataFrame) -> Dict[str, Any]:
    """Compute top-level Executive KPI Cards from filtered dataset."""
    if filtered_df.empty:
        return {
            "total_target": 0.0,
            "total_actual": 0.0,
            "achievement_pct": np.nan,
            "remaining_target": 0.0,
            "best_month": "—",
            "best_month_val": np.nan,
            "best_product": "—",
            "best_product_val": np.nan,
        }

    # For Achievement % & Remaining Target, align Target on periods where Actual exists if partial year
    valid_actual_mask = filtered_df["Actual"].notna()
    total_target_all = filtered_df["Target"].sum(skipna=True)
    total_actual = filtered_df["Actual"].sum(skipna=True)

    # Active target (for months with recorded actuals) ensures fair YTD achievement %
    active_target = filtered_df.loc[valid_actual_mask, "Target"].sum(skipna=True)
    eval_target = active_target if active_target > 0 else total_target_all

    achievement_pct = (total_actual / eval_target * 100.0) if eval_target > 0 and valid_actual_mask.any() else np.nan
    remaining_target = total_target_all - total_actual

    # Best Performing Month (by Actual sales among valid months)
    month_grp = (
        filtered_df[valid_actual_mask]
        .groupby(["Year", "Month"], as_index=False)
        .agg(Actual=("Actual", "sum"), Target=("Target", "sum"))
    )
    if not month_grp.empty:
        best_m_row = month_grp.loc[month_grp["Actual"].idxmax()]
        best_month = f"{best_m_row['Month']} {int(best_m_row['Year'])}"
        best_month_val = best_m_row["Actual"]
    else:
        best_month = "—"
        best_month_val = np.nan

    # Best Performing Product (by Actual volume)
    prod_grp = (
        filtered_df[valid_actual_mask]
        .groupby("Product", as_index=False)
        .agg(Actual=("Actual", "sum"), Target=("Target", "sum"))
    )
    if not prod_grp.empty:
        best_p_row = prod_grp.loc[prod_grp["Actual"].idxmax()]
        best_product = best_p_row["Product"]
        best_product_val = best_p_row["Actual"]
    else:
        best_product = "—"
        best_product_val = np.nan

    return {
        "total_target": total_target_all,
        "active_target": eval_target,
        "total_actual": total_actual,
        "achievement_pct": achievement_pct,
        "remaining_target": remaining_target,
        "best_month": best_month,
        "best_month_val": best_month_val,
        "best_product": best_product,
        "best_product_val": best_product_val,
    }


def build_summaries(filtered_df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """Generate aggregated Monthly, Annual, Quarterly, Half-Yearly, and Product tables."""
    # 1. Monthly Summary
    monthly_sum = (
        filtered_df.groupby(["Year", "Month_Num", "Month"], as_index=False)
        .agg(
            Target=("Target", lambda s: s.sum(min_count=1)),
            Actual=("Actual", lambda s: s.sum(min_count=1)),
        )
        .sort_values(["Year", "Month_Num"])
    )
    monthly_sum = compute_metrics(monthly_sum)

    # 2. Annual Summary
    annual_sum = (
        filtered_df.groupby(["Year"], as_index=False)
        .agg(
            Target=("Target", lambda s: s.sum(min_count=1)),
            Actual=("Actual", lambda s: s.sum(min_count=1)),
        )
        .sort_values("Year")
    )
    # Compute active target for fair YTD achievement % on partial years
    active_yr_t = (
        filtered_df[filtered_df["Actual"].notna()]
        .groupby(["Year"], as_index=False)["Target"]
        .sum()
        .rename(columns={"Target": "Active_Target"})
    )
    annual_sum = annual_sum.merge(active_yr_t, on="Year", how="left")
    annual_sum = compute_metrics(annual_sum)
    annual_sum["YTD_Achievement_Pct"] = np.where(
        annual_sum["Active_Target"].notna() & (annual_sum["Active_Target"] > 0) & annual_sum["Actual"].notna(),
        (annual_sum["Actual"] / annual_sum["Active_Target"]) * 100.0,
        np.nan,
    )

    # 3. Quarterly Summary
    quarterly_sum = (
        filtered_df.groupby(["Year", "Quarter"], as_index=False)
        .agg(
            Target=("Target", lambda s: s.sum(min_count=1)),
            Actual=("Actual", lambda s: s.sum(min_count=1)),
        )
        .sort_values(["Year", "Quarter"])
    )
    quarterly_sum = compute_metrics(quarterly_sum)

    # 4. Half-Yearly Summary
    half_sum = (
        filtered_df.groupby(["Year", "Half"], as_index=False)
        .agg(
            Target=("Target", lambda s: s.sum(min_count=1)),
            Actual=("Actual", lambda s: s.sum(min_count=1)),
        )
        .sort_values(["Year", "Half"])
    )
    half_sum = compute_metrics(half_sum)

    # 5. Product Performance Summary
    product_sum = (
        filtered_df.groupby(["Product"], as_index=False)
        .agg(
            Target=("Target", lambda s: s.sum(min_count=1)),
            Actual=("Actual", lambda s: s.sum(min_count=1)),
        )
    )
    product_sum = compute_metrics(product_sum)

    return {
        "monthly": monthly_sum,
        "annual": annual_sum,
        "quarterly": quarterly_sum,
        "half_yearly": half_sum,
        "product": product_sum,
    }
