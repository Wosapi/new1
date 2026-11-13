import pytest
import pandas as pd
from modules.calculations import calculate_dual_kpis, run_audit_engine
from modules.data_loader import load_data

def test_imports():
    """اختبار استيراد الوحدات بنجاح"""
    assert calculate_dual_kpis is not None
    assert run_audit_engine is not None
    assert load_data is not None

def test_kpi_calculations():
    """اختبار دقة حساب المستهدفات والفعلي ونسب الإنجاز"""
    df_actual = pd.DataFrame({'Year': [2026], 'Actual_Sales': [67.16]})
    df_annual = pd.DataFrame({'Year': [2026], 'Annual_Target': [84.07]})
    df_monthly = pd.DataFrame({'Year': [2026], 'Monthly_Target': [70.0]})

    kpis = calculate_dual_kpis(df_actual, df_annual, df_monthly, [2026])

    assert kpis['total_actual'] == 67.16
    assert kpis['total_annual_target'] == 84.07
    # التحقق من أن النسبة تعكس بدقة القيمة المطلوبة ولا تعود بخطأ 95.8% الوهمي
    expected_achievement = round((67.16 / 84.07) * 100, 2)
    assert kpis['annual_achievement'] == expected_achievement

def test_missing_values_handling():
    """اختبار التعامل مع القيم المفقودة أو الصفرية لتجنب القسمة على صفر"""
    df_actual = pd.DataFrame({'Year': [2026], 'Actual_Sales': [100]})
    df_annual = pd.DataFrame({'Year': [2026], 'Annual_Target': [0]})
    df_monthly = pd.DataFrame({'Year': [2026], 'Monthly_Target': [0]})

    kpis = calculate_dual_kpis(df_actual, df_annual, df_monthly, [2026])
    assert kpis['annual_achievement'] == 0.0
    assert kpis['monthly_achievement'] == 0.0
