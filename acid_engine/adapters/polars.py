import polars as pl
from ..core import Contract, QualityGate, ErrorRecord

def validate_polars(df: pl.DataFrame, contract: Contract, max_error_rate: float = 0.5,
                    mode: str = "quarantine", collect_errors: bool = True):
    """
    Проверяет Polars DataFrame построчно через контракт.
    Возвращает (valid_rows, errors, summary).
    """
    container = contract.create_container()
    gate = QualityGate(container, max_error_rate=max_error_rate,
                       mode=mode, collect_errors=collect_errors)

    rows = df.to_dicts()
    for row in rows:
        gate.add(row)

    return list(container), gate.error_records, gate.summary()
