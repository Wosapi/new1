"""
Data Cleaning, Structuring & Reconciliation Module:
Parses the 'Target' sheet dynamically across any years present (2024, 2025, 2026, or future years),
preserves NaN/notes without fabricating missing data, and audits Excel totals vs calculated sums.
"""

import re
from typing import Dict, List, Tuple, Any
import numpy as np
import pandas as pd
from config import PRODUCTS, MONTHS_ORDER, MONTH_TO_NUM, MONTH_TO_QUARTER, MONTH_TO_HALF


def _clean_str(val: Any) -> str:
    if val is None or (isinstance(val, float) and np.isnan(val)):
        return ""
    return str(val).strip()


def _to_float_or_nan(val: Any) -> Tuple[float, str]:
    """
    Convert cell value to float if numeric; otherwise return (np.nan, note_text).
    Never invents zeros for missing or text cells (e.g., 'Vacation').
    """
    if val is None or (isinstance(val, float) and np.isnan(val)):
        return np.nan, ""
    if isinstance(val, (int, float, np.number)):
        return float(val), ""
    s = str(val).strip()
    if s == "":
        return np.nan, ""
    try:
        return float(s), ""
    except ValueError:
        return np.nan, s


def _discover_year_blocks(df_raw: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Dynamically detect year blocks from Row 0 & Row 1 (e.g., 'Sales 2024', 'Sales 2025', 'Sales 2026', ...).
    Allows future years to be added in Excel without rewriting code.
    """
    row0 = df_raw.iloc[0]
    row1 = df_raw.iloc[1]
    year_blocks = []

    for col_idx in range(len(row0)):
        cell_text = _clean_str(row0.iloc[col_idx])
        match = re.search(r"(20\d{2})", cell_text)
        if match:
            year = int(match.group(1))
            prod_cols = {}
            total_col = None
            pct_col = None
            # Scan columns belonging to this year block until next year header
            for offset in range(0, 8):
                c = col_idx + offset
                if c >= len(row1):
                    break
                if offset > 0 and re.search(r"(20\d{2})", _clean_str(row0.iloc[c])):
                    break
                sub_hdr = _clean_str(row1.iloc[c])
                if sub_hdr in PRODUCTS:
                    prod_cols[sub_hdr] = c
                elif sub_hdr.lower() == "total":
                    total_col = c
                elif sub_hdr == "%":
                    pct_col = c

            year_blocks.append({
                "year": year,
                "start_col": col_idx,
                "prod_cols": prod_cols,
                "total_col": total_col,
                "pct_col": pct_col,
            })

    return sorted(year_blocks, key=lambda x: x["year"])


def parse_target_sheet(df_raw: pd.DataFrame) -> Dict[str, Any]:
    """
    Parse the entire 'Target' sheet into clean, structured DataFrames:
    1. monthly_df: Granular Year x Month x Product records (Target, Actual, Notes)
    2. monthly_totals_df: Monthly Total rows from Excel vs Calculated
    3. annual_excel_df: Annual summary block from Excel
    4. ytd_excel_df: YTD Target row from Excel
    5. quarterly_excel_df: Quarterly summary (Q1-Q4) from Excel
    6. half_yearly_excel_df: Half-yearly summary (H1-H2) from Excel
    7. audit_alerts: List of discrepancies and data quality notices
    """
    year_blocks = _discover_year_blocks(df_raw)
    if not year_blocks:
        raise ValueError("تعذر التعرف على أعمدة السنوات (مثل Sales 2024) في صف العناوين الأول من شيت Target.")

    monthly_records = []
    monthly_total_records = []
    annual_records = []
    ytd_records = []
    quarterly_records = []
    half_yearly_records = []
    audit_alerts = []

    current_month = None
    in_annual_block = False

    # 1. Parse Monthly Rows (Rows 2 to ~27) & Annual / YTD rows
    for r_idx in range(2, len(df_raw)):
        c0 = _clean_str(df_raw.iloc[r_idx, 0])
        c1 = _clean_str(df_raw.iloc[r_idx, 1])

        # Stop monthly parsing when reaching quarterly headers
        row_joined = " ".join([_clean_str(x) for x in df_raw.iloc[r_idx].tolist() if _clean_str(x)])
        if "ملخص الأرباع" in row_joined or c1 == "Q1" or _clean_str(df_raw.iloc[r_idx, 2]) == "Q1":
            break

        if c0 in MONTHS_ORDER:
            current_month = c0
            in_annual_block = False
        elif c0.lower().startswith("anuual") or c0.lower().startswith("annual"):
            current_month = None
            in_annual_block = True
        elif c0.lower() == "ytd target" or c1.lower() == "ytd target":
            for yb in year_blocks:
                yr = yb["year"]
                for prod, p_col in yb["prod_cols"].items():
                    val, note = _to_float_or_nan(df_raw.iloc[r_idx, p_col])
                    ytd_records.append({
                        "Year": yr,
                        "Product": prod,
                        "Excel_YTD_Ratio": val,
                        "Note": note,
                    })
                if yb["total_col"] is not None:
                    t_val, t_note = _to_float_or_nan(df_raw.iloc[r_idx, yb["total_col"]])
                    ytd_records.append({
                        "Year": yr,
                        "Product": "Total",
                        "Excel_YTD_Ratio": t_val,
                        "Note": t_note,
                    })
            continue

        row_type = None
        if c1.lower() == "target":
            row_type = "Target"
        elif c1.lower() == "actual":
            row_type = "Actual"

        if current_month and row_type:
            for yb in year_blocks:
                yr = yb["year"]
                for prod, p_col in yb["prod_cols"].items():
                    val, note = _to_float_or_nan(df_raw.iloc[r_idx, p_col])
                    monthly_records.append({
                        "Year": yr,
                        "Month": current_month,
                        "Month_Num": MONTH_TO_NUM[current_month],
                        "Quarter": MONTH_TO_QUARTER[current_month],
                        "Half": MONTH_TO_HALF[current_month],
                        "Product": prod,
                        "Metric_Type": row_type,
                        "Value": val,
                        "Note": note,
                    })
                if yb["total_col"] is not None:
                    tot_val, tot_note = _to_float_or_nan(df_raw.iloc[r_idx, yb["total_col"]])
                    pct_val = np.nan
                    if yb["pct_col"] is not None:
                        pct_val, _ = _to_float_or_nan(df_raw.iloc[r_idx, yb["pct_col"]])
                    monthly_total_records.append({
                        "Year": yr,
                        "Month": current_month,
                        "Month_Num": MONTH_TO_NUM[current_month],
                        "Metric_Type": row_type,
                        "Excel_Total": tot_val,
                        "Excel_Pct": pct_val,
                        "Note": tot_note,
                    })

        elif in_annual_block and row_type:
            for yb in year_blocks:
                yr = yb["year"]
                for prod, p_col in yb["prod_cols"].items():
                    val, note = _to_float_or_nan(df_raw.iloc[r_idx, p_col])
                    annual_records.append({
                        "Year": yr,
                        "Product": prod,
                        "Metric_Type": row_type,
                        "Excel_Value": val,
                        "Note": note,
                    })
                if yb["total_col"] is not None:
                    tot_val, tot_note = _to_float_or_nan(df_raw.iloc[r_idx, yb["total_col"]])
                    pct_val = np.nan
                    if yb["pct_col"] is not None:
                        pct_val, _ = _to_float_or_nan(df_raw.iloc[r_idx, yb["pct_col"]])
                    annual_records.append({
                        "Year": yr,
                        "Product": "Total",
                        "Metric_Type": row_type,
                        "Excel_Value": tot_val,
                        "Excel_Pct": pct_val,
                        "Note": tot_note,
                    })

    # Pivot monthly records into wide Target / Actual columns per (Year, Month, Product)
    raw_m_df = pd.DataFrame(monthly_records)
    target_m = raw_m_df[raw_m_df["Metric_Type"] == "Target"].rename(
        columns={"Value": "Target", "Note": "Target_Note"}
    ).drop(columns=["Metric_Type"])

    actual_m = raw_m_df[raw_m_df["Metric_Type"] == "Actual"].rename(
        columns={"Value": "Actual", "Note": "Actual_Note"}
    ).drop(columns=["Metric_Type"])

    monthly_df = pd.merge(
        target_m,
        actual_m,
        on=["Year", "Month", "Month_Num", "Quarter", "Half", "Product"],
        how="outer",
    )

    # Identify future/unrecorded zero months vs active months
    # Note: In 2026, Apr and Dec have 0.0 across all products while active months have positive sales.
    month_sum_actual = monthly_df.groupby(["Year", "Month"])["Actual"].transform(
        lambda s: s.sum(min_count=1)
    )
    monthly_df["Is_All_Zero_Actual"] = (month_sum_actual == 0)
    monthly_df["Is_Missing_Actual"] = monthly_df["Actual"].isna()
    monthly_df["Status_Note"] = np.where(
        monthly_df["Actual_Note"] != "",
        monthly_df["Actual_Note"],
        np.where(
            monthly_df["Is_Missing_Actual"],
            "غير مسجل (No Data)",
            np.where(monthly_df["Is_All_Zero_Actual"], "فترة صفرية / مستقبلية (Zero/Future)", "نشط (Active)"),
        ),
    )

    # 2. Parse Quarterly (Q1-Q4) & Half-Yearly (H1-H2) Excel Summary Blocks
    for r_idx in range(28, len(df_raw)):
        for yb in year_blocks:
            yr = yb["year"]
            base_c = yb["start_col"]
            label_cell = _clean_str(df_raw.iloc[r_idx, base_c]).replace(" ", "")
            if label_cell in {"Q1", "Q2", "Q3", "Q4", "H1", "H2"}:
                period_name = "H1" if label_cell == "H1" else ("H2" if label_cell == "H2" else label_cell)
                is_quarter = period_name.startswith("Q")
                # Next 3 rows are Target, Actual, %
                if r_idx + 3 < len(df_raw):
                    t_row = df_raw.iloc[r_idx + 1]
                    a_row = df_raw.iloc[r_idx + 2]
                    p_row = df_raw.iloc[r_idx + 3]

                    prod_map = {"Min": base_c + 1, "Syn": base_c + 2, "DEO": base_c + 3, "Fluids": base_c + 4, "Total": base_c + 5}
                    for p_name, c_i in prod_map.items():
                        if c_i < len(df_raw.columns):
                            t_v, _ = _to_float_or_nan(t_row.iloc[c_i])
                            a_v, _ = _to_float_or_nan(a_row.iloc[c_i])
                            pct_v, _ = _to_float_or_nan(p_row.iloc[c_i])
                            rec = {
                                "Year": yr,
                                "Period": period_name,
                                "Product": p_name,
                                "Excel_Target": t_v,
                                "Excel_Actual": a_v,
                                "Excel_Pct": pct_v * 100.0 if pd.notna(pct_v) else np.nan,
                            }
                            if is_quarter:
                                quarterly_records.append(rec)
                            else:
                                half_yearly_records.append(rec)

    monthly_totals_df = pd.DataFrame(monthly_total_records)
    annual_excel_df = pd.DataFrame(annual_records)
    ytd_excel_df = pd.DataFrame(ytd_records)
    quarterly_excel_df = pd.DataFrame(quarterly_records)
    half_yearly_excel_df = pd.DataFrame(half_yearly_records)

    # 3. Data Validation & Reconciliation Checks (Never hide discrepancies)
    # Check A: Notes like 'Vacation'
    notes_df = monthly_df[monthly_df["Actual_Note"] != ""][["Year", "Month", "Product", "Actual_Note"]].drop_duplicates()
    for _, nrow in notes_df.iterrows():
        audit_alerts.append({
            "Severity": "Info",
            "Category": "ملاحظة نصية في البيانات (Text Note)",
            "Details": f"السنة {nrow['Year']} - شهر {nrow['Month']} ({nrow['Product']}): مسجل كـ '{nrow['Actual_Note']}' وتم الحفاظ عليه دون تحويله إلى صفر.",
        })

    # Check B: Monthly product sum vs Excel Total column
    calc_m_tot = (
        monthly_df.groupby(["Year", "Month"], as_index=False)
        .agg(Calc_Target=("Target", lambda s: s.sum(min_count=1)), Calc_Actual=("Actual", lambda s: s.sum(min_count=1)))
    )
    if not monthly_totals_df.empty:
        for m_type, col_calc in [("Target", "Calc_Target"), ("Actual", "Calc_Actual")]:
            sub_mt = monthly_totals_df[monthly_totals_df["Metric_Type"] == m_type].merge(
                calc_m_tot, on=["Year", "Month"], how="left"
            )
            for _, r in sub_mt.iterrows():
                if pd.notna(r["Excel_Total"]) and pd.notna(r[col_calc]):
                    if abs(r["Excel_Total"] - r[col_calc]) > 1e-4:
                        audit_alerts.append({
                            "Severity": "Warning",
                            "Category": "اختلاف إجمالي شهري (Monthly Total Mismatch)",
                            "Details": f"{r['Year']} {r['Month']} ({m_type}): إجمالي Excel = {r['Excel_Total']:.4f} بينما مجموع المنتجات = {r[col_calc]:.4f}",
                        })

    # Check C: Quarterly Excel Summary vs Monthly Sum
    if not quarterly_excel_df.empty:
        q_calc = (
            monthly_df.groupby(["Year", "Quarter", "Product"], as_index=False)
            .agg(Calc_Target=("Target", lambda s: s.sum(min_count=1)), Calc_Actual=("Actual", lambda s: s.sum(min_count=1)))
            .rename(columns={"Quarter": "Period"})
        )
        q_merged = quarterly_excel_df[quarterly_excel_df["Product"] != "Total"].merge(
            q_calc, on=["Year", "Period", "Product"], how="left"
        )
        for _, r in q_merged.iterrows():
            if pd.notna(r["Excel_Target"]) and pd.notna(r["Calc_Target"]) and abs(r["Excel_Target"] - r["Calc_Target"]) > 1e-3:
                audit_alerts.append({
                    "Severity": "Warning",
                    "Category": "اختلاف ملخص الأرباع (Quarterly Target Discrepancy)",
                    "Details": f"{r['Year']} {r['Period']} ({r['Product']}): مستهدف Excel في جدول الأرباع = {r['Excel_Target']:.2f} بينما مجموع الأشهر = {r['Calc_Target']:.2f}",
                })
            # Check Excel % formula accuracy in Quarterly table
            if pd.notna(r["Excel_Target"]) and r["Excel_Target"] > 0 and pd.notna(r["Excel_Actual"]) and pd.notna(r["Excel_Pct"]):
                true_pct = (r["Excel_Actual"] / r["Excel_Target"]) * 100.0
                if abs(true_pct - r["Excel_Pct"]) > 0.05:
                    audit_alerts.append({
                        "Severity": "Warning",
                        "Category": "اختلاف معادلة النسبة في Excel (Excel % Formula Mismatch)",
                        "Details": f"{r['Year']} {r['Period']} ({r['Product']}): النسبة المسجلة في Excel = {r['Excel_Pct']:.2f}% بينما النسبة الحسابية الصحيحة = {true_pct:.2f}%",
                    })

    # Check D: Half-Yearly Excel Summary vs Monthly Sum
    if not half_yearly_excel_df.empty:
        h_calc = (
            monthly_df.groupby(["Year", "Half", "Product"], as_index=False)
            .agg(Calc_Target=("Target", lambda s: s.sum(min_count=1)), Calc_Actual=("Actual", lambda s: s.sum(min_count=1)))
            .rename(columns={"Half": "Period"})
        )
        h_merged = half_yearly_excel_df[half_yearly_excel_df["Product"] != "Total"].merge(
            h_calc, on=["Year", "Period", "Product"], how="left"
        )
        for _, r in h_merged.iterrows():
            if pd.notna(r["Excel_Target"]) and pd.notna(r["Calc_Target"]) and abs(r["Excel_Target"] - r["Calc_Target"]) > 1e-3:
                audit_alerts.append({
                    "Severity": "Warning",
                    "Category": "اختلاف الملخص النصفي (Half-Yearly Target Discrepancy)",
                    "Details": f"{r['Year']} {r['Period']} ({r['Product']}): مستهدف Excel في الملخص النصفي = {r['Excel_Target']:.2f} بينما مجموع الأشهر = {r['Calc_Target']:.2f}",
                })

    return {
        "years": [yb["year"] for yb in year_blocks],
        "monthly_df": monthly_df,
        "monthly_totals_df": monthly_totals_df,
        "annual_excel_df": annual_excel_df,
        "ytd_excel_df": ytd_excel_df,
        "quarterly_excel_df": quarterly_excel_df,
        "half_yearly_excel_df": half_yearly_excel_df,
        "audit_alerts": pd.DataFrame(audit_alerts),
    }
