"""
Configuration, Color Palette, Localization (AR/EN), and Constants.
"""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
ASSETS_DIR = BASE_DIR / "assets"

DEFAULT_EXCEL_CANDIDATES = [
    DATA_DIR / "Total_Sales.xlsb",
    DATA_DIR / "sales_data.xlsx",
    DATA_DIR / "sales_data.xlsb",
    BASE_DIR / "Total_Sales.xlsb",
]

PRODUCTS = ["Min", "Syn", "DEO", "Fluids"]

MONTHS_ORDER = [
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
]

MONTH_TO_NUM = {m: i + 1 for i, m in enumerate(MONTHS_ORDER)}

MONTH_TO_QUARTER = {
    "Jan": "Q1", "Feb": "Q1", "Mar": "Q1",
    "Apr": "Q2", "May": "Q2", "Jun": "Q2",
    "Jul": "Q3", "Aug": "Q3", "Sep": "Q3",
    "Oct": "Q4", "Nov": "Q4", "Dec": "Q4",
}

MONTH_TO_HALF = {
    "Jan": "H1", "Feb": "H1", "Mar": "H1", "Apr": "H1", "May": "H1", "Jun": "H1",
    "Jul": "H2", "Aug": "H2", "Sep": "H2", "Oct": "H2", "Nov": "H2", "Dec": "H2",
}

COLORS = {
    "navy": "#142B4A",
    "dark_blue": "#1E3A5F",
    "teal": "#00A6A6",
    "green": "#16A36A",
    "orange": "#F59E0B",
    "red": "#DC3545",
    "background": "#F4F7FB",
    "white": "#FFFFFF",
    "text": "#263445",
    "muted": "#64748B",
    "border": "#E2E8F0",
}

PRODUCT_COLORS = {
    "Min": "#142B4A",
    "Syn": "#00A6A6",
    "DEO": "#1E3A5F",
    "Fluids": "#F59E0B",
}

# Achievement Thresholds
THRESHOLD_GREEN = 100.0
THRESHOLD_ORANGE = 80.0

