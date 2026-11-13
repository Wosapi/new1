"""
Data Loading Module:
Reads all sheets from .xlsb or .xlsx workbooks without modifying the source file,
identifies the 'Target' sheet dynamically, and preserves exact raw cell values.
"""

from pathlib import Path
from typing import Dict, Tuple, Union, IO
import pandas as pd
import streamlit as st
from config import DEFAULT_EXCEL_CANDIDATES


def resolve_excel_source(uploaded_file=None) -> Union[Path, IO]:
    """Resolve uploaded file or locate the default workbook in repository."""
    if uploaded_file is not None:
        return uploaded_file
    for candidate in DEFAULT_EXCEL_CANDIDATES:
        if candidate.exists():
            return candidate
    raise FileNotFoundError(
        "لم يتم العثور على ملف Excel في مجلد data/. يرجى رفع الملف أو وضعه في data/Total_Sales.xlsb"
    )


def _detect_engine(source: Union[Path, IO]) -> str:
    """Detect appropriate pandas Excel engine based on file extension."""
    name = source.name if hasattr(source, "name") else str(source)
    ext = Path(name).suffix.lower()
    if ext == ".xlsb":
        return "pyxlsb"
    return "openpyxl"


@st.cache_data(show_spinner=False)
def load_all_sheets(file_bytes: bytes, file_name: str) -> Tuple[Dict[str, pd.DataFrame], str]:
    """
    Read all sheets from the Excel workbook into raw DataFrames (header=None)
    to preserve exact layout, merged headers, notes, and formulas.
    """
    import io

    ext = Path(file_name).suffix.lower()
    engine = "pyxlsb" if ext == ".xlsb" else "openpyxl"
    buffer = io.BytesIO(file_bytes)

    try:
        excel_file = pd.ExcelFile(buffer, engine=engine)
    except ImportError as exc:
        raise ImportError(
            f"المكتبة المطلوبة لقراءة ملفات {ext} غير مثبتة ({engine}). يرجى تثبيتها عبر requirements.txt."
        ) from exc
    except Exception as exc:
        raise RuntimeError(f"تعذر قراءة ملف Excel ({file_name}): {exc}") from exc

    sheets_dict: Dict[str, pd.DataFrame] = {}
    target_sheet_key = None

    for sheet_name in excel_file.sheet_names:
        df_raw = pd.read_excel(excel_file, sheet_name=sheet_name, header=None)
        sheets_dict[sheet_name] = df_raw
        if sheet_name.strip().lower() == "target":
            target_sheet_key = sheet_name

    if target_sheet_key is None:
        raise ValueError(
            f"لم يتم العثور على شيت باسم 'Target'. الشيتات المتوفرة: {excel_file.sheet_names}"
        )

    return sheets_dict, target_sheet_key
