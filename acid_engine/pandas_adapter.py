import pandas as pd
from .core import Contract, QualityGate, ErrorRecord

def validate_dataframe(df: pd.DataFrame, contract: Contract, max_error_rate: float = 0.5,
                       mode: str = "quarantine", collect_errors: bool = True):
    """
    Проверяет DataFrame построчно через контракт.
    Возвращает (valid_rows, errors, summary).
    """
    container = contract.create_container()
    gate = QualityGate(container, max_error_rate=max_error_rate,
                       mode=mode, collect_errors=collect_errors)

    for _, row in df.iterrows():
        row_dict = row.to_dict()
        gate.add(row_dict)

    return list(container), gate.error_records, gate.summary()