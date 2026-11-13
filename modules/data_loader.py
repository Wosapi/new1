import pandas as pd
import os
from datetime import datetime

def load_data(uploaded_file=None):
    """
    تحميل بيانات Excel أو XLSB الافتراضية أو المرفوعة من المستخدم مع التعامل الآمن مع الأخطاء.
    """
    default_path = "data/Total_Sales.xlsb"  # أو sales_data.xlsx حسب اسم الملف في المستودع
    alternative_path = "data/sales_data.xlsx"
    
    try:
        if uploaded_file is not None:
            file_name = uploaded_file.name
            update_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            # تحديد محرك القراءة بناءً على الامتداد
            engine = 'pyxlsb' if file_name.endswith('.xlsb') else None
            xls = pd.ExcelFile(uploaded_file, engine=engine)
        elif os.path.exists(default_path):
            file_name = "Total_Sales.xlsb (Default)"
            update_time = datetime.fromtimestamp(os.path.getmtime(default_path)).strftime("%Y-%m-%d %H:%M:%S")
            xls = pd.ExcelFile(default_path, engine='pyxlsb')
        elif os.path.exists(alternative_path):
            file_name = "sales_data.xlsx (Default)"
            update_time = datetime.fromtimestamp(os.path.getmtime(alternative_path)).strftime("%Y-%m-%d %H:%M:%S")
            xls = pd.ExcelFile(alternative_path)
        else:
            return None, None, None, None, "لم يتم العثور على ملف البيانات الافتراضي في المستودع (تأكد من وجود مجلد data ورفع الملف إليه على GitHub، أو ارفعه يدوياً من القائمة الجانبية)."

        # قراءة الأوراق المطلوبة (تأكد من مطابقة أسماء الأوراق لملفك أو اجعلها مرنة)
        sheets = xls.sheet_names
        
        # محاولة قراءة الجداول بناءً على أسماء الأوراق المتاحة
        actual_df = pd.read_excel(xls, sheet_name=sheets[0]) if len(sheets) > 0 else pd.DataFrame()
        annual_target_df = pd.read_excel(xls, sheet_name=sheets[1]) if len(sheets) > 1 else pd.DataFrame()
        monthly_target_df = pd.read_excel(xls, sheet_name=sheets[2]) if len(sheets) > 2 else pd.DataFrame()
        
        metadata = {
            "file_name": file_name,
            "update_time": update_time
        }
        
        return actual_df, annual_target_df, monthly_target_df, metadata, None
        
    except Exception as e:
        return None, None, None, None, f"حدث خطأ أثناء قراءة ملف البيانات: {str(e)}"
