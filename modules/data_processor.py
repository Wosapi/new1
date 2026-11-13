import pandas as pd

def process_data(actual_df, annual_df, monthly_df):
    """
    تنظيف ومعالجة الجداول وتجهيزها للعرض والتحليل.
    """
    if actual_df is None or actual_df.empty:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    # التأكد من وجود الأعمدة الأساسية
    for df in [actual_df, annual_df, monthly_df]:
        if df is not None and not df.empty and 'Year' not in df.columns:
            df['Year'] = 2026

    return actual_df, annual_df, monthly_df
