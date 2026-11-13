import streamlit as st
import pandas as pd
from modules.data_loader import load_data
from modules.data_processor import process_data
from modules.calculations import calculate_dual_kpis, run_audit_engine
from modules.charts import create_annual_comparison_chart, create_monthly_target_chart

st.set_page_config(
    page_title="Sales Dashboard V3",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# تحميل التصميم المخصص Style.css إن وجد
try:
    with open("assets/style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except:
    # تصميم احتياطي يدعم Navy Blue و Teal وتخطيط الموبايل
    st.markdown("""
        <style>
        .main { background-color: #F8FAFC; }
        h1, h2, h3 { color: #1E3A8A; }
        .stMetric { background-color: #FFFFFF; padding: 15px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
        </style>
    """, unsafe_allow_html=True)

st.title("📊 لوحة تحكم المبيعات الاحترافية — V3")

# الشريط الجانبي (فلاتر ومصدر البيانات)
st.sidebar.header("إدارة البيانات والفلاتر")
uploaded_file = st.sidebar.file_uploader("رفع ملف Excel جديد", type=["xlsx", "xls"])

actual_df, annual_df, monthly_df, metadata, error_msg = load_data(uploaded_file)

if error_msg:
    st.error(error_msg)
    st.stop()

# عرض معلومات الملف وتاريخ التحديث
st.sidebar.info(f"📁 **الملف:** {metadata['file_name']}\n\n🕒 **التحديث:** {metadata['update_time']}")

actual_df, annual_df, monthly_df = process_data(actual_df, annual_df, monthly_df)

# الفلاتر الزمنية
available_years = sorted(actual_df['Year'].unique()) if 'Year' in actual_df.columns else [2026]
selected_years = st.sidebar.multiselect("اختر السنوات", available_years, default=available_years)

# الحسابات
kpis = calculate_dual_kpis(actual_df, annual_df, monthly_df, selected_years)

# عرض بطاقات KPIs (متوافقة مع الجوال: 2-3 بطاقات في الصف)
st.subheader("مؤشرات الأداء الرئيسية (KPIs)")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("المبيعات الفعلية", f"{kpis['total_actual']:,.2f}")
with col2:
    st.metric("المستهدف السنوي الأصلي", f"{kpis['total_annual_target']:,.2f}")
with col3:
    st.metric("نسبة الإنجاز السنوي", f"{kpis['annual_achievement']}%")
with col4:
    st.metric("المتبقي لتحقيق الهدف", f"{kpis['remaining_target']:,.2f}")

st.markdown("---")

# الرسوم البيانية (عمود واحد للجوال / أعمدة متعددة للشاشات الكبيرة)
col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    st.subheader("المقارنة السنوية")
    fig_annual = create_annual_comparison_chart(kpis['total_annual_target'], kpis['total_actual'])
    st.plotly_chart(fig_annual, use_container_width=True)

with col_chart2:
    st.subheader("المستهدف الشهري المجمع")
    fig_monthly = create_monthly_target_chart(monthly_df)
    st.plotly_chart(fig_monthly, use_container_width=True)

# قسم التدقيق (Audit Engine)
st.markdown("---")
st.subheader("🔍 محرك التدقيق (Data Audit Engine)")
audit_df = run_audit_engine(monthly_df, annual_df, pd.DataFrame(), pd.DataFrame(), actual_df)
st.dataframe(audit_df, use_container_width=True)
