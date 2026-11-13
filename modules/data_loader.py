import pandas as pd
import os
from datetime import datetime

def load_data(uploaded_file=None):
    """
    تحميل بيانات Excel الافتراضية أو المرفوعة من المستخدم مع التعامل الآمن مع الأخطاء.
    """
    default_path = "data/sales_data.xlsx"
    
    try:
        if uploaded_file is not None:
            xls = pd.ExcelFile(uploaded_file)
            file_name = uploaded_file.name
            update_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        elif os.path.exists(default_path):
            xls = pd.ExcelFile(default_path)
            file_name = "sales_data.xlsx (Default)"
            update_time = datetime.fromtimestamp(os.path.getmtime(default_path)).strftime("%Y-%m-%d %H:%M:%S")
        else:
            return None, None, None, None, "لم يتم العثور على ملف البيانات الافتراضي. يرجى رفع ملف Excel."

        # قراءة الجداول الافتراضية من ملف الإكسل
        actual_df = pd.read_excel(xls, sheet_name="Actuals") if "Actuals" in xls.sheet_names else pd.DataFrame()
        annual_target_df = pd.read_excel(xls, sheet_name="Annual_Targets") if "Annual_Targets" in xls.sheet_names else pd.DataFrame()
        monthly_target_df = pd.read_excel(xls, sheet_name="Monthly_Targets") if "Monthly_Targets" in xls.sheet_names else pd.DataFrame()
        
        metadata = {
            "file_name": file_name,
            "update_time": update_time
        }
        
        return actual_df, annual_target_df, monthly_target_df, metadata, None
        
    except Exception as e:
        return None, None, None, None, f"حدث خطأ أثناء قراءة ملف البيانات: {str(e)}"
