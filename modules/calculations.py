"""
Financial & Sales KPI Calculations Module (V2):
Implements strict independent calculations for Monthly Aggregated vs Annual Excel Targets.
"""

from typing import Dict, Any
import numpy as np
import pandas as pd
from config import PRODUCTS, THRESHOLD_GREEN, THRESHOLD_ORANGE


def compute_metrics(df: pd.DataFrame, target_col: str = "Target", actual_col: str = "Actual") -> pd.DataFrame:
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
    df = monthly_df.copy()
    if selected_years:
        df = df[df["Year"].isin(selected_years)]
    if selected_months:
        df = df[df["Month"].isin(selected_months)]
    if selected_products:
        df = df[df["Product"].isin(selected_products)]

    if exclude_future_zeros:
        df.loc[df["Is_All_Zero_Actual"], "Actual"] = np.nan

    return compute_metrics(df)


def calculate_dual_kpis(filtered_df: pd.DataFrame, annual_excel_df: pd.DataFrame, selected_years: list) -> Dict[str, Any]:
    """
    Computes dual KPI metrics separating Monthly Aggregated Target from Annual Excel Target.
    """
    if filtered_df.empty:
        return {
            "monthly_target_sum": 0.0,
            "annual_excel_target": 0.0,
            "total_actual": 0.0,
            "monthly_achievement_pct": np.nan,
            "annual_achievement_pct": np.nan,
            "remaining_target": 0.0,
            "best_month": "—",
            "best_product": "—",
        }

    monthly_target_sum = filtered_df["Target"].sum(skipna=True)
    total_actual = filtered_df["Actual"].sum(skipna=True)

    # Retrieve Annual Excel Target for selected years if available
    if not annual_excel_df.empty and selected_years:
        sub_annual = annual_excel_df[annual_excel_df["Year"].isin(selected_years)]
        if not sub_annual.empty and "Excel_Value" in sub_annual.columns:
            # Filter for Total product row in annual summary
            tot_rows = sub_annual[sub_annual["Product"] == "Total"]
            if not tot_rows.empty:
                annual_excel_target = tot_rows["Excel_Value"].sum(skipna=True)
            else:
                annual_excel_target = sub_annual["Excel_Value"].sum(skipna=True) / max(len(PRODUCTS), 1)
        else:
            annual_excel_target = monthly_target_sum
    else:
        annual_excel_target = monthly_target_sum

    monthly_achievement_pct = (total_actual / monthly_target_sum * 100.0) if monthly_target_sum > 0 else np.nan
    annual_achievement_pct = (total_actual / annual_excel_target * 100.0) if annual_excel_target > 0 else np.nan
    remaining_target = monthly_target_sum - total_actual

    valid_mask = filtered_df["Actual"].notna()
    month_grp = filtered_df[valid_mask].groupby(["Year", "Month"], as_index=False).agg(Actual=("Actual", "sum"))
    best_month = f"{month_grp.loc[month_grp['Actual'].idxmax()]['Month']} {int(month_grp.loc[month_grp['Actual'].idxmax()]['Year'])}" if not month_grp.empty else "—"

    prod_grp = filtered_df[valid_mask].groupby("Product", as_index=False).agg(Actual=("Actual", "sum"))
    best_product = prod_grp.loc[prod_grp["Actual"].idxmax()]["Product"] if not prod_grp.empty else "—"

    return {
        "monthly_target_sum": monthly_target_sum,
        "annual_excel_target": annual_excel_target,
        "total_actual": total_actual,
        "monthly_achievement_pct": monthly_achievement_pct,
        "annual_achievement_pct": annual_achievement_pct,
        "remaining_target": remaining_target,
        "best_month": best_month,
        "best_product": best_product,
    }


def build_summaries(filtered_df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    monthly_sum = (
        filtered_df.groupby(["Year", "Month_Num", "Month"], as_index=False)
        .agg(Target=("Target", lambda s: s.sum(min_count=1)), Actual=("Actual", lambda s: s.sum(min_count=1)))
        .sort_values(["Year", "Month_Num"])
    )
    monthly_sum = compute_metrics(monthly_sum)

    annual_sum = (
        filtered_df.groupby(["Year"], as_index=False)
        .agg(Target=("Target", lambda s: s.sum(min_count=1)), Actual=("Actual", lambda s: s.sum(min_count=1)))
        .sort_values("Year")
    )
    annual_sum = compute_metrics(annual_sum)

    quarterly_sum = (
        filtered_df.groupby(["Year", "Quarter"], as_index=False)
        .agg(Target=("Target", lambda s: s.sum(min_count=1)), Actual=("Actual", lambda s: s.sum(min_count=1)))
        .sort_values(["Year", "Quarter"])
    )
    quarterly_sum = compute_metrics(quarterly_sum)

    half_sum = (
        filtered_df.groupby(["Year", "Half"], as_index=False)
        .agg(Target=("Target", lambda s: s.sum(min_count=1)), Actual=("Actual", lambda s: s.sum(min_count=1)))
        .sort_values(["Year", "Half"])
    )
    half_sum = compute_metrics(half_sum)

    product_sum = (
        filtered_df.groupby(["Product"], as_index=False)
        .agg(Target=("Target", lambda s: s.sum(min_count=1)), Actual=("Actual", lambda s: s.sum(min_count=1)))
    )
    product_sum = compute_metrics(product_sum)

    return {
        "monthly": monthly_sum,
        "annual": annual_sum,
        "quarterly": quarterly_sum,
        "half_yearly": half_sum,
        "product": product_sum,
    }
