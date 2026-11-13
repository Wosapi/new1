import pandas as pd
import numpy as np

def calculate_dual_kpis(df_actual, df_annual_target, df_monthly_target, selected_years):
    """
    حساب مؤشرات الأداء الرئيسية مع الفصل التام بين المستهدف السنوي ومجموع المستهدفات الشهرية.
    """
    # تصفية السنوات
    if selected_years and 'Year' in df_actual.columns:
        actual_filtered = df_actual[df_actual['Year'].isin(selected_years)]
    else:
        actual_filtered = df_actual

    total_actual = actual_filtered['Actual_Sales'].sum() if 'Actual_Sales' in actual_filtered.columns else 0

    # المستهدف السنوي من annual_excel_df
    if selected_years and 'Year' in df_annual_target.columns:
        annual_target_filtered = df_annual_target[df_annual_target['Year'].isin(selected_years)]
    else:
        annual_target_filtered = df_annual_target

    total_annual_target = annual_target_filtered['Annual_Target'].sum() if 'Annual_Target' in annual_target_filtered.columns else 0

    # المستهدف الشهري المجمع
    if selected_years and 'Year' in df_monthly_target.columns:
        monthly_target_filtered = df_monthly_target[df_monthly_target['Year'].isin(selected_years)]
    else:
        monthly_target_filtered = df_monthly_target

    total_monthly_target = monthly_target_filtered['Monthly_Target'].sum() if 'Monthly_Target' in monthly_target_filtered.columns else 0

    # نسب الإنجاز
    annual_achievement = (total_actual / total_annual_target * 100) if total_annual_target > 0 else 0.0
    monthly_achievement = (total_actual / total_monthly_target * 100) if total_monthly_target > 0 else 0.0
    
    # المتبقي بناءً على المستهدف السنوي الأصلي
    remaining_target = max(0, total_annual_target - total_actual)

    return {
        "total_actual": total_actual,
        "total_annual_target": total_annual_target,
        "total_monthly_target": total_monthly_target,
        "annual_achievement": round(annual_achievement, 2),
        "monthly_achievement": round(monthly_achievement, 2),
        "remaining_target": remaining_target
    }

def calculate_kpis(df_actual, df_annual_target, df_monthly_target, selected_years):
    """توافقية عكسية مع الاستيرادات القديمة في app.py"""
    return calculate_dual_kpis(df_actual, df_annual_target, df_monthly_target, selected_years)

def run_audit_engine(monthly_targets_df, annual_targets_df, quarterly_targets_df, half_yearly_targets_df, actual_df):
    """
    محرك التدقيق الشامل للمقارنة بين مصادر المستهدفات والفعلي.
    """
    audit_records = []
    # مثال تطبيقي للمقارنة والتدقيق
    years = actual_df['Year'].unique() if 'Year' in actual_df.columns else [2026]
    
    for year in years:
        act_val = actual_df[actual_df['Year'] == year]['Actual_Sales'].sum() if 'Year' in actual_df.columns else actual_df['Actual_Sales'].sum()
        ann_val = annual_targets_df[annual_targets_df['Year'] == year]['Annual_Target'].sum() if 'Year' in annual_targets_df.columns and not annual_targets_df.empty else 0
        
        diff = act_val - ann_val
        audit_records.append({
            "Year": year,
            "Product": "All Products",
            "Period": "Annual",
            "Excel Value": ann_val,
            "Calculated Value": act_val,
            "Difference": diff,
            "Source": "Excel Annual vs Actual"
        })
        
    return pd.DataFrame(audit_records)
