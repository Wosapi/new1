"""
Main Streamlit Application Entry Point:
Enterprise Sales Target & Performance BI Dashboard.
"""

from pathlib import Path
import numpy as np
import pandas as pd
import streamlit as st

from config import (
    ASSETS_DIR,
    COLORS,
    MONTHS_ORDER,
    PRODUCTS,
    THRESHOLD_GREEN,
    THRESHOLD_ORANGE,
    TRANSLATIONS,
)
from modules.data_loader import load_all_sheets, resolve_excel_source
from modules.data_processor import parse_target_sheet
from modules.calculations import build_summaries, calculate_kpis, compute_metrics, filter_monthly_data
from modules.charts import (
    chart_achievement_pct,
    chart_annual_comparison,
    chart_monthly_trend,
    chart_period_comparison,
    chart_product_performance,
    chart_target_vs_actual,
    chart_yoy_monthly,
)
from modules.exports import export_to_csv, export_to_excel

st.set_page_config(
    page_title="Sales Target & Performance Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


def inject_css(is_rtl: bool) -> None:
    css_path = ASSETS_DIR / "style.css"
    base_css = css_path.read_text(encoding="utf-8") if css_path.exists() else ""
    dir_css = (
        """
        .stApp, .main, [data-testid="stSidebar"] { direction: rtl; text-align: right; }
        """
        if is_rtl
        else """
        .stApp, .main, [data-testid="stSidebar"] { direction: ltr; text-align: left; }
        """
    )
    st.markdown(f"<style>{base_css}\n{dir_css}</style>", unsafe_allow_html=True)


def render_kpi_card(label: str, value: str, sub: str = "", accent: str = "") -> str:
    return f"""
    <div class="kpi-card {accent}">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value {accent}">{value}</div>
        <div class="kpi-sub">{sub}</div>
    </div>
    """


def format_display_table(df: pd.DataFrame, t: dict) -> pd.DataFrame:
    out = df.copy()
    if "Perf_Code" in out.columns:
        status_map = {
            "achieved": f"🟢 {t['status_achieved']}",
            "warning": f"🟠 {t['status_warning']}",
            "low": f"🔴 {t['status_low']}",
            "na": f"⚪ {t['status_na']}",
        }
        out[t["status"]] = out["Perf_Code"].map(status_map)
        out = out.drop(columns=["Perf_Code"])
    return out


def main() -> None:
    # Sidebar: Language & Data Source
    with st.sidebar:
        lang_choice = st.radio("Language / اللغة", options=["العربية", "English"], horizontal=True)
        lang = "ar" if lang_choice == "العربية" else "en"
        t = TRANSLATIONS[lang]
        is_rtl = lang == "ar"

    inject_css(is_rtl)

    with st.sidebar:
        st.markdown(f"### ⚙️ {t['sidebar_title']}")
        uploaded_file = st.file_uploader(t["upload_label"], type=["xlsb", "xlsx"])

    # Load & Parse Data
    try:
        source = resolve_excel_source(uploaded_file)
        if uploaded_file is not None:
            file_bytes = uploaded_file.getvalue()
            file_name = uploaded_file.name
        else:
            file_bytes = Path(source).read_bytes()
            file_name = Path(source).name

        sheets_dict, target_sheet_key = load_all_sheets(file_bytes, file_name)
        parsed = parse_target_sheet(sheets_dict[target_sheet_key])
    except Exception as exc:
        st.error(f"❌ خطأ في تحميل أو معالجة ملف البيانات: {exc}")
        st.stop()

    monthly_df = parsed["monthly_df"]
    available_years = parsed["years"]

    # Sidebar Interactive Filters
    with st.sidebar:
        selected_years = st.multiselect(
            t["year_filter"],
            options=available_years,
            default=available_years,
        )
        selected_months = st.multiselect(
            t["month_filter"],
            options=MONTHS_ORDER,
            default=MONTHS_ORDER,
        )
        selected_products = st.multiselect(
            t["product_filter"],
            options=PRODUCTS,
            default=PRODUCTS,
        )
        period_mode = st.selectbox(
            t["period_filter"],
            options=[t["period_all"], t["period_monthly"], t["period_quarterly"], t["period_half"]],
        )
        exclude_future_zeros = st.checkbox(t["exclude_future_zeros"], value=True)

        st.markdown("---")
        st.caption(f"📁 **{file_name}**")
        st.caption(f"📑 {t['sheets_loaded']} {len(sheets_dict)}")

    # Apply Filters & Calculations
    filtered_df = filter_monthly_data(
        monthly_df=monthly_df,
        selected_years=selected_years or available_years,
        selected_months=selected_months or MONTHS_ORDER,
        selected_products=selected_products or PRODUCTS,
        exclude_future_zeros=exclude_future_zeros,
    )
    kpis = calculate_kpis(filtered_df)
    summaries = build_summaries(filtered_df)

    # Top Executive Banner
    yr_span = f"{min(selected_years or available_years)}–{max(selected_years or available_years)}"
    st.markdown(
        f"""
        <div class="exec-banner">
            <div class="exec-badge">{t['banner_badge']} • {yr_span}</div>
            <h1 class="exec-title">{t['banner_title']}</h1>
            <div class="exec-sub">{t['banner_sub']}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Reconciliation Alert Banner (if discrepancies exist in Excel summary rows)
    audit_df = parsed["audit_alerts"]
    if not audit_df.empty:
        warn_count = (audit_df["Severity"] == "Warning").sum()
        with st.expander(f"⚠️ {t['audit_title']} ({warn_count} تنبيهات مطابقة / {len(audit_df)} ملاحظات)", expanded=False):
            st.dataframe(audit_df, use_container_width=True, hide_index=True)

    # 6 Interactive KPI Cards
    ach_val = kpis["achievement_pct"]
    if pd.isna(ach_val):
        ach_str, ach_accent = "N/A", ""
    elif ach_val >= THRESHOLD_GREEN:
        ach_str, ach_accent = f"{ach_val:.1f}%", "green"
    elif ach_val >= THRESHOLD_ORANGE:
        ach_str, ach_accent = f"{ach_val:.1f}%", "orange"
    else:
        ach_str, ach_accent = f"{ach_val:.1f}%", "red"

    rem_val = kpis["remaining_target"]
    rem_accent = "green" if rem_val <= 0 else "orange"

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    with c1:
        st.markdown(
            render_kpi_card(t["kpi_target"], f"{kpis['total_target']:,.2f}", t["unit_label"], ""),
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            render_kpi_card(t["kpi_actual"], f"{kpis['total_actual']:,.2f}", t["unit_label"], "teal"),
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            render_kpi_card(t["kpi_ach"], ach_str, f"Target ≥ {THRESHOLD_GREEN:.0f}%", ach_accent),
            unsafe_allow_html=True,
        )
    with c4:
        st.markdown(
            render_kpi_card(t["kpi_rem"], f"{rem_val:,.2f}", "Target - Actual", rem_accent),
            unsafe_allow_html=True,
        )
    with c5:
        bm_sub = f"{kpis['best_month_val']:,.2f}" if pd.notna(kpis["best_month_val"]) else "—"
        st.markdown(
            render_kpi_card(t["kpi_best_month"], kpis["best_month"], bm_sub, "teal"),
            unsafe_allow_html=True,
        )
    with c6:
        bp_sub = f"{kpis['best_product_val']:,.2f}" if pd.notna(kpis["best_product_val"]) else "—"
        st.markdown(
            render_kpi_card(t["kpi_best_prod"], kpis["best_product"], bp_sub, "green"),
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Navigation Tabs
    tab_main, tab_products, tab_periods, tab_tables = st.tabs([
        f"📈 {t['view_overview']}",
        f"🛢️ {t['view_products']}",
        f"📅 {t['view_periods']}",
        f"📋 {t['view_tables']}",
    ])

    # TAB 1: MAIN DASHBOARD
    with tab_main:
        st.markdown(f"<div class='section-header'>{t['sec_main_charts']}</div>", unsafe_allow_html=True)
        r1_c1, r1_c2 = st.columns(2)
        with r1_c1:
            st.plotly_chart(chart_target_vs_actual(summaries["monthly"], t), use_container_width=True)
        with r1_c2:
            st.plotly_chart(chart_monthly_trend(summaries["monthly"], t), use_container_width=True)

        r2_c1, r2_c2 = st.columns(2)
        with r2_c1:
            st.plotly_chart(chart_achievement_pct(summaries["monthly"], t), use_container_width=True)
        with r2_c2:
            st.plotly_chart(chart_product_performance(summaries["product"], t), use_container_width=True)

        r3_c1, r3_c2 = st.columns(2)
        with r3_c1:
            st.plotly_chart(chart_annual_comparison(summaries["annual"], t), use_container_width=True)
        with r3_c2:
            st.plotly_chart(chart_yoy_monthly(summaries["monthly"], t), use_container_width=True)

    # TAB 2: PRODUCT ANALYSIS
    with tab_products:
        st.markdown(f"<div class='section-header'>{t['sec_prod_analysis']}</div>", unsafe_allow_html=True)
        avail_prods = selected_products if selected_products else PRODUCTS
        chosen_prod = st.selectbox(t["select_product"], options=avail_prods)

        prod_df = filtered_df[filtered_df["Product"] == chosen_prod].copy()
        prod_kpis = calculate_kpis(prod_df)
        prod_var = prod_kpis["total_actual"] - prod_kpis["total_target"]

        pk1, pk2, pk3, pk4 = st.columns(4)
        with pk1:
            st.markdown(render_kpi_card(f"{chosen_prod} — {t['target']}", f"{prod_kpis['total_target']:,.2f}"), unsafe_allow_html=True)
        with pk2:
            st.markdown(render_kpi_card(f"{chosen_prod} — {t['actual']}", f"{prod_kpis['total_actual']:,.2f}", accent="teal"), unsafe_allow_html=True)
        with pk3:
            p_ach = f"{prod_kpis['achievement_pct']:.1f}%" if pd.notna(prod_kpis["achievement_pct"]) else "N/A"
            p_acc = "green" if (pd.notna(prod_kpis["achievement_pct"]) and prod_kpis["achievement_pct"] >= 100) else "orange"
            st.markdown(render_kpi_card(f"{chosen_prod} — {t['achievement']}", p_ach, accent=p_acc), unsafe_allow_html=True)
        with pk4:
            v_acc = "green" if prod_var >= 0 else "red"
            st.markdown(render_kpi_card(f"{chosen_prod} — {t['variance']}", f"{prod_var:+,.2f}", accent=v_acc), unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        prod_summaries = build_summaries(prod_df)
        pc1, pc2 = st.columns(2)
        with pc1:
            st.plotly_chart(chart_monthly_trend(prod_summaries["monthly"], t), use_container_width=True)
        with pc2:
            st.plotly_chart(chart_annual_comparison(prod_summaries["annual"], t), use_container_width=True)

        st.dataframe(
            format_display_table(prod_summaries["monthly"], t),
            use_container_width=True,
            hide_index=True,
        )

    # TAB 3: QUARTERLY & HALF-YEARLY ANALYSIS
    with tab_periods:
        if period_mode in (t["period_all"], t["period_quarterly"]):
            st.markdown(f"<div class='section-header'>{t['sec_quarterly']}</div>", unsafe_allow_html=True)
            qc1, qc2 = st.columns([1.3, 1])
            with qc1:
                st.plotly_chart(
                    chart_period_comparison(summaries["quarterly"], "Quarter", t["sec_quarterly"], t),
                    use_container_width=True,
                )
            with qc2:
                q_prod = (
                    filtered_df.groupby(["Quarter", "Product"], as_index=False)
                    .agg(Target=("Target", "sum"), Actual=("Actual", "sum"))
                )
                q_prod = compute_metrics(q_prod)
                st.dataframe(format_display_table(q_prod, t), use_container_width=True, hide_index=True)

        if period_mode in (t["period_all"], t["period_half"]):
            st.markdown(f"<div class='section-header'>{t['sec_half']}</div>", unsafe_allow_html=True)
            hc1, hc2 = st.columns([1.3, 1])
            with hc1:
                st.plotly_chart(
                    chart_period_comparison(summaries["half_yearly"], "Half", t["sec_half"], t),
                    use_container_width=True,
                )
            with hc2:
                h_prod = (
                    filtered_df.groupby(["Half", "Product"], as_index=False)
                    .agg(Target=("Target", "sum"), Actual=("Actual", "sum"))
                )
                h_prod = compute_metrics(h_prod)
                st.dataframe(format_display_table(h_prod, t), use_container_width=True, hide_index=True)

    # TAB 4: DATA TABLES, EXPORTS & AUDIT
    with tab_tables:
        st.markdown(f"<div class='section-header'>{t['sec_tables']}</div>", unsafe_allow_html=True)

        export_bundle = {
            "Monthly_Summary": format_display_table(summaries["monthly"], t),
            "Annual_Summary": format_display_table(summaries["annual"], t),
            "Quarterly_Summary": format_display_table(summaries["quarterly"], t),
            "Half_Yearly_Summary": format_display_table(summaries["half_yearly"], t),
            "Product_Performance": format_display_table(summaries["product"], t),
            "Granular_Data": format_display_table(filtered_df, t),
            "Audit_Reconciliation": audit_df,
        }

        dl1, dl2 = st.columns(2)
        with dl1:
            st.download_button(
                label=f"📥 {t['download_excel']}",
                data=export_to_excel(export_bundle),
                file_name="Sales_Target_Executive_Report.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )

        table_choice = st.selectbox(
            "اختر الجدول للعرض والتصدير / Select Table:",
            options=list(export_bundle.keys()),
        )
        active_table = export_bundle[table_choice]

        with dl2:
            st.download_button(
                label=f"📄 {t['download_csv']} ({table_choice})",
                data=export_to_csv(active_table),
                file_name=f"{table_choice}.csv",
                mime="text/csv",
                use_container_width=True,
            )

        st.dataframe(active_table, use_container_width=True, hide_index=True)


if __name__ == "__main__":
    main()
