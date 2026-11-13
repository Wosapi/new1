"""
Data Export Module:
Generates formatted Excel (.xlsx) workbooks with multiple sheets and CSV exports.
"""

import io
from typing import Dict
import pandas as pd


def export_to_csv(df: pd.DataFrame) -> bytes:
    """Convert DataFrame to UTF-8-SIG CSV bytes (Excel-friendly for Arabic text)."""
    return df.to_csv(index=False).encode("utf-8-sig")


def export_to_excel(tables: Dict[str, pd.DataFrame]) -> bytes:
    """Export multiple summary DataFrames into a styled OpenPyXL Excel workbook."""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        for sheet_name, df in tables.items():
            if df is None or df.empty:
                continue
            safe_name = sheet_name[:31]
            df.to_excel(writer, sheet_name=safe_name, index=False)
            ws = writer.sheets[safe_name]

            # Format headers and auto-adjust column widths
            from openpyxl.styles import Font, PatternFill, Alignment

            header_fill = PatternFill(start_color="142B4A", end_color="142B4A", fill_type="solid")
            header_font = Font(color="FFFFFF", bold=True)

            for cell in ws[1]:
                cell.fill = header_fill
                cell.font = header_font
                cell.alignment = Alignment(horizontal="center", vertical="center")

            for col in ws.columns:
                max_len = max(len(str(cell.value or "")) for cell in col)
                ws.column_dimensions[col[0].column_letter].width = min(max(max_len + 4, 12), 36)

    return output.getvalue()