TRANSLATIONS = {
    "ar": {
        "page_title": "لوحة تحليل أداء المبيعات والمستهدفات",
        "banner_badge": "EXECUTIVE SALES INTELLIGENCE",
        "banner_title": "لوحة تحليل أداء المبيعات والمستهدفات",
        "banner_sub": "مقارنة المستهدف بالمبيعات الفعلية • تحليل المنتجات والفترات الزمنية",
        "sidebar_title": "لوحة التحكم والفلاتر",
        "language": "اللغة / Language",
        "upload_label": "تحديث ملف Excel (اختياري)",
        "year_filter": "السنة (Year)",
        "month_filter": "الشهر (Month)",
        "product_filter": "فئة المنتج (Product)",
        "period_filter": "نوع الفترة (Period)",
        "analysis_type": "نوع التحليل (Analysis View)",
        "exclude_future_zeros": "استبعاد الأشهر المستقبلية الصفرية من نسب الإنجاز",
        "all_years": "جميع السنوات",
        "all_months": "جميع الأشهر",
        "all_products": "جميع المنتجات",
        "period_all": "الكل (شهري / ربعي / نصفي)",
        "period_monthly": "شهري (Monthly)",
        "period_quarterly": "ربع سنوي (Quarterly)",
        "period_half": "نصف سنوي (Half-Yearly)",
        "view_overview": "نظرة عامة شاملة (Executive Overview)",
        "view_products": "تحليل المنتجات (Product Deep-Dive)",
        "view_periods": "التحليل الربعي والنصفي (Q1-Q4 & H1-H2)",
        "view_tables": "الجداول والتصدير والتدقيق (Data & Audit)",
        "kpi_target": "إجمالي المستهدف (Total Target)",
        "kpi_actual": "إجمالي المبيعات الفعلية (Total Actual)",
        "kpi_ach": "نسبة التحقيق (Achievement %)",
        "kpi_rem": "المتبقي من المستهدف (Remaining Target)",
        "kpi_best_month": "أفضل شهر أداءً (Best Month)",
        "kpi_best_prod": "أفضل منتج أداءً (Best Product)",
        "sec_main_charts": "تحليل أداء المبيعات الرئيسي",
        "chart_tva": "مقارنة المستهدف بالمبيعات الفعلية (Target vs Actual)",
        "chart_trend": "تطور المبيعات الشهرية (Monthly Sales Trend)",
        "chart_ach": "نسبة تحقيق المستهدف % (Achievement Percentage)",
        "chart_prod": "أداء فئات المنتجات (Product Performance)",
        "chart_annual": "المقارنة السنوية (Annual Comparison)",
        "chart_yoy_month": "مقارنة الأشهر بين السنوات (Monthly YoY Comparison)",
        "sec_prod_analysis": "التحليل التفصيلي لفئات المنتجات",
        "select_product": "اختر فئة المنتج للتحليل العميق:",
        "variance": "الانحراف (Variance)",
        "sec_quarterly": "التحليل الربع سنوي (Quarterly Analysis: Q1 – Q4)",
        "sec_half": "التحليل النصف سنوي (Half-Yearly Analysis: H1 – H2)",
        "sec_tables": "الجداول التفصيلية وتصدير البيانات",
        "audit_title": "تنبيهات تدقيق البيانات ومطابقة Excel",
        "audit_ok": "تم التحقق من جميع البيانات ومطابقة الإجماليات بنجاح.",
        "download_excel": "تنزيل التقرير الكامل (Excel)",
        "download_csv": "تنزيل الجدول الحالي (CSV)",
        "target": "المستهدف (Target)",
        "actual": "الفعلي (Actual)",
        "achievement": "نسبة التحقيق %",
        "remaining": "المتبقي (Remaining)",
        "status": "الحالة",
        "status_achieved": "محقق / متجاوز",
        "status_warning": "يحتاج متابعة",
        "status_low": "انخفاض عن المستهدف",
        "status_na": "غير متاح / فترة مستقبلية",
        "sheets_loaded": "أوراق العمل المقروءة من الملف:",
        "unit_label": "طن / وحدة قياسية",
    },
    "en": {
        "page_title": "Sales Target & Performance Dashboard",
        "banner_badge": "EXECUTIVE SALES INTELLIGENCE",
        "banner_title": "SALES PERFORMANCE & TARGET ANALYTICS",
        "banner_sub": "Target vs Actual Tracking • Product Mix & Period Intelligence",
        "sidebar_title": "Controls & Filters",
        "language": "Language / اللغة",
        "upload_label": "Upload Updated Excel File (Optional)",
        "year_filter": "Year Selection",
        "month_filter": "Month Selection",
        "product_filter": "Product Category",
        "period_filter": "Period Selection",
        "analysis_type": "Analysis View",
        "exclude_future_zeros": "Exclude Future Zero Months from Achievement %",
        "all_years": "All Years",
        "all_months": "All Months",
        "all_products": "All Products",
        "period_all": "All Periods",
        "period_monthly": "Monthly",
        "period_quarterly": "Quarterly (Q1–Q4)",
        "period_half": "Half-Yearly (H1–H2)",
        "view_overview": "Executive Overview",
        "view_products": "Product Deep-Dive",
        "view_periods": "Quarterly & Half-Yearly Analysis",
        "view_tables": "Data Tables, Exports & Audit",
        "kpi_target": "Total Target",
        "kpi_actual": "Total Actual",
        "kpi_ach": "Achievement %",
        "kpi_rem": "Remaining Target",
        "kpi_best_month": "Best Performing Month",
        "kpi_best_prod": "Best Performing Product",
        "sec_main_charts": "Core Sales Performance Analytics",
        "chart_tva": "Target vs Actual Comparison",
        "chart_trend": "Monthly Sales Trend",
        "chart_ach": "Target Achievement Percentage (%)",
        "chart_prod": "Product Category Performance",
        "chart_annual": "Annual Comparison (Target vs Actual)",
        "chart_yoy_month": "Monthly Performance Across Years (YoY)",
        "sec_prod_analysis": "Product Category Deep-Dive",
        "select_product": "Select Product Category:",
        "variance": "Variance",
        "sec_quarterly": "Quarterly Analysis (Q1 – Q4)",
        "sec_half": "Half-Yearly Analysis (H1 – H2)",
        "sec_tables": "Executive Data Tables & Exports",
        "audit_title": "Data Audit & Excel Reconciliation Alerts",
        "audit_ok": "All data verified and reconciled successfully.",
        "download_excel": "Download Full Report (Excel)",
        "download_csv": "Download Active Table (CSV)",
        "target": "Target",
        "actual": "Actual",
        "achievement": "Achievement %",
        "remaining": "Remaining Target",
        "status": "Status",
        "status_achieved": "Achieved / Exceeded",
        "status_warning": "Needs Attention",
        "status_low": "Below Target",
        "status_na": "N/A / Future Period",
        "sheets_loaded": "Workbook Sheets Loaded:",
        "unit_label": "Tons / Standard Units",
    },
}
