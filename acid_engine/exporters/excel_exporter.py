# acid_engine/exporters/excel_exporter.py
# Экспорт отчёта о валидации в Excel (.xlsx)

import os
from typing import List, Union, Dict, Any
from ..core import ErrorRecord

def export_to_excel(errors: List[Union[ErrorRecord, Dict[str, Any]]], output_path: str = "validation_report.xlsx"):
    """
    Сохраняет список ошибок в Excel-файл.
    Принимает как объекты ErrorRecord, так и словари.
    """
    try:
        import openpyxl
    except ImportError:
        raise ImportError("openpyxl is required for Excel export. Install it with: pip install openpyxl")

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Violations"

    # Заголовки
    headers = ["Row Data", "Contract", "Violation", "Expected", "Received", "Reason", "Message"]
    ws.append(headers)

    # Данные
    for err in errors:
        if isinstance(err, ErrorRecord):
            ws.append([
                str(err.row),
                err.contract_name or "",
                err.violation or "",
                err.expected or "",
                err.received or "",
                err.reason or "",
                err.message or ""
            ])
        elif isinstance(err, dict):
            ws.append([
                str(err.get("row", "")),
                err.get("contract_name", ""),
                err.get("violation", ""),
                err.get("expected", ""),
                err.get("received", ""),
                err.get("reason", ""),
                err.get("message", "")
            ])
        else:
            ws.append([str(err), "", "", "", "", "", ""])

    # Автоширина колонок (приблизительно)
    for col in ws.columns:
        max_len = 0
        col_letter = col[0].column_letter
        for cell in col:
            if cell.value:
                max_len = max(max_len, len(str(cell.value)))
        ws.column_dimensions[col_letter].width = min(max_len + 2, 60)

    wb.save(output_path)
    return output_path